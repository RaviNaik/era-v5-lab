"""Tests for the G10 special-token list and ChatML-style chat format v0."""

from __future__ import annotations

import importlib.util
from pathlib import Path

TEAM = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


render_mod = _load("g10_render", TEAM / "chat-format" / "render.py")


def test_block_reserves_256_ids_and_every_marker_is_one_special_token():
    rows = render_mod.all_tokens()
    assert len(rows) == 256
    assert [row[0] for row in rows] == list(range(256))
    surfaces = [row[2] for row in rows]
    assert len(set(surfaces)) == 256
    assert all(surface.startswith("<|") and surface.endswith("|>") for surface in surfaces)
    assert all("\n" not in surface and " " not in surface for surface in surfaces)
    assigned = [row for row in rows if row[3] == "assigned"]
    assert [row[2] for row in assigned] == [
        "<|endoftext|>",
        "<|im_start|>",
        "<|im_end|>",
        "<|pad|>",
        "<|effort_1k|>",
        "<|effort_4k|>",
        "<|effort_16k|>",
        "<|effort_64k|>",
        "<|tools|>",
        "<|/tools|>",
        "<|think|>",
        "<|/think|>",
        "<|tool_call|>",
        "<|/tool_call|>",
        "<|tool_result|>",
        "<|/tool_result|>",
    ]


def test_effort_budgets_and_turn_tokens():
    assert render_mod.EFFORT_BUDGETS == {"1k": 1024, "4k": 4096, "16k": 16384, "64k": 65536}
    names = render_mod.by_name()
    assert names["im_start"] == "<|im_start|>"
    assert names["im_end"] == "<|im_end|>"
    assert names["endoftext"] == "<|endoftext|>"
    assert names["pad"] == "<|pad|>"
    assert names["tools"] == "<|tools|>"
    assert names["tools_end"] == "<|/tools|>"
    assert names["think"] == "<|think|>"
    assert names["think_end"] == "<|/think|>"
    assert names["tool_call"] == "<|tool_call|>"
    assert names["tool_call_end"] == "<|/tool_call|>"
    assert names["tool_result"] == "<|tool_result|>"
    assert names["tool_result_end"] == "<|/tool_result|>"
    for effort in render_mod.EFFORT_BUDGETS:
        assert names[f"effort_{effort}"] == f"<|effort_{effort}|>"
        assert render_mod.effort_limit(effort) == render_mod.EFFORT_BUDGETS[effort]


def test_render_parse_roundtrip_and_atomic_marker_tokenization():
    messages = [
        {"role": "system", "content": "You edit code and you report only what a tool returned."},
        {"role": "user", "content": "test_add fails in calc.py. Fix add."},
        {
            "role": "assistant",
            "think": "The return adds one too many.",
            "tool_calls": [{"name": "read_file", "arguments": {"path": "calc.py"}}],
            "content": "I am reading calc.py before editing it.",
        },
        {"role": "tool", "content": "def add(a, b):\n    return a + b + 1\n"},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "name": "apply_patch",
                    "arguments": {"path": "calc.py", "patch": "return a + b"},
                }
            ],
            "content": "Removed the extra increment.",
        },
    ]
    for effort in ("1k", "4k", "16k", "64k"):
        text = render_mod.render(messages, effort=effort)
        assert f"<|effort_{effort}|>" in text
        assert "<|im_start|>assistant\n" in text
        assert "<|think|>\nThe return adds one too many.\n<|/think|>" in text
        assert "<|tool_call|>\n" in text and "\n<|/tool_call|>" in text
        assert "<|tool_result|>\n" in text and "\n<|/tool_result|>" in text
        for other in ("1k", "4k", "16k", "64k"):
            if other != effort:
                assert f"<|effort_{other}|>" not in text
        parsed = render_mod.parse(text)
        assert parsed["effort"] == effort
        assert parsed["messages"] == messages

        # Verify every chat marker is tokenized as one atomic special token ID, never plain text.
        pieces = render_mod.tokenize_markers(text)
        special_ids = [val for kind, val in pieces if kind == "special"]
        assert 0 in special_ids  # <|endoftext|>
        assert 1 in special_ids  # <|im_start|>
        assert 2 in special_ids  # <|im_end|>
        assert 24 in special_ids and 25 in special_ids  # <|think|>, <|/think|>
        assert 26 in special_ids and 27 in special_ids  # <|tool_call|>, <|/tool_call|>
        assert 28 in special_ids and 29 in special_ids  # <|tool_result|>, <|/tool_result|>
        for kind, val in pieces:
            if kind == "text":
                assert "<|" not in str(val)


def test_render_rejects_bad_effort_role_and_plain_or_embedded_markers():
    ok = [{"role": "user", "content": "hello"}]
    for effort in ("2k", "8k", "", "64K"):
        try:
            render_mod.render(ok, effort=effort)
        except render_mod.RenderError:
            pass
        else:
            raise AssertionError(f"effort {effort!r} should fail")

    try:
        render_mod.render([{"role": "developer", "content": "no"}])
    except render_mod.RenderError:
        pass
    else:
        raise AssertionError("unknown role should fail")

    for bad in ("see <|im_start|> here", "plain <think> tag", "plain <tool_call> tag"):
        try:
            render_mod.render([{"role": "user", "content": bad}])
        except render_mod.RenderError:
            pass
        else:
            raise AssertionError(f"marker leak {bad!r} should fail")


def test_empty_optional_fields_are_omitted():
    text = render_mod.render(
        [{"role": "assistant", "content": "", "think": "", "tool_calls": []}],
        effort="1k",
    )
    parsed = render_mod.parse(text)
    assert parsed == {"effort": "1k", "messages": [{"role": "assistant"}]}
    assert "<|think|>" not in text
    assert "<|tool_call|>" not in text


def test_docs_match_the_plan_sheet_set():
    chat = (TEAM / "chat-format" / "chat_format_v0.md").read_text(encoding="utf-8")
    token_doc = (TEAM / "special-tokens" / "special_tokens_v0.md").read_text(encoding="utf-8")
    licence = (TEAM / "licences" / "licence_table.md").read_text(encoding="utf-8")
    for budget in ("1k", "4k", "16k", "64k"):
        assert budget in chat
        assert f"effort_{budget}" in token_doc
    for _, name, surface, status in render_mod.all_tokens():
        if status == "assigned":
            assert surface in token_doc
            assert name in token_doc
    assert "256" in token_doc
    assert "TSAI reserves" in token_doc
    assert "bigcode/starcoderdata" in licence
    assert "code-python" in licence
    assert "TSAI reserves" in licence

    decisions = []
    for line in licence.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0] in {"Set", ""} or set(cells[0]) <= set("-: "):
            continue
        decisions.append(cells[-1])
    assert decisions == ["TSAI reserves"]
