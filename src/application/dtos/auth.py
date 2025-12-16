from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class TokenDTO:
    access_token: str
    token_type: str = "bearer"


@dataclass(slots=True, kw_only=True)
class TokenDataDTO:
    user_id: int | None = None
    email: str | None = None
