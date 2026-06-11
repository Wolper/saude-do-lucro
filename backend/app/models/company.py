from dataclasses import dataclass


@dataclass(slots=True)
class Company:
    id: int
    name: str
