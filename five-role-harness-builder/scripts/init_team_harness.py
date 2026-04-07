#!/usr/bin/env python3
"""Initialize durable state for a five-role resumable harness project."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


TEAM_FILES = [
    "team/workflow.md",
    "team/leader.md",
    "team/pm.md",
    "team/develop.md",
    "team/designer.md",
    "team/qa.md",
]


ROLE_DOCS = {
    "pm": ("docs/pm/prd.md", "# Product Requirements\n\n## Problem\n\n## Users\n\n## Goals\n\n## Scope\n\n## Acceptance Criteria\n\n## Risks And Open Questions\n"),
    "leader": ("docs/leader/plan.md", "# Delivery Plan\n\n## Current Stage\n\n## Milestones\n\n## Active Item\n\n## Dependencies\n\n## Risks And Blockers\n"),
    "designer": ("docs/designer/design.md", "# Design Notes\n\n## User Flow\n\n## Screens And States\n\n## Components\n\n## Responsive And Accessibility Notes\n"),
    "develop": ("docs/develop/implementation.md", "# Implementation Notes\n\n## Goal\n\n## Technical Approach\n\n## Changed Files\n\n## Verification Notes\n\n## Known Limitations\n"),
    "qa": ("docs/qa/report.md", "# QA Report\n\n## Scope Tested\n\n## Test Cases\n\n## Evidence\n\n## Bugs\n\n## Verdict\n"),
}


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def detect_git_repo(root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0 and result.stdout.strip() == "true"


def ensure_dir(path: Path, created: List[str], existing: List[str]) -> None:
    if path.exists():
        existing.append(str(path))
        return
    path.mkdir(parents=True, exist_ok=True)
    created.append(str(path))


def ensure_file(
    path: Path,
    content: str,
    created: List[str],
    existing: List[str],
    overwrite: bool = False,
) -> None:
    existed = path.exists()
    if existed and not overwrite:
        existing.append(str(path))
        return
    path.write_text(content)
    created.append(str(path))


def load_manifest(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def build_rules_content(timestamp: str) -> str:
    return f"""# Harness Rules

Last refreshed: {timestamp}

