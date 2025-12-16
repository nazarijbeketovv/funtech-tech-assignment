from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class UserDTO:
    id: int
    email: str
    created_at: datetime


@dataclass(slots=True, kw_only=True)
class UserCreateDTO:
    email: str
    password: str
