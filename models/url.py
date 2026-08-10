from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class UrlRecord:

    id: Optional[int]

    domain_id: int

    url: str

    status: str = "PENDIENTE"

    response_code: int | None = None

    response_message: str = ""