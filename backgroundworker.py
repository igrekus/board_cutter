from typing import Any

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, QThreadPool


class Task(QRunnable):
    def __init__(self, fn=None, fn_started=None, fn_finished=None, fn_failed=None, cancel_token=None, **kwargs):
        super().__init__()
        self.fn = fn
        self.fn_started = fn_started
        self.fn_finished = fn_finished
        self.fn_failed = fn_failed
        self.cancel_token = cancel_token
        self.kwargs = kwargs

    def run(self):
        if self.fn_started:
            self.fn_started()
        result = False
        try:
            result = self.fn(self.cancel_token, **self.kwargs)
        except Exception as ex:
            if self.fn_failed:
                self.fn_failed(ex)
        if self.fn_finished:
            self.fn_finished(result)


class CancelToken:
    def __init__(self):
        self.cancelled = False


class BackgroundWorker(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._threads = QThreadPool()

    def runTask(self, fn=None, fn_started=None, fn_finished=None, fn_failed=None, token=None, **kwargs):
        self._threads.start(
            Task(
                fn=fn,
                fn_started=fn_started,
                fn_finished=fn_finished,
                fn_failed=fn_failed,
                cancel_token=token,
                kwargs=kwargs,
            )
        )
