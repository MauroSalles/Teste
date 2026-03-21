"""Models package for Gelateria System.

These dataclasses represent the application's domain objects used to
transfer data between layers without coupling to the database schema.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Sabor:
    id: int
    nome: str
    preco: float
    disponivel: bool = True


@dataclass
class Cliente:
    id: int
    nome: str
    telefone: Optional[str] = None
    email: Optional[str] = None


@dataclass
class Pedido:
    id: int
    cliente: str
    sabor: str
    quantidade: int
    total: float
    status: str = "pendente"
    criado_em: Optional[datetime] = None


@dataclass
class Estoque:
    id: int
    nome: str
    quantidade: int
    preco: float
