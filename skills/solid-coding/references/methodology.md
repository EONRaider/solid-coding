# The five-phase methodology

Both invocation modes (refactor/audit and in-flight advisory — see `SKILL.md`) run this same process. Advisory mode collapses phase 1 and skips phase 4; everything else is identical, because the judgment calls involved don't get easier just because the scope is smaller.

## Phase 1 — Discovery

Goal: know what language/ecosystem this is and what verification tooling *already exists*, without inventing anything new.

Run the bundled script rather than re-deriving this by eye every time — it's a deterministic, repeated lookup, exactly the kind of task that belongs in `scripts/`, not in freehand reasoning:

```bash
python3 <plugin-path>/skills/solid-coding/scripts/discover_ci_qa.py <repo-root>
```

It reports detected ecosystems, inferred `test`/`lint`/`typecheck`/`build` commands (sourced from the repo's own manifests — `package.json` scripts, `Cargo.toml`, `go.mod`, Makefile targets, and so on), and any CI config files found (`.github/workflows`, `.gitlab-ci.yml`, etc.). Treat its `verification_commands` output as the *only* commands phase 4 is allowed to run — never substitute a preferred tool the repo doesn't already declare.

If the report comes back empty (no ecosystem recognized, no commands inferred), say so plainly rather than guessing a command that might not exist in this environment. A repo with no verification tooling yet is a real, valid state — flag it as a gap, don't paper over it by inventing a check.

For a large repository, dispatch this phase to a subagent (a plain research/explore-style `Agent` call) so the scan's own tool-call noise doesn't pollute the main conversation — the discovery output the orchestrating conversation actually needs is the small JSON report, not the process of finding it.

**In-flight advisory mode skips this phase** when the session already knows the stack and verification commands from earlier work in the same conversation — re-running discovery on every small check is wasted work.

## Phase 2 — Analysis (parallel, per principle-cluster)

Goal: find candidate violations within the bounded scope (a path, a diff, or a full worktree if that's genuinely what was asked for), one dimension at a time so no single pass has to hold every principle in mind at once.

Dispatch the `solid-reviewer` subagent (see `../../agents/solid-reviewer.md`) once per cluster, **in parallel** — use the `Agent` tool directly rather than a gated multi-agent orchestration tool, so this always works regardless of whether the session has opted into any heavier orchestration mode:

| Cluster | Covers |
|---|---|
| `srp-soc-encapsulation` | SRP, Separation of Concerns, Encapsulation |
| `ocp-patterns` | OCP, design-pattern fit (both under- and over-application) |
| `lsp-isp-dip` | Liskov Substitution, Interface Segregation, Dependency Inversion |
| `dry-aha-yagni` | DRY violations and the AHA/YAGNI overreach they can tempt |
| `lod-cqs` | Law of Demeter, Command-Query Separation |

Pass each call the same `scope`, its one `principle_cluster`, and whatever `language_context`/`repo_conventions` phase 1 (or the ongoing conversation) already established. Five clusters is deliberate — fine enough that each reviewer holds a coherent, related set of signals in mind, coarse enough that this isn't fifteen-plus trivial single-principle dispatches producing overhead without added signal.

Bound the scope explicitly every time: refactor mode never expands past the requested path/diff on its own initiative, and advisory mode never expands past the files actually touched in the current session.

## Phase 3 — Adversarial verification

Goal: every finding gets independently re-examined by a subagent that didn't produce it, specifically checking for false positives and for fixes that overreach into their own YAGNI/AHA/KISS violations.

Dispatch `solid-verifier` (see `../../agents/solid-verifier.md`) once per finding — these can run in parallel with each other. Each call receives exactly one finding plus the code it refers to; the verifier re-derives the violation from the code itself rather than trusting the reviewer's summary, checks behavior preservation via its own call-site trace, and checks the proposed fix against `principle-tensions.md`.

Only `CONFIRMED` findings (and any `PLAUSIBLE` finding the user explicitly approves after seeing the verifier's stated uncertainty) proceed to phase 4. `REJECTED` findings are dropped — but keep the rejection reasoning in the final report; a rejected finding with its reasoning attached is useful context, a silently dropped one looks like the tool missed something.

This phase is not optional overhead — it's the mechanism that keeps a technically-correct-sounding finding from turning into an over-engineered "fix." If a full run through this skill never rejects anything, treat that as a signal the verification is rubber-stamping rather than actually checking, not as a sign the codebase is unusually clean.

## Phase 4 — Execution (refactor mode only)

Goal: apply confirmed fixes without ever stacking a new change on top of an already-broken state.

1. Order confirmed fixes smallest-safe-increment first.
2. If the touched area has no existing test coverage and adding one is feasible, propose a characterization test before refactoring it — ask before adding it, since it's new code the user should see, but don't refactor untested behavior blind when a cheap safety net is available.
3. Apply one increment.
4. Run the **discovered** (phase 1) verification commands — never a bespoke or invented check — after that increment.
5. On failure, stop immediately. Report exactly what broke rather than attempting further changes on top of a failing baseline.
6. Repeat from step 3 for the next confirmed fix.

**In-flight advisory mode skips this phase entirely** — it reports findings for the user (or the ongoing coding work) to act on, and never applies a fix on its own initiative.

## Phase 5 — Report

Every run — refactor or advisory — ends with a structured account, not just a list of edits:

- **Fixed:** which confirmed findings were applied, and what verification command confirmed each increment stayed green.
- **Deferred:** any `PLAUSIBLE` finding not yet approved, or any finding whose fix was intentionally left `proposed_fix: null` because the right shape isn't knowable yet — state *why* explicitly (e.g. "abstraction shape unclear — forcing a Strategy here now would be a YAGNI violation until a second variant exists").
- **Rejected:** what `solid-verifier` ruled out and why, so the record shows the check happened rather than looking like nothing was found.
- **Verification:** the exact commands run (from phase 1's discovery) and their outcome.

A run that reports zero findings, zero fixes, and an honest "discovery found no verification tooling in this repo" is a complete and correct report — never inflate findings or skip the discovery gap to look more useful.
