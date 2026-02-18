# Carron

**Carron** is a CLI tool that generates tests using an LLM and optionally executes them.

Carron does not attempt to analyze your repository or discover tests automatically.  
You explicitly tell Carron what to test — Carron helps you write and run those tests.

> Carron is a generator, not an analyzer.

Carron is named after the historic Carron Ironworks, reflecting the idea of producing reliable results through forging rather than manual construction.

---

## Goals

- Generate useful tests for explicitly specified targets
- Keep architecture small and stable
- Allow swapping LLM providers (OpenAI-compatible)
- Allow future multiple testing styles (property, diff, snapshot)
- Allow future alternative frontends (e.g. Rust CLI)

---

## Basic Usage

### Recommended Workflow

Generate and optionally run tests for a target:

```
carron test <target>
```

Carron will:

1. Analyze the target
2. Select the most appropriate testing style
3. Generate tests
4. Optionally execute them

Modes:

```
--mode emit Generate tests only (default)
--mode check Validate generated tests
--mode run Run tests via pytest
```

Example:

```
carron test mypkg.math:clamp --mode run
```

---

### Advanced Usage (Explicit Forge Selection)

You can bypass automatic strategy selection and choose a specific testing style:

```
carron prop <target>
carron diff <targetA> <targetB>
```


This is intended for users who want precise control over test style.

## Strategy Selection

The `test` command uses an internal planner to select the most appropriate forge (`prop`, `diff`, etc.) for the given target.

You can see the recommendation without generating tests:

```
carron suggest <target>
```


Or apply it automatically:

```
carron suggest <target> --apply --mode run
```


The planner does not scan your repository. It evaluates only the specified target and selects among implemented testing styles.

---

## Target Syntax (v0.1)

Supported forms:

```
module:func
module:Class.method
file.py:func
file.py:Class.method
```

Examples:

```
carron prop math_utils:clamp
carron prop src/cache.py:LRUCache.get
carron diff old.py:parse new.py:parse
```

Carron does not scan the repository.  
The user must specify the target.

---

## Testing Styles (Forges)

Carron generates tests using different *testing styles* (called **forges**).  
Each forge represents a different correctness strategy — not just a different template.

### Initial (v0.1)

#### `prop` — Property Tests
Generates property-based tests using **Hypothesis**.

Instead of checking specific examples, the test asserts invariants about behavior and lets Hypothesis search for counterexamples.

Best for:
- pure functions
- transformations
- parsing
- numeric logic
- edge-case discovery

Example idea:
> “Result is always within bounds”  
> “Encoding then decoding returns the original value”

---

#### `diff` — Differential Tests
Compares two implementations and verifies they behave identically.

No formal specification required — correctness is defined by agreement.

Best for:
- refactors
- rewrites
- performance replacements
- bug-compatible ports

Example idea:
> `new_parser(x) == old_parser(x)`

---

### Planned (future)

#### `snapshot`
Captures structured output and detects regressions across changes.

#### `meta` (Metamorphic)
Verifies relationships between inputs and outputs rather than fixed results.

Example:
> `sort(sort(x)) == sort(x)`

#### `audit`
Evaluates test strength by intentionally mutating behavior and checking failures.

---

> Each forge is independent.  
> Carron is designed so new testing styles can be added without changing the CLI or core logic.

---

## Default Tooling

Carron generates tests using specific libraries by default.

| Forge | Language | Default Library | Used At |
|------|------|------|------|
| prop | Python | Hypothesis | Inside generated test code |
| diff | Python | pytest assertions | Inside generated test code |
| snapshot | Python | pytest snapshot-style assertions (planned) | Generated test |
| meta | Python | Hypothesis (relations) (planned) | Generated test |
| audit | Python | mutation runner (planned) | Runner layer |

> Carron itself does not embed these libraries.  
> Generated tests import and use them.

Carron only runs `pytest` as a subprocess in `--mode run`.

---

## Execution Dependency Expectations

If a generated test requires a dependency:

- `emit` succeeds regardless
- `check/run` will report missing dependencies

Example:

```
Generated property test requires: hypothesis
Install with: pip install hypothesis
```

---

## Architecture Overview

Carron is a modular pipeline composed of a CLI, a strategy selector,
pluggable test generators (forges), language adapters, and an optional test runner.

### Design Rule

> Forges are pure generators.  
> Only the CLI interacts with the environment.

---

 
## Configuration

Carron reads configuration from CLI flags, environment variables, and `pyproject.toml`.
CLI options always override configuration file values.

Carron never modifies configuration files.

---

## Non-Goals (v0.1)

- automatic test discovery
- repository indexing
- pytest plugin integration
- framework-specific helpers
- multiple executables
- provider-specific LLM APIs

---

## Philosophy

Carron does not decide *what* to test.

You decide.

Carron helps generate and optionally execute tests for it.

Carron may assist in choosing a testing strategy, but it never analyzes or scans your repository automatically.

---

## License

Carron is licensed under the **GNU Affero General Public License v3 (AGPLv3)**.

See the [LICENSE](LICENSE) file for the full legal text.

### License Philosophy

Carron is intended to remain a shared tool, not a closed product.

You are free to:

- Use Carron for personal projects
- Use it inside a company
- Modify it
- Contribute improvements
- Run it as part of your workflow

However, if you:

- Modify Carron and distribute it, or
- Run a hosted service based on Carron

You must make the modified source available under the same license.

This ensures improvements benefit the community and prevents proprietary forks or closed SaaS wrappers from capturing the project.

This license is not intended to prevent commercial use — it is intended to ensure reciprocity.

If you require different licensing terms for a specific use case, please open a discussion.
