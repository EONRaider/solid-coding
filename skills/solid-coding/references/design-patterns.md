# Design patterns as vocabulary, not a checklist

Treat every entry below as a **recognized answer to a recurring structural problem** — something to reach for once the problem is actually present, or to name once it's already emerging in the code. Never impose a pattern to look sophisticated, and never impose one preemptively for a variant that doesn't exist yet — that's over-engineering, and it violates YAGNI/AHA exactly as much as any other premature abstraction (see `principle-tensions.md`).

Each entry lists: intent, the SOLID principle it concretely realizes, the smell that motivates reaching for it, and the anti-signal for when it's the wrong call.

## Creational — how construction is decoupled from use

**Factory Method / Abstract Factory**
- *Intent:* decouple "what to construct" from "how the constructed thing is used."
- *Realizes:* OCP — new constructible variants don't require editing call sites.
- *Reach for it when:* construction logic that varies by context/config is duplicated across multiple call sites.
- *Anti-signal:* a single concrete type with no real variation. A factory wrapping one constructor is indirection with no payoff.

**Builder**
- *Intent:* construct a value with many optional or order-sensitive parameters without a telescoping-constructor mess.
- *Reach for it when:* a constructor has grown enough optional parameters that call sites are already hard to read or getting argument order wrong is a real risk.
- *Anti-signal:* two or three parameters. A plain constructor or a keyword-argument call is simpler and just as clear.

**Singleton**
- *Intent:* guarantee exactly one instance, globally reachable.
- *Flag by default* as a testability and hidden-coupling smell rather than recommend it outright: global mutable access makes call sites implicitly coupled to a shared instance that's hard to substitute in tests and easy to reach from places that shouldn't know it exists.
- *Prefer instead:* construct the single instance once at the composition root and pass it explicitly (constructor/parameter injection) to whatever needs it — this gets the "only one" property without the global-access problem.

## Structural — composing units without changing their interfaces

**Adapter**
- *Intent:* bridge an interface you need to one you're given, without modifying either side.
- *Reach for it when:* integrating third-party or legacy code you don't control and can't change to match your domain's shape.
- *Anti-signal:* wrapping code you *do* control and could simply change to match the shape you need. An adapter around your own code is usually a sign the "needed" interface should have been the interface in the first place.

**Decorator**
- *Intent:* attach additional behavior to an object dynamically, without subclassing or modifying it.
- *Reach for it when:* the added behavior is cross-cutting and additive — caching, retry, logging, rate limiting — layered around a stable core operation.
- *Anti-signal:* the "decoration" actually changes core behavior rather than adding around it. That's not decoration, it's a different implementation — model it as one (Strategy, or just a different function).

**Facade**
- *Intent:* provide one simplified entry point in front of a complex subsystem.
- *Reach for it when:* callers routinely need to coordinate several APIs, in a specific order, to accomplish one coherent unit of work — and that coordination is duplicated at multiple call sites.
- *Anti-signal:* a facade around a subsystem with exactly one caller. Inline the coordination at that one call site instead.

**Composite**
- *Intent:* let clients treat an individual object and a group of objects uniformly.
- *Reach for it when:* the domain is genuinely tree-shaped (filesystem-like, UI-component-like, org-chart-like) and callers need to operate on a node or a subtree the same way.
- *Anti-signal:* a flat collection dressed up as a tree because Composite sounded like the "proper" pattern. If nothing nests, this doesn't apply.

**Proxy**
- *Intent:* control access to an object — lazy instantiation, access control, or standing in for something remote.
- *Reach for it when:* one of those three concerns (laziness, access control, remoteness) is real and would otherwise be tangled into the object's own logic.
- *Anti-signal:* using it as a synonym for "wrapper" when none of the three concerns apply — that's likely a Decorator or Adapter, named for what it actually does.

## Behavioral — how responsibility and communication are distributed

**Strategy**
- *Intent:* make an algorithm or policy swappable at runtime, selected independently of the code that uses it.
- *Realizes:* OCP directly — this is the **default mechanism** for open/closed extension in most modern codebases, ahead of inheritance-based approaches.
- *Reach for it when:* the OCP signal (a growing type-keyed conditional, duplicated at call sites) is present and a second real variant exists.
- *Anti-signal:* one strategy implementation, no second one on the horizon. A plain function is the zero-indirection version of the same idea until a second variant is real.

**Observer**
- *Intent:* decouple an event source from the (possibly many, possibly changing) things that react to it.
- *Reach for it when:* the source would otherwise need to know about and directly call every reactor, and that list changes independently of the source's own logic.
- *Anti-signal:* exactly one listener that will only ever be one listener. A direct call is simpler and equally correct.

**Command**
- *Intent:* encapsulate a request (action + parameters) as a first-class value, so it can be queued, logged, undone, or composed.
- *Reach for it when:* undo/redo, request queuing, or macro-style composition of actions is an actual requirement, not a hypothetical one.
- *Anti-signal:* wrapping a single, immediately-invoked function call in a Command object buys nothing if none of queuing/undo/logging is ever used.

**Template Method**
- *Intent:* fix an algorithm's skeleton in a base implementation, letting subclasses override specific steps.
- *Use sparingly* — it's inheritance-coupled (a subclass can't easily swap the skeleton itself, and testing a step in isolation usually means instantiating the whole hierarchy). Prefer Strategy or plain composition (pass the varying step in as a function/callback) in most codebases; reach for Template Method specifically when the *skeleton itself*, not just one step, is the thing that must stay fixed and enforced.

**State**
- *Intent:* let behavior vary with an object's internal state, without a state-keyed conditional scattered through every method.
- *Reach for it when:* the same state-keyed `if`/`switch` recurs across multiple methods of the same object.
- *Anti-signal:* one or two states with simple, stable behavior. A boolean flag and a conditional is clearer until the state machine actually grows.

**Chain of Responsibility**
- *Intent:* pass a request along a chain of handlers, each deciding whether to handle it or pass it on.
- *Reach for it when:* building a middleware-style pipeline where handlers are added/removed/reordered independently of each other.
- *Anti-signal:* a fixed, small sequence of steps that always all run in the same order — that's just a function calling other functions in sequence; a chain adds indirection without adding flexibility that's actually used.

**Mediator**
- *Intent:* centralize otherwise-tangled many-to-many communication between a set of objects into one coordinating object.
- *Reach for it when:* objects are directly wired to many peers and that web of direct references is itself the maintenance problem.
- *Anti-signal:* two or three objects with a simple, stable interaction. A mediator here just relocates the coupling rather than removing it.

**Visitor**
- *Intent:* add new operations over a fixed, closed set of types without modifying those types.
- *High complexity cost* — double dispatch is not intuitive in most languages, and adding a new *type* (as opposed to a new operation) is expensive under Visitor. Reach for it only when the type hierarchy is genuinely stable/closed and new *operations* are what actually keeps getting added — the inverse of the usual OCP case (new variants), which is exactly why it's niche rather than a default.

## Using this catalog during review

When `solid-reviewer` flags an `ocp-patterns` finding, check this file for the pattern whose *intent* matches the actual recurring problem — not the pattern whose name sounds most sophisticated. When `solid-verifier` checks for overreach, this file's anti-signals are the first thing to check the proposed fix against: a "correct" pattern application that trips its own anti-signal is exactly the over-engineering the verification phase exists to catch.
