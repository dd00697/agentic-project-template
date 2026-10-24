# Code review standard

Used by human reviewers and by the `review-standards` skill. Review the change against its
issue's acceptance criteria first, then against this checklist.

## Severity

| Level | Meaning | Merge? |
|---|---|---|
| 🔴 **Blocking** | Bug, security issue, data loss, unmet acceptance criterion, missing tests for new behaviour | No |
| 🟡 **Should fix** | Maintainability or clarity problem that will cost us later | Fix now or open a follow-up issue |
| ⚪ **Nit** | Preference or polish | Author's call |

## Checklist

### Correctness
- Every acceptance criterion is met, and you can point to where.
- Edge cases: empty, null, very large, unicode, concurrent, timezone, partial failure.
- No off-by-one errors, unhandled branches, or silent fallthroughs.

### Tests
- New behaviour has tests that would fail without the change.
- Tests assert behaviour, not implementation details or mock calls.
- Bug fixes include a regression test.
- No tests deleted, skipped, or loosened without a stated reason.

### Security
- Untrusted input is validated. Queries are parameterised. Output is encoded.
- Authorisation is checked where data is accessed, not just in the UI.
- No secrets, tokens, or personal data in code, logs, errors, or tests.
- New dependencies are needed, maintained, and licence-compatible.

### Errors and observability
- Errors are handled or propagated deliberately. Nothing is swallowed.
- Messages help the next person debug. Logs contain no sensitive data.

### Design and readability
- The change is as small as it can be and does one thing.
- Names say what things are. Functions are short enough to read in one pass.
- No duplication of existing helpers, and no speculative abstraction.
- Fits the existing architecture. Deviations have an ADR.

### Performance (only where it matters)
- No N+1 queries, unbounded loops or memory, or blocking I/O on hot paths.

### Docs
- README, AGENTS.md, or comments are updated where behaviour or commands changed.
- Comments explain *why*, not *what*.

## Common AI-generated problems

Look for these on purpose. They're frequent in agent-written code:

- **Invented APIs**: functions, flags, or config keys that don't exist in the installed version.
- **Scope creep**: unrelated refactors, renames, or formatting churn mixed into the change.
- **Gaming the checks**: weakened assertions, `skip`/`xfail`, broad `except`/`catch`, `# type: ignore`, `any`, lint disables.
- **Dead weight**: unused functions, parameters, imports, or files. Leftover debug code.
- **Over-engineering**: abstractions, options, or layers no requirement asked for.
- **Hollow tests**: tests that only exercise mocks, or assert that something "is not None".
- **Restating comments**: comments that narrate the code line by line.
- **Confident but wrong docs**: README or docstrings describing behaviour the code doesn't have.

## Output format

```
Verdict: APPROVE | CHANGES REQUESTED

🔴 Blocking
- path/to/file.ts:42 - <problem>. <why it matters>. Fix: <concrete suggestion>.

🟡 Should fix
- ...

⚪ Nits
- ...

Not reviewed: <anything skipped and why>
```

Leave out empty sections. Say "No findings" if there are none.
