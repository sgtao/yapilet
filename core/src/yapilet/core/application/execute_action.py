from __future__ import annotations

from pathlib import Path

from yapilet.core.application.execute_single import ExecuteSingleUseCase
from yapilet.core.models.result import Result
from yapilet.core.services.config_loader import ConfigLoader
from yapilet.core.services.placeholder import PlaceholderResolver


class ExecuteActionUseCase:
    """Runs a named action chain, wiring each step's extracted result into the next."""

    def __init__(
        self,
        *,
        single_usecase: ExecuteSingleUseCase,
        config_loader: ConfigLoader,
        resolver: PlaceholderResolver | None = None,
    ) -> None:
        self._loader = config_loader
        self._resolver = resolver or PlaceholderResolver()
        self._single = single_usecase

    def run(
        self,
        action_path: str | Path,
        *,
        user_inputs: list[str] | None = None,
        api_key: str | None = None,
    ) -> list[Result]:
        """Execute all steps in the named action chain and return their Results."""
        chain = self._loader.load_action(Path(action_path))
        inputs = user_inputs or []
        results: list[Result] = []

        for step in chain.steps:
            extracted_so_far = [str(r.extracted) for r in results]
            resolved_inputs = [
                self._resolver.resolve(
                    inp,
                    user_inputs=inputs,
                    action_results=extracted_so_far,
                    api_key=api_key,
                )
                for inp in step.inputs
            ]
            result = self._single.run(
                step.config,
                user_inputs=resolved_inputs,
                api_key=api_key,
            )
            results.append(result)

        return results
