import json
from socket import timeout as SocketTimeout
from time import sleep
from urllib.error import URLError
from urllib.request import Request, urlopen

REQUEST_TIMEOUT_SECONDS = 2


def get_json(request):
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return response.status, json.load(response)


def get_json_when_ready(request):
    for attempt in range(10):
        try:
            return get_json(request)
        except (SocketTimeout, URLError):
            if attempt == 9:
                raise
            sleep(0.5)


health_status, health_body = get_json_when_ready("http://127.0.0.1:5000/health")
assert health_status == 200
assert health_body == {"status": "healthy"}

plan_request = Request(
    "http://127.0.0.1:5000/plan",
    data=json.dumps(
        {
            "jobs": [
                {"id": "package", "needs": ["test"], "minutes": 2},
                {"id": "lint", "needs": [], "minutes": 1},
                {"id": "test", "needs": ["lint"], "minutes": 4},
            ]
        }
    ).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
plan_status, plan_body = get_json(plan_request)
assert plan_status == 200
assert plan_body == {
    "order": ["lint", "test", "package"],
    "total_minutes": 7,
    "critical_path_minutes": 7,
}
