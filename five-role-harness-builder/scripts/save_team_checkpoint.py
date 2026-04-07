#!/usr/bin/env python3
"""Save a durable checkpoint for a five-role harness project."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def now_local() -> datetime:
    return datetime.now().astimezone()


def now_iso() -> str:
    return now_local().isoformat(timespec="seconds")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    slug = slug.strip("-")
    return slug or "checkpoint"


def ensure_structure(root: Path) -> Dict[str, Path]:
    docs_dir = root / "docs"
    harness_dir = root / ".harness"
    state_dir = harness_dir / "state"
    checkpoints_dir = harness_dir / "checkpoints"
    for directory in (docs_dir, harness_dir, state_dir, checkpoints_dir):
        directory.mkdir(parents=True, exist_ok=True)
    return {
        "docs": docs_dir,
        "harness": harness_dir,
        "state": state_dir,
        "checkpoints": checkpoints_dir,
    }


def load_manifest(path: Path, root: Path, timestamp: str) -> Dict[str, object]:
    if not path.exists():
        return {
            "project_root": str(root),
            "created_at": timestamp,
            "updated_at": timestamp,
            "last_plan_id": None,
            "last_status": None,
            "last_roles": None,
            "last_commit_sha": None,
            "latest_checkpoint": None,
        }
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {
            "project_root": str(root),
            "created_at": timestamp,
        }


def read_summary(summary: str, summary_file: str) -> str:
    if summary_file:
        return Path(summary_file).read_text().strip()
    return summary.strip()


def format_list(items: List[str], empty_message: str) -> str:
    if not items:
        return f"- {empty_message}"
    return "\n".join(f"- {item}" for item in items)


def format_roles(roles: List[str]) -> str:
    return ", ".join(roles) if roles else "none"


def write_checkpoint(
    checkpoints_dir: Path,
    plan_id: str,
    status: str,
    title: str,
    timestamp: str,
    roles: List[str],
    summary: str,
    next_step: str,
    changed_files: List[str],
    tests: List[str],
    risks: List[str],
    commit_sha: str,
) -> Path:
    stamp = now_local().strftime("%Y%m%d-%H%M%S")
    filename = f"{stamp}-{safe_slug(plan_id)}-{safe_slug(status)}.md"
    path = checkpoints_dir / filename
    title_line = f"\n- Title: {title}" if title else ""
    commit_line = commit_sha if commit_sha else "none"
    content = f"""# Checkpoint: {plan_id}

- Recorded: {timestamp}
- Status: {status}{title_line}
- Roles touched: {format_roles(roles)}
- Commit SHA: {commit_line}

## Summary

{summary}

## Changed Files

{format_list(changed_files, "No file list provided.")}

## Verification

{format_list(tests, "No verification details recorded.")}

## Risks

{format_list(risks, "No open risks recorded.")}

## Next Step

{next_step}
"""
    path.write_text(content)
    return path


def append_progress_log(
    path: Path,
    timestamp: str,
    plan_id: str,
    status: str,
    roles: List[str],
    summary: str,
    next_step: str,
    commit_sha: str,
) -> None:
    existing = path.read_text() if path.exists() else "# Progress Log\n\n"
    block = f"""
## {timestamp}

- Plan item: {plan_id}
- Status: {status}
- Roles touched: {format_roles(roles)}
- Commit SHA: {commit_sha or 'none'}
- Summary: {summary.splitlines()[0].strip()}
- Next step: {next_step}
"""
    path.write_text(existing.rstrip() + "\n" + block)


def append_docs_progress(
    path: Path,
    timestamp: str,
    plan_id: str,
    status: str,
    roles: List[str],
    summary: str,
    next_step: str,
    commit_sha: str,
) -> None:
    existing = path.read_text() if path.exists() else "# Progress\n\n"
    block = f"""
## {timestamp}

- Plan item: {plan_id}
- Status: {status}
- Roles touched: {format_roles(roles)}
- Commit SHA: {commit_sha or 'none'}
- Summary: {summary.splitlines()[0].strip()}
- Next step: {next_step}
"""
    path.write_text(existing.rstrip() + "\n" + block)


def write_session_handoff(
    path: Path,
    timestamp: str,
    plan_id: str,
    status: str,
    roles: List[str],
    summary: str,
    next_step: str,
    changed_files: List[str],
    tests: List[str],
    risks: List[str],
    commit_sha: str,
    checkpoint_path: Path,
) -> None:
    content = f"""# Session Handoff

