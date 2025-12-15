from typing import Optional

from pydantic import BaseModel, Field


class CheckResult(BaseModel):
    """
    Base model for all check results.
    """

    target: str
    is_successful: bool
    latency: float = Field(
        ...,
        ge=0,
        description="Latency in seconds",
    )
    error: Optional[str] = None


class PingResult(CheckResult):
    host: str = ""


class HTTPResult(CheckResult):
    status_code: Optional[int] = None
    url: str = ""


class DNSResult(CheckResult):
    ip: Optional[str] = None
    domain: str = ""


class SSLResult(CheckResult):
    days_remaining: int = 0
    issuer: Optional[str] = None
    is_valid: bool = False
