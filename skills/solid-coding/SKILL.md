---
name: solid-coding
description: Language-agnostic methodology for writing and refactoring code against SOLID, GoF design patterns, and complementary principles (DRY, KISS, YAGNI, Boy Scout Rule, Separation of Concerns, Encapsulation, Law of Demeter, Command-Query Separation, TDD, AHA). Use when the user asks to refactor code, review or audit code quality/architecture, "clean this up", "does this violate SOLID", "is this over-engineered", wants a design-pattern recommendation, or wants a full-worktree code-quality pass. Also use proactively, without the user naming SOLID directly, right before finalizing or committing non-trivial new code in the current session — a new class hierarchy, a service layer, a module with more than one clear responsibility, or a growing conditional keyed on type/kind. Every finding is independently, adversarially re-verified by a second subagent before being reported or applied, and every fix runs only through the repo's own existing test/lint/build commands — this skill never invents new tooling for the occasion.
license: MIT (see plugin root LICENSE)
compatibility: Claude Code only — dispatches the solid-reviewer and solid-verifier subagents via the Agent tool and runs skills/solid-coding/scripts/discover_ci_qa.py via Bash (Python 3, stdlib only). Works on any repository language; ecosystem and verification tooling are detected from the repo itself, never assumed.
---

# solid-coding

A structural-quality lens for any codebase, in any language: SOLID, GoF design patterns, and the complementary principles that keep those two from being applied as unconditional rules. Read `references/principle-tensions.md` before treating any finding as automatically actionable — it is the load-bearing part of this skill. The goal is coherent, evolvable code for *this* codebase's actual, observed change patterns, not maximum compliance with every principle scored independently. A finding that is technically correct on one axis but overreaches on another (adds abstraction a YAGNI check would reject, for instance) is not a good fix — see the tensions file for the specific pairings and `agents/solid-verifier.md` for how the adversarial check enforces this.

## Two modes, one methodology

Both modes run the same five-phase process, detailed in full in `references/methodology.md`. Read that file before running either mode for the first time in a session — this section only summarizes it.

**Refactor/audit mode** — triggered by an explicit request to review, audit, or refactor a worktree, a path, or a diff (a PR, `git diff`, or a named set of files). Runs all five phases, including execution: confirmed fixes get applied, smallest safe increment first, verified against the repo's own discovered test/lint/build commands after every increment.

**In-flight advisory mode** — triggered proactively while code is being actively written or finalized in the current session, or by a direct ad hoc request to check specific just-written code. Scope is the touched files only. Skips phase 1 (discovery) when the session already knows the stack and verification commands from earlier work, and always skips phase 4 (execution) — this mode reports findings for the user or the ongoing work to act on; it never applies a fix on its own initiative.

## The five phases, in brief

1. **Discovery** — detect the repo's language/ecosystem and its *existing* verification commands (never new tooling) by running `scripts/discover_ci_qa.py`. Skipped in advisory mode when already known this session.
2. **Analysis** — dispatch the `solid-reviewer` subagent once per principle-cluster, in parallel, each scoped to the same bounded set of files:

   | Cluster | Covers |
   |---|---|
   | `srp-soc-encapsulation` | SRP, Separation of Concerns, Encapsulation |
   | `ocp-patterns` | OCP, design-pattern fit (over- and under-application both) |
   | `lsp-isp-dip` | Liskov Substitution, Interface Segregation, Dependency Inversion |
   | `dry-aha-yagni` | DRY violations, and the YAGNI/AHA overreach a fix could introduce |
   | `lod-cqs` | Law of Demeter, Command-Query Separation |

3. **Adversarial verification** — dispatch the `solid-verifier` subagent once per finding (in parallel across findings). It re-derives the violation from the code independently, traces call sites for behavior-preservation risk, and checks the proposed fix against `references/principle-tensions.md`. Verdicts: `CONFIRMED` / `PLAUSIBLE` / `REJECTED`.
4. **Execution** (refactor mode only) — apply `CONFIRMED` (and user-approved `PLAUSIBLE`) fixes one increment at a time, running the repo's own discovered verification commands after each; stop immediately on a failure rather than stacking more changes on a broken baseline.
5. **Report** — fixed / deferred (with the reason) / rejected (with the reason) / verification commands run and their outcome.

Use the plain `Agent` tool for phases 2 and 3, dispatched in parallel within each phase, rather than a gated multi-agent orchestration tool — this keeps the workflow available in every session regardless of whether heavier orchestration has been opted into separately.

## Reference material

Load these as the corresponding phase or judgment call needs them — they're kept out of this file to keep it lean, not because they're optional reading before using the skill for the first time:

- **`references/solid-principles.md`** — the language-agnostic signal and fix-mechanism for each SOLID letter.
- **`references/design-patterns.md`** — the GoF catalog as vocabulary: intent, which SOLID principle each pattern realizes, the motivating smell, and the anti-signal for when *not* to reach for it.
- **`references/complementary-principles.md`** — DRY, KISS, YAGNI, Boy Scout Rule, SoC, Encapsulation, Law of Demeter, CQS, TDD, AHA, each with its own unconditional-application failure mode.
- **`references/principle-tensions.md`** — read this before accepting any finding as actionable. The specific pairings (DRY vs. AHA/YAGNI, OCP vs. YAGNI, SRP vs. KISS, ISP vs. pragmatism, and others) and how to judge which side wins in a concrete case.
- **`references/methodology.md`** — the full five-phase process, including exact subagent dispatch parameters and edge-case handling for each phase.

## Subagents

- **`solid-reviewer`** (`agents/solid-reviewer.md`) — analysis-phase reviewer, parameterized by `scope` and `principle_cluster`.
- **`solid-verifier`** (`agents/solid-verifier.md`) — adversarial verifier, takes one finding at a time and returns a verdict.

Both can also be dispatched standalone, outside the full five-phase flow, for a narrower ad hoc request (e.g. "check this file for LSP violations" or "pressure-test this specific proposed refactor").

## What this skill will not do

Never introduce a new linter, test runner, formatter, or CI check that the repo doesn't already have configured — phase 1 exists specifically so this skill wires into what's there instead. Never apply a fix in refactor mode without a `CONFIRMED` (or explicitly user-approved `PLAUSIBLE`) verdict from phase 3. Never expand scope past what was requested (a diff stays a diff; advisory mode stays limited to files actually touched this session) without asking first.
