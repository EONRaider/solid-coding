# SOLID, reframed language-agnostically

Read each principle as a signal-to-watch-for plus a mechanism-family, not an OOP-specific rule. Every mechanism listed has an equivalent in functional, procedural, and dynamically-typed languages — apply whichever fits the file's actual idiom rather than importing a foreign one.

## S — Single Responsibility Principle

**Claim:** a unit (function, class, module) should have one reason to change — one axis of change, one stakeholder or concern it answers to.

**Signal it's violated:**
- Describing what the unit does requires "and" or "or" joining two unrelated verbs.
- Two unrelated stakeholders (e.g. "the billing team" and "the UI team") each force edits to the same file for reasons that have nothing to do with each other.
- A function mixes I/O, business-rule application, and output formatting at the same abstraction level.

**Fix mechanism:** split along axes of *change*, not axes of code that merely look separable. Two blocks of code that always change together for the same reason are not an SRP violation even if they look like they could be split — splitting them anyway is the SRP-vs-KISS tension (see `principle-tensions.md`).

## O — Open/Closed Principle

**Claim:** software entities should be open for extension, closed for modification — add new behavior without editing and re-testing existing, working code.

**Signal it's violated:**
- A growing `if`/`switch`/`match` chain keyed on a "kind" or "type" field, and the same chain (or its shape) is duplicated at more than one call site.
- Adding a new variant of something requires hunting down every place that switches on the old variants.

**Fix mechanism (language-agnostic — pick what the language actually gives):**
- Polymorphism / virtual dispatch (OOP)
- Strategy tables / maps from key to behavior (any language with first-class functions)
- Higher-order functions taking behavior as a parameter
- Exhaustive closed unions with compiler-enforced exhaustiveness checking (Rust, TypeScript, Haskell, Swift) — the "closed" half of open/closed is the exhaustiveness check itself, not inheritance

**Anti-signal — don't apply this reflexively:** if there is exactly one variant today and no second one is scheduled, an extension point is speculative infrastructure — that's the OCP-vs-YAGNI tension (see `principle-tensions.md`). Two real variants is the point at which extracting a Strategy/table starts paying for itself.

## L — Liskov Substitution Principle

**Claim:** anything substitutable for a contract (a subtype, an interface implementation, a duck-typed shape, a trait impl) must honor that contract's preconditions, postconditions, and invariants — a caller that only knows the contract must get correct behavior regardless of which implementation it holds.

**Signal it's violated:**
- An implementation throws `NotImplementedError` / panics / returns a sentinel error for a method the contract promises.
- An implementation silently no-ops where the contract implies an effect happens.
- Callers `instanceof`-check or type-switch on which concrete implementation they have before calling it correctly — that check is itself evidence the contract isn't actually uniform.
- An override strengthens a precondition (accepts a narrower input range than the contract promises) or weakens a postcondition (returns something less specific than callers were promised).

**Fix mechanism:** this is a contract-design problem, not a language-feature problem — it applies identically to interfaces, protocols, traits, ABCs, and pure structural/duck typing. Either fix the implementation to honor the full contract, or the contract was drawn too broadly and should be split (this overlaps with ISP below).

## I — Interface Segregation Principle

**Claim:** no client should be forced to depend on members of an interface it doesn't use. Prefer several small, cohesive contracts over one broad one.

**Signal it's violated:**
- An implementer has stub methods that throw/no-op because that implementer only ever needs part of the interface.
- A caller imports or receives a large interface/type but only ever calls one or two of its methods.

**Fix mechanism:** split the interface along actual client usage patterns — group methods by which callers need them together, not by which implementer happens to provide them together today.

**Anti-signal:** don't split an interface down to one method per interface pre-emptively "just in case" a future client needs a different subset — segregate once two real clients demonstrably need different slices (ISP-vs-pragmatism tension, see `principle-tensions.md`).

## D — Dependency Inversion Principle

**Claim:** high-level policy (business/domain logic) should not depend on low-level detail (infrastructure); both should depend on an abstraction the high-level module defines. Abstractions should not depend on implementation details.

**Signal it's violated:**
- Domain/business logic directly imports and instantiates a concrete infrastructure client (a specific DB driver, a specific HTTP client, a filesystem path) rather than receiving an abstraction.
- The unit cannot be tested without the real dependency (a live database, a real network call) because there's no seam to substitute a test double.

**Fix mechanism (language-agnostic):**
- Constructor or parameter injection of an interface/protocol/trait
- Ports-and-adapters (hexagonal) layering: domain defines the port, infrastructure implements the adapter
- In languages with first-class functions, simply passing behavior in as a closure/callback is enough — a full interface hierarchy isn't required to satisfy DIP

**Note:** DIP is about the *direction* of the dependency (detail depends on abstraction, never the reverse), not about how many layers of indirection exist. One well-placed seam is sufficient; stacking abstractions beyond what's needed to invert the one dependency that actually varies is over-application, not correctness.

## Cross-references

- For when a design pattern is the concrete mechanism that realizes one of these principles (Strategy for OCP, Adapter for DIP at integration boundaries, etc.), see `design-patterns.md`.
- For the tensions that keep these from being applied as unconditional rules, see `principle-tensions.md` — read it before treating any SOLID finding as automatically actionable.
