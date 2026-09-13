# Complementary principles

SOLID and design patterns cover structure and extension points. These principles cover the rest of what "correct" means day to day — and, just as importantly, what happens when each one is applied without limit.

## Core coding

**DRY — Don't Repeat Yourself.** Every piece of *knowledge* (a business rule, a formula, a constant with meaning) should have one authoritative representation. Duplicated knowledge means a rule change has to land correctly in every copy, and drift between copies is a bug waiting to be found the hard way.
- *Applied without limit:* merges code that merely *looks* similar today but encodes independently-changing rules — see `principle-tensions.md`'s DRY-vs-AHA entry.

**KISS — Keep It Simple.** Prefer the simplest design that correctly satisfies the actual, current requirement.
- *Applied without limit:* used as an excuse to skip structure a genuinely complex problem needs — "simple" means no more complexity than the problem requires, not less.

**YAGNI — You Aren't Gonna Need It.** Don't build capability, configurability, or an abstraction for a requirement that doesn't exist yet.
- *Applied without limit:* becomes an excuse to never generalize even after a real second use case has already shown up — that's the point AHA's "rule of three" and OCP's "wait for a second real variant" both aim at.

**Boy Scout Rule.** Leave code you touch slightly cleaner than you found it.
- *Applied without limit:* balloons an unrelated bug fix or feature diff with drive-by refactors, which makes the change harder to review and harder to revert cleanly if something goes wrong. Keep the incidental cleanup small and directly adjacent to what the change already touches — a large improvement to code you merely passed through belongs in its own change.

## Architectural

**Separation of Concerns (SoC).** Divide the system into distinct sections by responsibility (domain logic, presentation, persistence, infrastructure) so a change to one doesn't require touching the others.
- This is SRP applied at the module/layer level rather than the function/class level — same signal, larger scope.

**Encapsulation.** Hide a unit's internal representation; require interaction through behavior that preserves its invariants, not direct state manipulation.
- *Signal it's violated:* external code reads or writes an object's fields directly and has to independently re-implement invariant checks the object itself should own.

**Law of Demeter (LoD).** A unit should only invoke methods on: itself, objects passed to it, objects it creates, or its own direct components — not objects reached through a chain of accessors.
- *Signal:* `a.getB().getC().doSomething()` — the caller now depends on B's and C's shape, not just A's, even though it only needed A.
- *Fix:* add a method to A that does what the caller needed, delegating internally — the caller depends on A's behavior, not its internal graph.

**Command-Query Separation (CQS).** A method either performs a side effect (a command, returning nothing meaningful) or answers a question (a query, causing no observable side effect) — never both in the same call.
- *Signal:* a method mutates state *and* returns a meaningful value, so callers can't tell from the signature alone whether calling it twice is safe.
- *Known, deliberate exceptions exist* (a stack's `pop()` is both a command and a query, and is universally understood as such) — flag accidental mixing, not a well-known, intentional exception.

## Process and philosophy

**TDD — Test-Driven Development.** Write a failing test that specifies the next unit of behavior, make it pass with the minimum code that does so, then refactor with the test as a safety net.
- Relevance here: TDD's safety net is *why* the execution phase of this skill's methodology can refactor with confidence. When a refactor target has no test coverage, proposing a characterization test first (not silently skipping the safety net) is the direct application of this principle — see `methodology.md`.

**AHA — Avoid Hasty Abstractions.** Duplication is cheaper than the wrong abstraction; wait until a repeated pattern's actual shape is known (the common "rule of three": tolerate it twice, extract on the third real occurrence) before generalizing it.
- This is the direct counterweight to DRY and the sharpest tool against premature OCP/Strategy/Factory application. See `principle-tensions.md` for the specific pairings.

## Cross-reference

None of these principles are absolute; see `principle-tensions.md` for how they push against each other and against SOLID, and how to judge which one should win in a specific, concrete case rather than by default.
