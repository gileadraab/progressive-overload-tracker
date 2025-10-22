# Database Schema

Documentation for the Progressive Overload Tracker database structure.

## Database Technology

- **Primary**: PostgreSQL 13+
- **Development Fallback**: SQLite
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic

## Entity Relationship Diagram

```
User ─────────┐
              │
              ├──> Session ────┐
              │                │
              └──> Template ───┼──> ExerciseSession ──> Set
                               │           │
Exercise ─────────────────────┘           │
                                           │
                                    (references Exercise)
```

---

## Tables

### User

Stores user account information and authentication credentials.

| Column         | Type         | Constraints                    | Description                           |
|----------------|--------------|--------------------------------|---------------------------------------|
| id             | Integer      | PRIMARY KEY, AUTO INCREMENT    | Unique identifier                     |
| username       | String(50)   | UNIQUE, NOT NULL, INDEX        | Login username                        |
| email          | String(255)  | UNIQUE, NOT NULL, INDEX        | User email for authentication         |
| name           | String(100)  | NULLABLE                       | Display name                          |
| password_hash  | String(255)  | NULLABLE                       | Bcrypt hashed password                |
| oauth_provider | String(50)   | NULLABLE                       | OAuth provider (google, facebook, etc)|
| oauth_id       | String(255)  | NULLABLE                       | OAuth provider user ID                |

**Relationships:**
- `sessions`: One-to-Many → Session (cascade delete)
- `templates`: One-to-Many → Template (cascade delete)

**Indexes:**
- `ix_users_username` on `username`
- `ix_users_email` on `email`

**Authentication:**
- Email/password users have `password_hash` set and `oauth_provider` NULL
- OAuth users have `oauth_provider` and `oauth_id` set, `password_hash` may be NULL
- Passwords are hashed using bcrypt before storage
- JWT tokens are used for session management

---

### Exercise

Stores exercise definitions (shared across all users).

| Column      | Type         | Constraints                    | Description                |
|-------------|--------------|--------------------------------|----------------------------|
| id          | Integer      | PRIMARY KEY, AUTO INCREMENT    | Unique identifier          |
| name        | String(100)  | NOT NULL                       | Exercise name              |
| category    | Enum         | NOT NULL                       | Muscle group category      |
| subcategory | String(100)  | NULLABLE                       | Specific muscle area       |
| equipment   | Enum         | NULLABLE                       | Equipment type             |
| image_url   | String       | NULLABLE                       | URL to exercise image/demo |

**Enums:**
- `category`: `chest`, `back`, `legs`, `shoulders`, `arms`, `core`
- `equipment`: `machine`, `dumbbell`, `barbell`, `bodyweight`, `kettlebell`, `resistance_band`

**Relationships:**
- `exercise_sessions`: One-to-Many → ExerciseSession

---

### Session

Stores workout session data.

| Column  | Type     | Constraints                 | Description              |
|---------|----------|-----------------------------|--------------------------|
| id      | Integer  | PRIMARY KEY, AUTO INCREMENT | Unique identifier        |
| user_id | Integer  | FOREIGN KEY → User, NOT NULL| Owner of this session    |
| date    | DateTime | NOT NULL, DEFAULT NOW       | When workout occurred    |
| notes   | Text     | NULLABLE                    | Workout notes/comments   |

**Relationships:**
- `user`: Many-to-One → User
- `exercise_sessions`: One-to-Many → ExerciseSession (cascade delete)

**Indexes:**
- `ix_sessions_user_id` on `user_id`

**Cascading:**
- Deleting a User deletes all their Sessions
- Deleting a Session deletes all its ExerciseSessions and Sets

---

### Template

Stores reusable workout templates.

| Column      | Type        | Constraints                 | Description               |
|-------------|-------------|-----------------------------|---------------------------|
| id          | Integer     | PRIMARY KEY, AUTO INCREMENT | Unique identifier         |
| name        | String(100) | NOT NULL                    | Template name             |
| description | Text        | NULLABLE                    | Template description      |
| user_id     | Integer     | FOREIGN KEY → User, NOT NULL| Owner of this template    |

**Relationships:**
- `user`: Many-to-One → User
- `exercise_sessions`: One-to-Many → ExerciseSession (cascade delete)

**Indexes:**
- `ix_templates_user_id` on `user_id`

**Cascading:**
- Deleting a User deletes all their Templates
- Deleting a Template deletes all its ExerciseSessions

---

### ExerciseSession

Junction table linking exercises to sessions or templates. Represents an exercise within a specific workout or template.

| Column      | Type    | Constraints                    | Description                      |
|-------------|---------|--------------------------------|----------------------------------|
| id          | Integer | PRIMARY KEY, AUTO INCREMENT    | Unique identifier                |
| exercise_id | Integer | FOREIGN KEY → Exercise, NOT NULL| Which exercise                   |
| session_id  | Integer | FOREIGN KEY → Session, NULLABLE | Parent session (if workout)      |
| template_id | Integer | FOREIGN KEY → Template, NULLABLE| Parent template (if template)    |
| order       | Integer | NOT NULL, DEFAULT AUTO         | Display order within parent      |

