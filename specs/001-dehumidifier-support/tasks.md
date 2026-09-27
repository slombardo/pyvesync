# Tasks: VeSync Dehumidifier Support

> **Post-implementation revision**: The initial implementation nested dehumidifier
> support inside the existing Humidifier product family (`src/pyvesync/base_devices/humidifier_base.py`,
> `src/pyvesync/devices/vesynchumidifier.py`, `src/pyvesync/models/humidifier_models.py`,
> and `src/tests/api/vesynchumidifier/`), as originally decided in `research.md`. Based on
> maintainer feedback that a dehumidifier should not be grouped under `manager.devices.humidifiers`,
> the implementation was refactored into an independent `Dehumidifier` product family with its
> own `ProductTypes.DEHUMIDIFIER`, `DehumidifierMap`, `src/pyvesync/base_devices/dehumidifier_base.py`,
> `src/pyvesync/devices/vesyncdehumidifier.py`, `src/pyvesync/models/dehumidifier_models.py`,
> `manager.devices.dehumidifiers` container property, and `src/tests/api/vesyncdehumidifier/`
> fixtures/tests. The task descriptions below reflect the original (superseded) plan for
> historical reference; the file paths referenced in Phase 2-5 for the dehumidifier device
> logic have moved as described above.

**Input**: Design documents from `/specs/001-dehumidifier-support/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the existing humidifier architecture and fixture pattern before implementation.

- [X] T001 [P] Review the current humidifier architecture and device mapping pattern in src/pyvesync/base_devices/humidifier_base.py, src/pyvesync/device_map.py, and src/pyvesync/devices/vesynchumidifier.py
- [X] T002 [P] Review the existing fixture and test strategy in src/tests/test_humidifiers.py and src/tests/call_json_humidifiers.py to mirror the dehumidifier validation approach

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Set up the dehumidifier model metadata, shared state contract, and baseline fixtures before story work begins.

- [X] T003 Add dehumidifier model IDs and feature capability metadata to src/pyvesync/device_map.py
- [X] T004 Extend dehumidifier state and constants in src/pyvesync/const.py and src/pyvesync/base_devices/dehumidifier_base.py for dehumidifier-specific fields and validation ranges
- [X] T005 Create baseline API fixture payloads under src/tests/api/vesyncdehumidifier/ for representative dehumidifier responses
- [X] T006 [P] Define the dehumidifier command contract and call mapping in src/pyvesync/devices/vesyncdehumidifier.py using the established Bypass V2 conventions

**Checkpoint**: Foundation ready - dehumidifier discovery and device state contract can now be implemented in parallel across user stories.

---

## Phase 3: User Story 1 - Discover and manage a supported dehumidifier (Priority: P1) 🎯 MVP

**Goal**: Ensure a supported VeSync dehumidifier is recognized and exposed through the library's standard device discovery flow.

**Independent Test**: A valid user account with a dehumidifier can log in, enumerate devices, and retrieve the device state without ad hoc handling or custom API workarounds.

### Tests for User Story 1

- [X] T007 [P] [US1] Add a dehumidifier discovery regression test in src/tests/test_dehumidifiers.py covering model recognition and state parsing
- [X] T008 [P] [US1] Add a representative dehumidifier status fixture under src/tests/api/vesyncdehumidifier/ for the discovery/state test path

### Implementation for User Story 1

- [X] T009 [US1] Implement dehumidifier registration and model mapping in src/pyvesync/device_map.py so devices resolve to the correct class and feature set
- [X] T010 [US1] Update instantiation and parsing behavior in src/pyvesync/devices/vesyncdehumidifier.py for the dehumidifier model family
- [X] T011 [US1] Extend the dehumidifier state parsing in src/pyvesync/base_devices/dehumidifier_base.py and src/pyvesync/devices/vesyncdehumidifier.py to read dehumidifier power, humidity, target, and operating metrics from the real API payload

**Checkpoint**: User Story 1 is fully functional and independently testable as a dehumidifier discovery and state-read path.

---

## Phase 4: User Story 2 - Control the dehumidifier's core operating functions (Priority: P1)

**Goal**: Allow users to operate the dehumidifier using the standard library methods for power, mode, and target humidity controls.

**Independent Test**: A user can issue the primary power and operation commands for a dehumidifier and observe the device state update without custom per-model logic.

### Tests for User Story 2

- [X] T012 [P] [US2] Add command regression tests for power, mode, and humidity control in src/tests/test_dehumidifiers.py
- [X] T013 [P] [US2] Add fixture payloads for dehumidifier command responses in src/tests/api/vesyncdehumidifier/ so command validation is repeatable and reviewable

### Implementation for User Story 2

- [X] T014 [US2] Implement standard power and mode-control handlers in src/pyvesync/devices/vesyncdehumidifier.py
- [X] T015 [US2] Update humidity target and mode state mapping in src/pyvesync/base_devices/dehumidifier_base.py and src/pyvesync/devices/vesyncdehumidifier.py to reflect the commanded values and API returned payloads
- [X] T016 [US2] Add/adjust dehumidifier-specific command validation in src/pyvesync/const.py and related state helpers so invalid values fail through the project's existing error patterns

**Checkpoint**: User Story 2 is independently functional and validates the main operational use case.

---

## Phase 5: User Story 3 - Access advanced dehumidifier controls and monitoring (Priority: P2)

**Goal**: Expose advanced supported settings and monitoring fields in the same way the library exposes similar humidifier capabilities.

**Independent Test**: A dehumidifier exposing advanced controls exposes only the supported options, and each valid setting updates state consistently through the standard library API contract.

### Tests for User Story 3

- [X] T017 [P] [US3] Add advanced-control regression tests for fan speed, child lock, timer, or other supported features in src/tests/test_dehumidifiers.py
- [X] T018 [P] [US3] Add advanced control fixture payloads under src/tests/api/vesyncdehumidifier/ for the supported settings path

### Implementation for User Story 3

- [X] T019 [US3] Implement feature-gated advanced control methods in src/pyvesync/devices/vesyncdehumidifier.py and keep unsupported operations hidden behind the dehumidifier feature map
- [X] T020 [US3] Extend the dehumidifier state model in src/pyvesync/base_devices/dehumidifier_base.py and src/pyvesync/const.py to include advanced monitoring and settings fields with the repository's existing typed conventions
- [X] T021 [US3] Review and update README.md and docs/ if the user-visible API includes new public methods, examples, or supported-device listing changes

**Checkpoint**: All dehumidifier support work is independently functional and aligned with the project's public contract and docs rules.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation of the feature against the repo's quality gates and project constitution.

- [X] T022 [P] Run the targeted dehumidifier test suite and fixture validation from src/tests/test_dehumidifiers.py to confirm dehumidifier support remains stable
- [X] T023 [P] Execute the repo linting and type-check workflow from the existing project tools (ruff, pylint, mypy) against the affected device code
- [X] T024 Validate the completion criteria from specs/001-dehumidifier-support/quickstart.md and confirm the feature meets the documented success criteria
- [X] T025 Update any user-facing documentation impacted by the new dehumidifier support, including supported device references and examples where appropriate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies - can start immediately
- **Phase 2**: Depends on Phase 1 completion; blocks all user story work
- **Phase 3+**: All depend on Phase 2 completion
- **Phase 6**: Depends on all user story work being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 2 completion and is the minimum viable feature scope
- **User Story 2 (P1)**: Depends on User Story 1 completion and reuses the same device class and state model
- **User Story 3 (P2)**: Depends on User Story 1 and 2 completion, but is independently testable once the base contract is in place

### Parallel Opportunities

- Setup tasks T001 and T002 can run in parallel
- Foundation tasks T003, T004, and T005 can proceed in parallel where fixture creation and mapping work are independent
- Story tests for each user story can be drafted in parallel once the foundation is complete
- The final validation tasks T022 and T023 can run in parallel after the implementation is complete

---

## Parallel Example: User Story 1

```bash
# Run initial dehumidifier discovery tests and fixture preparation in parallel
Task: "Add a dehumidifier discovery regression test in src/tests/test_humidifiers.py"
Task: "Add a representative dehumidifier status fixture under src/tests/api/vesynchumidifier/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete User Story 1
3. Validate discovery and state parsing independently
4. Stop and confirm the device is recognized and usable before implementing richer control features

