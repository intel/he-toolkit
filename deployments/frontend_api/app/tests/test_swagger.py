from openapi_spec_validator import validate_spec_url


def test_swagger_specification(host):
    endpoint = f"{host}/api/docs/swagger.json"
    validate_spec_url(endpoint)
