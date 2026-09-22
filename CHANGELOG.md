# Changelog

All notable changes to solid-coding are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versioning
follows [Semantic Versioning](https://semver.org/) — pre-1.0, so behavior
can still shift between minor versions. Version headers here match the
repo's git tags, which follow GitHub's `vX.Y.Z` convention.

## [Unreleased]

## [v0.2.0] - 2026-09-22

### Added

- Phase-5 report section **Out-of-scope occurrences**: copies of a
  confirmed defect that the analysis or verification trace finds outside
  the requested scope, each listed as `path:line`, the principle, and the
  proposed fix. They are reported for the user to act on — never applied
  without asking, and never described as filed, queued, or fixed.
  Documented in `SKILL.md` and `references/methodology.md`.
- `out_of_scope_occurrences` field in `solid-reviewer`'s per-finding
  output and `solid-verifier`'s verdict output; the verifier's
  re-confirmed list feeds the report section. `solid-verifier` also
  takes the requested `scope` as input.
- Eval fixture `fixture-out-of-scope-duplication` and eval 5, where the
  verifier finds a duplicated helper outside the requested file.

### Fixed

- `discover_ci_qa.py`'s `detect_rust` now checks for a `justfile` /
  `Justfile` and, when present, reports `just <recipe>` commands (e.g.
  `just check`, `just clippy`, `just test`) instead of always defaulting
  to bare `cargo test`/`cargo clippy`/`cargo build` — matching how
  justfile-driven Rust crates actually gate CI.
- `detect_ci_configs` now walks up from the scanned root toward the
  actual git repository root (via `git rev-parse --show-toplevel`)
  looking for CI configs such as `.github/workflows/`, so a
  subdirectory-rooted package in a monorepo (e.g. a `backend/` crate
  under a superproject root) is correctly reported as CI-gated instead
  of showing an empty `ci_configs`.
- Added a Rust-in-a-monorepo eval fixture (`fixture-rust-monorepo`)
  covering both fixes together.

## [v0.1.0] - 2026-09-13

### Added

- Initial release: `solid-coding` skill with the five-phase methodology
  (discovery, parallel per-cluster analysis, adversarial verification,
  incremental execution, structured report) covering SOLID, the GoF
  design-pattern catalog, and complementary principles (DRY, KISS, YAGNI,
  Boy Scout Rule, Separation of Concerns, Encapsulation, Law of Demeter,
  Command-Query Separation, TDD, AHA), plus the principle-tensions
  reference that governs when a technically-correct finding should still
  be rejected or scaled down.
- `solid-reviewer` and `solid-verifier` subagents for parallel,
  per-cluster analysis and independent adversarial verification of every
  finding before it's reported or applied.
- `scripts/discover_ci_qa.py` for deterministic detection of a repo's
  existing verification tooling (Node/npm/yarn/pnpm, Python, Rust, Go,
  Java/Maven/Gradle, .NET, Ruby, PHP, Elixir, Makefile targets, and
  common CI configs) — discovery never invents tooling a repo doesn't
  already have.
- Three eval fixtures covering an untested SRP/OCP violation, a
  Node project with existing CI/QA tooling that discovery must respect
  rather than override, and a coincidental-duplication case that a naive
  DRY pass would wrongly merge.
