"""
Unit tests for the CMD service using a mocked database.
All DB calls are patched so no real PostgreSQL is needed.
"""
from unittest.mock import MagicMock, patch
import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sabor(id=1, nome="Chocolate", preco=10.0):
    return {"id": id, "nome": nome, "preco": preco}


def _pedido(id=1, sabor="Chocolate", quantidade=2):
    from datetime import datetime
    return {"id": id, "sabor": sabor, "quantidade": quantidade, "data": datetime.now()}


def _estoque(id=1, nome="Chocolate", quantidade=10):
    return {"id": id, "nome": nome, "quantidade": quantidade}


def _cliente(id=1, nome="João", tier="Bronze", pontos_fidelidade=0):
    return {"id": id, "nome": nome, "tier": tier, "pontos_fidelidade": pontos_fidelidade,
            "email": None, "telefone": None}


# ── Import subject under test ─────────────────────────────────────────────────

from backend.services.cmd_service import processar_comando


# ── Ajuda ─────────────────────────────────────────────────────────────────────

def test_ajuda_contains_key_sections():
    result = processar_comando("ajuda")
    assert "listar sabores" in result
    assert "fazer pedido" in result
    assert "ver estoque" in result
    assert "ver kpis" in result
    assert "listar clientes" in result
    assert "listar ingredientes" in result
    assert "abrir caixa" in result


# ── Sabores ───────────────────────────────────────────────────────────────────

@patch("backend.services.cmd_service.listar_sabores", return_value=[])
def test_listar_sabores_vazio(mock_listar):
    assert processar_comando("listar sabores") == "Nenhum sabor cadastrado."


@patch("backend.services.cmd_service.listar_sabores", return_value=[_sabor()])
def test_listar_sabores(mock_listar):
    result = processar_comando("listar sabores")
    assert "Chocolate" in result
    assert "10.00" in result


@patch("backend.services.cmd_service.adicionar_sabor", return_value=_sabor(nome="Morango"))
def test_add_sabor(mock_add):
    result = processar_comando("add sabor Morango 9.50")
    assert "Morango" in result
    mock_add.assert_called_once_with("Morango", 9.50)


def test_add_sabor_preco_invalido():
    result = processar_comando("add sabor X abc")
    assert "inválido" in result.lower() or "inválido" in result


def test_add_sabor_preco_negativo():
    result = processar_comando("add sabor X -5")
    assert "negativo" in result.lower()


@patch("backend.services.cmd_service.atualizar_sabor", return_value=_sabor(preco=15.0))
def test_atualizar_sabor(mock_atualizar):
    result = processar_comando("atualizar sabor 1 15.00")
    assert "15.00" in result


@patch("backend.services.cmd_service.remover_sabor", return_value=_sabor())
def test_remover_sabor(mock_remover):
    result = processar_comando("remover sabor 1")
    assert "removido" in result.lower()


@patch("backend.services.cmd_service.remover_sabor", return_value=None)
def test_remover_sabor_nao_encontrado(mock_remover):
    result = processar_comando("remover sabor 999")
    assert "não encontrado" in result.lower()


# ── Pedidos ───────────────────────────────────────────────────────────────────

@patch("backend.services.cmd_service.listar_pedidos", return_value=[])
def test_listar_pedidos_vazio(mock_listar):
    assert processar_comando("listar pedidos") == "Nenhum pedido registrado."


@patch("backend.services.cmd_service.buscar_sabor_por_nome", return_value=_sabor())
@patch("backend.services.cmd_service.obter_estoque", return_value=0)
@patch("backend.services.cmd_service.criar_pedido", return_value={"id": 1})
@patch("backend.services.cmd_service.ajustar_estoque")
def test_fazer_pedido(mock_ajust, mock_criar, mock_estoque, mock_buscar):
    result = processar_comando("fazer pedido Chocolate 2")
    assert "20.00" in result
    mock_criar.assert_called_once_with(1, 2)


@patch("backend.services.cmd_service.buscar_sabor_por_nome", return_value=_sabor())
@patch("backend.services.cmd_service.obter_estoque", return_value=1)
def test_fazer_pedido_estoque_insuficiente(mock_estoque, mock_buscar):
    result = processar_comando("fazer pedido Chocolate 5")
    assert "insuficiente" in result.lower()


def test_fazer_pedido_quantidade_invalida():
    result = processar_comando("fazer pedido Chocolate abc")
    assert "inválida" in result.lower() or "inválido" in result.lower()


# ── Estoque ───────────────────────────────────────────────────────────────────

@patch("backend.services.cmd_service.ver_estoque", return_value=[_estoque()])
def test_ver_estoque(mock_ver):
    result = processar_comando("ver estoque")
    assert "Chocolate" in result
    assert "10" in result


@patch("backend.services.cmd_service.buscar_sabor_por_nome", return_value=_sabor())
@patch("backend.services.cmd_service.definir_estoque", return_value=_estoque(quantidade=50))
def test_set_estoque(mock_def, mock_buscar):
    result = processar_comando("set estoque Chocolate 50")
    assert "50" in result


# ── Clientes ──────────────────────────────────────────────────────────────────

@patch("backend.services.cmd_service.listar_clientes", return_value=[])
def test_listar_clientes_vazio(mock_listar):
    assert processar_comando("listar clientes") == "Nenhum cliente cadastrado."


