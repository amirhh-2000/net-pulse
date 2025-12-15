import time

import dns.resolver

from netpulse.models import DNSResult


def check_dns(domain: str, record_type: str = "A") -> DNSResult:
    """
    Resolves a domain name to an IP address.
    """
    resolver = dns.resolver.Resolver()
    start_time = time.time()
    try:
        answer = resolver.resolve(domain, record_type)
        latency = time.time() - start_time
        ip_address = str(answer[0])

        return DNSResult(
            target=domain,
            domain=domain,
            is_successful=True,
            latency=latency,
            ip=ip_address,
        )
    except dns.resolver.NXDOMAIN:
        return DNSResult(
            target=domain,
            is_successful=False,
            latency=0.0,
            error="Domain not found (NXDOMAIN)",
        )
    except dns.resolver.NoAnswer:
        return DNSResult(
            target=domain,
            is_successful=False,
            latency=0.0,
            error="No answer for this record type",
        )
    except dns.resolver.Timeout:
        return DNSResult(
            target=domain,
            is_successful=False,
            latency=0.0,
            error="DNS query timed out",
        )
    except Exception as e:
        return DNSResult(
            target=domain,
            is_successful=False,
            latency=0.0,
            error=str(e),
        )
