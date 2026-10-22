from app import app

def test_homepage():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"Welcome to Runzivo CI/CD Testing!" in response.data


def test_health():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_plan_returns_stable_dependency_order_and_timing():
    client = app.test_client()

    response = client.post(
        "/plan",
        json={
            "jobs": [
                {"id": "package", "needs": ["test"], "minutes": 2},
                {"id": "lint", "needs": [], "minutes": 1},
                {"id": "test", "needs": ["lint"], "minutes": 4},
                {"id": "docs", "needs": [], "minutes": 3},
            ]
        },
    )

    assert response.status_code == 200
    assert response.json == {
        "order": ["lint", "test", "package", "docs"],
        "total_minutes": 10,
        "critical_path_minutes": 7,
    }


def test_plan_rejects_missing_dependency():
    client = app.test_client()

    response = client.post(
        "/plan",
        json={"jobs": [{"id": "deploy", "needs": ["build"], "minutes": 2}]},
    )

    assert response.status_code == 400
    assert response.json == {"error": "Job deploy depends on missing job: build."}


def test_plan_rejects_cycle():
    client = app.test_client()

    response = client.post(
        "/plan",
        json={
            "jobs": [
                {"id": "build", "needs": ["deploy"], "minutes": 2},
                {"id": "deploy", "needs": ["build"], "minutes": 1},
            ]
        },
    )

    assert response.status_code == 400
    assert response.json == {"error": "Job dependencies contain a cycle."}


def test_plan_rejects_malformed_jobs():
    client = app.test_client()

    response = client.post("/plan", json={"jobs": [{"id": "build"}]})

    assert response.status_code == 400
    assert response.json == {
        "error": "Each job must contain only id, needs, and minutes."
    }
