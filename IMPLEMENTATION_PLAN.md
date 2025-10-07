# 2-Week Implementation Plan
## Progressive Overload Tracker

**Project Status:** 50% Complete (6/12 steps done, 5 new steps added for API fixes)
**Start Date:** 2025-09-30
**Target Completion:** 2025-10-14

---

## Week 1: Core API Implementation (Days 1-7)

### Day 1: Service Layer Foundation ✅ COMPLETED
**Goal:** Implement business logic layer for core entities

**Tasks:**
1. ✅ Create `src/services/exercise_service.py` with CRUD operations
2. ✅ Create `src/services/session_service.py` with CRUD operations
3. ✅ Create `src/services/template_service.py` with CRUD operations
4. ✅ Create `src/services/set_service.py` with CRUD operations
5. ✅ Create `src/services/exercise_session_service.py` with CRUD operations
6. ✅ Create `src/services/user_service.py` with CRUD operations
7. ✅ Update `src/services/__init__.py` to export all services
8. ✅ Fix schema circular import issues (5 schemas)

**Commits (12 total):**
- ✅ `feat: add exercise service with CRUD operations`
- ✅ `feat: add session service with CRUD operations`
- ✅ `feat: add template service with CRUD operations`
- ✅ `feat: add set service with CRUD operations`
- ✅ `feat: add exercise_session service with CRUD operations`
- ✅ `feat: add user service with CRUD operations`
- ✅ `feat: update services module exports`
- ✅ `fix: resolve template schema circular imports`
- ✅ `fix: resolve exercise_session schema circular imports`
- ✅ `fix: resolve session schema circular imports`
- ✅ `fix: resolve set schema circular imports`
- ✅ `fix: resolve user schema circular imports`

**Verification:** ✅ All integrity tests passed
**Branch:** `feature/service-layer` (pushed to remote)
**PR:** Ready for review

---

### Day 2: FastAPI Routers - Part 1 (Exercises & Users) ✅ COMPLETED
**Goal:** Create API endpoints for exercises and users

**Tasks:**
1. ✅ Create `src/routers/exercises.py` with all endpoints:
   - GET /exercises (list with search)
   - GET /exercises/{id}
   - POST /exercises
   - PUT /exercises/{id}
   - DELETE /exercises/{id}
2. ✅ Create `src/routers/users.py` with all endpoints:
   - GET /users
   - GET /users/{id}
   - POST /users
   - PUT /users/{id}
   - DELETE /users/{id}
3. ✅ Update `src/main.py` to include routers
4. ✅ Add proper error handling and HTTP status codes

**Commits (2 total):**
- ✅ `feat: add exercises router with CRUD endpoints`
- ✅ `feat: add users router with CRUD endpoints`

