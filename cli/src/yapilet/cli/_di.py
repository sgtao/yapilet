from __future__ import annotations

from pathlib import Path

from yapilet.core.application.execute_action import ExecuteActionUseCase
from yapilet.core.application.execute_single import ExecuteSingleUseCase
from yapilet.core.infrastructure.httpx_adapter import HttpxAdapter
from yapilet.core.infrastructure.mock_adapter import MockAdapter
from yapilet.core.services.config_loader import ConfigLoader


def make_single_usecase(mock_echo: bool, configs_dir: Path) -> ExecuteSingleUseCase:
    """Create ExecuteSingleUseCase with appropriate HTTP adapter."""
    http_port = MockAdapter() if mock_echo else HttpxAdapter()
    return ExecuteSingleUseCase(
        http_port=http_port,
        config_loader=ConfigLoader(configs_dir),
    )


def make_action_usecase(mock_echo: bool, configs_dir: Path) -> ExecuteActionUseCase:
    """Create ExecuteActionUseCase with appropriate HTTP adapter."""
    http_port = MockAdapter() if mock_echo else HttpxAdapter()
    return ExecuteActionUseCase(
        http_port=http_port,
        config_loader=ConfigLoader(configs_dir),
    )
