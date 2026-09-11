"""
Threat scenario evaluation tests.
"""

from fastapi.testclient import TestClient

from backend.api.app import app


client = TestClient(app)


SCENARIOS = [
    {
        "name": "SSH Brute Force",
        "query": "failed SSH authentication brute force attack",
        "concepts": [
            ["ssh"],
            ["authentication", "login"],
            ["brute", "brute-force"],
            ["attack", "attempt"],
        ],
    },
    {
        "name": "Privilege Escalation",
        "query": "suspicious sudo privilege escalation activity",
        "concepts": [
            ["sudo"],
            ["privilege"],
            ["escalation"],
        ],
    },
    {
        "name": "Malware Activity",
        "query": "possible malware execution detected in system logs",
        "concepts": [
            ["malware", "malicious"],
            ["execution", "execute", "executing", "code execution"],
        ],
    },
    {
        "name": "SSH Service Exposure",
        "query": "SSH service listening on port 22",
        "concepts": [
            ["ssh", "sshd"],
            ["listening"],
            ["port", "22"],
        ],
    },
    {
        "name": "Repeated Login Failures",
        "query": "repeated failed login attempts",
        "concepts": [
            ["login", "authentication"],
            ["failed", "failure", "failures"],
        ],
    },
]


def _concept_matches(answer, concepts):
    """
    Check whether the answer addresses at least one term
    from every required security concept group.
    """

    answer_lower = answer.lower()

    return all(
        any(
            term.lower() in answer_lower
            for term in concept
        )
        for concept in concepts
    )


def analyse_scenario(scenario):
    response = client.post(
        "/analyze",
        json={"query": scenario["query"]},
    )

    if response.status_code != 200:
        return False, response, ""

    data = response.json()

    if "answer" not in data:
        return False, response, ""

    answer = data["answer"]

    if not isinstance(answer, str):
        return False, response, ""

    if not answer.strip():
        return False, response, ""

    passed = _concept_matches(
        answer,
        scenario["concepts"],
    )

    return passed, response, answer


def test_ssh_brute_force():
    passed, response, answer = analyse_scenario(
        SCENARIOS[0]
    )

    assert response.status_code == 200
    assert passed
    assert answer.strip()


def test_privilege_escalation():
    passed, response, answer = analyse_scenario(
        SCENARIOS[1]
    )

    assert response.status_code == 200
    assert passed
    assert answer.strip()


def test_malware_activity():
    passed, response, answer = analyse_scenario(
        SCENARIOS[2]
    )

    assert response.status_code == 200
    assert passed
    assert answer.strip()


def test_ssh_service_exposure():
    passed, response, answer = analyse_scenario(
        SCENARIOS[3]
    )

    assert response.status_code == 200
    assert passed
    assert answer.strip()


def test_repeated_login_failures():
    passed, response, answer = analyse_scenario(
        SCENARIOS[4]
    )

    assert response.status_code == 200
    assert passed
    assert answer.strip()


if __name__ == "__main__":

    print("=" * 60)
    print("THREAT SCENARIO EVALUATION")
    print("=" * 60)

    passed_count = 0

    for scenario in SCENARIOS:

        passed, response, answer = analyse_scenario(
            scenario
        )

        if passed:
            print(
                f"PASS: {scenario['name']}"
            )
            passed_count += 1
        else:
            print(
                f"FAIL: {scenario['name']}"
            )

    print("=" * 60)

    print(
        f"Evaluation Result: "
        f"{passed_count}/{len(SCENARIOS)} scenarios passed"
    )

    if passed_count == len(SCENARIOS):
        print("THREAT SCENARIO EVALUATION PASSED")
    else:
        print("THREAT SCENARIO EVALUATION FAILED")

    print("=" * 60)