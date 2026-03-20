import secrets
import threading
from dataclasses import dataclass, field

from app.game_logic import (
    check_bingo,
    generate_board,
    get_winning_square_ids,
    toggle_square,
)
from app.models import BingoLine, BingoSquareData, GameState


@dataclass
class GameSession:
    """Holds the state for a single game session."""

    game_state: GameState = GameState.START
    board: list[BingoSquareData] = field(default_factory=list)
    winning_line: BingoLine | None = None
    show_bingo_modal: bool = False

    @property
    def winning_square_ids(self) -> set[int]:
        return get_winning_square_ids(self.winning_line)

    @property
    def has_bingo(self) -> bool:
        return self.game_state == GameState.BINGO

    def start_game(self) -> None:
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


@dataclass
class TeamGameSession:
    """Shared game session for collaborative team/multiplayer mode."""

    team_code: str
    game_state: GameState = GameState.START
    board: list[BingoSquareData] = field(default_factory=list)
    winning_line: BingoLine | None = None
    show_bingo_modal: bool = False
    # Participant IDs tracked as a set to deduplicate concurrent joins
    participants: set[str] = field(default_factory=set)
    # RLock is excluded from __init__, repr, and comparison
    _lock: threading.RLock = field(
        default_factory=threading.RLock, init=False, repr=False, compare=False
    )

    @property
    def participant_count(self) -> int:
        return len(self.participants)

    @property
    def winning_square_ids(self) -> set[int]:
        return get_winning_square_ids(self.winning_line)

    @property
    def has_bingo(self) -> bool:
        return self.game_state == GameState.BINGO

    def add_participant(self, participant_id: str) -> None:
        with self._lock:
            self.participants.add(participant_id)

    def start_game(self) -> None:
        with self._lock:
            self.board = generate_board()
            self.winning_line = None
            self.game_state = GameState.PLAYING
            self.show_bingo_modal = False

    def handle_square_click(self, square_id: int) -> None:
        with self._lock:
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
        with self._lock:
            self.game_state = GameState.START
            self.board = []
            self.winning_line = None
            self.show_bingo_modal = False

    def dismiss_modal(self) -> None:
        with self._lock:
            self.show_bingo_modal = False
            self.game_state = GameState.PLAYING


# In-memory team session store keyed by team code
_team_sessions: dict[str, TeamGameSession] = {}
_team_sessions_lock = threading.Lock()


def create_team_session() -> TeamGameSession:
    """Create a new team session with a unique 6-character code."""
    with _team_sessions_lock:
        while True:
            code = secrets.token_hex(3).upper()
            if code not in _team_sessions:
                session = TeamGameSession(team_code=code)
                _team_sessions[code] = session
                return session


def get_team_session(code: str) -> TeamGameSession | None:
    """Return an existing team session by code, or None if not found."""
    return _team_sessions.get(code.upper())
