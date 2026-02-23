## Planner (`carron test` and `carron suggest`)

The planner is a core component of Carron v0.1.

Its responsibility is to choose the most appropriate forge for a target and return a structured decision. It never generates tests and never performs side effects. The planner is pure and deterministic given the provided summary.

Commands using the planner:

- `carron test <target>` → selects a forge and executes the workflow
- `carron suggest <target>` → displays the planner decision only

The planner produces a structured decision matching the schema defined in this document.
The initial implementation may construct this structure directly (without JSON) and later switch to an LLM that returns JSON.

### Implementation Strategy (v0.1)

The planner may initially be implemented using deterministic heuristics instead of an LLM.  LLM-backed planning is intended once ≥3 forges exist; until then, heuristics are the default.

However, it must still:

- Produce the same JSON structure as the LLM planner
- Be treated as advisory input by Carron
- Be replaceable by an LLM-backed planner without changing callers

Example heuristic behavior:

- Two targets provided → prefer `diff`
- Single target → prefer `prop`
- Low-confidence situations should set `confidence` lower rather than changing structure

### Validation Rules

Carron must never blindly trust the planner:

- Validate JSON structure
- Ensure `recommended_forge` exists and is implemented
- Fall back safely if invalid

The planner is a decision engine, not a control mechanism.

(LLM-backed planner behavior are defined below.)

## Input Context

Carron passes a small, non-discovery context to the planner:

- `target`: the user-supplied target string (e.g. `mypkg.mod:func`)
- `language`: `python`
- `summary` (from the language adapter, best-effort):
  - `kind`: `function` | `method`
  - `importable`: `true`/`false`
  - `signature`: string (optional)
  - `doc`: first line of docstring (optional)

## Output Schema (v1)

The planner decision structure has the following shape (JSON representation):

```json
{
  "recommended_forge": "prop",
  "confidence": 0.75,
  "rationale": ["short bullet", "short bullet"],
  "needs": ["hypothesis"]
}
```

Field rules:

- `recommended_forge`: one of: `prop`, `diff`
- `confidence`: number in `[0.0, 1.0]`
- `rationale`: array of 1–5 short strings
- `needs`: optional array of dependency identifiers (e.g. `hypothesis`, `pytest`) which may be omitted by heuristic planners

If uncertain, choose the safest option and set `confidence` low with rationale.

## Prompt Template (v1)

System:

- You are a planner for Carron, a test generation CLI.
- Choose the best forge from the allowed list.
- Return ONLY valid JSON matching the schema. No markdown, no prose.

User:

- Target: `{target}`
- Language: `python`
- Adapter summary: `{summary_json}`
- Allowed forges: `prop`, `diff`

Decision guidance:

- Prefer `prop` for pure/transformational logic with clear invariants and easy input generation.
- Prefer `diff` when comparing two implementations is available or when behavior is difficult to specify but agreement is meaningful.
- If the target likely has side effects, I/O, global state, timing, or concurrency, prefer `diff` (or report low confidence).

## Validation and Retries

When using an LLM-backed planner, Carron validates output by:

1. JSON parse
2. schema validation
3. `recommended_forge` ∈ allowed set

On failure, Carron retries up to `N` times (default 2) with a correction message: “Return ONLY valid JSON matching the schema.”
