import sys
from typing import Dict

import click

from eips.eips import EIPs
from eips.logging import setDebugLogging


@click.group()
@click.option("-d", "--debug", is_flag=True, default=False)
def main(debug: bool) -> None:
    """CLI"""
    if debug:
        setDebugLogging()


@main.command(help="Display an EIP")
@click.argument("eip_id", type=int)
@click.option(
    "-i", "--headers", "headers", help="Show headers only", is_flag=True, default=False
)
@click.option("-o", "--output", type=click.Choice(["json", "text"]), default="text")
def show(eip_id: int, headers: bool, output: str) -> None:
    eips = EIPs()
    eips.repo_fetch()
    res = eips.get(eip_id)

    if len(res) > 2:
        click.echo("Found more than one EIP")
        sys.exit(1)
    elif len(res) < 1:
        if output == "JSON":
            click.echo("[]")
        else:
            click.echo("EIP not found")
        sys.exit(0)

    eip = res[0]

    if output == "json":
        exclude: Dict[str, bool] = {}

        if headers:
            exclude["body"] = True

        click.echo(eip.json(exclude=exclude))
    else:
        click.echo("---")
        for k, v in eip.headers.items():
            click.echo(f"{k}: {', '.join(v) if isinstance(v, list) else v}")
        click.echo("---\n")

        if not headers:
            click.echo(eip.body)


@main.command(help="Check that EIPs in repo can be parsed")
def check() -> None:
    eips = EIPs()

    if eips.check():
        click.echo("No errors found")
        sys.exit(0)

    click.echo("Errors found")
    sys.exit(1)
