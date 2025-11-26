# chirp
A production-ready FastAPI backend providing user management, authentication, posts, voting, and health monitoring. The project includes complete test coverage with pytest, isolated test database setup, and GitHub Actions CI/CD with automated deployment to Render.

## Deployed Live API
Interactive Swagger UI: https://chirp-x80o.onrender.com/docs

Redoc: https://chirp-x80o.onrender.com/redoc

## Features
- User registration and authentication (JWT-based)
- CRUD operations for posts
- Voting system with upvote/downvote semantics
- Health check with uptime and DB status
- Strong input/output validation using Pydantic
- Fully isolated test DB for CI
- Automated test pipeline using GitHub Actions
- Auto-deploy to Render on successful build

## Tech Stack
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Alembic (migrations)
- Pytest
- JWT Authentication
- GitHub Actions CI/CD
- Render (production hosting)

## Project Structure
```pgsql
chirp/
│── .github/
│   └── workflows/
│       └── test-and-deploy.yaml
│── alembic/
│   │── versions/
│   │   └── e0661c2399bd_create_users_posts_and_votes_tables.py
│   │── env.py
│   │── README
│   └── script.py.mako
│── app/
│   │── routers/
│   │   ├── auth.py
│   │   ├── post.py
│   │   ├── user.py
│   │   └── vote.py
│   │── config.py
│   │── database.py
│   │── main.py
│   │── models.py
│   │── oauth2.py
│   │── schemas.py
│   └── utils.py
│── tests/
│   │── conftest.py
│   │── test_auth.py
│   │── test_health.py
│   │── test_post.py
│   │── test_user.py
│   └── test_vote.py
│── .coveragerc
│── .env
│── .gitignore
│── alembic.ini
│── LICENSE
│── pyproject.toml
│── README.md
└── requirements.txt
```

## Running Locally

### Install dependencies
```bash
pip install -r requirements.txt
pip install -e . # Install project (for package imports)
```

### Set environment variables using .env file
```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=chirp
DB_USER=postgres
DB_PASSWORD=postgres
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Start local PostgreSQL and Run Alembic migrations
```bash
alembic upgrade head
```
If any changes made to the model classes, create a new migration
```bash
alembic revision --autogenerate -m "description"
```

### Start the server
```bash
fastapi dev app/main.py
```
For Swagger UI, visit http://127.0.0.1:8000/docs or http://localhost:8000/docs

For ReDoc, visit http://127.0.0.1:8000/redoc or http://localhost:8000/redoc

### Testing & Coverage
Run all tests with coverage:
```bash
pytest --cov
```
This enforces a minimum test coverage of 94% (configured in `.coveragerc`). Tests run using a temporary PostgreSQL test database, set up via the `client` and `session` fixtures.

## CI/CD Pipeline Overview
Chirp is deployed on Render. Every push or pull request to main runs the full test suite with a PostgreSQL service. If tests pass on main, GitHub Actions automatically triggers a Render deploy via the deploy hook.

## License
MIT