### Incremental Delivery

1. Discovery + state parsing
2. Basic power and mode control
3. Advanced device features and final validation
4. Documentation and release-readiness checks

### Parallel Team Strategy

With multiple developers:

1. Shared baseline setup and fixtures are completed together
2. One developer works on discovery/state mapping while another drafts command tests
3. Once user story 1 is validated, work on user story 2 and advanced settings can proceed independently

---

## Notes

- [P] tasks represent different files or independent work streams with no blocking dependency
- [US1], [US2], and [US3] labels are required for story-scoped tasks
- Every task includes an exact file path or folder target to keep implementation executable and reviewable
- The implementation should be validated with the existing pytest fixture pattern before merging

---

## Phase 7: Convergence

- [X] T026 CRITICAL Align the dehumidifier status request, response model, and state parser in src/pyvesync/devices/vesyncdehumidifier.py and src/pyvesync/models/dehumidifier_models.py with the real dehumidifier payload so refreshes apply state correctly per US1/AC2 [gap: partial]
- [X] T027 Expand the LDH-H251S feature map, supported modes, and public dehumidifier state/control surface in src/pyvesync/device_map.py and related dehumidifier modules to cover the supported advanced controls exposed by the API per FR-006 [gap: partial]
- [X] T028 Add fixture-backed regression coverage for get_timer, set_timer, and clear_timer in src/tests/test_dehumidifiers.py and src/tests/call_json_dehumidifiers.py per SC-004 [gap: partial]
- [X] T029 Correct the recorded dehumidifier detail fixture in src/tests/api/vesyncdehumidifier/LDH-H251S.yaml so the discovery/state regression path validates the dehumidifier status method rather than the humidifier status method per FR-009 [gap: contradicts]
- [X] T030 Update the supported-device documentation in README.md to match the implemented LDH-H251S dehumidifier support per FR-010 [gap: contradicts]
- [X] T031 Rewrite the outdated humidifier-family summary, scope, and structure references in specs/001-dehumidifier-support/plan.md so the plan matches the delivered independent dehumidifier architecture per plan: architecture decision [gap: contradicts]
- [X] T032 Update the completed Phase 2-6 task descriptions and referenced file paths in specs/001-dehumidifier-support/tasks.md to reflect the independent dehumidifier modules actually used by the implementation per plan: architecture decision [gap: contradicts]

