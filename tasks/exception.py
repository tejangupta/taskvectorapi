import sys


class AppException(Exception):
    def __init__(self, error_message):
        """
        Custom exception class for the application.

        :param error_message: The error message describing what went wrong.
        """
        super().__init__(error_message)
        self.error_message = self._format_error_message(error_message)

    def __str__(self):
        return self.error_message

    @staticmethod
    def _format_error_message(error_message):
        """
        Formats the error message to include the file name, line number, and original error message.

        :param error_message: The original error message.
        :return: A formatted error message string.
        """
        exc_type, _, exc_tb = sys.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
        error_type = exc_type.__name__ if exc_type else 'UnknownError'

        formatted_message = (
            f"An error of type '{error_type}' occurred in script '{file_name}' at line {line_number}: {error_message}"
        )
        return formatted_message
