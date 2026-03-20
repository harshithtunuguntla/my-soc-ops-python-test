from dataclasses import dataclass, field

from app.game_logic import (
    check_bingo,
    generate_board,
    generate_board_for_persona,
    get_winning_square_ids,
    toggle_square,
)
from app.models import BingoLine, BingoSquareData, GameState
from app.tech_life_data import BoardPersona


@dataclass
class GameSession:
    """Holds the state for a single game session."""

    game_state: GameState = GameState.START
    board: list[BingoSquareData] = field(default_factory=list)
    winning_line: BingoLine | None = None
    show_bingo_modal: bool = False
    persona: str = ""

    @property
    def winning_square_ids(self) -> set[int]:
        return get_winning_square_ids(self.winning_line)

    @property
    def has_bingo(self) -> bool:
        return self.game_state == GameState.BINGO

    def start_game(self, persona: str = "") -> None:
        """Start a new game, optionally using a Tech Life persona preset.

        Args:
            persona: A persona key (e.g. ``"backend_engineer"``).  When
                provided the board is generated from Tech Life question pools
                biased toward the chosen persona.  Pass an empty string (the
                default) to use the original generic question pool.
        """
        self.persona = persona
        if persona:
            self.board = generate_board_for_persona(persona)
        else:
            self.board = generate_board()
        self.winning_line = None
        self.game_state = GameState.PLAYING
        self.show_bingo_modal = False

    def handle_square_click(self, square_id: int) -> None:
        if self.game_state != GameState.PLAYING:
            return
        self.board = toggle_square(self.board, square_id)

        if self.winning_line is None:
            bingo = check_bingo(self.board)
            if bingo is not None:
                self.winning_line = bingo
                self.game_state = GameState.BINGO
                self.show_bingo_modal = True

    def reset_game(self) -> None:
        self.game_state = GameState.START
        self.board = []
        self.winning_line = None
        self.show_bingo_modal = False
        self.persona = ""

    def dismiss_modal(self) -> None:
        self.show_bingo_modal = False
        self.game_state = GameState.PLAYING


# In-memory session store keyed by session ID
_sessions: dict[str, GameSession] = {}


def get_session(session_id: str) -> GameSession:
    """Get or create a game session for the given session ID."""
    if session_id not in _sessions:
        _sessions[session_id] = GameSession()
    return _sessions[session_id]


PERSONA_DISPLAY_NAMES: dict[str, str] = {
    BoardPersona.DEFAULT: "Default (all categories)",
    BoardPersona.BACKEND_ENGINEER: "Backend Engineer",
    BoardPersona.FRONTEND_ENGINEER: "Frontend Engineer",
    BoardPersona.TOOLING_DEVOPS: "Tooling / DevOps",
}
