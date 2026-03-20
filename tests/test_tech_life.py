"""Tests for Tech Life Bingo persona/category selection."""

import pytest

from app.game_logic import generate_board_for_persona
from app.tech_life_data import (
    PERSONA_WEIGHTS,
    TECH_LIFE_QUESTIONS,
    BoardPersona,
    TechLifeCategory,
    resolve_persona,
)


class TestResolvePersona:
    def test_valid_persona_default(self) -> None:
        assert resolve_persona("default") == BoardPersona.DEFAULT

    def test_valid_persona_backend(self) -> None:
        assert resolve_persona("backend_engineer") == BoardPersona.BACKEND_ENGINEER

    def test_valid_persona_frontend(self) -> None:
        assert resolve_persona("frontend_engineer") == BoardPersona.FRONTEND_ENGINEER

    def test_valid_persona_tooling(self) -> None:
        assert resolve_persona("tooling_devops") == BoardPersona.TOOLING_DEVOPS

    def test_invalid_persona_falls_back_to_default(self) -> None:
        assert resolve_persona("unknown_role") == BoardPersona.DEFAULT

    def test_empty_string_falls_back_to_default(self) -> None:
        assert resolve_persona("") == BoardPersona.DEFAULT

    def test_case_insensitive(self) -> None:
        assert resolve_persona("BACKEND_ENGINEER") == BoardPersona.BACKEND_ENGINEER

    def test_garbage_value_falls_back_to_default(self) -> None:
        assert resolve_persona("🤖") == BoardPersona.DEFAULT


class TestPersonaWeights:
    def test_all_personas_have_weights(self) -> None:
        for persona in BoardPersona:
            assert persona in PERSONA_WEIGHTS

    def test_all_categories_present_in_weights(self) -> None:
        for persona, weights in PERSONA_WEIGHTS.items():
            for cat in TechLifeCategory:
                assert cat in weights, (
                    f"Category {cat!r} missing from persona {persona!r}"
                )

    def test_weights_are_positive(self) -> None:
        for persona, weights in PERSONA_WEIGHTS.items():
            for cat, w in weights.items():
                assert w > 0, (
                    f"Weight for {cat!r} in {persona!r} must be positive"
                )


class TestTechLifeQuestions:
    def test_all_categories_have_questions(self) -> None:
        for cat in TechLifeCategory:
            assert cat in TECH_LIFE_QUESTIONS
            assert len(TECH_LIFE_QUESTIONS[cat]) >= 15, (
                f"Category {cat!r} has fewer than 15 questions"
            )

    def test_no_duplicate_questions_within_category(self) -> None:
        for cat, questions in TECH_LIFE_QUESTIONS.items():
            assert len(questions) == len(set(questions)), (
                f"Duplicate questions found in category {cat!r}"
            )


class TestGenerateBoardForPersona:
    def test_board_has_25_squares(self) -> None:
        board = generate_board_for_persona("default")
        assert len(board) == 25

    def test_center_is_free_space(self) -> None:
        from app.game_logic import CENTER_INDEX

        board = generate_board_for_persona("default")
        center = board[CENTER_INDEX]
        assert center.is_free_space is True
        assert center.is_marked is True

    def test_non_center_squares_not_free(self) -> None:
        from app.game_logic import CENTER_INDEX

        board = generate_board_for_persona("backend_engineer")
        for i, sq in enumerate(board):
            if i != CENTER_INDEX:
                assert sq.is_free_space is False
                assert sq.is_marked is False

    def test_no_duplicate_questions_on_board(self) -> None:
        board = generate_board_for_persona("frontend_engineer")
        texts = [sq.text for sq in board if not sq.is_free_space]
        assert len(texts) == len(set(texts))

    def test_all_questions_from_tech_life_pool(self) -> None:
        all_questions = {q for qs in TECH_LIFE_QUESTIONS.values() for q in qs}
        board = generate_board_for_persona("tooling_devops")
        for sq in board:
            if not sq.is_free_space:
                assert sq.text in all_questions

    def test_invalid_persona_produces_valid_board(self) -> None:
        """An unrecognised persona key should not raise; falls back to default."""
        board = generate_board_for_persona("nonexistent_persona")
        assert len(board) == 25

    def test_squares_have_sequential_ids(self) -> None:
        board = generate_board_for_persona("backend_engineer")
        for i, sq in enumerate(board):
            assert sq.id == i

    @pytest.mark.parametrize("persona", list(BoardPersona))
    def test_all_valid_personas_generate_full_board(
        self, persona: BoardPersona
    ) -> None:
        board = generate_board_for_persona(persona)
        assert len(board) == 25
        non_free = [sq for sq in board if not sq.is_free_space]
        assert len(non_free) == 24

    def test_backend_persona_biased_toward_coding_habits(self) -> None:
        """Backend engineer boards should have more coding_habits questions."""
        coding_habits_questions = set(
            TECH_LIFE_QUESTIONS[TechLifeCategory.CODING_HABITS]
        )
        # Run several boards and check coding_habits is most represented
        counts: list[int] = []
        for _ in range(10):
            board = generate_board_for_persona("backend_engineer")
            n = sum(
                1
                for sq in board
                if not sq.is_free_space and sq.text in coding_habits_questions
            )
            counts.append(n)
        # On average, coding_habits should be the largest category (weight 3/6)
        avg = sum(counts) / len(counts)
        assert avg >= 8, f"Expected ≥8 coding_habits questions on average, got {avg}"

    def test_frontend_persona_biased_toward_ide_preferences(self) -> None:
        """Frontend engineer boards should have more ide_preferences questions."""
        ide_questions = set(TECH_LIFE_QUESTIONS[TechLifeCategory.IDE_PREFERENCES])
        counts: list[int] = []
        for _ in range(10):
            board = generate_board_for_persona("frontend_engineer")
            n = sum(
                1 for sq in board if not sq.is_free_space and sq.text in ide_questions
            )
            counts.append(n)
        # ide_preferences has weight 3/6 ≈ 50% → expect ≥8 on average
        avg = sum(counts) / len(counts)
        assert avg >= 8, f"Expected ≥8 ide_preferences questions on average, got {avg}"

    def test_tooling_devops_persona_biased_toward_dev_culture(self) -> None:
        """Tooling/DevOps boards should have more dev_culture questions."""
        dev_culture_questions = set(
            TECH_LIFE_QUESTIONS[TechLifeCategory.DEV_CULTURE]
        )
        counts: list[int] = []
        for _ in range(10):
            board = generate_board_for_persona("tooling_devops")
            n = sum(
                1
                for sq in board
                if not sq.is_free_space and sq.text in dev_culture_questions
            )
            counts.append(n)
        # dev_culture has weight 3/6 ≈ 50% → expect ≥8 on average
        avg = sum(counts) / len(counts)
        assert avg >= 8, (
            f"Expected ≥8 dev_culture questions on average, got {avg}"
        )


class TestGameServicePersona:
    def test_start_game_with_persona(self) -> None:
        from app.game_service import GameSession

        session = GameSession()
        session.start_game("backend_engineer")
        assert session.persona == "backend_engineer"
        assert len(session.board) == 25

    def test_start_game_without_persona_uses_classic_questions(self) -> None:
        from app.data import QUESTIONS
        from app.game_service import GameSession

        session = GameSession()
        session.start_game("")
        texts = {sq.text for sq in session.board if not sq.is_free_space}
        assert texts.issubset(set(QUESTIONS))

    def test_reset_clears_persona(self) -> None:
        from app.game_service import GameSession

        session = GameSession()
        session.start_game("frontend_engineer")
        session.reset_game()
        assert session.persona == ""
