import requests


def test_users_get_users(api_v1_host):
    endpoint = f"{api_v1_host}/users"
    print(endpoint)
    response = requests.get(endpoint)
    assert response.status_code == 200
    json = response.json()
    assert "result" in json
    assert json["result"] == ["user1", "user2"]
