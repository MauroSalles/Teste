"""Services package for Gelateria System."""
from .sabores_service import listar_sabores, buscar_sabores, adicionar_sabor, remover_sabor
from .pedidos_service import listar_pedidos, fazer_pedido, cancelar_pedido
from .estoque_service import listar_estoque, atualizar_estoque
from .clientes_service import listar_clientes

__all__ = [
    "listar_sabores",
    "buscar_sabores",
    "adicionar_sabor",
    "remover_sabor",
    "listar_pedidos",
    "fazer_pedido",
    "cancelar_pedido",
    "listar_estoque",
    "atualizar_estoque",
    "listar_clientes",
]