@patch("backend.services.cmd_service.adicionar_cliente", return_value=_cliente(nome="Maria"))
def test_add_cliente(mock_add):
    result = processar_comando("add cliente Maria")
    assert "Maria" in result
    mock_add.assert_called_once_with("Maria")


@patch("backend.services.cmd_service.adicionar_pontos", return_value=_cliente(pontos_fidelidade=50))
def test_add_pontos(mock_add):
    result = processar_comando("add pontos 1 50")
    assert "50" in result


def test_add_pontos_invalido():
    result = processar_comando("add pontos abc 50")
    assert "inválido" in result.lower() or "inválidos" in result.lower()


def test_add_pontos_negativos():
    result = processar_comando("add pontos 1 -10")
    assert "maior" in result.lower() or "positivo" in result.lower()


@patch("backend.services.cmd_service.top_clientes", return_value=[_cliente(nome="Ana", pontos_fidelidade=100)])
def test_top_clientes(mock_top):
    result = processar_comando("top clientes")
    assert "Ana" in result
    assert "100" in result


# ── Ingredientes ──────────────────────────────────────────────────────────────

@patch("backend.services.cmd_service.listar_ingredientes", return_value=[])
def test_listar_ingredientes_vazio(mock_listar):
    assert processar_comando("listar ingredientes") == "Nenhum ingrediente cadastrado."


@patch("backend.services.cmd_service.adicionar_ingrediente", return_value={
    "id": 1, "nome": "Leite", "unidade": "litro", "preco_unitario": 3.5, "quantidade_atual": 0
})
def test_add_ingrediente(mock_add):
    result = processar_comando("add ingrediente Leite litro 3.50")
    assert "Leite" in result
    mock_add.assert_called_once_with("Leite", "litro", 3.50)


@patch("backend.services.cmd_service.ingredientes_em_alerta", return_value=[])
def test_alerta_ingredientes_ok(mock_alerta):
    result = processar_comando("alerta ingredientes")
    assert "✅" in result or "limites" in result.lower()


# ── Caixa ─────────────────────────────────────────────────────────────────────

@patch("backend.services.cmd_service.abrir_caixa", return_value={"id": 1, "valor_abertura": 100.0})
def test_abrir_caixa(mock_abrir):
    result = processar_comando("abrir caixa 100")
    assert "100.00" in result
    mock_abrir.assert_called_once_with(100.0)


@patch("backend.services.cmd_service.fechar_caixa", return_value={"id": 1, "valor_fechamento": 1500.0})
def test_fechar_caixa(mock_fechar):
    result = processar_comando("fechar caixa 1500")
    assert "1500.00" in result


@patch("backend.services.cmd_service.fechar_caixa", return_value=None)
def test_fechar_caixa_sem_caixa_aberto(mock_fechar):
    result = processar_comando("fechar caixa 0")
    assert "nenhum" in result.lower()


@patch("backend.services.cmd_service.caixa_atual", return_value=None)
def test_ver_caixa_fechado(mock_caixa):
    result = processar_comando("ver caixa")
    assert "nenhum" in result.lower()


@patch("backend.services.cmd_service.registrar_despesa", return_value={"id": 1})
@patch("backend.services.cmd_service.caixa_atual", return_value={"id": 1})
def test_add_despesa(mock_caixa, mock_desp):
    result = processar_comando("add despesa 50 Embalagens")
    assert "50.00" in result
    assert "Embalagens" in result


def test_add_despesa_valor_invalido():
    result = processar_comando("add despesa abc descricao")
    assert "inválido" in result.lower()


# ── Analytics ─────────────────────────────────────────────────────────────────

@patch("backend.services.cmd_service.kpis_gerais", return_value={
    "total_pedidos": 10, "pedidos_hoje": 2,
    "faturamento_total": 150.0, "faturamento_hoje": 30.0,
    "faturamento_mes": 120.0, "ticket_medio": 15.0,
})
def test_ver_kpis(mock_kpis):
    result = processar_comando("ver kpis")
    assert "150.00" in result
    assert "15.00" in result


@patch("backend.services.cmd_service.top_sabores", return_value=[
    {"nome": "Chocolate", "unidades_vendidas": 20, "faturamento": 200.0},
])
def test_top_sabores(mock_tops):
    result = processar_comando("top sabores")
    assert "Chocolate" in result
    assert "20" in result


# ── Sistema / Misc ────────────────────────────────────────────────────────────

def test_limpar():
    assert processar_comando("limpar") == "__LIMPAR__"


def test_comando_desconhecido():
    result = processar_comando("xyzzy nonsense 123")
    assert "não reconhecido" in result.lower()


@patch("backend.services.cmd_service.listar_sabores", return_value=[_sabor()])
@patch("backend.services.cmd_service.listar_pedidos", return_value=[_pedido()])
@patch("backend.services.cmd_service.ver_estoque", return_value=[_estoque()])
@patch("backend.services.cmd_service.listar_clientes", return_value=[_cliente()])
@patch("backend.services.cmd_service.ingredientes_em_alerta", return_value=[])
@patch("backend.services.cmd_service.kpis_gerais", return_value={
    "total_pedidos": 1, "pedidos_hoje": 0,
    "faturamento_total": 10.0, "faturamento_hoje": 0.0,
    "faturamento_mes": 0.0, "ticket_medio": 10.0,
})
def test_status(m1, m2, m3, m4, m5, m6):
    result = processar_comando("status")
    assert "Status" in result
    assert "1" in result  # sabores, pedidos, clientes
