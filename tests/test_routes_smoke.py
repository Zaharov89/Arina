from Arina.app import app


def test_main_pages_are_available():
    client = app.test_client()

    urls = [
        "/",
        "/subjects?student=Арина",
        "/math?student=Арина",
        "/math/learning?student=Арина",
        "/math/learning/topic/number_composition?student=Арина",
        "/math/test_setup?student=Арина&class=1&type=number_composition",
        "/russian?student=Арина",
        "/english/menu?student=Арина",
        "/diary?student=Арина",
    ]

    for url in urls:
        response = client.get(url)
        assert response.status_code == 200, f"{url} returned {response.status_code}"


def test_class_1_topic_example_api():
    client = app.test_client()

    response = client.post(
        "/generate_example",
        json={
            "class": "1",
            "type": "number_composition",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["topic"] == "number_composition"
    assert data["question"]
    assert "correct" in data
    assert data["answer_type"] in {"number", "choice"}


def test_class_1_topic_check_answer_api():
    client = app.test_client()

    response = client.post(
        "/check_answer",
        json={
            "class": "1",
            "type": "compare_numbers",
            "answer_type": "choice",
            "answer": ">",
            "correct": ">",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["result"] == "correct"


def test_save_result_is_temporarily_disabled_but_available():
    client = app.test_client()

    response = client.post(
        "/api/save_result",
        json={
            "subject": "math",
            "score_percent": 4,
            "studentName": "Арина",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "disabled"


def test_future_architecture_status_routes_are_available():
    client = app.test_client()

    auth_response = client.get("/auth/status")
    database_response = client.get("/database/status")

    assert auth_response.status_code == 200
    assert auth_response.get_json()["module"] == "auth"

    assert database_response.status_code == 200
    assert database_response.get_json()["module"] == "database"
