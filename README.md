# solid-coding

A Claude Code skill that turns SOLID, GoF design patterns, and their complementary principles (DRY, KISS, YAGNI, Boy Scout Rule, Separation of Concerns, Encapsulation, Law of Demeter, Command-Query Separation, TDD, AHA) into a language-agnostic methodology — usable both as a whole-worktree refactor pass and as advisory guidance while code is being actively written.

It never invents CI/QA tooling: discovery detects and reuses whatever test/lint/build commands a repo already has. Every finding is independently, adversarially re-verified by a second subagent (`solid-verifier`) before it's reported or applied — specifically checking that a proposed fix doesn't resolve one principle violation by introducing a YAGNI/AHA/KISS violation of its own. See [`references/principle-tensions.md`](skills/solid-coding/references/principle-tensions.md) for why that check exists; it's the part of this skill that actually keeps it from recommending over-engineered fixes.

## Install

```bash
claude plugin marketplace add EONRaider/claude-plugins
claude plugin install solid-coding@eonraider
```

Or, for local development (edits take effect immediately, no reinstall):

```bash
ln -s "$(pwd)/skills/solid-coding" ~/.claude/skills/solid-coding
```

Start a new Claude Code session after installing — skills and plugin subagents are only picked up at session start.

## Use

Ask Claude to refactor, review, or audit a worktree/path/diff against SOLID and design patterns — or just keep working normally: the skill also triggers proactively before finalizing non-trivial new code in the current session (a new class hierarchy, a service layer, a growing type-keyed conditional).

See [`skills/solid-coding/SKILL.md`](skills/solid-coding/SKILL.md) for the full methodology, and [`skills/solid-coding/references/`](skills/solid-coding/references/) for the underlying principle catalog.

## Structure

```
solid-coding/
├── .claude-plugin/plugin.json
├── skills/solid-coding/
│   ├── SKILL.md
│   ├── references/          # SOLID, patterns, complementary principles, tensions, methodology
│   ├── scripts/              # discover_ci_qa.py — deterministic CI/QA detection
│   └── evals/                # eval scenarios + fixtures
└── agents/
    ├── solid-reviewer.md     # analysis-phase subagent, parameterized by principle-cluster
    └── solid-verifier.md     # adversarial verification subagent
```

## License

MIT — see [`LICENSE`](LICENSE).
