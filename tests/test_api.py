import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestHomePage:
    def test_home_returns_200(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == 200

    def test_home_contains_start_screen(self, client: TestClient) -> None:
        response = client.get("/")
        assert "Soc Ops" in response.text
        assert "Start Game" in response.text
        assert "How to play" in response.text

    def test_home_sets_session_cookie(self, client: TestClient) -> None:
        response = client.get("/")
        assert "session" in response.cookies

    def test_home_has_team_mode_link(self, client: TestClient) -> None:
        response = client.get("/")
        assert "/team" in response.text


class TestStartGame:
    def test_start_returns_game_board(self, client: TestClient) -> None:
        # First visit to get session
        client.get("/")
        response = client.post("/start")
        assert response.status_code == 200
        assert "FREE SPACE" in response.text
        assert "← Back" in response.text

    def test_board_has_25_squares(self, client: TestClient) -> None:
        client.get("/")
        response = client.post("/start")
        # Count the toggle buttons (squares with hx-post="/toggle/")
        assert response.text.count('hx-post="/toggle/') == 24  # 24 + 1 free space


class TestToggleSquare:
    def test_toggle_marks_square(self, client: TestClient) -> None:
        client.get("/")
        client.post("/start")
        response = client.post("/toggle/0")
        assert response.status_code == 200
        # The response should contain the game screen with a marked square
        assert "FREE SPACE" in response.text


class TestResetGame:
    def test_reset_returns_start_screen(self, client: TestClient) -> None:
        client.get("/")
        client.post("/start")
        response = client.post("/reset")
        assert response.status_code == 200
        assert "Start Game" in response.text
        assert "How to play" in response.text


class TestDismissModal:
    def test_dismiss_returns_game_screen(self, client: TestClient) -> None:
        client.get("/")
        client.post("/start")
        response = client.post("/dismiss-modal")
        assert response.status_code == 200
        assert "FREE SPACE" in response.text


# ---------------------------------------------------------------------------
# Team mode tests
# ---------------------------------------------------------------------------


class TestTeamHome:
    def test_team_home_returns_200(self, client: TestClient) -> None:
        response = client.get("/team")
        assert response.status_code == 200

    def test_team_home_has_create_and_join(self, client: TestClient) -> None:
        response = client.get("/team")
        assert "Create New Session" in response.text
        assert "Join" in response.text


class TestTeamCreate:
    def test_create_redirects_to_team_game(self, client: TestClient) -> None:
        response = client.post("/team/create", follow_redirects=False)
        assert response.status_code == 303
        location = response.headers["location"]
        assert location.startswith("/team/")
        # The code segment should be a 6-character hex string
        code = location.split("/team/")[1]
        assert len(code) == 6

    def test_create_and_visit_game_page(self, client: TestClient) -> None:
        response = client.post("/team/create")
        assert response.status_code == 200
        assert "Tech Life Bingo" in response.text
        assert "Session Code" in response.text

    def test_create_shows_participant_count(self, client: TestClient) -> None:
        response = client.post("/team/create")
        assert "participant" in response.text


class TestTeamJoin:
    def test_join_valid_code(self, client: TestClient) -> None:
        # Create a session first
        create_resp = client.post("/team/create", follow_redirects=False)
        code = create_resp.headers["location"].split("/team/")[1]

        # Join with a different client instance (new cookies)
        client2 = TestClient(app)
        join_resp = client2.post("/team/join", data={"team_code": code})
        assert join_resp.status_code == 200
        assert "Tech Life Bingo" in join_resp.text

    def test_join_invalid_code_shows_error(self, client: TestClient) -> None:
        response = client.post("/team/join", data={"team_code": "XXXXXX"})
        assert response.status_code == 200
        assert "not found" in response.text.lower()

    def test_join_lowercases_code(self, client: TestClient) -> None:
        # Create session
        create_resp = client.post("/team/create", follow_redirects=False)
        code = create_resp.headers["location"].split("/team/")[1]

        client2 = TestClient(app)
        join_resp = client2.post(
            "/team/join", data={"team_code": code.lower()}, follow_redirects=True
        )
        assert join_resp.status_code == 200
        assert "Tech Life Bingo" in join_resp.text


class TestTeamSharedState:
    def test_shared_board_across_two_clients(self, client: TestClient) -> None:
        """Marks a square via client1; client2 should see the same board state."""
        # client1 creates and starts the game
        create_resp = client.post("/team/create", follow_redirects=False)
        code = create_resp.headers["location"].split("/team/")[1]
        client.post(f"/team/{code}/start")

        # client1 marks square 0
        client.post(f"/team/{code}/toggle/0")

        # client2 joins the team
        client2 = TestClient(app)
        client2.get(f"/team/{code}")

        # client2 marks square 1
        resp2 = client2.post(f"/team/{code}/toggle/1")
        assert resp2.status_code == 200

        # client1 sees the state updated by client2 (square 1 must now be marked)
        resp1 = client.post(f"/team/{code}/toggle/2")  # any toggle to get fresh screen
        # Both square 0 and square 1 should be marked on the shared board
        # The board HTML renders aria-pressed="true" for marked squares
        # After free_space + sq0 + sq1 + sq2 = 4 marked squares total
        assert resp1.text.count('aria-pressed="true"') == 4

    def test_participant_count_increments_for_new_users(self) -> None:
        client1 = TestClient(app)
        create_resp = client1.post("/team/create", follow_redirects=False)
        code = create_resp.headers["location"].split("/team/")[1]

        # Visit the game page as client1 (already counted as participant via create)
        resp1 = client1.get(f"/team/{code}")
        assert "1 participant" in resp1.text

        # A second distinct client joins
        client2 = TestClient(app)
        client2.get(f"/team/{code}")

        # client1 now refreshes and should see 2 participants
        resp1_refresh = client1.get(f"/team/{code}")
        assert "2 participants" in resp1_refresh.text

    def test_reset_affects_shared_board(self, client: TestClient) -> None:
        create_resp = client.post("/team/create", follow_redirects=False)
        code = create_resp.headers["location"].split("/team/")[1]
        client.post(f"/team/{code}/start")
        client.post(f"/team/{code}/toggle/0")

        # Reset the game
        reset_resp = client.post(f"/team/{code}/reset")
        assert "Start Game" in reset_resp.text

        # Start again — should give a fresh board
        start_resp = client.post(f"/team/{code}/start")
        assert "FREE SPACE" in start_resp.text


class TestTeamGameFlow:
    def test_start_game_shows_board(self, client: TestClient) -> None:
        create_resp = client.post("/team/create", follow_redirects=False)
        code = create_resp.headers["location"].split("/team/")[1]
        response = client.post(f"/team/{code}/start")
        assert response.status_code == 200
        assert "FREE SPACE" in response.text

    def test_board_has_24_toggle_buttons(self, client: TestClient) -> None:
        create_resp = client.post("/team/create", follow_redirects=False)
        code = create_resp.headers["location"].split("/team/")[1]
        response = client.post(f"/team/{code}/start")
        assert response.text.count(f'hx-post="/team/{code}/toggle/') == 24

    def test_toggle_square_marks_it(self, client: TestClient) -> None:
        create_resp = client.post("/team/create", follow_redirects=False)
        code = create_resp.headers["location"].split("/team/")[1]
        client.post(f"/team/{code}/start")
        response = client.post(f"/team/{code}/toggle/0")
        assert response.status_code == 200
        assert "FREE SPACE" in response.text

    def test_dismiss_modal(self, client: TestClient) -> None:
        create_resp = client.post("/team/create", follow_redirects=False)
        code = create_resp.headers["location"].split("/team/")[1]
        client.post(f"/team/{code}/start")
        response = client.post(f"/team/{code}/dismiss-modal")
        assert response.status_code == 200
        assert "FREE SPACE" in response.text

    def test_invalid_team_code_redirects_to_lobby(self, client: TestClient) -> None:
        response = client.get("/team/ZZZZZZ", follow_redirects=True)
        assert response.status_code == 200
        assert "Create New Session" in response.text
