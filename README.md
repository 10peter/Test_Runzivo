# Runzivo CI/CD Testing

A small Flask application for testing CI workflows.

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

## Run tests

```bash
python -m pytest -v
```

The [Python Application Tests workflow](.github/workflows/python-test.yml) runs these tests on pushes to `main`. You can also start it manually.

The [Runzivo workflow](.github/workflows/runzivo.yml) is manual and prints a readiness message on a Runzivo runner.