- Use five role perspectives: leader, pm, designer, develop, and qa.
- Treat team/workflow.md and team/*.md as the source of truth for role behavior.
- Keep role outputs under docs/ and resume state under .harness/.
- Keep exactly one plan item in_progress unless the user explicitly asks for parallel work.
- Do not mark a plan item complete until qa sign-off is recorded.
- Create a git commit after every completed requirement or plan item.
- Persist progress after every completed item and before any blocked or interrupted exit.
- Trust on-disk harness state over chat memory when resuming.
- Use ISO 8601 timestamps in durable state.
- Initialize git before the first completion cycle if the project is not already a repository.
"""


def build_project_brief(root: Path, source_request: str, has_git: bool, timestamp: str) -> str:
    request_text = source_request.strip() if source_request else "[Fill in the source request here.]"
    git_state = "present" if has_git else "absent"
    team_lines = "\n".join(
        f"- {relative_path}: {'present' if (root / relative_path).exists() else 'missing'}"
        for relative_path in TEAM_FILES
    )
    return f"""# Project Brief

Generated: {timestamp}
Project root: {root}

## Source Request

{request_text}

## Repository Facts

- git repository: {git_state}
- durable state root: .harness/
- role docs root: docs/

## Team File Map

{team_lines}

## Assumptions

- Update this section whenever product, design, implementation, or QA assumptions change.

## Scope Notes

- Record boundaries, exclusions, and important execution notes here.
"""


def build_current_plan(timestamp: str) -> str:
    return f"""# Current Plan

Initialized: {timestamp}

## Workflow

- Keep exactly one plan item in_progress unless the user explicitly asks for parallel work.
- Route each item through the roles required by team/workflow.md.
- Do not mark an item complete until qa verification passes.

## Item Format

- ID:
- Title:
- Stage:
- Owner:
- Status:
- Depends on:
- Deliverables:
- Acceptance:

## Plan Items

### P1-T1
- Title: Replace with the first concrete requirement or plan item.
- Stage: requirement-analysis
- Owner: pm
- Status: pending
- Depends on: none
- Deliverables: docs/pm/prd.md, docs/leader/plan.md
- Acceptance: Replace with the acceptance criteria.
"""


def build_progress_log(timestamp: str) -> str:
    return f"""# Progress Log

Initialized: {timestamp}

Append one entry per saved cycle.
"""


def build_session_handoff(timestamp: str) -> str:
    return f"""# Session Handoff

Last updated: {timestamp}
Plan item: not started
Status: waiting_for_planning
Roles touched: none
Commit SHA: none

## Summary

- Harness state initialized.

## Next Step

- Read team/workflow.md and the team role files, then write the first executable plan item.
"""


def build_docs_progress(timestamp: str) -> str:
    return f"""# Progress

Initialized: {timestamp}

Add one compact entry after each checkpoint.
"""


def write_manifest(path: Path, root: Path, timestamp: str, existing_manifest: Dict[str, object]) -> None:
    manifest = {
        "project_root": str(root),
        "created_at": existing_manifest.get("created_at", timestamp),
        "updated_at": timestamp,
        "last_plan_id": existing_manifest.get("last_plan_id"),
        "last_status": existing_manifest.get("last_status"),
        "last_roles": existing_manifest.get("last_roles"),
        "last_commit_sha": existing_manifest.get("last_commit_sha"),
        "latest_checkpoint": existing_manifest.get("latest_checkpoint"),
        "required_team_files": TEAM_FILES,
    }
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def initialize(root: Path, source_request: str, force_rules: bool) -> Tuple[List[str], List[str]]:
    created: List[str] = []
    existing: List[str] = []
    timestamp = now_iso()

    docs_dir = root / "docs"
    harness_dir = root / ".harness"
    state_dir = harness_dir / "state"
    checkpoints_dir = harness_dir / "checkpoints"

    for directory in (docs_dir, harness_dir, state_dir, checkpoints_dir):
        ensure_dir(directory, created, existing)

    for relative_path, contents in ROLE_DOCS.values():
        target_path = root / relative_path
        ensure_dir(target_path.parent, created, existing)
        ensure_file(target_path, contents, created, existing)

    ensure_file(root / "docs/progress.md", build_docs_progress(timestamp), created, existing)

    has_git = detect_git_repo(root)

    rules_path = state_dir / "rules.md"
    ensure_file(
        rules_path,
        build_rules_content(timestamp),
        created,
        existing,
        overwrite=force_rules,
    )

    ensure_file(
        state_dir / "project-brief.md",
        build_project_brief(root, source_request, has_git, timestamp),
        created,
        existing,
    )
    ensure_file(
        state_dir / "current-plan.md",
        build_current_plan(timestamp),
        created,
        existing,
    )
    ensure_file(
        state_dir / "progress-log.md",
        build_progress_log(timestamp),
        created,
        existing,
    )
    ensure_file(
        state_dir / "session-handoff.md",
        build_session_handoff(timestamp),
        created,
        existing,
    )

    manifest_path = state_dir / "manifest.json"
    existing_manifest = load_manifest(manifest_path)
    write_manifest(manifest_path, root, timestamp, existing_manifest)
    created.append(str(manifest_path))

    return created, existing


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize durable state for a five-role harness project.")
    parser.add_argument("--root", required=True, help="Project root directory.")
    parser.add_argument(
        "--source-request",
        default="",
        help="Optional source request or user request used to seed project-brief.md.",
    )
    parser.add_argument(
        "--force-rules",
        action="store_true",
        help="Rewrite .harness/state/rules.md with the bundled defaults.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)

    created, existing = initialize(root, args.source_request, args.force_rules)

    print(f"Project root: {root}")
    print("Created or refreshed:")
    for item in created:
        print(f"- {item}")
    if existing:
        print("Already present:")
        for item in existing:
            print(f"- {item}")

    missing_team_files = [relative_path for relative_path in TEAM_FILES if not (root / relative_path).exists()]
    if missing_team_files:
        print("Missing team files:")
        for item in missing_team_files:
            print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
