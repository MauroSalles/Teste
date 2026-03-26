"""
Unit-style tests for cmd_service.processar_comando.

Each test calls processar_comando() directly — no HTTP layer involved —
so they run fast and require only a live PostgreSQL connection.
"""

import pytest
from backend.services.cmd_service import processar_comando


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def cmd(text):
    return processar_comando(text)


# ─────────────────────────────────────────────────────────────────────────────
# ajuda / limpar
# ─────────────────────────────────────────────────────────────────────────────

def test_ajuda_contains_sections():
    resp = cmd("ajuda")
    assert "Sabores" in resp
    assert "Pedidos" in resp
    assert "Estoque" in resp
    assert "Relatórios" in resp
    assert "Sistema" in resp


def test_ajuda_lists_new_commands():
    resp = cmd("ajuda")
    assert "buscar sabor" in resp
    assert "buscar pedido" in resp
    assert "relatorio vendas" in resp
    assert "total vendas" in resp


def test_limpar_returns_sentinel():
    assert cmd("limpar") == "__LIMPAR__"


# ─────────────────────────────────────────────────────────────────────────────
# listar / buscar sabores
# ─────────────────────────────────────────────────────────────────────────────

def test_listar_sabores_shows_seeded_flavors():
    resp = cmd("listar sabores")
    assert "Chocolate" in resp
    assert "Morango" in resp
    assert "Baunilha" in resp


def test_buscar_sabor_exact():
    resp = cmd("buscar sabor Chocolate")
    assert "Chocolate" in resp
    assert "Morango" not in resp


def test_buscar_sabor_partial():
    resp = cmd("buscar sabor cho")
    assert "Chocolate" in resp


def test_buscar_sabor_case_insensitive():
    resp = cmd("buscar sabor MORANGO")
    assert "Morango" in resp


def test_buscar_sabor_not_found():
    resp = cmd("buscar sabor Pitaya")
    assert "não encontrado" in resp.lower()


def test_buscar_sabor_missing_term():
    resp = cmd("buscar sabor ")
    assert "Uso:" in resp


# ─────────────────────────────────────────────────────────────────────────────
# add / atualizar / remover sabor
# ─────────────────────────────────────────────────────────────────────────────

def test_add_sabor_success():
    resp = cmd("add sabor Pistache 12.00")
    assert "Pistache" in resp
    assert "adicionado" in resp.lower()


def test_add_sabor_negative_price():
    resp = cmd("add sabor Limão -1.00")
    assert "negativo" in resp.lower()


def test_add_sabor_invalid_price():
    resp = cmd("add sabor Limão abc")
    assert "inválido" in resp.lower()


def test_atualizar_sabor_success():
    # ID 1 is Chocolate after seeding
    resp = cmd("atualizar sabor 1 15.00")
    assert "15.00" in resp


def test_atualizar_sabor_not_found():
    resp = cmd("atualizar sabor 9999 5.00")
    assert "não encontrado" in resp.lower()


def test_remover_sabor_success():
    resp = cmd("remover sabor 1")
    assert "removido" in resp.lower()


def test_remover_sabor_not_found():
    resp = cmd("remover sabor 9999")
    assert "não encontrado" in resp.lower()


# ─────────────────────────────────────────────────────────────────────────────
# fazer pedido / listar pedidos / buscar pedido
# ─────────────────────────────────────────────────────────────────────────────

def test_fazer_pedido_success():
    # Chocolate costs R$10.00 per seed in conftest.py
    resp = cmd("fazer pedido Chocolate 2")
    assert "Chocolate" in resp
    assert "20.00" in resp


def test_fazer_pedido_flavor_not_found():
    resp = cmd("fazer pedido Inexistente 1")
    assert "não encontrado" in resp.lower()


def test_fazer_pedido_zero_quantity():
    resp = cmd("fazer pedido Chocolate 0")
    assert "maior que zero" in resp.lower()


def test_listar_pedidos_empty():
    resp = cmd("listar pedidos")
    assert "nenhum" in resp.lower()


def test_listar_pedidos_after_order():
    cmd("fazer pedido Morango 3")
    resp = cmd("listar pedidos")
    assert "Morango" in resp
    assert "3" in resp


def test_buscar_pedido_success():
    cmd("fazer pedido Chocolate 1")
    # List to find the ID
    lista = cmd("listar pedidos")
    # Extract the first ID from "ID: N |"
    first_line = [l for l in lista.splitlines() if "ID:" in l][0]
    pedido_id = first_line.split("ID:")[1].split("|")[0].strip()
    resp = cmd(f"buscar pedido {pedido_id}")
    assert "Chocolate" in resp
    assert "Total: R$" in resp


def test_buscar_pedido_not_found():
    resp = cmd("buscar pedido 99999")
    assert "não encontrado" in resp.lower()


def test_buscar_pedido_invalid_id():
    resp = cmd("buscar pedido abc")
    assert "inválido" in resp.lower()


# ─────────────────────────────────────────────────────────────────────────────
# estoque
# ─────────────────────────────────────────────────────────────────────────────

def test_ver_estoque_shows_flavors():
    resp = cmd("ver estoque")
    assert "Chocolate" in resp


def test_set_estoque_success():
    resp = cmd("set estoque Chocolate 50")
    assert "50" in resp


def test_add_estoque_success():
    cmd("set estoque Chocolate 10")
    resp = cmd("add estoque Chocolate 5")
    assert "15" in resp


def test_reduzir_estoque_success():
    cmd("set estoque Morango 20")
    resp = cmd("reduzir estoque Morango 5")
    assert "15" in resp


def test_estoque_nao_negativo():
    cmd("set estoque Baunilha 3")
    cmd("reduzir estoque Baunilha 100")
    resp = cmd("ver estoque")
    # Should not show negative quantities
    assert "-" not in resp.replace("R$ ", "").replace("ID:", "")


# ─────────────────────────────────────────────────────────────────────────────
# relatorio vendas / total vendas
# ─────────────────────────────────────────────────────────────────────────────

def test_relatorio_vendas_no_orders():
    resp = cmd("relatorio vendas")
    assert "nenhum" in resp.lower()


def test_relatorio_vendas_shows_ranking():
    cmd("fazer pedido Chocolate 5")
    cmd("fazer pedido Morango 2")
    resp = cmd("relatorio vendas")
    assert "Chocolate" in resp
    assert "Morango" in resp
    # Chocolate had more units — should appear first
    assert resp.index("Chocolate") < resp.index("Morango")


def test_total_vendas_no_orders():
    resp = cmd("total vendas")
    assert "nenhum" in resp.lower()


def test_total_vendas_calculates_correctly():
    # Seed prices (conftest.py): Chocolate=R$10.00, Morango=R$9.50
    cmd("fazer pedido Chocolate 2")   # 2 * 10.00 = 20.00
    cmd("fazer pedido Morango 1")     # 1 *  9.50 =  9.50
    resp = cmd("total vendas")
    assert "3" in resp   # total pedidos
    assert "29.50" in resp  # total receita


# ─────────────────────────────────────────────────────────────────────────────
# status
# ─────────────────────────────────────────────────────────────────────────────

def test_status_shows_counts():
    cmd("fazer pedido Chocolate 1")
    resp = cmd("status")
    assert "Sabores cadastrados" in resp
    assert "Pedidos registrados" in resp


# ─────────────────────────────────────────────────────────────────────────────
# unknown command
# ─────────────────────────────────────────────────────────────────────────────

def test_unknown_command():
    resp = cmd("comando_inexistente")
    assert "não reconhecido" in resp.lower()