**Verification:** ✅ Completed
**Branch:** `feature/api-routers` (merged to main)
**PR:** Merged (#17)

---

### Day 3: FastAPI Routers - Part 2 (Sessions & Templates) ✅ COMPLETED
**Goal:** Complete API endpoints for sessions and templates

**Tasks:**
1. ✅ Create `src/routers/sessions.py` with endpoints:
   - GET /sessions
   - GET /sessions/{id}
   - POST /sessions (with exercises and sets)
   - PUT /sessions/{id}
   - DELETE /sessions/{id}
2. ✅ Create `src/routers/templates.py` with endpoints:
   - GET /templates
   - GET /templates/{id}
   - POST /templates (with exercises)
   - PUT /templates/{id}
   - DELETE /templates/{id}
3. ✅ Update `src/main.py` to include new routers
4. ✅ Fix schema forward references
5. ✅ Test all endpoints manually

**Commits (3 total):**
- ✅ `fix: resolve forward references in SessionWithDetails and TemplateWithExerciseSessions schemas`
- ✅ `feat: add sessions router with nested exercise operations`
- ✅ `feat: add templates router with CRUD endpoints`

**Verification:** ✅ Completed - all endpoints tested successfully
**Branch:** `feature/sessions-templates-routers` (ready for PR)
**Additional branch:** `fix/session-schema-forward-refs` (merged into feature branch)

---

### Day 4: Testing Infrastructure Setup ✅ COMPLETED
**Goal:** Establish testing framework and fixtures

**Tasks:**
1. ✅ Create `pytest.ini` configuration
2. ✅ Create `tests/conftest.py` with:
   - Test database fixture (SQLite in-memory)
   - FastAPI TestClient fixture
   - Database session fixture
   - Sample data fixtures
3. ✅ Create `tests/__init__.py`
4. ✅ Create helper utilities in `tests/utils.py`

**Commits (2 total):**
- ✅ `test: add pytest configuration and test infrastructure`
- ✅ `test: add conftest with database and client fixtures`

**Verification:** ✅ Run `pytest --collect-only` - verified test discovery (0 tests collected as expected)
**Branch:** `feature/testing-infrastructure` (pushed to remote)
**PR:** Ready for review

---

### Day 5: Unit Tests for Services ✅ COMPLETED
**Goal:** Write comprehensive service layer tests

**Tasks:**
1. ✅ Fix Template model - add user_id relationship
2. ✅ Create database migration for template user_id
3. ✅ Create `tests/test_services/` directory
4. ✅ Create `tests/test_services/test_exercise_service.py` (21 tests):
   - CRUD operations
   - Search by name, category, equipment
   - Pagination and edge cases
5. ✅ Create `tests/test_services/test_user_service.py` (22 tests):
   - CRUD operations
   - Username uniqueness validation
   - Cascade deletion tests
6. ✅ Create `tests/test_services/test_session_service.py` (18 tests):
   - CRUD operations with nested data
   - Multiple exercises per session
   - Cascade deletion verification
7. ✅ Create `tests/test_services/test_template_service.py` (19 tests):
   - CRUD operations with user relationship
   - Template creation with exercises
   - Cascade deletion tests
8. ✅ Create `tests/test_services/test_set_service.py` (17 tests):
   - CRUD operations
   - Different unit types (kg, stacks)
   - Multiple field updates
9. ✅ Create `tests/test_services/test_exercise_session_service.py` (18 tests):
   - CRUD operations
   - Sessions and templates association
   - Nested data loading

**Commits (8 total):**
- ✅ `fix: add user_id foreign key to Template model with migration`
- ✅ `test: add comprehensive unit tests for exercise service (21 tests)`
- ✅ `test: add comprehensive unit tests for user service (22 tests)`
- ✅ `test: add comprehensive unit tests for session service (18 tests)`
- ✅ `test: add comprehensive unit tests for template service (19 tests)`
- ✅ `test: add comprehensive unit tests for set service (17 tests)`
- ✅ `test: add comprehensive unit tests for exercise_session service (18 tests)`

**Coverage:** 100% on all services (118 tests total, 266/266 statements)
**Verification:** ✅ All tests passing
**Branches (7 total):**
- `fix/add-template-user-relationship` (pushed to remote)
- `test/exercise-service` (pushed to remote)
- `test/user-service` (pushed to remote)
- `test/session-service` (pushed to remote)
- `test/template-service` (pushed to remote)
- `test/set-service` (pushed to remote)
- `test/exercise-session-service` (pushed to remote)
**PRs:** 7 PRs ready for review

---

### Day 6: Integration Tests for API Endpoints
**Goal:** Write end-to-end API tests

**Tasks:**
1. Create `tests/test_api/` directory
2. Create `tests/test_api/test_exercises.py`:
   - Test all CRUD endpoints
   - Test error cases (404, 422)
   - Test pagination and search
3. Create `tests/test_api/test_sessions.py`
4. Create `tests/test_api/test_templates.py`
5. Create `tests/test_api/test_users.py`
6. Test nested resource creation (session with exercises and sets)

**Commits:**
- `test: add integration tests for exercises API`
- `test: add integration tests for sessions API`
- `test: add integration tests for templates and users API`

**Verification:** Run `pytest tests/test_api/ -v`

---

### Day 6A: Fix Response Schema Serialization (Schema Bug Fix)
**Goal:** Fix API responses to include nested relationship data

**Problem Identified:**
Current API responses return incomplete data structures. When creating sessions/templates with nested exercises, the response includes the relationship IDs but not the full nested objects.

**Example of Current Broken Behavior:**
```json
POST /sessions/
Request: {
  "user_id": 1,
  "exercise_sessions": [{
    "exercise_id": 5,
    "sets": [{"weight": 100, "reps": 10, "unit": "kg"}]
  }]
}

Response: {
  "id": 1,
  "exercise_sessions": [{
    "id": 1,
    "exercise_id": 5,  // ❌ Only ID, missing full exercise object
    "session_id": 1
    // ❌ Missing "exercise": {...}
    // ❌ Missing "sets": [...]
  }]
}
```

**Root Cause:**
- Service layer correctly loads data using `joinedload()` ✅
- Database has all data ✅
- Pydantic response schema doesn't serialize nested relationships ❌

**Technical Issue:**
`SessionWithDetails` schema uses `ExerciseSessionResponse` (basic) instead of `ExerciseSessionWithDetails` (full).

```python
# src/schemas/session.py - Current (BROKEN)
class SessionWithDetails(SessionResponse):
    exercise_sessions: List["ExerciseSessionResponse"] = ...  # ❌ Missing nested data

# Should be:
class SessionWithDetails(SessionResponse):
    exercise_sessions: List["ExerciseSessionWithDetails"] = ...  # ✅ Includes exercise & sets
```

**Tasks:**
1. Update `SessionWithDetails` schema to use `ExerciseSessionWithDetails`
2. Update `TemplateWithExerciseSessions` schema to use `ExerciseSessionWithDetails`
3. Verify schemas have `model_config = ConfigDict(from_attributes=True)`
4. Test that responses now include nested `exercise` objects
5. Test that responses now include nested `sets` arrays
6. Unskip and run previously failing integration tests

**Affected Files:**
- `src/schemas/session.py`
- `src/schemas/template.py`
- `tests/test_api/test_sessions.py` (unskip 2 tests)
- `tests/test_api/test_templates.py` (unskip 2 tests)

**Commits:**
- `fix: update SessionWithDetails to include nested exercise and set details`
- `fix: update TemplateWithExerciseSessions to include nested exercise details`
- `test: unskip integration tests for nested resource responses`

**Verification:**
- Run `pytest tests/test_api/ -v`
- All previously skipped "Nested exercise details" tests should now pass

**Architectural Decision Required:** ❓
**Question:** Should we ALWAYS return full nested data, or add a query parameter like `?include=exercises,sets`?
- **Option A:** Always return full data (simpler, but larger responses)
- **Option B:** Query parameter to opt-in to nested data (more complex, but efficient)
- **Recommendation:** Start with Option A (always include), optimize later if needed

**Impact:** Medium - Changes response structure, frontend may need updates

---

### Day 6B: Add Foreign Key Validation (Service Layer Enhancement)
**Goal:** Validate foreign key references before database insertion

**Problem Identified:**
Services don't validate that referenced entities exist, leading to confusing errors.

**Example of Current Broken Behavior:**
```python
POST /sessions/ {"user_id": 99999, "exercise_sessions": []}
Response: 201 Created  # ❌ Should be 404 Not Found

# User 99999 doesn't exist, but API accepts it
# Later operations may fail or create orphaned records
```

**Root Cause:**
Services rely solely on database FK constraints, which throw generic IntegrityError instead of clear 404 responses.

**Tasks:**
1. Update `session_service.create_session()` to validate `user_id` exists
2. Update `session_service.create_session()` to validate each `exercise_id` exists
3. Update `template_service.create_template()` to validate `user_id` exists
4. Update `template_service.create_template()` to validate each `exercise_id` exists
5. Add helper function `validate_foreign_keys()` to reduce duplication
6. Unskip and run FK validation tests

**Implementation Pattern:**
```python
def create_session(session_data: SessionCreate, db: DbSession):
    # Validate user exists
    user = db.get(User, session_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {session_data.user_id} not found"
        )

    # Validate each exercise exists
    for es in session_data.exercise_sessions:
        exercise = db.get(Exercise, es.exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exercise with id {es.exercise_id} not found"
            )

    # Continue with creation...
```

**Affected Files:**
- `src/services/session_service.py`
- `src/services/template_service.py`
- `tests/test_api/test_sessions.py` (unskip 2 tests)
- `tests/test_api/test_templates.py` (unskip 2 tests)

**Commits:**
- `feat: add foreign key validation in session service`
- `feat: add foreign key validation in template service`
- `test: unskip FK validation integration tests`

**Verification:** Run `pytest tests/test_api/ -v`

**Architectural Decision Required:** ❓
**Question:** Should we validate FKs in service layer or catch IntegrityError from database?
- **Option A (Recommended):** Service layer validation - Clear errors, better UX
- **Option B:** Catch IntegrityError - Less code, but generic error messages
- **Recommendation:** Option A - User experience is worth the extra code

**Impact:** Low - Only changes error responses, no breaking changes

---

### Day 6C: Add Query Parameter Filtering (Router & Service Enhancement)
**Goal:** Enable filtering resources by category, equipment, user, etc.

**Problem Identified:**
Endpoints ignore filter query parameters, forcing clients to fetch all data and filter client-side.

**Example of Current Broken Behavior:**
```python
GET /exercises/?category=chest&equipment=barbell
# Returns ALL exercises, ignores query params ❌

GET /sessions/?user_id=5
# Returns ALL sessions, ignores user_id ❌
```

**Tasks:**

**Part 1: Exercise Filtering**
1. Update `exercise_service.get_exercises()` to accept `category`, `equipment` params
2. Update `exercises` router to pass query params to service
3. Add WHERE clauses to filter query
4. Update API documentation with filter parameters

**Part 2: Session Filtering**
1. Update `session_service.get_sessions()` to accept `user_id` param
2. Update `sessions` router to pass `user_id` to service
3. Add WHERE clause for user filtering

**Part 3: Template Filtering**
1. Update `template_service.get_templates()` to accept `user_id`, `name` params
2. Update `templates` router to pass query params to service
3. Add WHERE clauses for filtering

**Implementation Pattern:**
```python
# Service layer
def get_exercises(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
    category: Optional[CategoryEnum] = None,  # ← New
    equipment: Optional[EquipmentEnum] = None  # ← New
):
    query = select(Exercise)

    if category:
        query = query.where(Exercise.category == category)
    if equipment:
        query = query.where(Exercise.equipment == equipment)

    result = db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

# Router layer
@router.get("/", response_model=List[ExerciseResponse])
def list_exercises(
    category: Optional[CategoryEnum] = Query(None),  # ← New
    equipment: Optional[EquipmentEnum] = Query(None),  # ← New
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    return exercise_service.get_exercises(
        db, skip, limit, category, equipment  # ← Pass params
    )
```

**Affected Files:**
- `src/services/exercise_service.py`
- `src/services/session_service.py`
- `src/services/template_service.py`
- `src/routers/exercises.py`
- `src/routers/sessions.py`
- `src/routers/templates.py`
- `tests/test_api/*.py` (unskip 5 tests)

**Commits:**
- `feat: add category and equipment filtering to exercises endpoint`
- `feat: add user_id filtering to sessions endpoint`
- `feat: add user_id and name filtering to templates endpoint`
- `test: unskip query parameter filtering integration tests`

**Verification:** Run `pytest tests/test_api/ -v`

**Architectural Decision Required:** ❓
**Question:** Should we use query parameters or a more sophisticated filtering approach?
- **Option A (Recommended):** Simple query params - `?category=chest&equipment=barbell`
- **Option B:** JSON filter object - `?filter={"category":"chest","equipment":"barbell"}`
- **Option C:** GraphQL-style filtering with operators - `?filter[category][eq]=chest`
- **Recommendation:** Option A - Simple, RESTful, easy to document

**Impact:** Medium - Changes service signatures, backward compatible (new params are optional)

---

### Day 6D: Add Template Update with Exercises (Service Enhancement)
**Goal:** Enable updating template's exercises via PUT endpoint

**Problem Identified:**
Template update only handles name/user_id changes, can't modify exercise list.

**Example of Current Broken Behavior:**
```python
PUT /templates/1
{
  "user_id": 1,
  "name": "Updated Template",
  "exercise_sessions": [{"exercise_id": 5}]  # ❌ Ignored
}

# Only name updates, exercise_sessions ignored
```

**Tasks:**
1. Update `template_service.update_template()` to handle nested `exercise_sessions`
2. Clear existing exercise_sessions relationships
3. Add new exercise_sessions from request
4. Handle partial updates (only update if exercise_sessions provided)
5. Unskip test

**Implementation Pattern:**
```python
def update_template(template_id: int, template_data: TemplateUpdate, db: DbSession):
    db_template = db.get(Template, template_id)
    if not db_template:
        raise HTTPException(404, f"Template {template_id} not found")

    update_data = template_data.model_dump(exclude_unset=True)

    # Handle exercise_sessions update if provided
    if 'exercise_sessions' in update_data:
        # Clear existing
        db_template.exercise_sessions = []

        # Add new ones
        for es_data in update_data.pop('exercise_sessions'):
            db_es = ExerciseSession(**es_data)
            db_template.exercise_sessions.append(db_es)

    # Update other fields
    for field, value in update_data.items():
        setattr(db_template, field, value)

    db.commit()
    db.refresh(db_template)
    return get_template(template_id, db)
```

**Affected Files:**
- `src/services/template_service.py`
- `src/schemas/template.py` (add exercise_sessions to TemplateUpdate)
- `tests/test_api/test_templates.py` (unskip 1 test)

**Commits:**
- `feat: add exercise_sessions update support to template service`
- `test: unskip template update with exercises test`

**Verification:** Run `pytest tests/test_api/ -v`

**Architectural Decision Required:** ❓
**Question:** How should we handle exercise_sessions updates?
- **Option A:** Replace all exercise_sessions (current implementation)
- **Option B:** Merge with existing (add new, keep existing)
- **Option C:** Separate endpoints - `POST /templates/{id}/exercises` to add
- **Recommendation:** Option A (replace) - Simpler, more predictable. Can add Option C later for convenience.

**Impact:** Low - Enhances existing endpoint, backward compatible

---

### Day 6E: Add UserWithSessions Response (Schema Enhancement)
**Goal:** Optionally return user's sessions when fetching user details

**Problem Identified:**
User endpoint always returns basic info, requires separate call to get sessions.

**Current Behavior:**
```python
GET /users/1
Response: {"id": 1, "username": "foo", "name": null}
# To get sessions: separate call to GET /sessions/?user_id=1
```

**Tasks:**
1. Add optional `include_sessions` query parameter to user endpoint
2. Return `UserWithSessions` schema when parameter is true
3. Return `UserResponse` schema when parameter is false (default)
4. Update service to conditionally load sessions
5. Unskip test

**Implementation Pattern:**
```python
# Router
@router.get("/{user_id}")
def get_user(
    user_id: int,
    include_sessions: bool = Query(False, description="Include user's sessions"),
    db: Session = Depends(get_db),
):
    if include_sessions:
        return user_service.get_user_with_sessions(user_id, db)
    return user_service.get_user(user_id, db)

# Service - add new function
def get_user_with_sessions(user_id: int, db: DbSession) -> User:
    result = db.execute(
        select(User)
        .options(joinedload(User.sessions))  # ← Load sessions
        .where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(404, f"User {user_id} not found")
    return user
```

**Affected Files:**
- `src/services/user_service.py`
- `src/routers/users.py`
- `tests/test_api/test_users.py` (unskip 1 test, add `?include_sessions=true`)

**Commits:**
- `feat: add optional include_sessions parameter to user endpoint`
- `test: unskip and update user with sessions test`

**Verification:** Run `pytest tests/test_api/ -v`

**Architectural Decision Required:** ❓
**Question:** How should we handle optional nested data?
- **Option A (Recommended):** Query parameter `?include_sessions=true`
- **Option B:** Separate endpoint `GET /users/{id}/sessions`
- **Option C:** Always include sessions (simple but inefficient)
- **Recommendation:** Option A - Flexible, one endpoint, opt-in for performance

**Impact:** Low - Adds optional parameter, fully backward compatible

---

### Day 7: Code Quality & Week 1 Review
**Goal:** Ensure code quality and fix any issues

**Tasks:**
1. Run and fix all linting issues: `flake8 .`
2. Format all code: `black . && isort .`
3. Run type checking: `mypy src/`
4. Fix any type errors
5. Run full test suite: `pytest -v --cov=src`
6. Review test coverage report
7. Fix any failing tests
8. Document any known issues

**Commits:**
- `chore: format code with black and isort`
- `fix: resolve type checking errors`
- `test: improve test coverage for edge cases`

**Verification:** All tests pass, coverage >80%, no type errors

---

## Week 2: DevOps, Tools & Polish (Days 8-14)

### Day 8: Docker Configuration
**Goal:** Complete containerization setup

**Tasks:**
1. Create `Dockerfile` for FastAPI application:
   - Multi-stage build
   - Python 3.11+ base image
   - Install dependencies
   - Copy application code
   - Set up healthcheck
2. Update `docker-compose.yml`:
   - Add API service
   - Configure environment variables
   - Set up volumes for development
   - Add health checks
   - Configure networking
3. Create `.dockerignore`
4. Create `docker-compose.prod.yml` for production
5. Test full stack with Docker

**Commits:**
- `docker: add Dockerfile for FastAPI application`
- `docker: update docker-compose with API service`
- `docker: add production docker-compose configuration`

**Verification:** Run `docker-compose up`, test API at http://localhost:8000

---

### Day 9: Development Tools - Makefile & Scripts
**Goal:** Automate common development tasks

**Tasks:**
1. Create `Makefile` with targets:
   - `make install` - Install dependencies
   - `make dev` - Start development server
   - `make test` - Run tests
   - `make test-cov` - Run tests with coverage
   - `make lint` - Run linting
   - `make format` - Format code
   - `make type-check` - Run mypy
   - `make migrate` - Run database migrations
   - `make migrate-create` - Create new migration
   - `make docker-up` - Start Docker services
   - `make docker-down` - Stop Docker services
   - `make clean` - Clean up generated files
2. Create `setup.sh` for initial environment setup
3. Test all make targets

**Commits:**
- `chore: add Makefile with development commands`
- `chore: add setup script for environment initialization`

**Verification:** Test each make command

---

### Day 10: Pre-commit Hooks & CI/CD Prep
**Goal:** Automate code quality checks

**Tasks:**
1. Create `.pre-commit-config.yaml`:
   - black formatter
   - isort import sorting
   - flake8 linting
   - mypy type checking
   - trailing whitespace removal
   - yaml/json validation
2. Install pre-commit hooks: `pre-commit install`
3. Test hooks: `pre-commit run --all-files`
4. Create `.github/workflows/ci.yml` (GitHub Actions):
   - Run tests on push
   - Check code formatting
   - Type checking
   - Generate coverage report
5. Create `.github/workflows/docker.yml` (Docker build test)

**Commits:**
- `chore: add pre-commit hooks configuration`
- `ci: add GitHub Actions workflow for tests and linting`
- `ci: add Docker build workflow`

**Verification:** Make a test commit, ensure hooks run

---

### Day 11: API Documentation & Enhancements
**Goal:** Improve API documentation and add features

**Tasks:**
1. Update `src/main.py`:
   - Add comprehensive API metadata
   - Add tags for route grouping
   - Configure CORS if needed
   - Add API versioning (optional)
2. Add detailed docstrings to all router functions
3. Add request/response examples in Pydantic schemas
4. Test and refine Swagger UI documentation
5. Add any missing API endpoints (e.g., statistics, analytics)
6. Consider pagination helpers if not done

**Commits:**
- `docs: enhance API documentation in routers`
- `feat: add comprehensive API metadata and tags`
- `feat: add pagination and filtering helpers`

**Verification:** Review Swagger UI at /docs for completeness

---

### Day 12: Project Documentation
**Goal:** Complete all documentation

**Tasks:**
1. Update `README.md`:
   - Project overview
   - Features list
   - Technology stack
   - Quick start guide
   - Installation instructions
   - Usage examples
   - API documentation link
   - Contributing guidelines link
   - License
2. Create `CONTRIBUTING.md`:
   - How to set up development environment
   - Code style guidelines
   - Testing requirements
   - Pull request process
3. Create `docs/` directory with:
   - `docs/API.md` - Detailed API documentation
   - `docs/DATABASE.md` - Database schema documentation
   - `docs/DEVELOPMENT.md` - Development workflow
   - `docs/DEPLOYMENT.md` - Deployment guide
4. Add architecture diagrams (optional but recommended)

**Commits:**
- `docs: update README with comprehensive project information`
- `docs: add CONTRIBUTING guide`
- `docs: add detailed documentation in docs/ directory`

**Verification:** Review all docs for clarity and completeness

---

### Day 13: Performance & Security Review
**Goal:** Optimize and secure the application

**Tasks:**
1. Add database connection pooling configuration
2. Add query optimization (eager loading where needed)
3. Add request/response compression
4. Add rate limiting (optional)
5. Review and fix any security issues:
   - SQL injection prevention (should be handled by SQLAlchemy)
   - Input validation
   - Error message sanitization
   - Environment variable security
6. Add logging configuration
7. Add health check endpoint
8. Performance testing with load tests (optional)

**Commits:**
- `perf: optimize database queries with eager loading`
- `feat: add logging configuration`
- `feat: add health check endpoint`
- `security: enhance input validation and error handling`

**Verification:** Test endpoints, check logs, verify security

---

### Day 14: Final Testing & Release Prep
**Goal:** Final validation and prepare for release

**Tasks:**
1. Run complete test suite: `pytest -v --cov=src --cov-report=html`
2. Review coverage report, add tests for uncovered code
3. Run all code quality tools:
   - `black --check .`
   - `isort --check .`
   - `flake8 .`
   - `mypy src/`
4. Test full Docker stack end-to-end
5. Create sample data seed script (optional)
6. Test database migrations on fresh database
7. Create release notes/changelog
8. Tag version 1.0.0
9. Update all documentation with final changes
10. Celebrate! 🎉

**Commits:**
- `test: achieve >85% test coverage`
- `chore: add database seed script for sample data`
- `docs: update changelog for v1.0.0`
- `chore: prepare for v1.0.0 release`

**Verification:** Full end-to-end manual testing

---

## Quick Task & Commit Checklist

### Week 1: Core API (Days 1-7)
- [x] Day 1: Service Layer (3 commits)
  - [x] `feat: add exercise service with CRUD operations`
  - [x] `feat: add session service with CRUD operations`
  - [x] `feat: add template, set, exercise_session, and user services`

- [x] Day 2: Exercises & Users Routers (2 commits)
  - [x] `feat: add exercises router with CRUD endpoints`
  - [x] `feat: add users router with CRUD endpoints`

- [x] Day 3: Sessions & Templates Routers (3 commits)
  - [x] `fix: resolve forward references in SessionWithDetails and TemplateWithExerciseSessions schemas`
  - [x] `feat: add sessions router with nested exercise operations`
  - [x] `feat: add templates router with CRUD endpoints`

- [x] Day 4: Testing Infrastructure (2 commits)
  - [x] `test: add pytest configuration and test infrastructure`
  - [x] `test: add conftest with database and client fixtures`

- [x] Day 5: Service Unit Tests (8 commits - separated by service)
  - [x] `fix: add user_id foreign key to Template model with migration`
  - [x] `test: add comprehensive unit tests for exercise service (21 tests)`
  - [x] `test: add comprehensive unit tests for user service (22 tests)`
  - [x] `test: add comprehensive unit tests for session service (18 tests)`
  - [x] `test: add comprehensive unit tests for template service (19 tests)`
  - [x] `test: add comprehensive unit tests for set service (17 tests)`
  - [x] `test: add comprehensive unit tests for exercise_session service (18 tests)`

- [ ] Day 6: API Integration Tests (3 commits)
  - [ ] `test: add integration tests for exercises API`
  - [ ] `test: add integration tests for sessions API`
  - [ ] `test: add integration tests for templates and users API`

- [ ] Day 7: Code Quality (3 commits)
  - [ ] `chore: format code with black and isort`
  - [ ] `fix: resolve type checking errors`
  - [ ] `test: improve test coverage for edge cases`

### Week 2: DevOps & Polish (Days 8-14)
- [ ] Day 8: Docker (3 commits)
  - [ ] `docker: add Dockerfile for FastAPI application`
  - [ ] `docker: update docker-compose with API service`
  - [ ] `docker: add production docker-compose configuration`

- [ ] Day 9: Development Tools (2 commits)
  - [ ] `chore: add Makefile with development commands`
  - [ ] `chore: add setup script for environment initialization`

- [ ] Day 10: CI/CD (3 commits)
  - [ ] `chore: add pre-commit hooks configuration`
  - [ ] `ci: add GitHub Actions workflow for tests and linting`
  - [ ] `ci: add Docker build workflow`

- [ ] Day 11: API Enhancements (3 commits)
  - [ ] `docs: enhance API documentation in routers`
  - [ ] `feat: add comprehensive API metadata and tags`
  - [ ] `feat: add pagination and filtering helpers`

- [ ] Day 12: Documentation (3 commits)
  - [ ] `docs: update README with comprehensive project information`
  - [ ] `docs: add CONTRIBUTING guide`
  - [ ] `docs: add detailed documentation in docs/ directory`

- [ ] Day 13: Performance & Security (4 commits)
  - [ ] `perf: optimize database queries with eager loading`
  - [ ] `feat: add logging configuration`
  - [ ] `feat: add health check endpoint`
  - [ ] `security: enhance input validation and error handling`

- [ ] Day 14: Release Prep (4 commits)
  - [ ] `test: achieve >85% test coverage`
  - [ ] `chore: add database seed script for sample data`
  - [ ] `docs: update changelog for v1.0.0`
  - [ ] `chore: prepare for v1.0.0 release`

---

## Total Commits: 39

## Success Metrics
- ✅ All 12 guide steps completed
- ✅ >85% test coverage
- ✅ Zero type checking errors
- ✅ Zero linting errors
- ✅ All tests passing
- ✅ Docker stack running successfully
- ✅ Complete API documentation
- ✅ Comprehensive project documentation
- ✅ Pre-commit hooks configured
- ✅ CI/CD pipeline working
- ✅ Ready for production deployment

---

## Notes
- Adjust timeline based on complexity encountered
- Can combine related commits if working faster
- Can split larger tasks across multiple days if needed
- Prioritize functionality over perfection
- Test continuously throughout development
- Keep commits atomic and well-described
