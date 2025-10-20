# API Documentation

Complete documentation for the Progressive Overload Tracker API.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: Configure based on your deployment

## Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Authentication

Currently, the API does not implement authentication. This will be added in a future version.

## Common Response Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content to return
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error

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
GET /exercises/{id}/history?user_id={user_id}
```

**THE CORE FEATURE** - Returns complete performance history and progressive overload suggestions.

**Query Parameters:**
- `user_id` (int, required): User ID to get history for

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

### List Sessions

```http
GET /sessions/
```

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100, max: 1000)
- `user_id` (int, optional): Filter sessions by user

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

**Response:** Same as list item above

### Create Session

```http
POST /sessions/
```

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

### Update Session

```http
PUT /sessions/{id}
```

**Request Body:**
```json
{
  "date": "2025-10-19T14:00:00",
  "notes": "Updated notes"
}
```

**Note:** This endpoint updates session metadata only, not nested exercises/sets.

**Response:** Updated session object

### Delete Session

```http
DELETE /sessions/{id}
```

**Response:** 204 No Content (cascades to exercise_sessions and sets)

### Copy Session (Progressive Overload Workflow)

```http
GET /sessions/from-session/{id}?user_id={user_id}
```

**THE PRIMARY PROGRESSIVE OVERLOAD WORKFLOW** - "Repeat last workout"

Returns a session structure that can be modified and submitted to create a new session.

**Query Parameters:**
- `user_id` (int, required): User ID for the new session

**Response:** SessionCreate format with previous workout data

**Usage:**
1. Get previous session data
2. Modify weights/reps for progression
3. Submit to `POST /sessions/` to create new session

### Create Session from Template

```http
GET /sessions/from-template/{template_id}?user_id={user_id}
```

Returns a session structure from a template.

**Query Parameters:**
- `user_id` (int, required): User ID for the new session

**Response:** SessionCreate format with template exercises

### Reorder Session

```http
PATCH /sessions/{id}/reorder
```

Reorder exercises and sets within a session.

**Request Body:**
```json
{
  "exercise_sessions": [
    {
      "id": 10,
      "order": 2,
      "sets": [
        {"id": 25, "order": 1},
        {"id": 24, "order": 2}
      ]
    },
    {
      "id": 9,
      "order": 1
    }
  ]
}
```

**Response:** Updated session with new ordering

---

## Templates

### List Templates

```http
GET /templates/
```

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100, max: 1000)
- `user_id` (int, optional): Filter templates by user

**Response:**
```json
[
  {
    "id": 1,
    "name": "Push Day",
    "description": "Chest, shoulders, and triceps",
    "user_id": 1,
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

**Response:** Same as list item above

### Create Template

```http
POST /templates/
```

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

### Update Template

```http
PUT /templates/{id}
```

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

### Delete Template

```http
DELETE /templates/{id}
```

**Response:** 204 No Content

### Create Template from Session

```http
POST /templates/from-session/{session_id}?user_id={user_id}&name={name}
```

Create a reusable template from an existing session.

**Query Parameters:**
- `user_id` (int, required): User ID who owns the template
- `name` (string, required): Name for the new template

**Response:** Created template object

---

## Users

### List Users

```http
GET /users/
```

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

**Response:** Same as list item above

### Create User

```http
POST /users/
```

**Request Body:**
```json
{
  "username": "john_doe",
  "name": "John Doe"
}
```

**Response:** Created user object with `id`

### Update User

```http
PUT /users/{id}
```

**Request Body:**
```json
{
  "name": "Johnny Doe"
}
```

**Response:** Updated user object

### Delete User

```http
DELETE /users/{id}
```

**Response:** 204 No Content (cascades to sessions)

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
