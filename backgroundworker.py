from typing import Any

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, QThreadPool


class Task(QRunnable):
    def __init__(self, fn=None, fn_started=None, fn_finished=None, fn_failed=None,
                 cancel_token=None, fn_progress=None, **kwargs):
        super().__init__()
        self.fn = fn
        self.fn_started = fn_started
        self.fn_finished = fn_finished
        self.fn_failed = fn_failed
        self.cancel_token = cancel_token
        self.fn_progress = fn_progress
        self.kwargs = kwargs

    def run(self):
        if self.fn_started:
            self.fn_started()
        result = False
        try:
            result = self.fn(self.cancel_token, fn_progress=self.fn_progress, **self.kwargs)
        except Exception as ex:
            if self.fn_failed:
                self.fn_failed(ex)
            result = result, str(ex)
            print('Exception:', ex)
        if self.fn_finished:
            self.fn_finished(result)


class CancelToken:
    def __init__(self):
        self.cancelled = False

    def __str__(self):
        return f'<{self.__class__.__name__}> (cancelled={self.cancelled})'


class BackgroundWorker(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._threads = QThreadPool()

    def runTask(self, fn=None, fn_started=None, fn_finished=None, fn_failed=None, token=None, fn_progress=None, **kwargs):
        self._threads.start(
            Task(
                fn=fn,
                fn_started=fn_started,
                fn_finished=fn_finished,
                fn_failed=fn_failed,
                cancel_token=token,
                fn_progress=fn_progress,
                **kwargs,
            )
        )


class TaskResult:
    def __init__(self, ok, data):
        self.ok = ok
        self.data = data

    @property
    def values(self):
        return self.ok, self.data
