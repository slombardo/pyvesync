# Tasks: VeSync Dehumidifier Support

**Input**: Design documents from `/specs/001-dehumidifier-support/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the existing humidifier architecture and fixture pattern before implementation.

- [ ] T001 [P] Review the current humidifier architecture and device mapping pattern in src/pyvesync/base_devices/humidifier_base.py, src/pyvesync/device_map.py, and src/pyvesync/devices/vesynchumidifier.py
- [ ] T002 [P] Review the existing fixture and test strategy in src/tests/test_humidifiers.py and src/tests/call_json_humidifiers.py to mirror the dehumidifier validation approach

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Set up the dehumidifier model metadata, shared state contract, and baseline fixtures before story work begins.

- [ ] T003 Add dehumidifier model IDs and feature capability metadata to src/pyvesync/device_map.py
- [ ] T004 Extend shared humidifier state and constants in src/pyvesync/const.py and src/pyvesync/base_devices/humidifier_base.py for dehumidifier-specific fields and validation ranges
- [ ] T005 Create baseline API fixture payloads under src/tests/api/vesynchumidifier/ for representative dehumidifier responses
- [ ] T006 [P] Define the dehumidifier command contract and call mapping in src/pyvesync/devices/vesynchumidifier.py using the established humidifier conventions

**Checkpoint**: Foundation ready - dehumidifier discovery and device state contract can now be implemented in parallel across user stories.

---

## Phase 3: User Story 1 - Discover and manage a supported dehumidifier (Priority: P1) 🎯 MVP

**Goal**: Ensure a supported VeSync dehumidifier is recognized and exposed through the library's standard device discovery flow.

**Independent Test**: A valid user account with a dehumidifier can log in, enumerate devices, and retrieve the device state without ad hoc handling or custom API workarounds.

### Tests for User Story 1

- [ ] T007 [P] [US1] Add a dehumidifier discovery regression test in src/tests/test_humidifiers.py covering model recognition and state parsing
- [ ] T008 [P] [US1] Add a representative dehumidifier status fixture under src/tests/api/vesynchumidifier/ for the discovery/state test path

### Implementation for User Story 1

- [ ] T009 [US1] Implement dehumidifier registration and model mapping in src/pyvesync/device_map.py so devices resolve to the correct class and feature set
- [ ] T010 [US1] Update instantiation and parsing behavior in src/pyvesync/devices/vesynchumidifier.py for the dehumidifier model family
- [ ] T011 [US1] Extend the shared state parsing in src/pyvesync/base_devices/humidifier_base.py to read dehumidifier power, humidity, target, and operating metrics from the real API payload

**Checkpoint**: User Story 1 is fully functional and independently testable as a dehumidifier discovery and state-read path.

---

## Phase 4: User Story 2 - Control the dehumidifier's core operating functions (Priority: P1)

**Goal**: Allow users to operate the dehumidifier using the standard library methods for power, mode, and target humidity controls.

**Independent Test**: A user can issue the primary power and operation commands for a dehumidifier and observe the device state update without custom per-model logic.

### Tests for User Story 2

- [ ] T012 [P] [US2] Add command regression tests for power, mode, and humidity control in src/tests/test_humidifiers.py
- [ ] T013 [P] [US2] Add fixture payloads for dehumidifier command responses in src/tests/api/vesynchumidifier/ so command validation is repeatable and reviewable

### Implementation for User Story 2

- [ ] T014 [US2] Implement standard power and mode-control handlers in src/pyvesync/devices/vesynchumidifier.py
- [ ] T015 [US2] Update humidity target and mode state mapping in src/pyvesync/base_devices/humidifier_base.py to reflect the commanded values and API returned payloads
- [ ] T016 [US2] Add/adjust dehumidifier-specific command validation in src/pyvesync/const.py and related state helpers so invalid values fail through the project's existing error patterns

**Checkpoint**: User Story 2 is independently functional and validates the main operational use case.

---

## Phase 5: User Story 3 - Access advanced dehumidifier controls and monitoring (Priority: P2)

**Goal**: Expose advanced supported settings and monitoring fields in the same way the library exposes similar humidifier capabilities.

**Independent Test**: A dehumidifier exposing advanced controls exposes only the supported options, and each valid setting updates state consistently through the standard library API contract.

### Tests for User Story 3

- [ ] T017 [P] [US3] Add advanced-control regression tests for fan speed, child lock, timer, or other supported features in src/tests/test_humidifiers.py
- [ ] T018 [P] [US3] Add advanced control fixture payloads under src/tests/api/vesynchumidifier/ for the supported settings path

### Implementation for User Story 3

- [ ] T019 [US3] Implement feature-gated advanced control methods in src/pyvesync/devices/vesynchumidifier.py and keep unsupported operations hidden behind the dehumidifier feature map
- [ ] T020 [US3] Extend the dehumidifier state model in src/pyvesync/base_devices/humidifier_base.py and src/pyvesync/const.py to include advanced monitoring and settings fields with the repository's existing typed conventions
- [ ] T021 [US3] Review and update README.md and docs/ if the user-visible API includes new public methods, examples, or supported-device listing changes

**Checkpoint**: All dehumidifier support work is independently functional and aligned with the project's public contract and docs rules.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation of the feature against the repo's quality gates and project constitution.

- [ ] T022 [P] Run the targeted humidifier test suite and fixture validation from src/tests/test_humidifiers.py to confirm dehumidifier support remains stable
- [ ] T023 [P] Execute the repo linting and type-check workflow from the existing project tools (ruff, pylint, mypy) against the affected device code
- [ ] T024 Validate the completion criteria from specs/001-dehumidifier-support/quickstart.md and confirm the feature meets the documented success criteria
- [ ] T025 Update any user-facing documentation impacted by the new dehumidifier support, including supported device references and examples where appropriate

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
