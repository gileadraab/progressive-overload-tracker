# API Documentation

Complete documentation for the Progressive Overload Tracker API.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: Configure based on your deployment

## Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Authentication

The API uses JWT (JSON Web Token) authentication. Most endpoints require authentication.

### Public Endpoints (No Authentication Required)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc documentation
- `GET /exercises/` - List exercises
- `GET /exercises/{id}` - Get exercise details
- `POST /exercises/` - Create exercise
- `PUT /exercises/{id}` - Update exercise
- `DELETE /exercises/{id}` - Delete exercise

### Protected Endpoints (Authentication Required)
All other endpoints require a valid JWT access token in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

### Getting Started
1. Register a new user via `POST /auth/register`
2. Login via `POST /auth/login` to get access and refresh tokens
3. Include the access token in the `Authorization` header for all protected endpoints
4. When the access token expires, use `POST /auth/refresh` with the refresh token to get a new access token

## Common Response Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content to return
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - Valid token but insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error

---

## Authentication Endpoints

### Register User

```http
POST /auth/register
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "name": "John Doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "name": "John Doe"
}
```

**Notes:**
- Password must be at least 8 characters
- Username and email must be unique
- Password is hashed with bcrypt before storage

### Login

```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Notes:**
- Access token expires in 30 minutes
- Refresh token expires in 7 days
- Use access token for API requests
- Use refresh token to get new access token

### Refresh Token

```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Notes:**
- Returns a new access token
- Returns the same refresh token
- Use when access token expires

### Logout

```http
POST /auth/logout
```

**Response:**
```json
{
  "message": "Successfully logged out. Please remove tokens from client."
}
```

**Notes:**
- JWT tokens are stateless, so logout is client-side
- Remove both access and refresh tokens from client storage

---

## Exercises

### List Exercises

```http
GET /exercises/
```

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100, max: 1000)
- `search` (string, optional): Search term for name, category, or subcategory
- `category` (string, optional): Filter by category (`chest`, `back`, `legs`, `shoulders`, `arms`, `core`)
- `equipment` (string, optional): Filter by equipment (`machine`, `dumbbell`, `barbell`, `bodyweight`, `kettlebell`, `resistance_band`)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Bench Press",
    "category": "chest",
    "subcategory": "Upper Chest",
    "equipment": "barbell",
    "image_url": "https://example.com/bench.jpg"
  }
]
```

### Get Exercise

```http
GET /exercises/{id}
```

**Response:** Same as list item above

### Create Exercise

```http
POST /exercises/
```

**Request Body:**
```json
{
  "name": "Bench Press",
  "category": "chest",
  "subcategory": "Upper Chest",
  "equipment": "barbell",
  "image_url": "https://example.com/bench.jpg"
}
```

**Response:** Created exercise object with `id`

### Update Exercise

```http
PUT /exercises/{id}
```

**Request Body:** Same as create (all fields optional)

**Response:** Updated exercise object

### Delete Exercise

```http
DELETE /exercises/{id}
```

**Response:** 204 No Content

### Get Exercise History

```http
GET /exercises/{id}/history
```

**Authentication:** Required

**THE CORE FEATURE** - Returns complete performance history and progressive overload suggestions for the authenticated user.

**Response:**
```json
{
  "exercise_id": 5,
  "last_performed": {
    "session_id": 42,
    "date": "2025-10-15T10:30:00",
    "sets": [
      {"weight": 100.0, "reps": 10, "unit": "kg"},
      {"weight": 100.0, "reps": 8, "unit": "kg"}
    ],
    "max_weight": 100.0,
    "total_volume": 1800.0
  },
  "personal_best": {
    "weight": 120.0,
    "reps": 5,
    "date": "2025-09-15T14:00:00",
    "session_id": 38,
    "estimated_1rm": 135.0
  },
  "recent_sessions": [
    {
      "session_id": 42,
      "date": "2025-10-15T10:30:00",
      "sets": [...],
      "best_set": {"weight": 100.0, "reps": 10, "unit": "kg"}
    }
  ],
  "progression_suggestion": {
    "recommended_weight": 102.5,
    "recommended_reps": 10,
    "rationale": "You hit target reps - increase weight by 2.5 kg"
  }
}
```

---

## Sessions

**Note:** All session endpoints require authentication. Users can only access their own sessions.

### List Sessions

```http
GET /sessions/
```

**Authentication:** Required

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100, max: 1000)

**Note:** Sessions are automatically filtered to the authenticated user.

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "date": "2025-10-19T10:30:00",
    "notes": "Great workout!",
    "exercise_sessions": [
      {
        "id": 1,
        "exercise_id": 5,
        "order": 1,
        "exercise": {
          "id": 5,
          "name": "Bench Press",
          "category": "chest"
        },
        "sets": [
          {
            "id": 1,
            "weight": 100.0,
            "reps": 10,
            "unit": "kg",
            "order": 1
          }
        ]
      }
    ]
  }
]
```

