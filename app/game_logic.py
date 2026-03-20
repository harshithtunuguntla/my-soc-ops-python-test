import functools
import random

from app.data import FREE_SPACE, QUESTIONS
from app.models import BingoLine, BingoSquareData
from app.tech_life_data import (
    PERSONA_WEIGHTS,
    TECH_LIFE_QUESTIONS,
    TechLifeCategory,
    resolve_persona,
)

BOARD_SIZE = 5
CENTER_INDEX = 12  # 5x5 grid, center is index 12 (row 2, col 2)
_NON_FREE_SQUARES = BOARD_SIZE * BOARD_SIZE - 1  # 24


def generate_board() -> list[BingoSquareData]:
    """Generate a new 5x5 bingo board using the default question pool."""
    questions = iter(random.sample(QUESTIONS, _NON_FREE_SQUARES))
    return [
        BingoSquareData(id=i, text=FREE_SPACE, is_marked=True, is_free_space=True)
        if i == CENTER_INDEX
        else BingoSquareData(id=i, text=next(questions))
        for i in range(BOARD_SIZE * BOARD_SIZE)
    ]


def _distribute_counts(
    weights: dict[TechLifeCategory, int], total: int
) -> dict[TechLifeCategory, int]:
    """Distribute *total* slots across categories proportional to *weights*.

    The last category absorbs any rounding remainder so the sum is exact.
    """
    total_weight = sum(weights.values())
    counts: dict[TechLifeCategory, int] = {}
    categories = list(weights.keys())
    assigned = 0
    for cat in categories[:-1]:
        n = round(weights[cat] / total_weight * total)
        counts[cat] = n
        assigned += n
    counts[categories[-1]] = total - assigned
    return counts


def generate_board_for_persona(persona_key: str) -> list[BingoSquareData]:
    """Generate a 5x5 Tech Life Bingo board biased by the given persona.

    Questions are sampled from :data:`~app.tech_life_data.TECH_LIFE_QUESTIONS`
    according to the category weights defined for *persona_key*.  If the key
    is unrecognised the ``default`` persona is used (equal weights).

    Args:
        persona_key: A persona identifier string (e.g. ``"backend_engineer"``).

    Returns:
        A 25-element list of :class:`~app.models.BingoSquareData` with the
        centre square pre-marked as FREE SPACE.
    """
    persona = resolve_persona(persona_key)
    weights = PERSONA_WEIGHTS[persona]
    counts = _distribute_counts(weights, _NON_FREE_SQUARES)

    sampled: list[str] = []
    for cat, n in counts.items():
        pool = TECH_LIFE_QUESTIONS[cat]
        draw = min(n, len(pool))
        sampled.extend(random.sample(pool, draw))

    # If rounding caused us to land short, top up from any remaining questions
    if len(sampled) < _NON_FREE_SQUARES:
        used = set(sampled)
        extras: list[str] = [
            q
            for cat_pool in TECH_LIFE_QUESTIONS.values()
            for q in cat_pool
            if q not in used
        ]
        needed = _NON_FREE_SQUARES - len(sampled)
        sampled.extend(random.sample(extras, min(needed, len(extras))))

    random.shuffle(sampled)
    questions = iter(sampled)
    return [
        BingoSquareData(id=i, text=FREE_SPACE, is_marked=True, is_free_space=True)
        if i == CENTER_INDEX
        else BingoSquareData(id=i, text=next(questions))
        for i in range(BOARD_SIZE * BOARD_SIZE)
    ]


def toggle_square(
    board: list[BingoSquareData], square_id: int
) -> list[BingoSquareData]:
    """Toggle a square's marked state. Returns a new board list."""
    return [
        sq.model_copy(update={"is_marked": not sq.is_marked})
        if sq.id == square_id and not sq.is_free_space
        else sq
        for sq in board
    ]


@functools.cache
def _get_winning_lines() -> tuple[BingoLine, ...]:
    """Get all possible winning lines (cached)."""
    lines: list[BingoLine] = []

    for row in range(BOARD_SIZE):
        squares = [row * BOARD_SIZE + col for col in range(BOARD_SIZE)]
        lines.append(BingoLine(type="row", index=row, squares=squares))

    for col in range(BOARD_SIZE):
        squares = [row * BOARD_SIZE + col for row in range(BOARD_SIZE)]
        lines.append(BingoLine(type="column", index=col, squares=squares))

    lines.append(BingoLine(type="diagonal", index=0, squares=[0, 6, 12, 18, 24]))
    lines.append(BingoLine(type="diagonal", index=1, squares=[4, 8, 12, 16, 20]))

    return tuple(lines)


def check_bingo(board: list[BingoSquareData]) -> BingoLine | None:
    """Check if there's a bingo and return the winning line."""
    if len(board) < BOARD_SIZE * BOARD_SIZE:
        return None
    return next(
        (
            line
            for line in _get_winning_lines()
            if all(board[idx].is_marked for idx in line.squares)
        ),
        None,
    )


def get_winning_square_ids(line: BingoLine | None) -> set[int]:
    """Get the square IDs that are part of a winning line."""
    return set(line.squares) if line else set()
