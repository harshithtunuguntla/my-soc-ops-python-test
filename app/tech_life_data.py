"""Tech Life Bingo: category-based question pools and persona presets.

Personas bias which categories of questions appear more frequently on the board.
To select a persona when starting a game, pass ``?persona=<key>`` to the
``POST /start`` endpoint (or choose from the dropdown on the start screen).

Available persona keys:
    - ``default``           – equal mix of all three categories
    - ``backend_engineer``  – heavy coding habits (weight 3), moderate dev
                              culture (weight 2), light IDE preferences (weight 1)
    - ``frontend_engineer`` – heavy IDE/tooling (weight 3), moderate coding
                              habits (weight 2), light dev culture (weight 1)
    - ``tooling_devops``    – heavy dev culture (weight 3), moderate IDE
                              preferences (weight 2), light coding habits (weight 1)

If an unrecognised value is provided the server falls back to ``default``.

Trade-off note
--------------
Increased flexibility: boards feel tailored to a player's role; engineers can
relate to the questions more readily, improving engagement.

Added complexity: the additional data module and weighted-sampling logic mean
there is more surface area to maintain.  Category question pools must each
contain enough questions (≥ 15 is recommended) so that the board generator
never runs out of unique items even for heavily weighted personas.
"""

from enum import StrEnum
from typing import Final


class TechLifeCategory(StrEnum):
    """Categories for Tech Life Bingo questions."""

    CODING_HABITS = "coding_habits"
    IDE_PREFERENCES = "ide_preferences"
    DEV_CULTURE = "dev_culture"


class BoardPersona(StrEnum):
    """Persona presets that bias category weights on the board."""

    DEFAULT = "default"
    BACKEND_ENGINEER = "backend_engineer"
    FRONTEND_ENGINEER = "frontend_engineer"
    TOOLING_DEVOPS = "tooling_devops"


# ---------------------------------------------------------------------------
# Question pools (≥ 20 per category for comfortable sampling)
# ---------------------------------------------------------------------------

TECH_LIFE_QUESTIONS: Final[dict[TechLifeCategory, list[str]]] = {
    TechLifeCategory.CODING_HABITS: [
        "has committed directly to main",
        "writes tests before code (TDD)",
        "has a consistent naming convention",
        "refactors code regularly",
        "has pair-programmed before",
        "uses linters in every project",
        "has debug-printed today",
        "has copy-pasted code from Stack Overflow",
        "has pushed a 'WIP' commit",
        "writes code after midnight",
        "has skipped writing documentation",
        "keeps a coding to-do list",
        "uses keyboard shortcuts for everything",
        "has written a one-liner they're proud of",
        "reads code before writing it",
        "has deleted commented-out code this week",
        "has written a function longer than 200 lines",
        "prefers tabs over spaces",
        "has accidentally broken the build",
        "reviews their own PR before merging",
    ],
    TechLifeCategory.IDE_PREFERENCES: [
        "uses VS Code as primary editor",
        "has more than 10 IDE extensions installed",
        "uses Vim or Neovim",
        "uses a dark IDE theme",
        "memorizes keyboard shortcuts",
        "has customised their editor font",
        "uses AI coding assistant (Copilot etc.)",
        "has multiple editor panes open at once",
        "uses a terminal inside the IDE",
        "switches between editors regularly",
        "has a saved snippets library",
        "uses split panes for coding",
        "prefers minimal IDE plugins",
        "has a custom keybinding setup",
        "uses JetBrains IDEs",
        "runs tests from within the IDE",
        "has configured linter integration",
        "customises the IDE theme per project",
        "uses tab autocomplete heavily",
        "uses Emacs",
    ],
    TechLifeCategory.DEV_CULTURE: [
        "attends or watches tech conferences",
        "contributes to open source projects",
        "has a tech blog or newsletter",
        "uses Slack or Discord for dev communities",
        "has reviewed a pull request today",
        "participates in code reviews regularly",
        "prefers async communication over meetings",
        "has given a tech talk",
        "reads documentation before asking for help",
        "follows tech influencers on social media",
        "has mentored a junior developer",
        "subscribes to a tech podcast",
        "has attended a hackathon",
        "cares about accessibility in products",
        "has taken an online certification",
        "argues about tabs vs spaces",
        "has starred more than 50 repos on GitHub",
        "uses personal kanban or TODO apps",
        "knows the difference between Docker and a VM",
        "has broken production at least once",
    ],
}

# ---------------------------------------------------------------------------
# Persona weights – relative frequency of each category on the board
# ---------------------------------------------------------------------------

PERSONA_WEIGHTS: Final[dict[BoardPersona, dict[TechLifeCategory, int]]] = {
    BoardPersona.DEFAULT: {
        TechLifeCategory.CODING_HABITS: 1,
        TechLifeCategory.IDE_PREFERENCES: 1,
        TechLifeCategory.DEV_CULTURE: 1,
    },
    BoardPersona.BACKEND_ENGINEER: {
        TechLifeCategory.CODING_HABITS: 3,
        TechLifeCategory.IDE_PREFERENCES: 1,
        TechLifeCategory.DEV_CULTURE: 2,
    },
    BoardPersona.FRONTEND_ENGINEER: {
        TechLifeCategory.CODING_HABITS: 2,
        TechLifeCategory.IDE_PREFERENCES: 3,
        TechLifeCategory.DEV_CULTURE: 1,
    },
    BoardPersona.TOOLING_DEVOPS: {
        TechLifeCategory.CODING_HABITS: 1,
        TechLifeCategory.IDE_PREFERENCES: 2,
        TechLifeCategory.DEV_CULTURE: 3,
    },
}


def resolve_persona(key: str) -> BoardPersona:
    """Return the matching ``BoardPersona``, falling back to ``DEFAULT``.

    Args:
        key: A string persona identifier (case-insensitive).

    Returns:
        The resolved :class:`BoardPersona`, or ``BoardPersona.DEFAULT`` when
        *key* does not match any known persona.
    """
    try:
        return BoardPersona(key.lower())
    except ValueError:
        return BoardPersona.DEFAULT