### Get Session

```http
GET /sessions/{id}
```

**Authentication:** Required

**Authorization:** Users can only access their own sessions.

**Response:** Same as list item above

**Error Responses:**
- `403 Forbidden` - Attempting to access another user's session

### Create Session

```http
POST /sessions/
```

**Authentication:** Required

**Request Body:**
```json
{
  "user_id": 1,
  "date": "2025-10-19T10:30:00",
  "notes": "Great chest and triceps workout!",
  "exercise_sessions": [
    {
      "exercise_id": 5,
      "sets": [
        {"weight": 100.0, "reps": 10, "unit": "kg"},
        {"weight": 100.0, "reps": 8, "unit": "kg"}
      ]
    }
  ]
}
```

**Response:** Created session with nested details

**Error Responses:**
- `403 Forbidden` - user_id does not match authenticated user

### Update Session

```http
PUT /sessions/{id}
```

**Authentication:** Required

**Authorization:** Users can only update their own sessions.

This endpoint supports two modes:

#### 1. Partial Update (date/notes only)
Update only session metadata without modifying exercises/sets.

**Request Body:**
```json
{
  "date": "2025-10-19T14:00:00",
  "notes": "Updated notes"
}
```

#### 2. Full Replacement (complete editing)
Replace all exercises and sets. Use this to fix typos, add forgotten exercises, or correct historical data.

**Request Body:**
```json
{
  "date": "2025-10-19T14:00:00",
  "notes": "Chest day - fixed weight typo",
  "exercise_sessions": [
    {
      "exercise_id": 5,
      "sets": [
        {"weight": 100.0, "reps": 10, "unit": "kg"},
        {"weight": 100.0, "reps": 8, "unit": "kg"}
      ]
    }
  ]
}
```

**Workflow for Full Editing:**
1. GET /sessions/{id} to fetch current session
2. Modify the data in your application
3. PUT /sessions/{id} with the modified data
4. All existing exercise_sessions and sets are replaced atomically

**Use Cases:**
- Fix weight typos (e.g., 1000kg → 100kg)
- Add forgotten exercises
- Remove incorrect sets
- Correct historical data

**Response:** Updated session object with all nested relationships

**Error Responses:**
- `403 Forbidden` - Attempting to update another user's session
- `404 Not Found` - Exercise ID in exercise_sessions does not exist

### Delete Session

```http
DELETE /sessions/{id}
```

**Authentication:** Required

**Authorization:** Users can only delete their own sessions.

**Response:** 204 No Content (cascades to exercise_sessions and sets)

**Error Responses:**
- `403 Forbidden` - Attempting to delete another user's session

### Copy Session (Progressive Overload Workflow)

```http
GET /sessions/from-session/{id}?user_id={user_id}
```

**Authentication:** Required

**THE PRIMARY PROGRESSIVE OVERLOAD WORKFLOW** - "Repeat last workout"

Returns a session structure that can be modified and submitted to create a new session.

**Query Parameters:**
- `user_id` (int, required): User ID for the new session (must match authenticated user)

**Response:** SessionCreate format with previous workout data

**Usage:**
1. Get previous session data
2. Modify weights/reps for progression
3. Submit to `POST /sessions/` to create new session

**Error Responses:**
- `403 Forbidden` - user_id does not match authenticated user or session does not belong to user

### Create Session from Template

```http
GET /sessions/from-template/{template_id}?user_id={user_id}
```

**Authentication:** Required

Returns a session structure from a template.

**Query Parameters:**
- `user_id` (int, required): User ID for the new session (must match authenticated user)

**Response:** SessionCreate format with template exercises

**Error Responses:**
- `403 Forbidden` - user_id does not match authenticated user

