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

## Design Guide

### Current Theme: Cyberpunk Neon Noir Galaxy

The game features a futuristic cyberpunk aesthetic with neon glows, dark space backgrounds, and intense visual effects.

#### Theme Colors

```css
/* Primary Colors (CSS Custom Properties) */
--primary: #00ffff;        /* Electric cyan - main accent */
--secondary: #ff00ff;      /* Hot magenta - highlights */
--accent: #00ffff;         /* Bright cyan - text & borders */
--warning: #ffff00;        /* Plasma yellow - winning states */
--background: linear-gradient(135deg, #0a0a0a 0%, #1a0033 50%, #000033 100%);
--surface: rgba(10, 10, 10, 0.9);  /* Dark translucent */
--text-primary: #00ffff;
--text-secondary: #ff00ff;
--marked: #ff00ff;         /* Marked squares */
--winning: #ffff00;        /* Winning line squares */
```

#### Key Visual Elements

**Typography:**
- Font: `'Courier New', monospace` (retro terminal feel)
- All text has neon glow effects via `text-shadow`

**Borders & Shadows:**
- `.btn`: `2px solid #00ffff` with triple-layered neon glow (`box-shadow`)
- Marked squares: `0 0 20px var(--marked)` glow effect
- Winning squares: Plasma animation with oscillating opacity

**Animations:**
- `@keyframes plasma`: Winning squares pulse with glow
- `@keyframes blink`: Status indicators (if used)
- Neon scanline overlay for CRT monitor effect
- Starfield background for space atmosphere

**Interactive States:**
- Hover: Background shifts to `--secondary` with enhanced glow
- Active: Background becomes `--warning` with maximum glow intensity

### Customizing the Theme

To change the theme, modify CSS variables in `app/static/css/app.css`:

```css
:root {
    --primary: #00ffff;        /* Change primary color */
    --secondary: #ff00ff;      /* Change secondary color */
    --accent: #00ffff;         /* Change accent color */
    --warning: #ffff00;        /* Change warning color */
    --background: linear-gradient(...); /* Change background gradient */
}
```

Then update:
1. **Text shadows** in `.text-*` classes for new glow colors
2. **Button glows** in `.btn` class
3. **Scanline color** in `body::before` for matching theme
4. **Starfield colors** in `body::after` if needed

### Design Patterns

**Light/Dark Contrast:**
- Dark backgrounds (#0a0a0a, #1a0033) with bright neon text
- Ensures readability and dramatic cyberpunk aesthetic

**Glow Effects:**
- Multi-layered shadows: `0 0 10px, 0 0 20px, 0 0 30px`
- Creates depth and neon intensity

**Pixel-Perfect Alignment:**
- No border-radius (sharp edges for retro feel)
- 1-2px borders for crisp appearance
- Grid layout with consistent spacing

### Component Customization

**Buttons:**
- Class: `.btn` for neon styling
- Inherits background color from parent class (`.bg-accent`, etc.)
- Glow responds to hover/active states

**Board Squares:**
- Class: `.square` 
- States: unmarked (white bg), marked (magenta glow), winning (yellow plasma)
- Minimum 60px height for mobile touch targets

**Modal:**
- Background: Space galaxy gradient
- Border: 2px cyan with neon glow
- Animation: Bounce with plasma effects

### Responsive Design

- Mobile-first: 100% viewport height with flexbox centering
- Touch targets: Minimum 60px height
- No hover-only states (mobile compatibility)
- CSS Grid for bingo board (5x5 auto-scaling)