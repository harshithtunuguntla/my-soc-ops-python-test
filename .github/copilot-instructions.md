# Copilot Workspace Instructions

## Development Checklist

Before committing any changes, ensure:

- [ ] `uv run ruff check .` passes with no errors
- [ ] `uv run pytest` passes
- [ ] Code follows Python conventions (snake_case, type hints)
- [ ] No unused variables or imports

## Project Overview

**Soc Ops** is a Social Bingo game built with Python (FastAPI + Jinja2 + HTMX). Players find people who match questions to mark squares and get 5 in a row.

## Architecture

```
app/
├── templates/       # Jinja2 HTML templates (base.html, home.html, components/)
├── static/          # CSS & JS assets
├── models.py        # Pydantic models (GameState, BingoSquare)
├── game_logic.py    # Board generation & bingo detection
├── game_service.py  # Session management (GameSession)
├── data.py          # Question bank
└── main.py          # FastAPI routes & HTMX endpoints
tests/
├── test_api.py      # API endpoint tests (httpx + TestClient)
└── test_game_logic.py  # Game logic unit tests
```

## Key Commands

```bash
uv run uvicorn app.main:app --reload --port 8000  # Run dev server
uv run pytest                                       # Run tests
uv run ruff check .                                 # Lint
```

## Styling

Custom CSS utility classes (Tailwind-like) in `app/static/css/app.css`:
- Layout: `.flex`, `.grid`, `.items-center`
- Spacing: `.p-4`, `.mb-2`, `.mx-auto`
- Colors: `.bg-accent`, `.bg-marked`, `.text-gray-700`

## State Management

- `GameSession` manages game state server-side
- State persisted via signed cookies (itsdangerous)
- HTMX handles partial page updates without full reloads

## Code Patterns

### Immutability
Game logic returns new objects using `model_copy()`; no mutations.

### Pure Functions
Game logic functions are pure (no side effects) in `game_logic.py`.

### Session Management
Cookie-based with UUID; lazy creation via `_get_game_session()`.

### Frozen Models
Pydantic models use `ConfigDict(frozen=True)` to prevent mutations.