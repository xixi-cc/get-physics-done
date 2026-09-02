"""Tests for the model-invisible Codex session trace summarizer."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.thinning.codex_session_trace import summarize_codex_session


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def test_trace_summarizes_usage_and_omits_sensitive_payloads(tmp_path: Path) -> None:
    source = tmp_path / "rollout.jsonl"
    _write_jsonl(
        source,
        [
            {"type": "session_meta", "payload": {"id": "session-1"}},
            {
                "type": "event_msg",
                "payload": {
                    "type": "item_completed",
                    "item": {
                        "type": "CommandExecution",
                        "id": "cmd-1",
                        "status": "completed",
                        "cwd": "file:///work",
                        "command": ["bash", "-lc", "read secret-value"],
                        "stdout": "secret-output",
                        "parsed_cmd": [{"type": "read", "path": "/work/input.md", "cmd": "secret-value"}],
                    },
                },
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "item_completed",
                    "item": {
                        "type": "McpToolCall",
                        "id": "mcp-1",
                        "server": "gpd-state",
                        "tool": "state_get",
                        "arguments": {"project_dir": "/work"},
                        "result": {"secret": "do-not-copy"},
                        "status": "completed",
                    },
                },
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {"total_token_usage": {"input_tokens": 120, "output_tokens": 30, "total_tokens": 150}},
                },
            },
        ],
    )

    payload = summarize_codex_session(source)
    rendered = json.dumps(payload)

    assert payload["session_id"] == "session-1"
    assert payload["usage"]["total_tokens"] == 150
    assert payload["totals"]["command_count"] == 1
    assert payload["totals"]["mcp_call_count"] == 1
    assert payload["file_reads"] == [{"path": "/work/input.md", "count": 1}]
    assert payload["sensitive_payloads_omitted"] is True
    assert "secret-value" not in rendered
    assert "secret-output" not in rendered
    assert "do-not-copy" not in rendered


def test_trace_uses_last_cumulative_token_count_and_tracks_changes(tmp_path: Path) -> None:
    source = tmp_path / "rollout.jsonl"
    _write_jsonl(
        source,
        [
            {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 10}}}},
            {
                "type": "event_msg",
                "payload": {
                    "type": "item_completed",
                    "item": {
                        "type": "FileChange",
                        "changes": {"/work/result.md": {"type": "add", "content": "private"}},
                    },
                },
            },
            {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 25}}}},
        ],
    )

    payload = summarize_codex_session(source)

    assert payload["usage"] == {"total_tokens": 25}
    assert payload["file_changes"] == [{"path": "/work/result.md", "type": "add"}]
    assert payload["totals"]["file_change_count"] == 1
