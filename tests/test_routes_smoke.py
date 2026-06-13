from Arina.app import app


def test_main_pages_are_available():
    client = app.test_client()

    urls = [
        "/",
        "/subjects?student=Арина",
        "/math?student=Арина",
        "/russian?student=Арина",
        "/english/menu?student=Арина",
        "/diary?student=Арина",
    ]

    for url in urls:
        response = client.get(url)
        assert response.status_code == 200, f"{url} returned {response.status_code}"


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