---

## Templates

**Note:** All template endpoints require authentication. Users can see global templates (is_global=true) plus their own templates. Users cannot modify or delete global templates.

### List Templates

```http
GET /templates/
```

**Authentication:** Required

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100, max: 1000)

**Note:** Automatically returns global templates plus templates owned by the authenticated user.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Push Day",
    "description": "Chest, shoulders, and triceps",
    "user_id": 1,
    "is_global": false,
    "exercise_sessions": [
      {
        "id": 1,
        "exercise_id": 5,
        "order": 1,
        "exercise": {
          "id": 5,
          "name": "Bench Press",
          "category": "chest"
        }
      }
    ]
  }
]
```

### Get Template

```http
GET /templates/{id}
```

**Authentication:** Required

**Authorization:** Users can access global templates or their own templates.

**Response:** Same as list item above

**Error Responses:**
- `403 Forbidden` - Attempting to access another user's template (non-global)

### Create Template

```http
POST /templates/
```

**Authentication:** Required

**Request Body:**
```json
{
  "name": "Push Day",
  "description": "Chest, shoulders, and triceps workout",
  "user_id": 1,
  "exercise_sessions": [
    {"exercise_id": 5},
    {"exercise_id": 8},
    {"exercise_id": 12}
  ]
}
```

**Response:** Created template with nested details

**Note:** is_global defaults to false. Only administrators can create global templates.

### Update Template

```http
PUT /templates/{id}
```

**Authentication:** Required

**Authorization:** Users can only update their own templates. Global templates cannot be modified.

**Request Body:**
```json
{
  "name": "Advanced Push Day",
  "description": "Updated push workout with more volume",
  "exercise_sessions": [
    {"exercise_id": 5},
    {"exercise_id": 8},
    {"exercise_id": 12},
    {"exercise_id": 15}
  ]
}
```

**Response:** Updated template object

**Error Responses:**
- `403 Forbidden` - Attempting to update another user's template or a global template

### Delete Template

```http
DELETE /templates/{id}
```

**Authentication:** Required

**Authorization:** Users can only delete their own templates. Global templates cannot be deleted.

**Response:** 204 No Content

**Error Responses:**
- `403 Forbidden` - Attempting to delete another user's template or a global template

### Create Template from Session

```http
POST /templates/from-session/{session_id}?user_id={user_id}&name={name}
```

**Authentication:** Required

Create a reusable template from an existing session.

**Query Parameters:**
- `user_id` (int, required): User ID who owns the template (must match authenticated user)
- `name` (string, required): Name for the new template

**Response:** Created template object

**Error Responses:**
- `403 Forbidden` - user_id does not match authenticated user or session does not belong to user

---

## Users

**Note:** User registration is handled via `/auth/register`. There is no public user creation endpoint.

### List Users

```http
GET /users/
```

**Authentication:** Not required

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100, max: 1000)

**Response:**
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "name": "John Doe"
  }
]
```

### Get User

```http
GET /users/{id}
```

**Authentication:** Not required

**Response:** Same as list item above

### Update User

```http
PUT /users/{id}
```

**Authentication:** Required

**Authorization:** Users can only update their own profile.

**Request Body:**
```json
{
  "name": "Johnny Doe"
}
```

**Response:** Updated user object

**Error Responses:**
- `403 Forbidden` - Attempting to update another user's profile

### Delete User

```http
DELETE /users/{id}
```

**Authentication:** Required

**Authorization:** Users can only delete their own account.

**Response:** 204 No Content (cascades to sessions)

**Error Responses:**
- `403 Forbidden` - Attempting to delete another user's account

---

## Progressive Overload Formulas

### Brzycki 1RM Formula

```
1RM = weight × (36 / (37 - reps))
```

Used to estimate the maximum weight you can lift for one repetition.

### Progressive Overload Logic

- **If reps ≥ 8**: Increase weight by 2.5kg (or 1 stack for machine exercises)
- **If reps < 8**: Keep weight, aim for more reps next time

### Volume Calculation

```
Volume = weight × reps × sets
```

Tracks total work performed for an exercise.

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

Common errors:
- `Exercise with id {id} not found` (404)
- `User with id {id} not found` (404)
- `Session with id {id} not found` (404)
- `Template with id {id} not found` (404)
- Validation errors return 422 with field-specific details
