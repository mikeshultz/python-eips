"""CLI defining `eips` and `ercs` commands."""

import sys

import click

from eips.eips import EIPs, ERCs
from eips.logging import set_debug_logging


@click.group()
@click.option("-d", "--debug", is_flag=True, default=False)
def eips_cli(debug: bool) -> None:
    """Eips command"""
    if debug:
        set_debug_logging()


@eips_cli.command(help="Display an EIP")
@click.argument("eip_id", type=int)
@click.option(
    "-i", "--headers", "headers", help="Show headers only", is_flag=True, default=False
)
@click.option("-o", "--output", type=click.Choice(["json", "text"]), default="text")
def show(eip_id: int, headers: bool, output: str) -> None:
    """Display an EIP."""
    eips = EIPs()
    eips.repo_fetch()
    res = list(eips.get(eip_id))

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
        exclude = dict()

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


@eips_cli.command(help="Check that EIPs in repo can be parsed")
def check() -> None:
    """Check that EIPs in repo can be parsed."""
    eips = EIPs()

    if eips.check():
        click.echo("No errors found")
        sys.exit(0)

    click.echo("Errors found")
    sys.exit(1)


@click.group()
@click.option("-d", "--debug", is_flag=True, default=False)
def ercs_cli(debug: bool) -> None:
    """`ercs` command."""
    if debug:
        set_debug_logging()


@ercs_cli.command("show", help="Display an ERC")
@click.argument("erc_id", type=int)
@click.option(
    "-i", "--headers", "headers", help="Show headers only", is_flag=True, default=False
)
@click.option("-o", "--output", type=click.Choice(["json", "text"]), default="text")
def ercs_show(erc_id: int, headers: bool, output: str) -> None:
    """Display an ERC."""
    ercs = ERCs()
    ercs.repo_fetch()
    res = list(ercs.get(erc_id))

    if len(res) > 2:
        click.echo("Found more than one ERC")
        sys.exit(1)
    elif len(res) < 1:
        if output == "JSON":
            click.echo("[]")
        else:
            click.echo("ERC not found")
        sys.exit(0)

    erc = res[0]

    if output == "json":
        exclude = dict()

        if headers:
            exclude["body"] = True

        click.echo(erc.json(exclude=exclude))
    else:
        click.echo("---")
        for k, v in erc.headers.items():
            click.echo(f"{k}: {', '.join(v) if isinstance(v, list) else v}")
        click.echo("---\n")

        if not headers:
            click.echo(erc.body)


@ercs_cli.command("check", help="Check that ERCs in repo can be parsed")
def ercs_check() -> None:
    """Check that ERCs in repo can be parsed."""
    ercs = ERCs()

    if ercs.check():
        click.echo("No errors found")
        sys.exit(0)

    click.echo("Errors found")
    sys.exit(1)
