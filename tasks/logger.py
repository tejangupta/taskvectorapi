import logging
import logging.handlers
import os
from django.conf import settings


def setup_logger():
    """
    Set up and configure a logger for the tasks app.
    Log rotation is used to limit the log file size.
    """
    # Log file name
    log_file = 'tasks.log'

    # Log file path
    log_dir = os.path.join(settings.BASE_DIR, 'log')
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, log_file)

    # Configure the logger
    logger = logging.getLogger('tasks_logger')
    logger.setLevel(logging.INFO)

    # Creating and setting the file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Adding the handler to the logger
    logger.addHandler(file_handler)

    return logger
