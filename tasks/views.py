from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOwnerOrReadOnly
import numpy as np
from .utils import get_model, cosine_similarity

# Initialize the model for vector encoding
model = get_model()


class TaskViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing tasks in the task management system.
    It supports creating, retrieving, updating, and deleting tasks,
    as well as searching tasks based on text similarity.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        """
        Sets the owner of the task to the current user before saving.
        """
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'], url_path='search/(?P<query>.+)')
    def search_tasks(self, request, query=None):
        """
        Custom action to search tasks based on a provided title, description,
        or a combination of both, using the vector retrieval system.

        Args:
            request: The HTTP request object.
            query (str): The query string to search for.

        Returns:
            Response: A list of tasks that match the search criteria.
        """
        if not query:
            return Response({'message': 'No query provided'}, status=status.HTTP_400_BAD_REQUEST)

        query_vector = model.encode(query, convert_to_tensor=True).cpu().numpy()
        tasks = Task.objects.all()
        similar_tasks = []

        # Compare the query vector with the vector representation of each task
        for task in tasks:
            if task.vector_representation:
                similarity = cosine_similarity(np.array(query_vector), np.array(task.vector_representation))
                if similarity > 0.5:  # Adjust threshold as needed
                    similar_tasks.append(task)

        serializer = TaskSerializer(similar_tasks, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
