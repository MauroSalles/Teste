"""
Unit tests for cmd_service.processar_comando.
Each test uses the real database (via conftest fixtures), so the DB must be
running and schema applied (done in CI before pytest is executed).
"""
import pytest
from backend.services.cmd_service import processar_comando
from backend.models.sabor import adicionar_sabor
from backend.models.estoque import definir_estoque


# ---------------------------------------------------------------------------
# ajuda
# ---------------------------------------------------------------------------

def test_ajuda_lists_commands():
    resp = processar_comando("ajuda")
    assert "listar sabores" in resp
    assert "fazer pedido" in resp
    assert "ver estoque" in resp


# ---------------------------------------------------------------------------
# Sabores
# ---------------------------------------------------------------------------

def test_listar_sabores_empty():
    resp = processar_comando("listar sabores")
    assert resp == "Nenhum sabor cadastrado."


def test_add_sabor_success():
    resp = processar_comando("add sabor Chocolate 10.00")
    assert "Chocolate" in resp
    assert "adicionado" in resp


def test_add_sabor_invalid_price():
    resp = processar_comando("add sabor Morango abc")
    assert "inválido" in resp.lower() or "inválido" in resp


def test_add_sabor_negative_price():
    resp = processar_comando("add sabor Limão -5")
    assert "negativo" in resp.lower()


def test_listar_sabores_with_data():
    processar_comando("add sabor Baunilha 8.00")
    resp = processar_comando("listar sabores")
    assert "Baunilha" in resp


def test_atualizar_sabor_success():
    processar_comando("add sabor Morango 9.50")
    resp_lista = processar_comando("listar sabores")
    # Extract ID from the listing output
    for line in resp_lista.splitlines():
        if "Morango" in line:
            sabor_id = int(line.split("|")[0].replace("ID:", "").strip())
            break
    resp = processar_comando(f"atualizar sabor {sabor_id} 11.00")
    assert "11.00" in resp


def test_atualizar_sabor_not_found():
    resp = processar_comando("atualizar sabor 9999 10.00")
    assert "não encontrado" in resp


def test_remover_sabor_success():
    processar_comando("add sabor Pistache 12.00")
    resp_lista = processar_comando("listar sabores")
    for line in resp_lista.splitlines():
        if "Pistache" in line:
            sabor_id = int(line.split("|")[0].replace("ID:", "").strip())
            break
    resp = processar_comando(f"remover sabor {sabor_id}")
    assert "removido" in resp


def test_remover_sabor_not_found():
    resp = processar_comando("remover sabor 9999")
    assert "não encontrado" in resp


def test_remover_sabor_invalid_id():
    resp = processar_comando("remover sabor abc")
    assert "inválido" in resp.lower()


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------

def test_listar_pedidos_empty():
    resp = processar_comando("listar pedidos")
    assert resp == "Nenhum pedido registrado."


def test_fazer_pedido_success():
    processar_comando("add sabor Chocolate 10.00")
    resp = processar_comando("fazer pedido Chocolate 2")
    assert "Chocolate" in resp
    assert "R$" in resp


def test_fazer_pedido_sabor_not_found():
    resp = processar_comando("fazer pedido Inexistente 1")
    assert "não encontrado" in resp


def test_fazer_pedido_invalid_quantity():
    processar_comando("add sabor Morango 9.50")
    resp = processar_comando("fazer pedido Morango abc")
    assert "inválid" in resp.lower()


def test_fazer_pedido_zero_quantity():
    processar_comando("add sabor Limão 9.00")
    resp = processar_comando("fazer pedido Limão 0")
    assert "maior que zero" in resp


def test_fazer_pedido_estoque_insuficiente():
    processar_comando("add sabor Pistache 12.00")
    # Get flavor id and set stock to 1
    from backend.models.sabor import buscar_sabor_por_nome
    sabor = buscar_sabor_por_nome("Pistache")
    definir_estoque(sabor["id"], 1)
    resp = processar_comando("fazer pedido Pistache 5")
    assert "insuficiente" in resp.lower()


def test_listar_pedidos_with_data():
    processar_comando("add sabor Baunilha 8.00")
    processar_comando("fazer pedido Baunilha 3")
    resp = processar_comando("listar pedidos")
    assert "Baunilha" in resp


# ---------------------------------------------------------------------------
# Estoque
# ---------------------------------------------------------------------------

def test_ver_estoque_empty():
    resp = processar_comando("ver estoque")
    assert resp == "Nenhum sabor cadastrado."


def test_set_estoque_success():
    processar_comando("add sabor Chocolate 10.00")
    resp = processar_comando("set estoque Chocolate 50")
    assert "50" in resp


def test_set_estoque_sabor_not_found():
    resp = processar_comando("set estoque Inexistente 10")
    assert "não encontrado" in resp


def test_add_estoque_success():
    processar_comando("add sabor Morango 9.50")
    processar_comando("set estoque Morango 10")
    resp = processar_comando("add estoque Morango 5")
    assert "15" in resp


def test_reduzir_estoque_success():
    processar_comando("add sabor Morango 9.50")
    processar_comando("set estoque Morango 10")
    resp = processar_comando("reduzir estoque Morango 3")
    assert "7" in resp


def test_reduzir_estoque_nao_negativo():
    processar_comando("add sabor Morango 9.50")
    processar_comando("set estoque Morango 2")
    resp = processar_comando("reduzir estoque Morango 10")
    # Stock should be clamped to 0, not negative
    assert "0" in resp


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def test_status_shows_summary():
    processar_comando("add sabor Chocolate 10.00")
    resp = processar_comando("status")
    assert "Status do Sistema" in resp
    assert "1" in resp  # 1 sabor


# ---------------------------------------------------------------------------
# Limpar
# ---------------------------------------------------------------------------

def test_limpar_returns_signal():
    resp = processar_comando("limpar")
    assert resp == "__LIMPAR__"


# ---------------------------------------------------------------------------
# Comando desconhecido
# ---------------------------------------------------------------------------

def test_comando_desconhecido():
    resp = processar_comando("xyz123")
    assert "não reconhecido" in resp
