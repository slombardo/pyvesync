<!-- Sync Impact Report
Version: unversioned scaffold -> 1.0.0
Modified principles: all five scaffold principles replaced with pyvesync-specific governance
Added sections: Technical Constraints; Workflow and Quality Gates
Removed sections: none
Deferred items: RATIFICATION_DATE is unknown and recorded as TODO(RATIFICATION_DATE)
-->
# pyvesync Constitution

## Core Principles

### I. Public Device Contracts Are Stable
Public classes, methods, attributes, and serialized response shapes are the project contract.
Changes to those contracts MUST preserve existing behavior unless a deliberate breaking
change is approved, documented, and versioned with migration guidance.

This keeps automation built on pyvesync predictable and reduces device-specific surprises.

### II. Network I/O Stays Async and Explicit
VeSync communication MUST remain asynchronous, session-aware, and transparent about
errors. Library code MUST not introduce hidden blocking requests or silent retries that
change user-visible behavior.

This preserves the library's aiohttp-based design and keeps failure modes observable.

### III. Tests Prove Behavior Before Release
Behavioral changes MUST be covered by focused tests, and bug fixes SHOULD reproduce the
failure before the fix. Fixtures, recorded responses, and regression coverage are required
for parsing, auth, device mapping, and state transitions.

This project integrates with remote devices and APIs, so tests are the cheapest reliable
proof that behavior still matches expectations.

### IV. Types, Lint, and Errors Are First-Class
New code MUST include accurate type hints and MUST satisfy the repository's linting and
typing expectations. Exceptions MUST be specific, propagated intentionally, and never
swallowed just to make a call site look successful.

This keeps the codebase maintainable and makes API failures easier to debug.

### V. Documentation Tracks User-Facing Behavior
Any change that affects setup, supported devices, public APIs, response semantics, or
error handling MUST be reflected in the README or docs before release.

This project is consumed as a library, so documentation is part of the contract.

## Technical Constraints

- Supported runtime: Python 3.11 or newer.
- HTTP and session handling MUST use aiohttp-based async patterns consistent with the
	existing library architecture.
- Sensitive values such as usernames, passwords, tokens, and request payloads MUST be
	redacted from logs by default unless a caller explicitly disables that behavior.
- Public behavior SHOULD remain compatible across supported device families unless a
	versioned breaking change is intentional and documented.

## Workflow and Quality Gates

- Implementations MUST include or update tests for the affected slice before merge.
- Device support changes SHOULD be validated against representative fixtures for the
	relevant product type and device map behavior.
- Pull requests that change public behavior MUST call out the impact on consumers and the
	expected versioning consequence.
- Release-ready changes MUST leave the repository in a state where pytest, typing, and
	lint checks pass for the touched area.

## Governance

This constitution supersedes informal workflow notes and governs decisions that affect the
library's public contract, quality bars, and release discipline.

Amendments require a documented rationale, a version bump, and review of downstream impact.
Versioning follows semantic rules: MAJOR for incompatible governance or principle changes,
MINOR for new principles or materially expanded guidance, and PATCH for clarifications or
non-semantic refinements.

Compliance is checked in review by confirming the change set matches the constitution,
tests cover the affected behavior, and documentation is updated when user-visible behavior
changes.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date not recorded | **Last Amended**: 2026-09-26