**Relationships:**
- `exercise`: Many-to-One → Exercise
- `session`: Many-to-One → Session
- `template`: Many-to-One → Template
- `sets`: One-to-Many → Set (cascade delete, ordered by `order`)

**Constraints:**
- Either `session_id` OR `template_id` must be set (not both)

**Indexes:**
- `ix_exercise_sessions_exercise_id` on `exercise_id`
- `ix_exercise_sessions_session_id` on `session_id`
- `ix_exercise_sessions_template_id` on `template_id`

**Cascading:**
- Deleting a Session/Template deletes all its ExerciseSessions
- Deleting an ExerciseSession deletes all its Sets

---

### Set

Stores individual set data (weight, reps) for an exercise in a session.

| Column               | Type    | Constraints                           | Description                    |
|----------------------|---------|---------------------------------------|--------------------------------|
| id                   | Integer | PRIMARY KEY, AUTO INCREMENT           | Unique identifier              |
| weight               | Float   | NOT NULL, CHECK >= 0                  | Weight used (0 for bodyweight) |
| reps                 | Integer | NOT NULL, CHECK > 0                   | Number of repetitions          |
| unit                 | Enum    | NOT NULL                              | Unit of measurement            |
| exercise_session_id  | Integer | FOREIGN KEY → ExerciseSession, NOT NULL| Parent exercise session        |
| order                | Integer | NOT NULL, DEFAULT AUTO                | Display order within exercise  |

**Enums:**
- `unit`: `kg`, `stacks`

**Relationships:**
- `exercise_session`: Many-to-One → ExerciseSession

**Indexes:**
- `ix_sets_exercise_session_id` on `exercise_session_id`

**Cascading:**
- Deleting an ExerciseSession deletes all its Sets

---

## Relationships Summary

### User (1) → (N) Session
- A user can have many workout sessions
- Deleting a user deletes all their sessions
- FK: `session.user_id → user.id`

### User (1) → (N) Template
- A user can have many workout templates
- Deleting a user deletes all their templates
- FK: `template.user_id → user.id`

### Session (1) → (N) ExerciseSession
- A session contains multiple exercises
- Deleting a session deletes all its exercise records
- FK: `exercise_session.session_id → session.id`

### Template (1) → (N) ExerciseSession
- A template contains multiple exercises
- Deleting a template deletes all its exercise records
- FK: `exercise_session.template_id → template.id`

### Exercise (1) → (N) ExerciseSession
- An exercise can be used in many sessions/templates
- Deleting an exercise is restricted if in use
- FK: `exercise_session.exercise_id → exercise.id`

### ExerciseSession (1) → (N) Set
- Each exercise in a session has multiple sets
- Deleting an exercise session deletes all its sets
- FK: `set.exercise_session_id → exercise_session.id`

---

## Indexes

Performance optimization indexes:

- `users.username` - Fast username lookups
- `sessions.user_id` - Fast session filtering by user
- `templates.user_id` - Fast template filtering by user
- `exercise_sessions.exercise_id` - Fast exercise lookups
- `exercise_sessions.session_id` - Fast session exercise lookups
- `exercise_sessions.template_id` - Fast template exercise lookups
- `sets.exercise_session_id` - Fast set lookups

---

## Data Integrity

### Foreign Key Constraints

All relationships enforce referential integrity:
- Cannot create a session for a non-existent user
- Cannot add exercises to non-existent sessions/templates
- Cannot create sets for non-existent exercise sessions

### Check Constraints

- `Set.weight >= 0` - Allows bodyweight exercises (0.0 weight)
- `Set.reps > 0` - Must have at least one rep

### Unique Constraints

- `User.username` - Usernames must be unique

---

## Migrations

### Running Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback one version
alembic downgrade -1
```

### Migration History

Migrations are stored in `migrations/versions/` and tracked in the `alembic_version` table.

---

## Connection Pooling

The application uses SQLAlchemy connection pooling for performance:

- `pool_size`: 10 connections
- `max_overflow`: 20 additional connections
- `pool_recycle`: 3600 seconds (1 hour)
- `pool_pre_ping`: Enabled (detects stale connections)

---

## Example Queries

### Get all sessions for a user with exercises and sets

```sql
SELECT
    s.id, s.date, s.notes,
    es.id as exercise_session_id, es.order as exercise_order,
    e.name as exercise_name,
    st.weight, st.reps, st.unit, st.order as set_order
FROM sessions s
JOIN exercise_sessions es ON s.id = es.session_id
JOIN exercises e ON es.exercise_id = e.id
JOIN sets st ON es.id = st.exercise_session_id
WHERE s.user_id = 1
ORDER BY s.date DESC, es.order, st.order;
```

### Get exercise history for progressive overload

```sql
SELECT
    s.id as session_id, s.date,
    st.weight, st.reps, st.unit
FROM sets st
JOIN exercise_sessions es ON st.exercise_session_id = es.id
JOIN sessions s ON es.session_id = s.id
WHERE es.exercise_id = 5
  AND s.user_id = 1
  AND s.id IS NOT NULL
ORDER BY s.date DESC, s.id DESC;
```

---

## Environment Variables

```env
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/progressive_overload

# SQLite (development)
DATABASE_URL=sqlite:///./progressive_overload.db
```
