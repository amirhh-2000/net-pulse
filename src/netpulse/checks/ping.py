import socket
import time

from netpulse.models import PingResult


def check_ping(host: str, port: int = 80, timeout: int = 2) -> PingResult:
    """
    Checks connectivity to a host via a TCP handshake.
    Does not use ICMP (requires root), uses TCP (user-space friendly).
    """
    start_time = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            latency = time.time() - start_time
            return PingResult(
                target=host,
                host=host,
                is_successful=True,
                latency=latency,
            )
    except socket.timeout:
        return PingResult(
            target=host,
            is_successful=False,
            latency=0.0,
            error="Connection timed out",
        )
    except socket.gaierror:
        return PingResult(
            target=host,
            is_successful=False,
            latency=0.0,
            error="DNS resolution failed",
        )
    except ConnectionRefusedError:
        return PingResult(
            target=host,
            is_successful=False,
            latency=0.0,
            error="Connection refused (Port closed)",
        )
    except Exception as e:
        return PingResult(
            target=host,
            is_successful=False,
            latency=0.0,
            error=str(e),
        )
