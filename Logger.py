class Logger:
    verbose: bool = True

    @classmethod
    def log(cls, *args, **kwargs):
        if cls.verbose:
            print(*args, **kwargs)
