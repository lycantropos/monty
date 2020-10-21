from typing import Any


class Secured:
    def __init__(self, value: Any) -> None:
        self.value = value

    def __repr__(self) -> str:
        return '...' if self.value is not None else repr(self.value)
