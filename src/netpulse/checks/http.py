import time

import httpx

from netpulse.models import HTTPResult


def check_http(url: str, timeout: int = 5) -> HTTPResult:
    """
    Checks an HTTP endpoint for status code and latency.
    """
    start_time = time.time()
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url)
            latency = time.time() - start_time

            return HTTPResult(
                target=url,
                url=url,
                is_successful=response.status_code < 400,
                status_code=response.status_code,
                latency=latency,
            )
    except httpx.TimeoutException:
        return HTTPResult(
            target=url,
            is_successful=False,
            latency=0.0,
            error="Request timed out",
        )
    except httpx.ConnectError:
        return HTTPResult(
            target=url,
            is_successful=False,
            latency=0.0,
            error="Connection failed",
        )
    except Exception as e:
        return HTTPResult(
            target=url,
            is_successful=False,
            latency=0.0,
            error=str(e),
        )
