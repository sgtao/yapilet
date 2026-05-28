from __future__ import annotations

import pytest

from yapilet.core.services.placeholder import PlaceholderResolver


def test_resolve_user_input() -> None:
    r = PlaceholderResolver()
    out = r.resolve("hello ＜user_input_0＞!", user_inputs=["world"])
    assert out == "hello world!"


def test_resolve_user_input_brace_alias() -> None:
    r = PlaceholderResolver()
    out = r.resolve("hello {{user_input_0}}!", user_inputs=["world"])
    assert out == "hello world!"


def test_resolve_multiple_user_inputs() -> None:
    r = PlaceholderResolver()
    out = r.resolve("＜user_input_0＞-{{user_input_1}}", user_inputs=["a", "b"])
    assert out == "a-b"


def test_resolve_api_key_both_notations() -> None:
    r = PlaceholderResolver()
    assert r.resolve("Bearer ＜API_KEY＞", api_key="sk-xxx") == "Bearer sk-xxx"
    assert r.resolve("Bearer {{API_KEY}}", api_key="sk-xxx") == "Bearer sk-xxx"


def test_resolve_action_result() -> None:
    r = PlaceholderResolver()
    out = r.resolve("prev=＜action_result_0＞", action_results=["42"])
    assert out == "prev=42"


def test_resolve_out_of_range_user_input_raises() -> None:
    r = PlaceholderResolver()
    with pytest.raises(ValueError, match="user_input index 0 out of range"):
        r.resolve("＜user_input_0＞", user_inputs=[])


def test_resolve_in_object_nested_dict() -> None:
    r = PlaceholderResolver()
    template = {
        "headers": {"Authorization": "Bearer ＜API_KEY＞"},
        "body": {"msg": "{{user_input_0}}"},
    }
    out = r.resolve_in_object(template, user_inputs=["hi"], api_key="K")
    assert out == {
        "headers": {"Authorization": "Bearer K"},
        "body": {"msg": "hi"},
    }


def test_mask_api_key() -> None:
    out = PlaceholderResolver.mask_api_key("Authorization: Bearer sk-secret", "sk-secret")
    assert out == "Authorization: Bearer ***"
