from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from yapilet.cli._di import (
    load_action_chain,
    make_action_usecase,
    make_chat_usecase,
    make_single_usecase,
)


@click.group()
def cli() -> None:
    """YAML-driven API request and action chain runner."""


@cli.command()
@click.argument("config_path", type=click.Path())
@click.option("--user-input", "user_inputs", multiple=True, help="User inputs (repeatable)")
@click.option("--api-key", default=None, envvar="API_KEY", help="API key (or set API_KEY env var)")
@click.option("--mock-echo", is_flag=True, help="Use MockAdapter — echo request offline")
def single(
    config_path: str,
    user_inputs: tuple[str, ...],
    api_key: str | None,
    mock_echo: bool,
) -> None:
    """Run a single API request config (relative path to .yaml file)."""
    uc = make_single_usecase(mock_echo=mock_echo)
    try:
        result = uc.run(config_path, user_inputs=list(user_inputs), api_key=api_key)
    except FileNotFoundError as e:
        click.echo(f"[ERROR] {e}", err=True)
        sys.exit(1)
    if not result.is_success:
        click.echo(f"[ERROR {result.status_code}] {result.error}", err=True)
        sys.exit(1)
    if result.extracted is not None:
        click.echo(result.extracted)
    else:
        click.echo(json.dumps(result.body, ensure_ascii=False))


@cli.command()
@click.argument("chain_path", type=click.Path())
@click.option("--user-input", "user_inputs", multiple=True, help="User inputs (repeatable)")
@click.option("--api-key", default=None, envvar="API_KEY", help="API key (or set API_KEY env var)")
@click.option("--mock-echo", is_flag=True, help="Use MockAdapter — echo request offline")
def action(
    chain_path: str,
    user_inputs: tuple[str, ...],
    api_key: str | None,
    mock_echo: bool,
) -> None:
    """Run an action chain config (relative path to .yaml file)."""
    uc = make_action_usecase(mock_echo=mock_echo)
    try:
        chain_cfg = load_action_chain(Path(chain_path))
        results = uc.run(chain_path, user_inputs=list(user_inputs), api_key=api_key)
    except FileNotFoundError as e:
        click.echo(f"[ERROR] {e}", err=True)
        sys.exit(1)
    for i, (step, result) in enumerate(zip(chain_cfg.steps, results, strict=True), start=1):
        if not result.is_success:
            click.echo(f"[ERROR step {i}] {result.error}", err=True)
            sys.exit(1)
        value = (
            result.extracted
            if result.extracted is not None
            else json.dumps(result.body, ensure_ascii=False)
        )
        click.echo(f"step {i} ({Path(step.config).stem}): {value}")


@cli.command()
@click.argument("config_path", type=click.Path())
@click.option("--api-key", default=None, envvar="API_KEY", help="API key (or set API_KEY env var)")
@click.option("--mock-echo", is_flag=True, help="Use MockAdapter — echo request offline")
def chat(
    config_path: str,
    api_key: str | None,
    mock_echo: bool,
) -> None:
    """Interactive multi-turn chat using a single_config YAML with messages body."""
    uc = make_chat_usecase(mock_echo=mock_echo)
    try:
        uc.load(config_path)
    except FileNotFoundError as e:
        click.echo(f"[ERROR] {e}", err=True)
        sys.exit(1)
    click.echo("Chat started. Type 'exit' or press Ctrl+C to quit.")
    while True:
        try:
            user_input = input("> ")
        except (KeyboardInterrupt, EOFError):
            break
        if user_input.strip().lower() in ("exit", "quit"):
            break
        response = uc.send(user_input, api_key=api_key)
        if response is None:
            click.echo("[ERROR] Request failed.", err=True)
        else:
            click.echo(response)
    click.echo("Goodbye.")