Last updated: {timestamp}
Plan item: {plan_id}
Status: {status}
Roles touched: {format_roles(roles)}
Commit SHA: {commit_sha or 'none'}
Latest checkpoint: {checkpoint_path}

## Summary

{summary}

## Changed Files

{format_list(changed_files, "No file list provided.")}

## Verification

{format_list(tests, "No verification details recorded.")}

## Risks

{format_list(risks, "No open risks recorded.")}

## Next Step

{next_step}
"""
    path.write_text(content)


def main() -> int:
    parser = argparse.ArgumentParser(description="Save a checkpoint for a five-role harness project.")
    parser.add_argument("--root", required=True, help="Project root directory.")
    parser.add_argument("--plan-id", required=True, help="Plan item identifier, for example P1-T1.")
    parser.add_argument(
        "--status",
        required=True,
        choices=("completed", "blocked", "in_progress"),
        help="Cycle status for this checkpoint.",
    )
    parser.add_argument("--title", default="", help="Optional short title for the plan item.")
    parser.add_argument("--role", action="append", default=[], help="Repeatable role name, for example --role pm.")
    parser.add_argument("--summary", default="", help="Short or multiline summary text.")
    parser.add_argument("--summary-file", default="", help="Path to a file containing the summary.")
    parser.add_argument("--next-step", required=True, help="Exact next step for the next session.")
    parser.add_argument("--changed-file", action="append", default=[], help="Repeatable changed file entry.")
    parser.add_argument("--test", action="append", default=[], help="Repeatable verification entry.")
    parser.add_argument("--risk", action="append", default=[], help="Repeatable risk entry.")
    parser.add_argument("--commit-sha", default="", help="Optional commit SHA for the completed item.")
    args = parser.parse_args()

    summary = read_summary(args.summary, args.summary_file)
    if not summary:
        raise SystemExit("Either --summary or --summary-file must provide non-empty content.")

    root = Path(args.root).resolve()
    paths = ensure_structure(root)
    timestamp = now_iso()
    roles = list(dict.fromkeys(args.role))

    checkpoint_path = write_checkpoint(
        checkpoints_dir=paths["checkpoints"],
        plan_id=args.plan_id,
        status=args.status,
        title=args.title,
        timestamp=timestamp,
        roles=roles,
        summary=summary,
        next_step=args.next_step,
        changed_files=args.changed_file,
        tests=args.test,
        risks=args.risk,
        commit_sha=args.commit_sha,
    )

    progress_log_path = paths["state"] / "progress-log.md"
    append_progress_log(
        progress_log_path,
        timestamp,
        args.plan_id,
        args.status,
        roles,
        summary,
        args.next_step,
        args.commit_sha,
    )

    docs_progress_path = paths["docs"] / "progress.md"
    append_docs_progress(
        docs_progress_path,
        timestamp,
        args.plan_id,
        args.status,
        roles,
        summary,
        args.next_step,
        args.commit_sha,
    )

    session_handoff_path = paths["state"] / "session-handoff.md"
    write_session_handoff(
        session_handoff_path,
        timestamp,
        args.plan_id,
        args.status,
        roles,
        summary,
        args.next_step,
        args.changed_file,
        args.test,
        args.risk,
        args.commit_sha,
        checkpoint_path,
    )

    manifest_path = paths["state"] / "manifest.json"
    manifest = load_manifest(manifest_path, root, timestamp)
    manifest["project_root"] = str(root)
    manifest["updated_at"] = timestamp
    manifest["last_plan_id"] = args.plan_id
    manifest["last_status"] = args.status
    manifest["last_roles"] = roles
    manifest["last_commit_sha"] = args.commit_sha or None
    manifest["latest_checkpoint"] = str(checkpoint_path)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    print(f"Checkpoint saved: {checkpoint_path}")
    print(f"Handoff updated: {session_handoff_path}")
    print(f"Manifest updated: {manifest_path}")
    print(f"Docs progress updated: {docs_progress_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
