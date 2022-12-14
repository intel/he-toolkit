import requests


def test_jobs_get_jobs(api_v1_host):
    endpoint = f"{api_v1_host}/jobs"
    response = requests.get(endpoint)
    assert response.status_code == 200
    json = response.json()
    assert "result" in json
    assert json["result"] == ["job1", "job2"]
