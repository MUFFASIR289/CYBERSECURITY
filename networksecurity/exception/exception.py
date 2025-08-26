import os
import sys

class NetworkSecurityException(Exception):
    def __init__(self, error_message: Exception, error_detail: sys):
        super().__init__(str(error_message))
        self.error_message = error_message

        _, _, exc_tb = sys.exc_info()
        if exc_tb is not None:
            self.filename = exc_tb.tb_frame.f_code.co_filename
            self.lineno = exc_tb.tb_lineno
        else:
            self.filename = "Unknown"
            self.lineno = -1

    def __str__(self):
        return f"Error occurred in Python script [{self.filename}] at line [{self.lineno}]: {self.error_message}"