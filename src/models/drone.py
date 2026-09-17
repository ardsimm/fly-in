from dataclasses import dataclass
from typing import List

from src.models import Node


@dataclass
class Drone:
    id: int
    name: str
    path: List[Node]
