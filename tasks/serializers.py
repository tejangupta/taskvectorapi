from .logger import setup_logger
from rest_framework import serializers
from .models import Task
from django.utils import timezone

logger = setup_logger()


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.

    Includes fields for id, title, description, status, deadline, vector representation, and owner.
    The vector representation is read-only and automatically generated.
    The owner field is also read-only and set to the current user when a task is created.
    """
    vector_representation = serializers.JSONField(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'vector_representation', 'owner']
        read_only_fields = ['owner', 'vector_representation']

    def validate_deadline(self, value):
        """
        Validates that the deadline is not set in the past.

        Args:
            value (datetime): The deadline date and time to be validated.

        Returns:
            datetime: The validated deadline date and time.

        Raises:
            serializers.ValidationError: If the deadline is in the past.
        """
        logger.info("Validating deadline")
        if value < timezone.now():
            logger.warning(f"Attempted to set deadline in the past: {value}")
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    def create(self, validated_data):
        """
        Creates and returns a new Task instance, setting the owner to the current user.

        Args:
            validated_data (dict): Data for the new Task instance.

        Returns:
            Task: The newly created Task instance.

        Raises:
            serializers.ValidationError: If there is an error during creation.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        try:
            task = Task.objects.create(**validated_data)
            logger.info(f"Created new task: {task.id}")
            return task
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise serializers.ValidationError(f"Error creating task: {e}")

    def update(self, instance, validated_data):
        """
        Updates and returns an existing Task instance.

        Args:
            instance (Task): The Task instance to be updated.
            validated_data (dict): Data to update the Task instance.

        Returns:
            Task: The updated Task instance.

        Raises:
            serializers.ValidationError: If there is an error during update.
        """
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            logger.info(f"Updated task: {instance.id}")
            return instance
        except Exception as e:
            logger.error(f"Error updating task: {instance.id}, {e}")
            raise serializers.ValidationError(f"Error updating task: {e}")
