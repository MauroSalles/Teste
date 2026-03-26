"""Unit tests for the command service (processar_comando)."""
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sabor(id=1, nome="TestChocolate", preco=10.00):
    return {"id": id, "nome": nome, "preco": preco}


def _pedido(id=1, sabor="TestChocolate", quantidade=2, data=None):
    from datetime import datetime
    return {
        "id": id,
        "sabor": sabor,
        "quantidade": quantidade,
        "data": data or datetime(2024, 1, 1, 12, 0),
    }


# ---------------------------------------------------------------------------
# ajuda
# ---------------------------------------------------------------------------

def test_ajuda():
    from backend.services.cmd_service import processar_comando
    result = processar_comando("ajuda")
    assert "listar sabores" in result
    assert "fazer pedido" in result
    assert "ver estoque" in result


# ---------------------------------------------------------------------------
# listar sabores
# ---------------------------------------------------------------------------

@patch("backend.services.cmd_service.listar_sabores")
def test_listar_sabores_vazio(mock_list):
    from backend.services.cmd_service import processar_comando
    mock_list.return_value = []
    assert processar_comando("listar sabores") == "Nenhum sabor cadastrado."


@patch("backend.services.cmd_service.listar_sabores")
def test_listar_sabores_com_dados(mock_list):
    from backend.services.cmd_service import processar_comando
    mock_list.return_value = [_sabor()]
    result = processar_comando("listar sabores")
    assert "TestChocolate" in result
    assert "10.00" in result


# ---------------------------------------------------------------------------
# add sabor
# ---------------------------------------------------------------------------

@patch("backend.services.cmd_service.adicionar_sabor")
def test_add_sabor_valido(mock_add):
    from backend.services.cmd_service import processar_comando
    mock_add.return_value = _sabor(nome="Morango", preco=9.50)
    result = processar_comando("add sabor Morango 9.50")
    assert "Morango" in result
    mock_add.assert_called_once_with("Morango", 9.50)


def test_add_sabor_sem_preco():
    from backend.services.cmd_service import processar_comando
    result = processar_comando("add sabor SemPreco")
    assert "Uso:" in result


def test_add_sabor_preco_invalido():
    from backend.services.cmd_service import processar_comando
    result = processar_comando("add sabor Morango abc")
    assert "inválido" in result.lower() or "Preço" in result


def test_add_sabor_preco_negativo():
    from backend.services.cmd_service import processar_comando
    result = processar_comando("add sabor Morango -5.00")
    assert "negativo" in result.lower()


# ---------------------------------------------------------------------------
# atualizar sabor
# ---------------------------------------------------------------------------

@patch("backend.services.cmd_service.atualizar_sabor")
def test_atualizar_sabor_encontrado(mock_update):
    from backend.services.cmd_service import processar_comando
    mock_update.return_value = _sabor(preco=15.00)
    result = processar_comando("atualizar sabor 1 15.00")
    assert "15.00" in result
    mock_update.assert_called_once_with(1, 15.00)


@patch("backend.services.cmd_service.atualizar_sabor")
def test_atualizar_sabor_nao_encontrado(mock_update):
    from backend.services.cmd_service import processar_comando
    mock_update.return_value = None
    result = processar_comando("atualizar sabor 99 15.00")
    assert "não encontrado" in result.lower()


def test_atualizar_sabor_args_invalidos():
    from backend.services.cmd_service import processar_comando
    result = processar_comando("atualizar sabor 1")  # missing new price
    assert "Uso:" in result


# ---------------------------------------------------------------------------
# remover sabor
# ---------------------------------------------------------------------------

@patch("backend.services.cmd_service.remover_sabor")
def test_remover_sabor_encontrado(mock_remove):
    from backend.services.cmd_service import processar_comando
    mock_remove.return_value = _sabor()
    result = processar_comando("remover sabor 1")
    assert "removido" in result.lower()


