#!/usr/bin/env python3
"""Build an offline, skills-only review ZIP; never upload or claim approval."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile


SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
PLUGIN = Path("plugins/commit-rationale")
# An explicit allowlist prevents hooks, repository history, benchmark results,
# caches, credentials, and newly added unrelated files from leaking into a ZIP.
SKILL_FILES = (
    "skills/commit-rationale/SKILL.md",
    "skills/commit-rationale/agents/openai.yaml",
    "skills/read-commit-history/SKILL.md",
    "skills/read-commit-history/agents/openai.yaml",
    "skills/read-commit-history/scripts/read_commit.py",
)
SEMVER = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)


def read_source(root, relative):
    """Read a regular, nonsymlinked file entirely inside the source tree."""
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe source path: {relative}")
    path = root
    for component in relative.parts:
        path = path / component
        if path.is_symlink():
            raise ValueError(f"Symlinked source is not allowed: {relative}")
    if not path.is_file():
        raise ValueError(f"Missing regular source file: {relative}")
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"Source escapes repository: {relative}")
    return path.read_bytes()


def make_manifest(version):
    if len(version) > 64 or not SEMVER.fullmatch(version):
        raise ValueError("Version must be a semantic version of at most 64 characters")
    # The portable format allows publisher fields to be absent in a draft.
    # A GitHub username is not evidence of a verified Platform identity.
    return {
        "$schema": SCHEMA,
        "name": "commit-rationale",
        "version": version,
        "description": "Preserve useful Git commit rationale and consult relevant history during maintenance.",
        "repository": "https://github.com/SunneeYang/commit-rationale",
        "license": "MIT",
        "keywords": ["git", "commits", "rationale", "maintenance"],
        "extensions": {
            "com.openai": {
                "interface": {
                    "displayName": "Commit Rationale",
                    "shortDescription": "Keep the why in Git",
                    "longDescription": (
                        "Preserve constraints, decisions, and verification limits that code and diffs do not explain. "
                        "Consult relevant full commit messages before changing or reviewing existing code. "
                        "History reading requires an authorized repository with Git available in the task environment. "
                        "Skill selection depends on the host and task; installation does not grant repository access "
                        "or guarantee execution at every session start."
                    ),
                    "category": "Developer Tools",
                    "capabilities": ["Draft commit rationale", "Read relevant Git history"],
                    "defaultPrompt": [
                        "Draft a commit message from my current changes and the context of this task.",
                        "Assess this proposed code change using relevant commit history and current evidence.",
                    ],
                }
            }
        },
    }


def build_package(repo, output, version=None):
    repo = Path(repo).resolve()
    output = Path(output).absolute()
    report_path = output.with_suffix(".preflight.json")
    source_manifest = json.loads(read_source(repo, PLUGIN / ".codex-plugin/plugin.json"))
    if source_manifest.get("name") != "commit-rationale":
        raise ValueError("Expected the commit-rationale source plugin")
    manifest = make_manifest(version or source_manifest["version"])
    entries = {
        "plugin.json": (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode(),
        "LICENSE": read_source(repo, "LICENSE"),
    }
    for relative in SKILL_FILES:
        entries[relative] = read_source(repo, PLUGIN / relative)
    if output.suffix.lower() != ".zip":
        raise ValueError("Output must use a .zip extension")
    if output.exists() or report_path.exists():
        raise ValueError("Output ZIP or preflight report already exists; choose a new output path")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as target:
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(entries.items()):
                info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
    report = {
        "status": "review-only",
        "submission_ready": False,
        "version": manifest["version"],
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "archive_entries": sorted(entries),
        "blockers": [
            "Select a verified Platform publishing identity; add matching author.name and interface.developerName.",
            "Add licensed logo/composerIcon assets and their package-relative manifest paths.",
            "Prepare a published privacy policy and accurate listing links; ZIP validation alone does not establish policy compliance.",
            "Confirm the product-specific review path for core local Git execution with OpenAI before submission.",
            "Test this exact package on supported hosts and complete Platform scans, attestations, and review.",
        ],
        "limits": "Offline packaging only. No identity verification, official schema validation, security scan, upload, submission, or publication was performed.",
    }
    with report_path.open("x", encoding="utf-8") as target:
        json.dump(report, target, ensure_ascii=False, indent=2)
        target.write("\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", required=True, type=Path, help="New local review ZIP path")
    parser.add_argument("--version", help="Optional explicit release semver")
    args = parser.parse_args()
    try:
        report = build_package(args.repo, args.output, args.version)
    except (KeyError, OSError, ValueError, zipfile.BadZipFile) as error:
        parser.exit(2, f"Packaging failed: {error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
