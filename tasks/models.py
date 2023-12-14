from .logger import setup_logger
from .exception import AppException
from django.db import models
from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from .utils import get_model

logger = setup_logger()
model = get_model()


class Task(DirtyFieldsMixin, models.Model):
    """
   Task model representing a task in the task management system.
   Includes a title, description, status, deadline, and an automatically
   generated vector representation for enhanced search capabilities.
   """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    title = models.CharField(max_length=200, help_text="Title of the task.")
    description = models.TextField(help_text="Detailed description of the task.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING',
                              help_text="Current status of the task.")
    deadline = models.DateTimeField(help_text="Deadline for task completion.")
    vector_representation = models.JSONField(null=True, blank=True,
                                             help_text="Vector representation of the task for search functionality.")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text="User who owns this task.")

    class Meta:
        ordering = ['deadline']

    def __str__(self):
        """
        Returns a string representation of the Task, which is its title.
        """
        return self.title

    def save(self, *args, **kwargs):
        """
        Overridden save method to generate a vector representation
        whenever a task is created or its title or description is modified.
        """
        if not self.pk or 'title' in self.get_dirty_fields() or 'description' in self.get_dirty_fields():
            self.vector_representation = self.generate_vector_representation()
        super().save(*args, **kwargs)

    def clean(self):
        """
        Custom validation method to ensure the deadline is not set in the past.
        """
        if self.deadline < timezone.now():
            raise ValidationError("Deadline cannot be in the past.")

    def generate_vector_representation(self):
        """
        Generates a vector representation of the task based on its title and description.
        Used for searching tasks based on text similarity.
        """
        logger.info(f"Generating vector representation for Task: {self.title}")
        combined_text = self.title + ' ' + self.description
        try:
            vector = model.encode(combined_text)
            return vector.tolist()
        except Exception as e:
            logger.error(f"Error in generating vector representation for Task: {self.title}: {e}")
            raise AppException(str(e))
