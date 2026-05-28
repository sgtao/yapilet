from __future__ import annotations

import re
from typing import Any

_USER_INPUT_PATTERN = re.compile(r"[<＜]user_input_(\d+)[>＞]|\{\{\s*user_input_(\d+)\s*\}\}")
_ACTION_RESULT_PATTERN = re.compile(
    r"[<＜]action_result_(\d+)[>＞]|\{\{\s*action_result_(\d+)\s*\}\}"
)
_API_KEY_PATTERN = re.compile(r"[<＜]API_KEY[>＞]|\{\{\s*API_KEY\s*\}\}")
_API_KEY_MASK = "***"


def _index_from_match(match: re.Match[str]) -> int:
    """Return the captured digit group regardless of which notation matched."""
    raw = match.group(1) if match.group(1) is not None else match.group(2)
    return int(raw)


class PlaceholderResolver:
    """Expands user_input_N, action_result_N, API_KEY placeholders.

    Supports both <...> and {{...}} notations as aliases.
    Stateless. Pure string transformation only.
    """

    def resolve(
        self,
        template: str,
        *,
        user_inputs: list[str] | None = None,
        action_results: list[str] | None = None,
        api_key: str | None = None,
    ) -> str:
        """Expand placeholders in `template` and return the resolved string."""
        inputs = user_inputs or []
        results = action_results or []

        def _user_input_repl(match: re.Match[str]) -> str:
            idx = _index_from_match(match)
            if idx >= len(inputs):
                raise ValueError(f"user_input index {idx} out of range (have {len(inputs)})")
            return inputs[idx]

        def _action_result_repl(match: re.Match[str]) -> str:
            idx = _index_from_match(match)
            if idx >= len(results):
                raise ValueError(f"action_result index {idx} out of range (have {len(results)})")
            return results[idx]

        out = _USER_INPUT_PATTERN.sub(_user_input_repl, template)
        out = _ACTION_RESULT_PATTERN.sub(_action_result_repl, out)
        out = _API_KEY_PATTERN.sub(api_key if api_key is not None else "", out)
        return out

    def resolve_in_object(
        self,
        obj: Any,
        *,
        user_inputs: list[str] | None = None,
        action_results: list[str] | None = None,
        api_key: str | None = None,
    ) -> Any:
        """Recursively resolve placeholders in dict / list / str structures."""
        if isinstance(obj, str):
            return self.resolve(
                obj,
                user_inputs=user_inputs,
                action_results=action_results,
                api_key=api_key,
            )
        if isinstance(obj, dict):
            return {
                k: self.resolve_in_object(
                    v,
                    user_inputs=user_inputs,
                    action_results=action_results,
                    api_key=api_key,
                )
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            return [
                self.resolve_in_object(
                    v,
                    user_inputs=user_inputs,
                    action_results=action_results,
                    api_key=api_key,
                )
                for v in obj
            ]
        return obj

    @staticmethod
    def mask_api_key(text: str, api_key: str) -> str:
        """Replace occurrences of `api_key` in `text` with the mask token."""
        if not api_key:
            return text
        return text.replace(api_key, _API_KEY_MASK)
