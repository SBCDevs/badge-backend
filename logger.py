from traceback import format_exc
from time import strftime
from utils import exceptions

class Logger:
    def __init__(self):
        self.__debug_enabled = False

    def raw(self, message: str, level="", show_level=True):
        if show_level: print(f"[{level}] {message}")
        else: print(message)
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(f"{strftime('[%m/%d/%Y %H:%M:%S]')} [{level}] {message}\n")
    
    def log_traceback(self, error: Exception = None, traceback: str = None):
        if error:
            exceptions.log_error(error)
            try: raise error from error
            except Exception: traceback = format_exc()
        if traceback:
            for line in traceback.split("\n"):
                self.raw(message=line, level="TRACEBACK", show_level=False)

    def debug(self, message: str):
        if not self.__debug_enabled: return
        self.raw(message=message, level="DEBUG")

    def success(self, message: str):
        self.raw(message=message, level="SUCCESS")

    def info(self, message: str):
        self.raw(message=message, level="INFO")

    def warn(self, message: str):
        self.raw(message=message, level="WARN")

    def error(self, message: str):
        self.raw(message=message, level="ERROR")

    def fatal(self, message: str, traceback: str = None, error: Exception = None):
        self.raw(message=message, level="FATAL")
        if error:
            try: raise error from error
            except Exception: traceback = format_exc()
        if traceback:
            self.log_traceback(traceback=traceback)