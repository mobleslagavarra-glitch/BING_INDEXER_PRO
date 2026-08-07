from dataclasses import dataclass
from typing import Optional


@dataclass
class Domain:

    id: Optional[int] = None

    domain: str = ""

    api_key: str = ""

    enabled: bool = True