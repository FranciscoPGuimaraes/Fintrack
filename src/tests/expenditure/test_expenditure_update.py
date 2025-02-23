import pytest
import requests
from tests.utils.test_utils import (
    BASE_URL,
    register_user,
    add_expenditure,
    update_expenditure,
    generate_random_email,
    generate_random_date,
)

# ------------------------------------------------------------------------------------------------------------

# Tests for the expenditure update endpoint


def test_expenditure_update_missing_email():
    """
    Test that the API returns a 400 status code if the 'email' parameter is missing when trying to update an expenditure.
    """
    data = {
        "type": "Aluguel Atualizado",
        "value": 1600.00,
        "annotation": "Ajuste de aluguel de outubro",
        "date": "2024-10-31",
    }
    response = requests.put(f"{BASE_URL}/update/expenditure", json=data)
    assert (
        response.status_code == 400
    ), f"Expected 400 for missing email parameter, got {response.status_code}"
    json_response = response.json()
    assert "detail" in json_response
    assert "The 'email' parameter is required." in json_response["detail"]


def test_expenditure_update_nonexistent_email():
    """
    Test that the API returns a 404 status code if an attempt is made to update an expenditure with a non-existent email.
    """
    params = {"email": "nonexistent@example.com"}
    data = {
        "type": "Aluguel Atualizado",
        "value": 1600.00,
        "annotation": "Ajuste de aluguel de outubro",
        "date": "2024-10-31",
    }
    response = update_expenditure(params, data)
    assert (
        response.status_code == 404
    ), f"Expected 404 for nonexistent email, got {response.status_code}"
    json_response = response.json()
    assert "detail" in json_response
    assert "Email not found" in json_response["detail"]


def test_expenditure_update_invalid_email_format():
    """
    Test that the API returns a 400 status code if an invalid email format is provided when attempting to update an expenditure.
    """
    params = {"email": "invalidemailformat"}
    data = {
        "type": "Aluguel Atualizado",
        "value": 1600.00,
        "annotation": "Ajuste de aluguel de outubro",
        "date": "2024-10-31",
    }
    response = update_expenditure(params, data)
    assert (
        response.status_code == 400
    ), f"Expected 400 for invalid email format, got {response.status_code}"
    json_response = response.json()
    assert "detail" in json_response
    assert (
        "The email must be in the format 'name@domain.com' or 'name@domain.br'."
        in json_response["detail"]
    )


def test_expenditure_update_success():
    """
    Test successful update of an expenditure after registering a user and adding an expenditure entry.
    """
    # Register a user to test update of expenditures
    email = generate_random_email()
    register_data = {
        "name": "Test User",
        "email": email,
        "password": "senha123",
    }
    register_response = register_user(register_data)
    assert (
        register_response.status_code == 200
    ), "User registration failed during expenditure update test."

    # Add expenditure data for updating
    date = generate_random_date()
    data = {
        "email_id": email,
        "item_type": "Supermarket",
        "value": 200.00,
        "annotation": "October purchase",
        "date": date,
    }
    add_response = add_expenditure(data)
    assert (
        add_response.status_code == 200
    ), f"Expected 200, got {add_response.status_code}"

    # Update expenditure
    update_data = {
        "type": "Aluguel Atualizado",
        "value": 1600.00,
        "annotation": "Ajuste de aluguel de outubro",
        "date": date,
    }
    params = {"email": email}
    response = update_expenditure(params, update_data)
    assert (
        response.status_code == 200
    ), f"Expected 200 for successful expenditure update, got {response.status_code}"
    json_response = response.json()
    assert json_response["message"] == "Expenditure updated successfully!"


@pytest.mark.parametrize("method", ["post", "delete", "get", "patch"])
def test_expenditure_update_disallowed_methods(method):
    """
    Test that the API returns a 405 status code for HTTP methods that are not allowed for the update expenditure endpoint.
    """
    response = getattr(requests, method)(f"{BASE_URL}/update/expenditure")
    assert (
        response.status_code == 405
    ), f"Expected 405 for {method.upper()}, got {response.status_code}"
    json_response = response.json()
    assert "detail" in json_response
    assert "Method Not Allowed" in json_response["detail"]
