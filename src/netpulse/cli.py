import time

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from netpulse.checks.dns import check_dns
from netpulse.checks.http import check_http
from netpulse.checks.ping import check_ping
from netpulse.checks.ssl import check_ssl

app = typer.Typer(help="NetPulse: Developer-friendly Network Diagnostics")
console = Console()


@app.command()
def ping(host: str, port: int = 80, count: int = 1):
    """Check connectivity to a host."""
    for i in range(count):
        result = check_ping(host, port)
        if result.is_successful:
            console.print(
                f"[green]✓[/green] Connected to [bold]{result.target}[/bold] in [cyan]{result.latency:.3f}s[/cyan]"
            )
        else:
            console.print(
                f"[red]✗[/red] Failed to connect to [bold]{result.target}[/bold]: {result.error}"
            )

        if count > 1:
            time.sleep(1)


@app.command()
def http(url: str):
    """Check an HTTP endpoint."""
    with console.status(f"Checking {url}..."):
        result = check_http(url)

    if result.is_successful:
        console.print(
            Panel(
                f"Status: [green]{result.status_code}[/green]\nLatency: [cyan]{result.latency:.3f}s[/cyan]",
                title=f"[bold green]HTTP Check: {result.target}[/bold]",
                expand=False,
            )
        )
    else:
        console.print(f"[red]Error:[/red] {result.error}")


@app.command()
def dns(domain: str):
    """Resolve a domain name."""
    result = check_dns(domain)
    if result.is_successful:
        console.print(
            f"[green]✓[/green] Resolved [bold]{result.domain}[/bold] to [yellow]{result.ip}[/yellow] in {result.latency:.3f}s"
        )
    else:
        console.print(f"[red]DNS Error:[/red] {result.error}")


@app.command()
def ssl(domain: str):
    """Check SSL certificate expiry."""
    with console.status("Verifying SSL certificate..."):
        result = check_ssl(domain)

    if not result.is_successful:
        console.print(f"[red]SSL Error:[/red] {result.error}")
        return

    color = "green" if result.days_remaining > 30 else "red"
    table = Table(title="SSL Report")
    table.add_column("Domain", style="cyan")
    table.add_column("Issuer", style="magenta")
    table.add_column("Days Remaining", style=color)

    table.add_row(result.target, result.issuer, str(result.days_remaining))
    console.print(table)


@app.command()
def monitor(host: str, interval: float = 1.0):
    """Live monitor connectivity to a host (Ctrl+C to stop)."""
    console.print(f"Monitoring [bold cyan]{host}[/bold]... (Press Ctrl+C to stop)")

    try:
        while True:
            result = check_ping(host)
            timestamp = time.strftime("%H:%M:%S")
            if result.is_successful:
                console.print(f"[{timestamp}] [green]✓[/green] {result.latency:.3f}s")
            else:
                console.print(f"[{timestamp}] [red]✗ {result.error}[/red]")
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped.[/yellow]")


if __name__ == "__main__":
    app()
