"""Summarize a Codex rollout JSONL without copying prompts or tool outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

SCHEMA_VERSION = "gpd.codex-session-trace.v1"


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _json_chars(value: object) -> int:
    return len(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _command_fingerprint(command: object) -> tuple[str, int]:
    if isinstance(command, list):
        rendered = "\0".join(str(part) for part in command)
    else:
        rendered = str(command or "")
    raw = rendered.encode("utf-8")
    return _sha256(raw), len(rendered)


def _normalized_parsed_commands(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    rows: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        row: dict[str, object] = {"type": str(item.get("type") or "unknown")}
        for key in ("name", "path"):
            candidate = item.get(key)
            if isinstance(candidate, str) and candidate:
                row[key] = candidate
        rows.append(row)
    return rows


def _item_completed(payload: object) -> dict[str, object] | None:
    if not isinstance(payload, dict) or payload.get("type") != "item_completed":
        return None
    item = payload.get("item")
    return item if isinstance(item, dict) else None


def summarize_codex_session(path: Path) -> dict[str, object]:
    """Return a bounded trace of tool use, file access, changes, and token totals."""

    source = path.resolve()
    raw_source = source.read_bytes()
    event_counts: Counter[str] = Counter()
    item_counts: Counter[str] = Counter()
    file_read_counts: Counter[str] = Counter()
    commands: list[dict[str, object]] = []
    mcp_calls: list[dict[str, object]] = []
    extensions: list[dict[str, object]] = []
    file_changes: list[dict[str, object]] = []
    malformed_line_count = 0
    session_id: str | None = None
    final_usage: dict[str, object] = {}

    for line in raw_source.decode("utf-8", errors="replace").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            malformed_line_count += 1
            continue
        if not isinstance(row, dict):
            continue
        row_type = str(row.get("type") or "unknown")
        event_counts[row_type] += 1
        payload = row.get("payload")

        if row_type == "session_meta" and isinstance(payload, dict):
            candidate = payload.get("id")
            if isinstance(candidate, str):
                session_id = candidate

        if row_type == "event_msg" and isinstance(payload, dict) and payload.get("type") == "token_count":
            info = payload.get("info")
            if isinstance(info, dict) and isinstance(info.get("total_token_usage"), dict):
                final_usage = dict(info["total_token_usage"])

        item = _item_completed(payload) if row_type == "event_msg" else None
        if item is None:
            continue
        item_type = str(item.get("type") or "unknown")
        item_counts[item_type] += 1

        if item_type == "CommandExecution":
            fingerprint, chars = _command_fingerprint(item.get("command"))
            parsed = _normalized_parsed_commands(item.get("parsed_cmd"))
            commands.append(
                {
                    "id": item.get("id"),
                    "status": item.get("status"),
                    "cwd": item.get("cwd"),
                    "command_sha256": fingerprint,
                    "command_chars": chars,
                    "parsed_commands": parsed,
                }
            )
            for parsed_item in parsed:
                if parsed_item.get("type") not in {"read", "search"}:
                    continue
                parsed_path = parsed_item.get("path")
                if isinstance(parsed_path, str) and parsed_path:
                    file_read_counts[parsed_path] += 1
            continue

        if item_type == "McpToolCall":
            arguments = item.get("arguments")
            mcp_calls.append(
                {
                    "id": item.get("id"),
                    "server": item.get("server"),
                    "tool": item.get("tool"),
                    "status": item.get("status"),
                    "argument_chars": _json_chars(arguments),
                }
            )
            continue

        if item_type == "Extension":
            extensions.append(
                {
                    "id": item.get("id"),
                    "kind": item.get("kind"),
                    "action_type": item.get("action", {}).get("type")
                    if isinstance(item.get("action"), dict)
                    else None,
                }
            )
            continue

        if item_type == "FileChange":
            changes = item.get("changes")
            if isinstance(changes, dict):
                for changed_path, change in changes.items():
                    change_type = change.get("type") if isinstance(change, dict) else None
                    file_changes.append({"path": changed_path, "type": change_type})

    return {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "path": str(source),
            "sha256": _sha256(raw_source),
            "bytes": len(raw_source),
            "malformed_line_count": malformed_line_count,
        },
        "session_id": session_id,
        "sensitive_payloads_omitted": True,
        "event_counts": dict(sorted(event_counts.items())),
        "item_counts": dict(sorted(item_counts.items())),
        "usage": final_usage,
        "totals": {
            "command_count": len(commands),
            "command_input_chars": sum(int(row["command_chars"]) for row in commands),
            "mcp_call_count": len(mcp_calls),
            "mcp_argument_chars": sum(int(row["argument_chars"]) for row in mcp_calls),
            "extension_count": len(extensions),
            "file_read_event_count": sum(file_read_counts.values()),
            "unique_file_read_count": len(file_read_counts),
            "file_change_count": len(file_changes),
        },
        "file_reads": [
            {"path": read_path, "count": count} for read_path, count in sorted(file_read_counts.items())
        ],
        "commands": commands,
        "mcp_calls": mcp_calls,
        "extensions": extensions,
        "file_changes": file_changes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session_jsonl", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    payload = summarize_codex_session(args.session_jsonl)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
