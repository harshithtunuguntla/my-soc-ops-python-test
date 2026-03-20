import uuid
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.game_service import (
    GameSession,
    create_team_session,
    get_session,
    get_team_session,
)
from app.models import GameState

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Soc Ops - Social Bingo")
app.add_middleware(SessionMiddleware, secret_key="soc-ops-secret-key")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")


def _get_session_id(request: Request) -> str:
    """Get or create a persistent session ID for the current user."""
    if "session_id" not in request.session:
        request.session["session_id"] = uuid.uuid4().hex
    return request.session["session_id"]


def _get_game_session(request: Request) -> GameSession:
    """Get or create a solo game session using cookie-based sessions."""
    return get_session(_get_session_id(request))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    session = _get_game_session(request)
    return templates.TemplateResponse(
        request,
        "home.html",
        {"session": session, "GameState": GameState},
    )


@app.post("/start", response_class=HTMLResponse)
async def start_game(request: Request) -> Response:
    session = _get_game_session(request)
    session.start_game()
    return templates.TemplateResponse(
        request, "components/game_screen.html", {"session": session}
    )


@app.post("/toggle/{square_id}", response_class=HTMLResponse)
async def toggle_square(request: Request, square_id: int) -> Response:
    session = _get_game_session(request)
    session.handle_square_click(square_id)
    return templates.TemplateResponse(
        request, "components/game_screen.html", {"session": session}
    )


@app.post("/reset", response_class=HTMLResponse)
async def reset_game(request: Request) -> Response:
    session = _get_game_session(request)
    session.reset_game()
    return templates.TemplateResponse(
        request,
        "components/start_screen.html",
        {"session": session, "GameState": GameState},
    )


@app.post("/dismiss-modal", response_class=HTMLResponse)
async def dismiss_modal(request: Request) -> Response:
    session = _get_game_session(request)
    session.dismiss_modal()
    return templates.TemplateResponse(
        request, "components/game_screen.html", {"session": session}
    )


def run() -> None:
    """Entry point for the application."""
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


# ---------------------------------------------------------------------------
# Team mode routes
# ---------------------------------------------------------------------------


@app.get("/team", response_class=HTMLResponse)
async def team_home(request: Request) -> Response:
    """Team mode lobby — create a new session or join an existing one."""
    return templates.TemplateResponse(request, "team_home.html", {})


@app.post("/team/create", response_class=HTMLResponse)
async def team_create(request: Request) -> Response:
    """Create a new shared team session and redirect the creator to it."""
    session_id = _get_session_id(request)
    team_session = create_team_session()
    team_session.add_participant(session_id)
    return RedirectResponse(url=f"/team/{team_session.team_code}", status_code=303)


@app.post("/team/join", response_class=HTMLResponse)
async def team_join(request: Request) -> Response:
    """Join an existing team session identified by a team code."""
    form = await request.form()
    code = str(form.get("team_code", "")).strip().upper()
    team_session = get_team_session(code)
    if team_session is None:
        return templates.TemplateResponse(
            request,
            "team_home.html",
            {"error": f"Session '{code}' not found. Check the code and try again."},
        )
    session_id = _get_session_id(request)
    team_session.add_participant(session_id)
    return RedirectResponse(url=f"/team/{code}", status_code=303)


@app.get("/team/{team_code}", response_class=HTMLResponse)
async def team_game_page(request: Request, team_code: str) -> Response:
    """View a team session's game page. Registers the visitor as a participant."""
    team_session = get_team_session(team_code)
    if team_session is None:
        return RedirectResponse(url="/team", status_code=303)
    session_id = _get_session_id(request)
    team_session.add_participant(session_id)
    return templates.TemplateResponse(
        request,
        "team_game.html",
        {"team_session": team_session, "GameState": GameState},
    )


@app.post("/team/{team_code}/start", response_class=HTMLResponse)
async def team_start_game(request: Request, team_code: str) -> Response:
    """Start the shared game for the team."""
    team_session = get_team_session(team_code)
    if team_session is None:
        return RedirectResponse(url="/team", status_code=303)
    team_session.start_game()
    return templates.TemplateResponse(
        request,
        "components/team_game_screen.html",
        {"team_session": team_session},
    )


@app.post("/team/{team_code}/toggle/{square_id}", response_class=HTMLResponse)
async def team_toggle_square(
    request: Request, team_code: str, square_id: int
) -> Response:
    """Toggle a square on the shared team board."""
    team_session = get_team_session(team_code)
    if team_session is None:
        return RedirectResponse(url="/team", status_code=303)
    team_session.handle_square_click(square_id)
    return templates.TemplateResponse(
        request,
        "components/team_game_screen.html",
        {"team_session": team_session},
    )


@app.post("/team/{team_code}/reset", response_class=HTMLResponse)
async def team_reset_game(request: Request, team_code: str) -> Response:
    """Reset the shared team game back to the lobby state."""
    team_session = get_team_session(team_code)
    if team_session is None:
        return RedirectResponse(url="/team", status_code=303)
    team_session.reset_game()
    return templates.TemplateResponse(
        request,
        "components/team_start_screen.html",
        {"team_session": team_session, "GameState": GameState},
    )


@app.post("/team/{team_code}/dismiss-modal", response_class=HTMLResponse)
async def team_dismiss_modal(request: Request, team_code: str) -> Response:
    """Dismiss the bingo celebration modal and continue playing."""
    team_session = get_team_session(team_code)
    if team_session is None:
        return RedirectResponse(url="/team", status_code=303)
    team_session.dismiss_modal()
    return templates.TemplateResponse(
        request,
        "components/team_game_screen.html",
        {"team_session": team_session},
    )
