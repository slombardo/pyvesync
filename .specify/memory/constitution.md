<!-- Sync Impact Report
Version: 1.0.0 -> 1.1.0
Modified principles: all five principles aligned to the project’s documented contribution and quality process
Added sections: none; expanded Technical Constraints and Workflow and Quality Gates to match contributor requirements
Removed sections: none
Deferred items: RATIFICATION_DATE is unknown and recorded as TODO(RATIFICATION_DATE)
-->
# pyvesync Constitution

## Core Principles

### I. Public Device Contracts Are Stable
Public classes, methods, attributes, and serialized response shapes are the project contract.
Changes to those contracts MUST preserve current behavior unless a deliberate breaking change
is approved, documented, and versioned with migration guidance.

This keeps automation built on pyvesync predictable and consistent across all supported
Etekcity, Levoit, Cosori, and related device integrations.

### II. Network I/O Stays Async and Explicit
VeSync communication MUST remain asynchronous, session-aware, and transparent about errors.
Library code MUST NOT introduce hidden blocking requests, silent retries, or opaque exception
swallowing that alter user-visible behavior.

This preserves the library's aiohttp-based design and keeps failures debuggable.

### III. Tests Prove Behavior Before Release
Behavioral changes MUST be covered by focused tests, and bug fixes SHOULD reproduce the
failure before the fix. Recorded API fixtures, regression tests, and device-specific coverage
are required for parsing, auth, device mapping, and state transitions.

This project heavily relies on YAML-backed API fixtures, so tests are the primary proof that a
change remains compatible with the real VeSync API behavior.

### IV. Tooling, Types, and Linting Are Mandatory
New code MUST be compatible with Python 3.11+, use type hints for all function signatures,
and satisfy the repository's linting and typing expectations. Pylint, Ruff, and mypy are not
optional quality gates for the project.

Exceptions MUST be specific, intentional, and propagated clearly rather than hidden to make the
call site appear successful.

### V. Documentation and PR Discipline Are Part of the Product
Any change that affects setup, supported devices, public APIs, response semantics, or error
handling MUST be reflected in the README, docs, or contribution guidance before release.
Pull requests MUST follow the repository's documented review and release process, including
Conventional Commit titles and required CI checks.

This project is consumed as a library, so documentation and review discipline are part of the
public contract.

## Technical Constraints

- Supported runtime: Python 3.11 or newer.
- HTTP and session handling MUST use aiohttp-based async patterns consistent with the
  existing library architecture.
- Sensitive values such as usernames, passwords, tokens, and request payloads MUST be
  redacted from logs by default unless a caller explicitly disables that behavior.
- Public behavior SHOULD remain compatible across supported device families unless a
  versioned breaking change is intentional and documented.
- Device support changes MUST follow the repository's test fixture pattern in the tests
  directory and must be validated with the project's API recording workflow.
- Pre-commit hooks MUST be used for local quality enforcement when making changes. The
  repository's hooks include syntax validation, whitespace cleanup, mypy, Ruff linting,
  and formatting.

## Workflow and Quality Gates

- Changes MUST be made in a dedicated branch and committed with a Conventional Commit-style
  title such as `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, or `chore:`.
- Implementations MUST include or update tests for the affected slice before merge.
- Device support changes SHOULD be validated against representative fixtures for the relevant
  product type and device map behavior.
- Pull requests targeting `master` or `dev` MUST pass the repository's required checks:
  Ruff, Pylint, pytest, and the documentation build where applicable.
- Release-ready changes MUST leave the repository in a state where linting, typing,
  and the relevant test suites pass.
- If a change affects user-facing behavior, the PR summary MUST document the compatibility
  impact and the expected versioning consequence.

## Governance

This constitution supersedes informal workflow notes and governs decisions that affect the
library's public contract, quality bars, and release discipline.

Amendments require a documented rationale, a version bump, and review of downstream impact.
Versioning follows semantic rules: MAJOR for incompatible governance or principle changes,
MINOR for new principles or materially expanded guidance, and PATCH for clarifications or
non-semantic refinements.

Compliance is checked by confirming that the change set matches this constitution; that
pre-commit, linting, typing, and tests pass; and that documentation is updated when
user-visible behavior changes.

**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date not recorded | **Last Amended**: 2026-09-26
