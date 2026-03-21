from backend.models.sabor import (
    listar_sabores,
    adicionar_sabor,
    remover_sabor,
    buscar_sabor_por_nome,
)
from backend.models.pedido import listar_pedidos, criar_pedido


def processar_comando(comando):
    comando = comando.strip()

    if comando == "ajuda":
        return (
            "Comandos disponíveis:\n"
            "  listar sabores              → lista todos os sabores\n"
            "  add sabor <nome> <preco>    → adiciona um novo sabor\n"
            "  remover sabor <id>          → remove um sabor pelo ID\n"
            "  fazer pedido <sabor> <qtd>  → registra um pedido\n"
            "  listar pedidos              → lista todos os pedidos\n"
            "  ajuda                       → exibe este menu\n"
        )

    elif comando == "listar sabores":
        sabores = listar_sabores()
        if not sabores:
            return "Nenhum sabor cadastrado."
        linhas = [f"ID: {s['id']} | {s['nome']} - R$ {float(s['preco']):.2f}" for s in sabores]
        return "\n".join(linhas)

    elif comando.startswith("add sabor "):
        partes = comando[len("add sabor "):].strip().split()
        if len(partes) < 2:
            return "Uso: add sabor <nome> <preco>  (ex: add sabor Chocolate 10.00)"
        try:
            preco = float(partes[-1])
            nome = " ".join(partes[:-1])
        except ValueError:
            return "Preço inválido. Use um número como 10.00"
        adicionar_sabor(nome, preco)
        return f"Sabor '{nome}' adicionado com sucesso!"

    elif comando.startswith("remover sabor "):
        partes = comando[len("remover sabor "):].strip()
        try:
            sabor_id = int(partes)
        except ValueError:
            return "ID inválido. Use: remover sabor <id>  (ex: remover sabor 2)"
        sabor = remover_sabor(sabor_id)
        if sabor:
            return f"Sabor ID {sabor_id} removido com sucesso."
        return f"Sabor ID {sabor_id} não encontrado."

    elif comando.startswith("fazer pedido "):
        partes = comando[len("fazer pedido "):].strip().rsplit(" ", 1)
        if len(partes) < 2:
            return "Uso: fazer pedido <sabor> <quantidade>  (ex: fazer pedido Chocolate 2)"
        nome_sabor, qtd_str = partes
        try:
            quantidade = int(qtd_str)
        except ValueError:
            return "Quantidade inválida. Use um número inteiro."
        sabor = buscar_sabor_por_nome(nome_sabor)
        if not sabor:
            return f"Sabor '{nome_sabor}' não encontrado. Use 'listar sabores' para ver os disponíveis."
        criar_pedido(sabor["id"], quantidade)
        return f"Pedido registrado: {quantidade}x {sabor['nome']} — R$ {float(sabor['preco']) * quantidade:.2f}"

    elif comando == "listar pedidos":
        pedidos = listar_pedidos()
        if not pedidos:
            return "Nenhum pedido registrado."
        linhas = [
            f"ID: {p['id']} | {p['sabor']} x{p['quantidade']} | {p['data'].strftime('%d/%m/%Y %H:%M')}"
            for p in pedidos
        ]
        return "\n".join(linhas)

    else:
        return f"Comando não reconhecido: '{comando}'. Digite 'ajuda' para ver os comandos disponíveis."
