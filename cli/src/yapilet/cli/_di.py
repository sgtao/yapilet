from __future__ import annotations

from pathlib import Path

from yapilet.core.application.execute_action import ExecuteActionUseCase
from yapilet.core.application.execute_single import ExecuteSingleUseCase
from yapilet.core.infrastructure.httpx_adapter import HttpxAdapter
from yapilet.core.infrastructure.mock_adapter import MockAdapter
from yapilet.core.models.action_chain import ActionChain
from yapilet.core.services.config_loader import ConfigLoader


def make_single_usecase(mock_echo: bool) -> ExecuteSingleUseCase:
    """Create ExecuteSingleUseCase with appropriate HTTP adapter."""
    http_port = MockAdapter() if mock_echo else HttpxAdapter()
    return ExecuteSingleUseCase(
        http_port=http_port,
        config_loader=ConfigLoader(),
    )


def make_action_usecase(mock_echo: bool) -> ExecuteActionUseCase:
    """Create ExecuteActionUseCase backed by a pre-configured ExecuteSingleUseCase."""
    single = make_single_usecase(mock_echo=mock_echo)
    return ExecuteActionUseCase(
        single_usecase=single,
        config_loader=ConfigLoader(),
    )


def load_action_chain(action_path: Path) -> ActionChain:
    """Load an action chain config for display purposes."""
    return ConfigLoader().load_action(action_path)
