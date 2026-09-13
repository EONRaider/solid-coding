# Principle tensions — the actual judgment call

Every principle in `solid-principles.md`, `design-patterns.md`, and `complementary-principles.md` has a failure mode when applied as an unconditional rule instead of a tool for a specific situation. Tooling that treats "apply SOLID" as "maximize compliance with every principle simultaneously" reliably produces over-engineered code — more indirection, more abstraction, more configurability than the actual codebase needs, all defensible one principle at a time.

The job of this skill's methodology — and specifically the adversarial verification phase — is to balance these tensions for *this* codebase's real, observed change patterns, not to chase perfect scores on each axis independently. Read this file before treating any `solid-reviewer` finding as automatically actionable.

## DRY vs. AHA / YAGNI

**The pull:** DRY says merge duplication. AHA says duplication is cheaper than the wrong abstraction; YAGNI says don't build for a variant that isn't real yet.

**Resolution:** don't deduplicate on the first repetition. Two occurrences of similar-looking code are not yet evidence of a stable, shared shape — the "rule of three" (tolerate it twice, extract on the third real occurrence) exists because the *right* shape of an abstraction usually isn't visible until there's a third data point to triangulate against. Merging on the second occurrence risks building an abstraction shaped by two examples that happen to look similar today but drift apart tomorrow — at which point the abstraction gets forced to cover a case it wasn't designed for, which is worse than the duplication it replaced.

**Also check:** is this actually duplicated *knowledge*, or coincidentally similar code that encodes independently-changing business rules? Two validation functions that both currently check "value > 0" are not a DRY violation if one is a price constraint and the other is an age constraint — they'll diverge the moment either business rule changes, and merging them creates a false coupling between unrelated domains.

## OCP vs. YAGNI

**The pull:** OCP says make the code open for extension without modification. YAGNI says don't build for a variant that doesn't exist.

**Resolution:** an extension point (Strategy table, plugin registry, exhaustive union with a placeholder for "more later") is only earning its cost once a second real variant exists or is concretely, immediately planned — not "might exist someday." One variant plus a speculative extension point is pure YAGNI violation wearing OCP's justification. Wait for the second variant; extract the seam then, informed by what the second variant actually needs rather than a guess.

## SRP vs. KISS

**The pull:** SRP says split by axis of change. KISS says don't add complexity the problem doesn't require.

**Resolution:** a function or class doing three *genuinely independent* things (each changes for a different, unrelated reason) is a real SRP violation regardless of how simple it currently looks. But fragmenting a simple, cohesive function into several indirection layers because it happens to contain three *steps* — not three independent axes of change — isn't SRP, it's needless ceremony. The test: if two of the "responsibilities" always change together, for the same reason, they're one responsibility wearing two names.

## ISP vs. pragmatism

**The pull:** ISP says split fat interfaces by client usage. Pragmatism says don't multiply files/types for a distinction nobody's asked for.

**Resolution:** segregate once two real clients demonstrably need different subsets of an interface — not preemptively, one interface per method, on the theory that some future client might want a different slice. A single current client using all the methods it's handed is not evidence of an ISP violation, no matter how large the interface is.

## Encapsulation vs. debuggability / observability

**The pull:** Encapsulation says hide internal state. Diagnosing production issues often wants to see exactly that state.

**Resolution:** encapsulation restricts *mutation* paths, not *visibility* for diagnostics — read-only introspection (structured logging, a debug/inspect method, exposed metrics) doesn't violate encapsulation the way letting external code mutate internals directly does. Don't use "encapsulation" as a reason to make a system harder to debug; do use it to keep external code from reaching in and breaking an invariant.

## Boy Scout Rule vs. change-scope discipline

**The pull:** Boy Scout Rule says leave touched code cleaner. Minimal, reviewable diffs say don't expand a change's blast radius.

**Resolution:** the cleanup has to be small and directly adjacent to what the change already touches (rename a locally-confusing variable, delete a dead branch you just noticed while editing the function). A cleanup that would itself need its own review — restructuring a class, extracting a new module — belongs in its own change, proposed separately, not folded into an unrelated fix or feature.

## How the adversarial verification phase uses this file

`solid-verifier` (see `../../agents/solid-verifier.md`) checks every confirmed finding's *proposed fix* — not just the violation — against the relevant tension above. A technically accurate SOLID/pattern finding whose fix trips one of these tensions gets rejected or cut down to the smaller, right-sized version, not approved on the principle's technical correctness alone. This is the specific mechanism that keeps the skill from degrading into "add abstractions everywhere."
