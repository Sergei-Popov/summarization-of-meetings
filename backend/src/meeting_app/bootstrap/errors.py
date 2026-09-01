class ApplicationStartupError(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code
        self.stage = "startup"
        self.retryable = False
        self.cleanup_failed = False
