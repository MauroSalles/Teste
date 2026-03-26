from backend.models.sabor import (
    listar_sabores,
    adicionar_sabor,
    atualizar_sabor,
    remover_sabor,
    buscar_sabor_por_nome,
)
from backend.models.pedido import listar_pedidos, criar_pedido
from backend.models.estoque import ver_estoque, definir_estoque, ajustar_estoque, obter_estoque
from backend.services.energy_service import recommend as energy_recommend


def processar_comando(comando):
    comando = comando.strip()

    if comando == "ajuda":
        return (
            "Comandos disponíveis:\n"
            "\n"
            "  Sabores:\n"
            "    listar sabores                   → lista todos os sabores\n"
            "    add sabor <nome> <preco>          → adiciona um novo sabor\n"
            "    atualizar sabor <id> <preco>      → atualiza o preço de um sabor\n"
            "    remover sabor <id>                → remove um sabor pelo ID\n"
            "\n"
            "  Pedidos:\n"
            "    fazer pedido <sabor> <qtd>        → registra um pedido\n"
            "    listar pedidos                    → exibe o histórico de pedidos\n"
            "\n"
            "  Estoque:\n"
            "    ver estoque                       → mostra o estoque atual\n"
            "    set estoque <sabor> <qtd>         → define a quantidade em estoque\n"
            "    add estoque <sabor> <qtd>         → aumenta o estoque de um sabor\n"
            "    reduzir estoque <sabor> <qtd>     → reduz o estoque de um sabor\n"
            "\n"
            "  Energia:\n"
            "    recomendar                        → recomendação baseada na sua energia\n"
            "\n"
            "  Sistema:\n"
            "    status                            → resumo geral do sistema\n"
            "    limpar                            → limpa a tela\n"
            "    ajuda                             → exibe este menu\n"
        )

    # ── Sabores ──────────────────────────────────────────────────────────────

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
            if preco < 0:
                return "Preço não pode ser negativo."
            nome = " ".join(partes[:-1])
        except ValueError:
            return "Preço inválido. Use um número como 10.00"
        adicionar_sabor(nome, preco)
        return f"Sabor '{nome}' adicionado com sucesso!"

    elif comando.startswith("atualizar sabor "):
        partes = comando[len("atualizar sabor "):].strip().split()
        if len(partes) < 2:
            return "Uso: atualizar sabor <id> <novo_preco>  (ex: atualizar sabor 1 12.50)"
        try:
            sabor_id = int(partes[0])
            novo_preco = float(partes[1])
            if novo_preco < 0:
                return "Preço não pode ser negativo."
        except ValueError:
            return "ID ou preço inválido."
        sabor = atualizar_sabor(sabor_id, novo_preco)
        if sabor:
            return f"Sabor '{sabor['nome']}' atualizado para R$ {float(sabor['preco']):.2f}."
        return f"Sabor ID {sabor_id} não encontrado."

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

    # ── Pedidos ───────────────────────────────────────────────────────────────

    elif comando.startswith("fazer pedido "):
        partes = comando[len("fazer pedido "):].strip().rsplit(" ", 1)
        if len(partes) < 2:
            return "Uso: fazer pedido <sabor> <quantidade>  (ex: fazer pedido Chocolate 2)"
        nome_sabor, qtd_str = partes
        try:
            quantidade = int(qtd_str)
            if quantidade <= 0:
                return "Quantidade deve ser maior que zero."
        except ValueError:
            return "Quantidade inválida. Use um número inteiro."
        sabor = buscar_sabor_por_nome(nome_sabor)
        if not sabor:
            return f"Sabor '{nome_sabor}' não encontrado. Use 'listar sabores' para ver os disponíveis."
        estoque_atual = obter_estoque(sabor["id"])
        # Only enforce stock limits when stock tracking has been set up for this flavor.
        # estoque_atual == 0 means either "no stock record" or "stock not yet configured",
        # so we allow the order to pass through in that case.
        if estoque_atual > 0 and quantidade > estoque_atual:
            return (
                f"Estoque insuficiente para '{sabor['nome']}'. "
                f"Disponível: {estoque_atual} | Solicitado: {quantidade}"
            )
        criar_pedido(sabor["id"], quantidade)
        if estoque_atual > 0:
            ajustar_estoque(sabor["id"], -quantidade)
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

    # ── Estoque ───────────────────────────────────────────────────────────────

    elif comando == "ver estoque":
        itens = ver_estoque()
        if not itens:
            return "Nenhum sabor cadastrado."
        linhas = [
            f"ID: {i['id']} | {i['nome']} — {i['quantidade']} unidades"
            for i in itens
        ]
        return "\n".join(linhas)

    elif comando.startswith("set estoque "):
        partes = comando[len("set estoque "):].strip().rsplit(" ", 1)
        if len(partes) < 2:
            return "Uso: set estoque <sabor> <qtd>  (ex: set estoque Chocolate 50)"
        nome_sabor, qtd_str = partes
        try:
            qtd = int(qtd_str)
            if qtd < 0:
                return "Quantidade não pode ser negativa."
        except ValueError:
            return "Quantidade inválida. Use um número inteiro."
        sabor = buscar_sabor_por_nome(nome_sabor)
        if not sabor:
            return f"Sabor '{nome_sabor}' não encontrado."
        definir_estoque(sabor["id"], qtd)
        return f"Estoque de '{sabor['nome']}' definido para {qtd} unidades."

    elif comando.startswith("add estoque "):
        partes = comando[len("add estoque "):].strip().rsplit(" ", 1)
        if len(partes) < 2:
            return "Uso: add estoque <sabor> <qtd>  (ex: add estoque Morango 20)"
        nome_sabor, qtd_str = partes
        try:
            qtd = int(qtd_str)
            if qtd <= 0:
                return "Quantidade deve ser maior que zero."
        except ValueError:
            return "Quantidade inválida."
        sabor = buscar_sabor_por_nome(nome_sabor)
        if not sabor:
            return f"Sabor '{nome_sabor}' não encontrado."
        resultado = ajustar_estoque(sabor["id"], qtd)
        return f"Estoque de '{sabor['nome']}' aumentado. Total: {resultado['quantidade']} unidades."

    elif comando.startswith("reduzir estoque "):
        partes = comando[len("reduzir estoque "):].strip().rsplit(" ", 1)
        if len(partes) < 2:
            return "Uso: reduzir estoque <sabor> <qtd>  (ex: reduzir estoque Morango 5)"
        nome_sabor, qtd_str = partes
        try:
            qtd = int(qtd_str)
            if qtd <= 0:
                return "Quantidade deve ser maior que zero."
        except ValueError:
            return "Quantidade inválida."
        sabor = buscar_sabor_por_nome(nome_sabor)
        if not sabor:
            return f"Sabor '{nome_sabor}' não encontrado."
        resultado = ajustar_estoque(sabor["id"], -qtd)
        return f"Estoque de '{sabor['nome']}' reduzido. Total: {resultado['quantidade']} unidades."

    # ── Sistema ───────────────────────────────────────────────────────────────

    elif comando == "status":
        sabores = listar_sabores()
        pedidos = listar_pedidos()
        itens = ver_estoque()
        total_sabores = len(sabores)
        total_pedidos = len(pedidos)
        sem_estoque = [i for i in itens if int(i["quantidade"]) == 0]
        linhas = [
            "═══ Status do Sistema ═══",
            f"  Sabores cadastrados : {total_sabores}",
            f"  Pedidos registrados : {total_pedidos}",
            f"  Sabores sem estoque : {len(sem_estoque)}",
        ]
        if sem_estoque:
            nomes = ", ".join(i["nome"] for i in sem_estoque)
            linhas.append(f"    ⚠ {nomes}")
        return "\n".join(linhas)

    elif comando == "limpar":
        return "__LIMPAR__"

    elif comando == "recomendar":
        # Fallback text-based recommendation (no session tracking)
        try:
            result = energy_recommend(
                session_id="cmd-anonymous",
                energy_score=50,
                mood=None,
                purpose=None,
            )
            if result.get("flavor"):
                return (
                    f"{result['copy']}\n"
                    f"  Recomendação: {result['flavor']} — R$ {result['price']:.2f}\n"
                    f"  (use o painel de energia para personalizar)"
                )
            return "Nenhum sabor disponível para recomendar."
        except Exception:
            return "Recomendação indisponível no momento."

    else:
        return f"Comando não reconhecido: '{comando}'. Digite 'ajuda' para ver os comandos disponíveis."

