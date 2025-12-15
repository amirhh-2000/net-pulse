import socket
import ssl
from datetime import datetime, timezone
from typing import cast
from urllib.parse import urlparse

from netpulse.models import SSLResult


def check_ssl(target: str, timeout: int = 5) -> SSLResult:
    """
    Checks SSL certificate expiry days.
    """
    # Handle URL vs Domain
    if "://" in target:
        hostname = urlparse(target).hostname or target
    else:
        hostname = target

    context = ssl.create_default_context()

    try:
        with socket.create_connection((hostname, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

                if not cert:
                    return SSLResult(
                        target=hostname,
                        is_successful=False,
                        latency=0,
                        error="No certificate found",
                    )

                not_after_str = cast(str, cert.get("notAfter", ""))

                # Parse date (Example: 'May 20 12:00:00 2025 GMT')
                expiry_date = datetime.strptime(not_after_str, r"%b %d %H:%M:%S %Y %Z")
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)

                remaining = expiry_date - datetime.now(timezone.utc)

                issuer_info = cert.get("issuer", ())
                issuer_dict = {}

                if isinstance(issuer_info, (tuple, list)):
                    for rdn in issuer_info:
                        for key, value in rdn:
                            issuer_dict[key] = value

                issuer_name = str(issuer_dict.get("commonName", "Unknown"))

                return SSLResult(
                    target=hostname,
                    is_successful=remaining.days > 0,
                    latency=0.0,
                    days_remaining=remaining.days,
                    issuer=issuer_name,
                    is_valid=remaining.days > 0,
                )

    except socket.timeout:
        return SSLResult(
            target=hostname,
            is_successful=False,
            latency=0,
            error="Connection timed out",
        )
    except socket.gaierror:
        return SSLResult(
            target=hostname,
            is_successful=False,
            latency=0,
            error="DNS resolution failed",
        )
    except Exception as e:
        return SSLResult(
            target=hostname,
            is_successful=False,
            latency=0,
            error=str(e),
        )
