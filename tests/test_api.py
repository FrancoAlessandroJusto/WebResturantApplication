from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_ingredienti():
    # ensure endpoint returns a list and status 200
    response = client.get("/ingredienti")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # items should have id and nome keys
    if data:
        item = data[0]
        assert "id" in item and "nome" in item


def test_create_and_delete_ingrediente():
    # create a new ingredient
    new_name = "test_ing_123"
    response = client.post("/ingredienti", json={"nome": new_name})
    assert response.status_code == 200
    created = response.json()
    assert created["nome"] == new_name
    assert "id" in created

    ing_id = created["id"]
    # delete the ingredient
    del_resp = client.delete(f"/ingredienti/{ing_id}")
    assert del_resp.status_code == 200
    assert "message" in del_resp.json()

    # subsequent GET should not include it
    response2 = client.get("/ingredienti")
    assert response2.status_code == 200
    assert all(ing["id"] != ing_id for ing in response2.json())
