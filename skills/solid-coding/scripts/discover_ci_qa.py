#!/usr/bin/env python3
"""Detect a repo's existing language/ecosystem and verification commands.

Discovery must never invent tooling a repo doesn't already have — this script
exists so that inference is deterministic and repeatable instead of being
re-derived by eye on every invocation of the solid-coding skill. It only
reports what it finds; it runs nothing and writes nothing.

Usage:
    python3 discover_ci_qa.py [ROOT]

ROOT defaults to the current directory. Manifests are read at ROOT only —
for a monorepo, run once per package root rather than pointing this at the
superproject. Output is always a JSON report on stdout — one shape, always
machine-parseable, matching how the rest of the skill consumes it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CI_CONFIG_PATTERNS = [
    (".github/workflows", "GitHub Actions", "dir"),
    (".gitlab-ci.yml", "GitLab CI", "file"),
    ("Jenkinsfile", "Jenkins", "file"),
    (".circleci/config.yml", "CircleCI", "file"),
    ("azure-pipelines.yml", "Azure Pipelines", "file"),
    (".travis.yml", "Travis CI", "file"),
    ("bitbucket-pipelines.yml", "Bitbucket Pipelines", "file"),
]

# npm/yarn/pnpm "scripts" keys that map to each verification category.
NODE_SCRIPT_MAP = {
    "test": ["test", "test:unit", "test:ci"],
    "lint": ["lint", "lint:check"],
    "typecheck": ["typecheck", "type-check", "tsc"],
    "build": ["build"],
}


def detect_node(root: Path, commands: dict, notes: list, ecosystems: list):
    pkg = root / "package.json"
    if not pkg.exists():
        return
    ecosystems.append("node")
    try:
        data = json.loads(pkg.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        notes.append(f"package.json present but unreadable: {exc}")
        return
    scripts = data.get("scripts", {})
    for category, candidates in NODE_SCRIPT_MAP.items():
        for key in candidates:
            if key in scripts:
                pm = "npm run" if (root / "package-lock.json").exists() else \
                     "pnpm run" if (root / "pnpm-lock.yaml").exists() else \
                     "yarn" if (root / "yarn.lock").exists() else "npm run"
                commands.setdefault(category, []).append(f"{pm} {key}")
                break


def detect_python(root: Path, commands: dict, notes: list, ecosystems: list):
    pyproject = root / "pyproject.toml"
    setup_cfg = root / "setup.cfg"
    has_pytest_ini = (root / "pytest.ini").exists()
    if not (pyproject.exists() or setup_cfg.exists() or has_pytest_ini or (root / "requirements.txt").exists()):
        return
    ecosystems.append("python")
    text = pyproject.read_text(encoding="utf-8", errors="ignore") if pyproject.exists() else ""
    if has_pytest_ini or "[tool.pytest" in text or (root / "tests").is_dir():
        commands.setdefault("test", []).append("pytest")
    if "[tool.ruff" in text:
        commands.setdefault("lint", []).append("ruff check .")
    if "[tool.flake8" in text or (root / ".flake8").exists():
        commands.setdefault("lint", []).append("flake8")
    if "[tool.black" in text:
        commands.setdefault("lint", []).append("black --check .")
    if "[tool.mypy" in text or (root / "mypy.ini").exists():
        commands.setdefault("typecheck", []).append("mypy .")
    if "[tool.poetry" in text:
        notes.append("Poetry project detected — verification commands likely run via 'poetry run <cmd>'")


def detect_rust(root: Path, commands: dict, ecosystems: list):
    if not (root / "Cargo.toml").exists():
        return
    ecosystems.append("rust")
    commands.setdefault("test", []).append("cargo test")
    commands.setdefault("lint", []).append("cargo clippy")
    commands.setdefault("build", []).append("cargo build")


def detect_go(root: Path, commands: dict, ecosystems: list):
    if not (root / "go.mod").exists():
        return
    ecosystems.append("go")
    commands.setdefault("test", []).append("go test ./...")
    commands.setdefault("lint", []).append("go vet ./...")
    commands.setdefault("build", []).append("go build ./...")


def detect_jvm(root: Path, commands: dict, ecosystems: list):
    if (root / "pom.xml").exists():
        ecosystems.append("java-maven")
        commands.setdefault("test", []).append("mvn test")
        commands.setdefault("build", []).append("mvn package")
    for gradle_file in ("build.gradle", "build.gradle.kts"):
        if (root / gradle_file).exists():
            ecosystems.append("java-gradle")
            wrapper = "./gradlew" if (root / "gradlew").exists() else "gradle"
            commands.setdefault("test", []).append(f"{wrapper} test")
            commands.setdefault("build", []).append(f"{wrapper} build")
            break


def detect_dotnet(root: Path, commands: dict, ecosystems: list):
    if any(root.glob("*.csproj")) or any(root.glob("*.sln")):
        ecosystems.append("dotnet")
        commands.setdefault("test", []).append("dotnet test")
        commands.setdefault("build", []).append("dotnet build")


def detect_ruby(root: Path, commands: dict, ecosystems: list):
    if not (root / "Gemfile").exists():
        return
    ecosystems.append("ruby")
    commands.setdefault("test", []).append("bundle exec rspec")
    if (root / ".rubocop.yml").exists():
        commands.setdefault("lint", []).append("bundle exec rubocop")


def detect_php(root: Path, commands: dict, ecosystems: list):
    composer = root / "composer.json"
    if not composer.exists():
        return
    ecosystems.append("php")
    try:
        data = json.loads(composer.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    scripts = data.get("scripts", {})
    for key in ("test", "tests"):
        if key in scripts:
            commands.setdefault("test", []).append(f"composer run {key}")


def detect_elixir(root: Path, commands: dict, ecosystems: list):
    if not (root / "mix.exs").exists():
        return
    ecosystems.append("elixir")
    commands.setdefault("test", []).append("mix test")
    commands.setdefault("lint", []).append("mix credo")


def detect_makefile(root: Path, commands: dict):
    makefile = root / "Makefile"
    if not makefile.exists():
        return
    try:
        text = makefile.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return
    for category, pattern in (
        ("test", r"^test:"), ("lint", r"^lint:"),
        ("build", r"^build:"), ("typecheck", r"^(typecheck|check):"),
    ):
        if re.search(pattern, text, re.MULTILINE):
            commands.setdefault(category, []).append(f"make {category}")


def detect_ci_configs(root: Path) -> list:
    found = []
    for rel_path, name, kind in CI_CONFIG_PATTERNS:
        target = root / rel_path
        if kind == "dir" and target.is_dir():
            workflow_files = sorted(str(p.relative_to(root)) for p in target.glob("*.yml")) + \
                              sorted(str(p.relative_to(root)) for p in target.glob("*.yaml"))
            if workflow_files:
                found.append({"system": name, "files": workflow_files})
        elif kind == "file" and target.is_file():
            found.append({"system": name, "files": [rel_path]})
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Repository root to scan (default: cwd)")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(json.dumps({"error": f"not a directory: {root}"}), file=sys.stderr)
        return 1

    commands: dict = {}
    notes: list = []
    ecosystems: list = []

    detect_node(root, commands, notes, ecosystems)
    detect_python(root, commands, notes, ecosystems)
    detect_rust(root, commands, ecosystems)
    detect_go(root, commands, ecosystems)
    detect_jvm(root, commands, ecosystems)
    detect_dotnet(root, commands, ecosystems)
    detect_ruby(root, commands, ecosystems)
    detect_php(root, commands, ecosystems)
    detect_elixir(root, commands, ecosystems)
    detect_makefile(root, commands)

    ci_configs = detect_ci_configs(root)

    for category in ("test", "lint", "typecheck", "build"):
        if category in commands:
            commands[category] = sorted(set(commands[category]))

    if not ecosystems:
        notes.append(
            "No recognized manifest at this root — for a monorepo, re-run once per package "
            "directory; otherwise this repo genuinely has no verification tooling yet "
            "(do not invent any; say so plainly in the report)."
        )
    if not commands:
        notes.append(
            "No verification commands could be inferred. Ask before running anything the repo "
            "doesn't already declare, and say plainly that no existing CI/QA gate was found."
        )

    report = {
        "root": str(root.resolve()),
        "ecosystems": sorted(set(ecosystems)),
        "verification_commands": commands,
        "ci_configs": ci_configs,
        "notes": notes,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
