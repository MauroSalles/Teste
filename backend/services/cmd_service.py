from backend.models.sabor import (
    listar_sabores,
    adicionar_sabor,
    atualizar_sabor,
    remover_sabor,
    buscar_sabor_por_nome,
)
from backend.models.pedido import listar_pedidos, criar_pedido
from backend.models.estoque import ver_estoque, definir_estoque, ajustar_estoque, obter_estoque
from backend.models.cliente import (
    listar_clientes,
    adicionar_cliente,
    buscar_cliente_por_nome,
    adicionar_pontos,
    top_clientes,
)
from backend.models.ingrediente import (
    listar_ingredientes,
    adicionar_ingrediente,
    atualizar_estoque_ingrediente,
    ingredientes_em_alerta,
)
from backend.models.financeiro import (
    abrir_caixa,
    fechar_caixa,
    caixa_atual,
    registrar_despesa,
    listar_despesas,
    kpis_gerais,
    top_sabores,
)


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
            "  Clientes & Fidelidade:\n"
            "    listar clientes                   → lista todos os clientes\n"
            "    add cliente <nome>                → cadastra um novo cliente\n"
            "    buscar cliente <nome>             → busca clientes pelo nome\n"
            "    top clientes                      → top 5 clientes por pontos\n"
            "    add pontos <cliente_id> <pontos>  → adiciona pontos de fidelidade\n"
            "\n"
            "  Ingredientes:\n"
            "    listar ingredientes               → lista todos os ingredientes\n"
            "    add ingrediente <nome> <unidade> <preco>  → cadastra ingrediente\n"
            "    alerta ingredientes               → ingredientes em falta ou vencendo\n"
            "\n"
            "  Caixa:\n"
            "    abrir caixa [valor]               → abre o caixa do dia\n"
            "    fechar caixa <valor>              → fecha o caixa com o valor final\n"
            "    ver caixa                         → situação do caixa atual\n"
            "    add despesa <valor> <descricao>   → registra uma despesa\n"
            "    ver despesas                      → lista despesas do caixa atual\n"
            "\n"
            "  Analytics:\n"
            "    ver kpis                          → KPIs gerais do negócio\n"
            "    top sabores                       → top 5 sabores mais vendidos\n"
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
        clientes = listar_clientes()
        alertas = ingredientes_em_alerta()
        kpis = kpis_gerais()
        total_sabores = len(sabores)
        total_pedidos = len(pedidos)
        sem_estoque = [i for i in itens if int(i["quantidade"]) == 0]
        linhas = [
            "═══ Status do Sistema ERP ═══",
            f"  Sabores cadastrados : {total_sabores}",
            f"  Pedidos registrados : {total_pedidos}",
            f"  Clientes            : {len(clientes)}",
            f"  Faturamento total   : R$ {float(kpis['faturamento_total']):.2f}",
            f"  Faturamento hoje    : R$ {float(kpis['faturamento_hoje']):.2f}",
            f"  Sabores sem estoque : {len(sem_estoque)}",
        ]
        if sem_estoque:
            nomes = ", ".join(i["nome"] for i in sem_estoque)
            linhas.append(f"    ⚠ {nomes}")
        if alertas:
            linhas.append(f"  Alertas ingredientes: {len(alertas)}")
        return "\n".join(linhas)

    elif comando == "limpar":
        return "__LIMPAR__"

    # ── Clientes ──────────────────────────────────────────────────────────────

    elif comando == "listar clientes":
        clientes = listar_clientes()
        if not clientes:
            return "Nenhum cliente cadastrado."
        linhas = [
            f"ID: {c['id']} | {c['nome']} | {c['tier']} | {c['pontos_fidelidade']} pts"
            for c in clientes
        ]
        return "\n".join(linhas)

    elif comando.startswith("add cliente "):
        nome = comando[len("add cliente "):].strip()
        if not nome:
            return "Uso: add cliente <nome>  (ex: add cliente João Silva)"
        adicionar_cliente(nome)
        return f"Cliente '{nome}' cadastrado com sucesso!"

    elif comando.startswith("buscar cliente "):
        termo = comando[len("buscar cliente "):].strip()
        if not termo:
            return "Uso: buscar cliente <nome>"
        resultados = buscar_cliente_por_nome(termo)
        if not resultados:
            return f"Nenhum cliente encontrado para '{termo}'."
        linhas = [
            f"ID: {c['id']} | {c['nome']} | {c['tier']} | {c['pontos_fidelidade']} pts"
            for c in resultados
        ]
        return "\n".join(linhas)

    elif comando == "top clientes":
        tops = top_clientes(5)
        if not tops:
            return "Nenhum cliente cadastrado."
        linhas = ["🏆 Top 5 Clientes por Fidelidade:"]
        for i, c in enumerate(tops, 1):
            linhas.append(f"  {i}. {c['nome']} — {c['pontos_fidelidade']} pts ({c['tier']})")
        return "\n".join(linhas)

    elif comando.startswith("add pontos "):
        partes = comando[len("add pontos "):].strip().split()
        if len(partes) < 2:
            return "Uso: add pontos <cliente_id> <pontos>  (ex: add pontos 1 50)"
        try:
            cliente_id = int(partes[0])
            pontos = int(partes[1])
            if pontos <= 0:
                return "Pontos devem ser maiores que zero."
        except ValueError:
            return "ID ou pontos inválidos."
        cliente = adicionar_pontos(cliente_id, pontos)
        if not cliente:
            return f"Cliente ID {cliente_id} não encontrado."
        return (
            f"✅ {pontos} pontos adicionados a '{cliente['nome']}'.\n"
            f"   Total: {cliente['pontos_fidelidade']} pts | Tier: {cliente['tier']}"
        )

    # ── Ingredientes ──────────────────────────────────────────────────────────

    elif comando == "listar ingredientes":
        ingredientes = listar_ingredientes()
        if not ingredientes:
            return "Nenhum ingrediente cadastrado."
        linhas = [
            f"ID: {i['id']} | {i['nome']} ({i['unidade']}) — "
            f"R$ {float(i['preco_unitario']):.2f} | Estoque: {float(i['quantidade_atual']):.3g}"
            for i in ingredientes
        ]
        return "\n".join(linhas)

    elif comando.startswith("add ingrediente "):
        partes = comando[len("add ingrediente "):].strip().split()
        if len(partes) < 3:
            return "Uso: add ingrediente <nome> <unidade> <preco>  (ex: add ingrediente Leite litro 3.50)"
        try:
            preco = float(partes[-1])
            if preco < 0:
                return "Preço não pode ser negativo."
            unidade = partes[-2]
            nome = " ".join(partes[:-2])
        except ValueError:
            return "Preço inválido."
        adicionar_ingrediente(nome, unidade, preco)
        return f"Ingrediente '{nome}' cadastrado com sucesso!"

    elif comando == "alerta ingredientes":
        alertas = ingredientes_em_alerta()
        if not alertas:
            return "✅ Todos os ingredientes estão dentro dos limites!"
        linhas = ["⚠️  Alertas de Ingredientes:"]
        for a in alertas:
            val = float(a["quantidade_atual"])
            minimo = float(a["quantidade_minima"])
            validade = a["data_validade"]
            motivo = []
            if val <= minimo:
                motivo.append(f"estoque baixo ({val:.3g}/{minimo:.3g} {a['unidade']})")
            if validade:
                motivo.append(f"validade: {validade}")
            linhas.append(f"  ⚠ {a['nome']} — {', '.join(motivo)}")
        return "\n".join(linhas)

    # ── Caixa ─────────────────────────────────────────────────────────────────

    elif comando.startswith("abrir caixa"):
        resto = comando[len("abrir caixa"):].strip()
        valor = 0.0
        if resto:
            try:
                valor = float(resto)
                if valor < 0:
                    return "Valor não pode ser negativo."
            except ValueError:
                return "Valor inválido. Uso: abrir caixa [valor_abertura]"
        caixa = abrir_caixa(valor)
        return f"🟢 Caixa aberto! ID: {caixa['id']} | Valor inicial: R$ {float(caixa['valor_abertura']):.2f}"

    elif comando.startswith("fechar caixa "):
        partes = comando[len("fechar caixa "):].strip()
        try:
            valor = float(partes)
            if valor < 0:
                return "Valor não pode ser negativo."
        except ValueError:
            return "Uso: fechar caixa <valor_final>  (ex: fechar caixa 1500.00)"
        caixa = fechar_caixa(valor)
        if not caixa:
            return "Nenhum caixa aberto para fechar."
        return f"🔴 Caixa fechado! Valor final: R$ {float(caixa['valor_fechamento']):.2f}"

    elif comando == "ver caixa":
        caixa = caixa_atual()
        if not caixa:
            return "Nenhum caixa aberto no momento."
        despesas = listar_despesas(int(caixa["id"]))
        total_desp = sum(float(d["valor"]) for d in despesas)
        return (
            f"🟢 Caixa ID {caixa['id']} — Aberto em {caixa['data_abertura'].strftime('%d/%m/%Y %H:%M')}\n"
            f"   Valor abertura : R$ {float(caixa['valor_abertura']):.2f}\n"
            f"   Despesas       : R$ {total_desp:.2f} ({len(despesas)} lançamentos)"
        )

    elif comando.startswith("add despesa "):
        partes = comando[len("add despesa "):].strip().split(None, 1)
        if len(partes) < 2:
            return "Uso: add despesa <valor> <descricao>  (ex: add despesa 50.00 Embalagens)"
        try:
            valor = float(partes[0])
            if valor <= 0:
                return "Valor deve ser positivo."
        except ValueError:
            return "Valor inválido."
        descricao = partes[1]
        caixa = caixa_atual()
        caixa_id = int(caixa["id"]) if caixa else None
        registrar_despesa(descricao, valor, caixa_id)
        return f"Despesa registrada: R$ {valor:.2f} — {descricao}"

    elif comando == "ver despesas":
        caixa = caixa_atual()
        caixa_id = int(caixa["id"]) if caixa else None
        despesas = listar_despesas(caixa_id)
        if not despesas:
            return "Nenhuma despesa registrada."
        total = sum(float(d["valor"]) for d in despesas)
        linhas = [f"ID: {d['id']} | R$ {float(d['valor']):.2f} | {d['descricao']}" for d in despesas]
        linhas.append(f"─────\nTotal: R$ {total:.2f}")
        return "\n".join(linhas)

    # ── Analytics ─────────────────────────────────────────────────────────────

    elif comando == "ver kpis":
        kpis = kpis_gerais()
        return (
            "📊 KPIs do Negócio:\n"
            f"  Pedidos totais    : {int(kpis['total_pedidos'])}\n"
            f"  Pedidos hoje      : {int(kpis['pedidos_hoje'])}\n"
            f"  Faturamento total : R$ {float(kpis['faturamento_total']):.2f}\n"
            f"  Faturamento hoje  : R$ {float(kpis['faturamento_hoje']):.2f}\n"
            f"  Faturamento mês   : R$ {float(kpis['faturamento_mes']):.2f}\n"
            f"  Ticket médio      : R$ {float(kpis['ticket_medio']):.2f}"
        )

    elif comando == "top sabores":
        tops = top_sabores(5)
        if not tops:
            return "Nenhum pedido registrado."
        linhas = ["🍦 Top 5 Sabores Mais Vendidos:"]
        for i, s in enumerate(tops, 1):
            linhas.append(
                f"  {i}. {s['nome']} — {int(s['unidades_vendidas'])} unid. | R$ {float(s['faturamento']):.2f}"
            )
        return "\n".join(linhas)

    else:
        return f"Comando não reconhecido: '{comando}'. Digite 'ajuda' para ver os comandos disponíveis."

