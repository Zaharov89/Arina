import pytest


class DummySession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def dummy_session_factory():
    return DummySession()


class FakeReferenceDataRepository:
    def __init__(self, session):
        self.session = session

    def get_subjects(self):
        return [{"id": 1, "code": "math", "title": "Математика", "is_active": True}]

    def get_school_classes(self):
        return [{"id": 1, "class_number": 1, "title": "1 класс"}]

    def get_topics(self, subject_code=None, class_number=None):
        return [
            {
                "id": 1,
                "subject_id": 1,
                "subject_code": subject_code or "math",
                "subject_title": "Математика",
                "class_number": class_number or 1,
                "code": "counting",
                "title": "Счёт предметов",
                "is_active": True,
            }
        ]


@pytest.fixture(autouse=True)
def patch_reference_data(monkeypatch):
    import Arina.database.routes as database_routes
    import Arina.backend.routes.vocabulary_api as vocabulary_api

    monkeypatch.setattr(database_routes, "get_session_factory", lambda: dummy_session_factory)
    monkeypatch.setattr(database_routes, "ReferenceDataRepository", FakeReferenceDataRepository)
    monkeypatch.setattr(vocabulary_api, "get_session_factory", lambda: dummy_session_factory)
    monkeypatch.setattr(
        vocabulary_api,
        "get_russian_vocabulary_words",
        lambda session, class_number=None: [{"id": 1, "class_number": class_number or 1, "word": "ворона", "answer": "ворона", "is_active": True}],
    )
    monkeypatch.setattr(
        vocabulary_api,
        "get_english_vocabulary_words",
        lambda session, class_number=None: [
            {"id": 1, "class_number": class_number or 2, "en": ["Sheep"], "ru": ["Овца"], "transcription": ["[ʃiːp]"], "is_active": True}
        ],
    )


def test_database_subjects_smoke(client):
    response = client.get("/database/subjects")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_database_school_classes_smoke(client):
    response = client.get("/database/school-classes")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_database_topics_smoke(client):
    response = client.get("/database/topics?subject_code=math&class_number=1")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_russian_vocabulary_smoke(client):
    response = client.get("/api/russian/vocabulary?class_number=1")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_english_vocabulary_smoke(client):
    response = client.get("/api/english/vocabulary?class_number=2")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_stats_without_token_returns_401(client):
    response = client.get("/api/stats")
    assert response.status_code == 401
    assert response.get_json()["status"] == "unauthorized"


def test_save_test_attempt_without_token_returns_401(client):
    response = client.post(
        "/api/test-attempts",
        json={
            "subject_code": "math",
            "class_number": 1,
            "topic_code": "counting",
            "total_questions": 1,
            "correct_answers": 1,
            "wrong_answers": 0,
            "empty_answers": 0,
            "score_percent": 100,
        },
    )
    assert response.status_code == 401
    assert response.get_json()["status"] == "unauthorized"


def test_auth_me_without_token_returns_401(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.get_json()["status"] == "unauthorized"


def test_legacy_save_result_removed(client):
    response = client.post("/api/save_result", json={})
    assert response.status_code == 404
