"""Tests for the terminal /cmd endpoint."""


def test_cmd_ajuda(client):
    resp = client.post("/cmd", json={"comando": "ajuda"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "Comandos disponíveis" in data["resposta"]


def test_cmd_listar_sabores(client):
    resp = client.post("/cmd", json={"comando": "listar sabores"})
    assert resp.status_code == 200
    assert "Chocolate" in resp.get_json()["resposta"]


def test_cmd_status(client):
    resp = client.post("/cmd", json={"comando": "status"})
    assert resp.status_code == 200
    assert "Status do Sistema" in resp.get_json()["resposta"]


def test_cmd_add_sabor(client):
    resp = client.post("/cmd", json={"comando": "add sabor TestCMD 7.77"})
    assert resp.status_code == 200
    assert "TestCMD" in resp.get_json()["resposta"]


def test_cmd_invalid_command(client):
    resp = client.post("/cmd", json={"comando": "xyz_unknown_cmd"})
    assert resp.status_code == 200
    assert "não reconhecido" in resp.get_json()["resposta"]


def test_cmd_missing_body(client):
    resp = client.post("/cmd", json={})
    assert resp.status_code == 400


def test_cmd_non_string_comando(client):
    resp = client.post("/cmd", json={"comando": 123})
    assert resp.status_code == 400


def test_cmd_too_long(client):
    resp = client.post("/cmd", json={"comando": "a" * 501})
    assert resp.status_code == 400


def test_cmd_ver_estoque(client):
    resp = client.post("/cmd", json={"comando": "ver estoque"})
    assert resp.status_code == 200


def test_cmd_fazer_pedido(client):
    resp = client.post("/cmd", json={"comando": "fazer pedido Chocolate 1"})
    assert resp.status_code == 200
    data = resp.get_json()["resposta"]
    assert "Pedido registrado" in data or "Estoque" in data


def test_cmd_add_sabor_invalid_preco(client):
    resp = client.post("/cmd", json={"comando": "add sabor Teste abc"})
    assert resp.status_code == 200
    assert "inválido" in resp.get_json()["resposta"].lower()


def test_cmd_remover_sabor_not_found(client):
    resp = client.post("/cmd", json={"comando": "remover sabor 999999"})
    assert resp.status_code == 200
    assert "não encontrado" in resp.get_json()["resposta"]
