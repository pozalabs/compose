import signal


class SignalHandler:
    def __init__(self):
        self._received_signal = False

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        self._received_signal = True

    @property
    def received_signal(self) -> bool:
        return self._received_signal