---

## Phase 8: Convergence

- [X] T033 Align the verified dehumidifier setter method names and payload mappings in src/pyvesync/devices/vesyncdehumidifier.py, src/tests/call_json_dehumidifiers.py, and src/tests/api/vesyncdehumidifier/LDH-H251S.yaml with the protocol documented in specs/001-dehumidifier-support/research.md, including `setWorkMode` and the verified advanced-switch payload keys, per FR-005 [gap: partial]
- [X] T034 Add dehumidifier-specific response handling and regression coverage for successful setter envelopes without nested result payloads, nested validation failure code `11003000`, and outer `device timeout` responses with `result: null` in src/pyvesync/utils/device_mixins.py, src/pyvesync/devices/vesyncdehumidifier.py, src/tests/call_json_dehumidifiers.py, and src/tests/test_dehumidifiers.py per FR-007 [gap: partial]
- [X] T035 Extend the dehumidifier state/model contract and fixture-backed assertions in src/pyvesync/models/dehumidifier_models.py, src/pyvesync/base_devices/dehumidifier_base.py, src/pyvesync/devices/vesyncdehumidifier.py, src/tests/call_json_dehumidifiers.py, and src/tests/test_dehumidifiers.py to preserve the verified live status fields from specs/001-dehumidifier-support/research.md such as `errorCodes`, pump/drainage state, and distinct operating-state indicators per FR-003 [gap: partial]
