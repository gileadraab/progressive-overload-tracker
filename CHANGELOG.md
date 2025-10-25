# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-25

Initial release of the Progressive Overload Tracker API.

### Features

#### Progressive Overload Tracking
- Exercise history with personal best tracking (estimated 1RM using Brzycki formula)
- Intelligent progression suggestions based on recent performance
- Recent session trends (last 5 workouts)
- `GET /exercises/{id}/history` endpoint for complete exercise analysis

#### Workout Management
- Full CRUD operations for workout sessions
- Session copying workflow - repeat previous workouts as starting point
- Session editing - modify historical data
- Nested creation of exercises and sets in single request
- Template system for reusable workout plans
- Global templates for built-in workout programs

#### Exercise Library
- Pre-loaded with 20+ common exercises
- Category-based organization (chest, back, legs, shoulders, arms, core)
- Equipment type classification (barbell, dumbbell, machine, bodyweight, kettlebell, resistance band)
- Filtering by category and equipment

#### Authentication & Security
- JWT-based authentication (access + refresh tokens)
- Email/password registration and login
- Protected API routes with user data isolation
- Password hashing with bcrypt
- OAuth provider support ready (Google, Facebook, Instagram)

#### Developer Experience
- Complete OpenAPI/Swagger documentation
- Docker Compose setup for local development
- Database seed script with sample data
- Comprehensive Makefile with common commands
- Pre-commit hooks for code quality
- GitHub Actions CI/CD pipeline

### Technical Stack
- **Backend**: FastAPI 0.104.1, Python 3.11+
- **Database**: PostgreSQL 16, SQLAlchemy 2.0.44
- **Authentication**: JWT (python-jose), bcrypt
- **Testing**: pytest with 79% coverage
- **Containerization**: Docker, Docker Compose

### API Endpoints

#### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token

#### Exercises
- `GET /exercises/` - List all exercises (with filtering)
- `GET /exercises/{id}` - Get exercise details
- `GET /exercises/{id}/history` - Get exercise history with progression data

#### Sessions
- `GET /sessions/` - List user's workout sessions
- `POST /sessions/` - Create new workout session
- `GET /sessions/{id}` - Get session details
- `PUT /sessions/{id}` - Update existing session
- `DELETE /sessions/{id}` - Delete session
- `GET /sessions/from-session/{id}` - Copy session as template
- `GET /sessions/from-template/{id}` - Instantiate template as session

#### Templates
- `GET /templates/` - List templates (user + global)
- `POST /templates/` - Create new template
- `GET /templates/{id}` - Get template details
- `PUT /templates/{id}` - Update template
- `DELETE /templates/{id}` - Delete template
- `POST /templates/from-session/{id}` - Create template from session

#### Users
- `GET /users/{id}` - Get user profile
- `PUT /users/{id}` - Update user profile
- `DELETE /users/{id}` - Delete user account

#### Health
- `GET /health` - API health check

### Documentation
- Interactive API documentation at `/docs` (Swagger UI)
- Complete README with quick start guide
- API reference documentation
- Database schema documentation
- Development setup guide

### Security
- All passwords hashed with bcrypt
- JWT tokens for stateless authentication
- User data isolation - users can only access their own data
- Environment-based configuration (no secrets in code)
- Security scanning via pre-commit hooks

---

**Full Changelog**: Initial v1.0.0 release