@patch("backend.services.cmd_service.remover_sabor")
def test_remover_sabor_nao_encontrado(mock_remove):
    from backend.services.cmd_service import processar_comando
    mock_remove.return_value = None
    result = processar_comando("remover sabor 99")
    assert "não encontrado" in result.lower()


def test_remover_sabor_id_invalido():
    from backend.services.cmd_service import processar_comando
    result = processar_comando("remover sabor abc")
    assert "inválido" in result.lower()


# ---------------------------------------------------------------------------
# fazer pedido
# ---------------------------------------------------------------------------

@patch("backend.services.cmd_service.obter_estoque")
@patch("backend.services.cmd_service.criar_pedido")
@patch("backend.services.cmd_service.ajustar_estoque")
@patch("backend.services.cmd_service.buscar_sabor_por_nome")
def test_fazer_pedido_sem_estoque_cadastrado(mock_buscar, mock_ajustar, mock_criar, mock_estoque):
    from backend.services.cmd_service import processar_comando
    mock_buscar.return_value = _sabor()
    mock_estoque.return_value = 0  # stock not configured
    mock_criar.return_value = {"id": 1}
    result = processar_comando("fazer pedido TestChocolate 2")
    assert "Pedido registrado" in result
    mock_ajustar.assert_not_called()


@patch("backend.services.cmd_service.obter_estoque")
@patch("backend.services.cmd_service.criar_pedido")
@patch("backend.services.cmd_service.ajustar_estoque")
@patch("backend.services.cmd_service.buscar_sabor_por_nome")
def test_fazer_pedido_com_estoque_suficiente(mock_buscar, mock_ajustar, mock_criar, mock_estoque):
    from backend.services.cmd_service import processar_comando
    mock_buscar.return_value = _sabor()
    mock_estoque.return_value = 10
    mock_criar.return_value = {"id": 1}
    result = processar_comando("fazer pedido TestChocolate 2")
    assert "Pedido registrado" in result
    mock_ajustar.assert_called_once_with(1, -2)


@patch("backend.services.cmd_service.obter_estoque")
@patch("backend.services.cmd_service.buscar_sabor_por_nome")
def test_fazer_pedido_estoque_insuficiente(mock_buscar, mock_estoque):
    from backend.services.cmd_service import processar_comando
    mock_buscar.return_value = _sabor()
    mock_estoque.return_value = 1
    result = processar_comando("fazer pedido TestChocolate 5")
    assert "insuficiente" in result.lower()


@patch("backend.services.cmd_service.buscar_sabor_por_nome")
def test_fazer_pedido_sabor_inexistente(mock_buscar):
    from backend.services.cmd_service import processar_comando
    mock_buscar.return_value = None
    result = processar_comando("fazer pedido Inexistente 2")
    assert "não encontrado" in result.lower()


def test_fazer_pedido_quantidade_invalida():
    from backend.services.cmd_service import processar_comando
    result = processar_comando("fazer pedido TestChocolate abc")
    assert "inválida" in result.lower() or "inválido" in result.lower()


def test_fazer_pedido_quantidade_zero():
    from backend.services.cmd_service import processar_comando
    result = processar_comando("fazer pedido TestChocolate 0")
    assert "maior" in result.lower()


# ---------------------------------------------------------------------------
# listar pedidos
# ---------------------------------------------------------------------------

@patch("backend.services.cmd_service.listar_pedidos")
def test_listar_pedidos_vazio(mock_list):
    from backend.services.cmd_service import processar_comando
    mock_list.return_value = []
    assert processar_comando("listar pedidos") == "Nenhum pedido registrado."


@patch("backend.services.cmd_service.listar_pedidos")
def test_listar_pedidos_com_dados(mock_list):
    from backend.services.cmd_service import processar_comando
    mock_list.return_value = [_pedido()]
    result = processar_comando("listar pedidos")
    assert "TestChocolate" in result


# ---------------------------------------------------------------------------
# ver estoque
# ---------------------------------------------------------------------------

