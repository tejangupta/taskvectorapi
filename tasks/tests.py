from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Task


class TaskAPITestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = get_user_model().objects.create_user(username='user1', password='password1')
        self.user2 = get_user_model().objects.create_user(username='user2', password='password2')

        # Create tasks
        self.task1 = Task.objects.create(title='Task 1', description='Description 1', owner=self.user1,
                                         deadline=timezone.now() + timedelta(days=3))
        self.task2 = Task.objects.create(title='Task 2', description='Description 2', owner=self.user1,
                                         deadline=timezone.now() + timedelta(days=1))

        # Set up client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_task_creation(self):
        """
        Ensure we can create a new task and that vector representation is generated.
        """
        url = reverse('task-list')
        data = {'title': 'New Task', 'description': 'New Description', 'deadline': timezone.now() + timedelta(days=5)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['vector_representation'])
        self.assertEqual(Task.objects.count(), 3)

    def test_task_list_retrieval(self):
        """
        Ensure we can retrieve a list of tasks.
        """
        url = reverse('task-list')
        response = self.client.get(url)

        # Check for pagination
        if 'results' in response.data:
            tasks = response.data['results']
            self.assertEqual(len(tasks), 2)
        else:
            self.assertEqual(len(response.data), 2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_detail_retrieval(self):
        """
        Ensure we can retrieve a single task by id.
        """
        url = reverse('task-detail', kwargs={'pk': self.task1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.task1.pk)

    def test_task_update(self):
        """
        Ensure we can update a task.
        """
        url = reverse('task-detail', kwargs={'pk': self.task1.pk})

        # Prepare new data for update
        updated_data = {
            'title': 'Updated Task Title',
            'description': 'Updated Task Description',
            'deadline': (timezone.now() + timedelta(days=7)).isoformat(),
            'status': 'IN_PROGRESS'  # Assuming 'IN_PROGRESS' is a valid status option
        }

        # Perform the update operation
        response = self.client.put(url, updated_data, format='json')

        # Check if the update was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Retrieve the task again to verify changes
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, updated_data['title'])
        self.assertEqual(self.task1.description, updated_data['description'])
        self.assertEqual(self.task1.status, updated_data['status'])
        self.assertTrue(abs(self.task1.deadline - timezone.now() - timedelta(days=7)) < timedelta(seconds=1))

    def test_task_delete(self):
        """
        Ensure we can delete a task.
        """
        url = reverse('task-detail', kwargs={'pk': self.task1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 1)

    def test_search_tasks(self):
        """
        Ensure we can search tasks based on title or description.
        """
        query = 'Task'
        url = f'/api/tasks/search/{query}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_unauthorized_access(self):
        """
        Ensure unauthorized users cannot access the tasks.
        """
        self.client.force_authenticate(user=None)
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_permission_denied_for_non_owner(self):
        """
        Ensure users can't update or delete tasks they don't own.
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse('task-detail', kwargs={'pk': self.task1.pk})
        data = {'title': 'Unauthorized Update'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_task_with_invalid_data(self):
        """
        Test creating a task with invalid data like missing title or past deadline.
        """
        url = reverse('task-list')

        # Missing title
        data = {'description': 'New Description', 'deadline': timezone.now() + timedelta(days=5)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Past deadline
        data = {'title': 'Task with Past Deadline', 'description': 'Description',
                'deadline': timezone.now() - timedelta(days=1)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_task_to_past_deadline(self):
        """
        Test updating a task to a past deadline.
        """
        url = reverse('task-detail', kwargs={'pk': self.task1.pk})
        data = {'deadline': timezone.now() - timedelta(days=1)}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_nonexistent_task(self):
        """
        Test deletion of a task that doesn't exist.
        """
        url = reverse('task-detail', kwargs={'pk': 9999})  # Non-existent task ID
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_task_search_with_vector_representation(self):
        """
        Test searching tasks based on vector representation.
        """
        # Create tasks with similar and dissimilar titles/descriptions
        self.client.post(reverse('task-list'), {'title': 'Similar Task', 'description': 'This task is similar',
                                                'deadline': timezone.now() + timedelta(days=5)}, format='json')
        self.client.post(reverse('task-list'), {'title': 'Dissimilar Task', 'description': 'This task is different',
                                                'deadline': timezone.now() + timedelta(days=5)}, format='json')

        # Use a query that should match one of the tasks
        query = 'Similar'
        url = f'/api/tasks/search/{query}/'
        response = self.client.get(url)

        # Verify that at least one task matches the search
        self.assertTrue(len(response.data) > 0)
        self.assertTrue(any('Similar Task' in task['title'] for task in response.data))

    def test_permission_denied_for_other_user(self):
        """
        Test that a regular user cannot update or delete tasks owned by another user.
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse('task-detail', kwargs={'pk': self.task1.pk})

        # Attempt to update
        data = {'title': 'Unauthorized Update Attempt'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Attempt to delete
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
