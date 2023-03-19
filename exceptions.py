class InvalidCLIArguement(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class StrategyNotExists(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidStrategy(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidPair(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidLongCondition(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidShortCondition(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidPortoflio(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidDataset(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)