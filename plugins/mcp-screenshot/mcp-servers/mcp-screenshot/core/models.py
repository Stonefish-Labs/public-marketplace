from dataclasses import dataclass


@dataclass
class WindowInfo:
    id: int
    title: str
    app: str
    bounds: tuple[int, int, int, int]
