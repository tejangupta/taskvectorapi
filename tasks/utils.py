from .logger import setup_logger
from .exception import AppException
from sentence_transformers import SentenceTransformer
import numpy as np

logger = setup_logger()
model = None


def get_model():
    """
    initializes this model only once (lazy initialization) with the 'all-MiniLM-L6-v2' model,
    which is an efficient choice for generating text embeddings.
    Handles any exceptions during model loading and logs them.
    """
    global model

    if model is None:
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.error(f"Error initializing SentenceTransformer model: {e}")
            raise AppException("Failed to load SentenceTransformer model.") from e

    return model


def cosine_similarity(a, b):
    """
    Calculate the cosine similarity between two vectors.
    Validates input vectors for compatibility.
    """
    if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
        raise AppException("Inputs must be NumPy arrays.")

    if a.shape != b.shape:
        raise AppException("Input vectors must be of the same shape.")

    try:
        similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        return similarity
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {e}")
        raise AppException("Failed to calculate cosine similarity.") from e
