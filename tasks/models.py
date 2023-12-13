import logging
from django.db import models
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Initialize the model
model = SentenceTransformer('all-MiniLM-L6-v2')


class Task(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    deadline = models.DateTimeField()
    vector_representation = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Update vector representation on save
        try:
            self.vector_representation = self.generate_vector_representation()
        except Exception as e:
            # Log the error
            logger.error(f"Error generating vector representation: {e}")
        super(Task, self).save(*args, **kwargs)

    def generate_vector_representation(self):
        # Combine title and description
        combined_text = self.title + ' ' + self.description

        # Generate vector representation
        vector = model.encode(combined_text, convert_to_tensor=True)
        return vector.cpu().numpy().tolist()  # Convert to list for JSONField compatibility

# Add any other models here if needed
