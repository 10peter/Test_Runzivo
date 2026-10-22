import heapq

from flask import Flask, jsonify, request

app = Flask(__name__)


def bad_request(message):
    return jsonify({"error": message}), 400


def validate_jobs(payload):
    if not isinstance(payload, dict) or set(payload) != {"jobs"}:
        return None, "Request body must be an object with a jobs field."

    jobs = payload["jobs"]
    if not isinstance(jobs, list) or not jobs:
        return None, "jobs must be a non-empty list."

    by_id = {}
    for job in jobs:
        if not isinstance(job, dict) or set(job) != {"id", "needs", "minutes"}:
            return None, "Each job must contain only id, needs, and minutes."

        job_id = job["id"]
        needs = job["needs"]
        minutes = job["minutes"]
        if not isinstance(job_id, str) or not job_id:
            return None, "Each job id must be a non-empty string."
        if job_id in by_id:
            return None, f"Duplicate job id: {job_id}."
        if not isinstance(needs, list) or any(
            not isinstance(dependency, str) or not dependency for dependency in needs
        ):
            return None, f"needs for {job_id} must be a list of non-empty strings."
        if len(needs) != len(set(needs)):
            return None, f"needs for {job_id} must not contain duplicates."
        if isinstance(minutes, bool) or not isinstance(minutes, int) or minutes < 0:
            return None, f"minutes for {job_id} must be a non-negative integer."

        by_id[job_id] = {"needs": needs, "minutes": minutes}

    for job_id, job in by_id.items():
        for dependency in job["needs"]:
            if dependency not in by_id:
                return None, f"Job {job_id} depends on missing job: {dependency}."

    return by_id, None


def make_plan(jobs):
    positions = {job_id: position for position, job_id in enumerate(jobs)}
    indegree = {job_id: len(job["needs"]) for job_id, job in jobs.items()}
    dependents = {job_id: [] for job_id in jobs}
    for job_id, job in jobs.items():
        for dependency in job["needs"]:
            dependents[dependency].append(job_id)

    ready = [(positions[job_id], job_id) for job_id, count in indegree.items() if count == 0]
    heapq.heapify(ready)
    order = []
    critical_path = {}

    while ready:
        _, job_id = heapq.heappop(ready)
        job = jobs[job_id]
        critical_path[job_id] = job["minutes"] + max(
            (critical_path[dependency] for dependency in job["needs"]), default=0
        )
        order.append(job_id)

        for dependent in dependents[job_id]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(ready, (positions[dependent], dependent))

    if len(order) != len(jobs):
        return None

    return {
        "order": order,
        "total_minutes": sum(job["minutes"] for job in jobs.values()),
        "critical_path_minutes": max(critical_path.values()),
    }

@app.route("/")
def home():
    return "Welcome to Runzivo CI/CD Testing!"

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.post("/plan")
def plan():
    payload = request.get_json(silent=True)
    jobs, error = validate_jobs(payload)
    if error:
        return bad_request(error)

    result = make_plan(jobs)
    if result is None:
        return bad_request("Job dependencies contain a cycle.")
    return jsonify(result), 200

if __name__ == "__main__":
    app.run()
