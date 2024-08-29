
class NoValidWellError(RuntimeError):
    def __init__(self, *args: object) -> None:
        pass

class SourceRunout(NoValidWellError):
    def __init__(self, *args: object) -> None:
        pass
