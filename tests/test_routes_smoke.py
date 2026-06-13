from Arina.app import app


def test_main_pages_are_available():
    client = app.test_client()

    urls = [
        "/",
        "/subjects?student=Арина",
        "/math?student=Арина",
        "/math/class/1?student=Арина",
        "/math/class/2?student=Арина",
        "/math/class/3?student=Арина",
        "/math/class/11?student=Арина",
        "/math/learning?class=1&student=Арина",
        "/math/learning/topic/number_composition?student=Арина",
        "/math/test_setup?student=Арина&class=1&type=number_composition",
        "/math/test_setup?student=Арина&class=2",
        "/math/test_setup?student=Арина&class=3",
        "/russian?student=Арина",
        "/russian/class/1?student=Арина",
        "/russian/class/2?student=Арина",
        "/russian/class/3?student=Арина",
        "/russian/class/11?student=Арина",
        "/russian/learning?class=1&student=Арина",
        "/russian/learning/topic/vowels?student=Арина",
        "/russian/test_setup?student=Арина&class=1&type=vowels",
        "/russian/test_setup?student=Арина&class=2",
        "/russian/test_setup?student=Арина&class=3",
        "/english/menu?student=Арина",
        "/diary?student=Арина",
    ]

    for url in urls:
        response = client.get(url)
        assert response.status_code == 200, f"{url} returned {response.status_code}"


def test_all_math_class_pages_are_available():
    client = app.test_client()

    for class_num in range(1, 12):
        response = client.get(f"/math/class/{class_num}?student=Арина")
        assert response.status_code == 200, f"class {class_num} returned {response.status_code}"


def test_all_russian_class_pages_are_available():
    client = app.test_client()

    for class_num in range(1, 12):
        response = client.get(f"/russian/class/{class_num}?student=Арина")
        assert response.status_code == 200, f"class {class_num} returned {response.status_code}"


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


def test_russian_class_1_topic_task_api():
    client = app.test_client()

    response = client.post(
        "/russian/generate_task",
        json={
            "class": "1",
            "topic": "vowels",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["topic"] == "vowels"
    assert data["question"]
    assert "correct" in data
    assert data["answer_type"] in {"number", "choice", "text"}


def test_russian_class_1_topic_check_answer_api():
    client = app.test_client()

    response = client.post(
        "/russian/check_task",
        json={
            "answer": "звук",
            "correct": "звук",
            "answer_type": "choice",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["result"] == "correct"


def test_class_2_and_3_example_api_still_work():
    client = app.test_client()

    for class_num in [2, 3]:
        response = client.post(
            "/generate_example",
            json={
                "class": str(class_num),
                "type": "all",
                "table_num": "all",
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "correct" in data


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
