# Runzivo CI/CD Testing

This Flask app plans job dependencies and supports unit tests and live HTTP
checks.

## Run locally

Use Python 3.12, as configured in the test workflow:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

The app listens on `http://127.0.0.1:5000` by default.

| Route | Response |
| --- | --- |
| `/` | `Welcome to Runzivo CI/CD Testing!` |
| `/health` | JSON: `{"status":"healthy"}` |
| `POST /plan` | Builds a dependency-safe job plan and estimates its duration. |

## Plan a job graph

Send a JSON object with a non-empty `jobs` list. Each job has a unique string
`id`, a `needs` list containing existing job IDs, and a non-negative integer
`minutes` estimate.

```bash
curl --request POST http://127.0.0.1:5000/plan \
  --header 'Content-Type: application/json' \
  --data '{"jobs":[{"id":"package","needs":["test"],"minutes":2},{"id":"lint","needs":[],"minutes":1},{"id":"test","needs":["lint"],"minutes":4}]}'
```

The response is deterministic. When several jobs are ready, the service uses
their order in the input list to break ties. `total_minutes` sums all work.
`critical_path_minutes` is the total duration of the longest dependency chain,
assuming jobs run in parallel once their dependencies complete.

```json
{
  "critical_path_minutes": 7,
  "order": ["lint", "test", "package"],
  "total_minutes": 7
}
```

Malformed requests, missing dependencies, and dependency cycles return a JSON
error with HTTP 400.

## Run tests

```bash
python -m pytest -v
```

The [Python Application Tests workflow](.github/workflows/python-test.yml) runs these tests on pushes to `main`. You can also start it manually.

You trigger the [Runzivo workflow](.github/workflows/runzivo.yml) manually.
It installs Python dependencies, runs the test suite with a JUnit report,
starts the app, checks both `/health` and `/plan` response bodies, and uploads
the test report and app log as workflow artifacts.
