"""Services package for Gelateria System."""
from .sabores_service import listar_sabores, adicionar_sabor, remover_sabor
from .pedidos_service import listar_pedidos, fazer_pedido
from .estoque_service import listar_estoque, atualizar_estoque

__all__ = [
    "listar_sabores",
    "adicionar_sabor",
    "remover_sabor",
    "listar_pedidos",
    "fazer_pedido",
    "listar_estoque",
    "atualizar_estoque",
]
