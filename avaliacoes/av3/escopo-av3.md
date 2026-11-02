# Escopo declarado antes da mudança — AV3 (B1, R4)

- **Objetivo:** `handlers.get_pedido` só devolve pedidos do próprio usuário (R4.1).
- **Pode tocar:** `caso/miniloja/handlers.py` (só `get_pedido`); novo `avaliacoes/av3/test_av3_r4.py`; este arquivo.
- **Não pode tocar:** `caso/regras.md`, `testes/`, `caso/testes_existentes/`, `caso/dados/`, demais módulos, dependências.
- **Invariantes:** `--codigo caso` segue 11 verificações com 3 falhas (v08–v10); `--existentes` 26 OK; pedido próprio continua 200; id inexistente continua 404.
- **Decisão de contrato (omissa em R4):** pedido de outro usuário responde **404**, igual a inexistente, para não revelar que o id existe.
- **Pronto quando:** teste negativo falha antes e passa depois; `git diff --name-only` só lista os arquivos acima.
- **Pare e pergunte se:** precisar alterar teste existente, outro módulo ou o formato do pedido.