@patch("backend.services.cmd_service.ver_estoque")
def test_ver_estoque_vazio(mock_estoque):
    from backend.services.cmd_service import processar_comando
    mock_estoque.return_value = []
    assert processar_comando("ver estoque") == "Nenhum sabor cadastrado."


@patch("backend.services.cmd_service.ver_estoque")
def test_ver_estoque_com_dados(mock_estoque):
    from backend.services.cmd_service import processar_comando
    mock_estoque.return_value = [{"id": 1, "nome": "TestChocolate", "quantidade": 5}]
    result = processar_comando("ver estoque")
    assert "TestChocolate" in result
    assert "5" in result


# ---------------------------------------------------------------------------
# set estoque
# ---------------------------------------------------------------------------

@patch("backend.services.cmd_service.definir_estoque")
@patch("backend.services.cmd_service.buscar_sabor_por_nome")
def test_set_estoque_valido(mock_buscar, mock_definir):
    from backend.services.cmd_service import processar_comando
    mock_buscar.return_value = _sabor()
    mock_definir.return_value = {"sabor_id": 1, "quantidade": 50}
    result = processar_comando("set estoque TestChocolate 50")
    assert "50" in result


@patch("backend.services.cmd_service.buscar_sabor_por_nome")
def test_set_estoque_sabor_inexistente(mock_buscar):
    from backend.services.cmd_service import processar_comando
    mock_buscar.return_value = None
    result = processar_comando("set estoque Inexistente 50")
    assert "não encontrado" in result.lower()


def test_set_estoque_quantidade_negativa():
    from backend.services.cmd_service import processar_comando
    result = processar_comando("set estoque TestChocolate -1")
    assert "negativa" in result.lower()


# ---------------------------------------------------------------------------
# add estoque / reduzir estoque
# ---------------------------------------------------------------------------

@patch("backend.services.cmd_service.ajustar_estoque")
@patch("backend.services.cmd_service.buscar_sabor_por_nome")
def test_add_estoque_valido(mock_buscar, mock_ajustar):
    from backend.services.cmd_service import processar_comando
    mock_buscar.return_value = _sabor()
    mock_ajustar.return_value = {"sabor_id": 1, "quantidade": 20}
    result = processar_comando("add estoque TestChocolate 20")
    assert "20" in result


@patch("backend.services.cmd_service.ajustar_estoque")
@patch("backend.services.cmd_service.buscar_sabor_por_nome")
def test_reduzir_estoque_valido(mock_buscar, mock_ajustar):
    from backend.services.cmd_service import processar_comando
    mock_buscar.return_value = _sabor()
    mock_ajustar.return_value = {"sabor_id": 1, "quantidade": 5}
    result = processar_comando("reduzir estoque TestChocolate 5")
    assert "5" in result


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

@patch("backend.services.cmd_service.ver_estoque")
@patch("backend.services.cmd_service.listar_pedidos")
@patch("backend.services.cmd_service.listar_sabores")
def test_status(mock_sabores, mock_pedidos, mock_estoque):
    from backend.services.cmd_service import processar_comando
    mock_sabores.return_value = [_sabor()]
    mock_pedidos.return_value = [_pedido()]
    mock_estoque.return_value = [{"id": 1, "nome": "TestChocolate", "quantidade": 0}]
    result = processar_comando("status")
    assert "Status" in result
    assert "1" in result  # sabores count


# ---------------------------------------------------------------------------
# limpar
# ---------------------------------------------------------------------------

def test_limpar():
    from backend.services.cmd_service import processar_comando
    assert processar_comando("limpar") == "__LIMPAR__"


# ---------------------------------------------------------------------------
# comando desconhecido
# ---------------------------------------------------------------------------

def test_comando_desconhecido():
    from backend.services.cmd_service import processar_comando
    result = processar_comando("xyz_invalido_123")
    assert "não reconhecido" in result.lower()


def test_whitespace_normalizado():
    from backend.services.cmd_service import processar_comando
    result = processar_comando("   ajuda   ")
    assert "listar sabores" in result
