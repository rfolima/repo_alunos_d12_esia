# Corrige acesso a pedidos de outro usuário (R4.1)

**Intenção:** `get_pedido` devolvia qualquer pedido pelo id. Agora só o dono vê; outro usuário recebe 404, igual a inexistente.
**Escopo:** só `get_pedido` em `caso/miniloja/handlers.py` + teste novo (`avaliacoes/av3/`). Escopo completo em `escopo-av3.md`, escrito antes.
**Plano:** teste negativo falhando → correção de uma condição → verificações.
**Verificação (raiz do repo):**
- `python -B avaliacoes/av3/test_av3_r4.py` → antes `FAILED (failures=2)` (`200 != 404`), depois `OK` (3 testes)
- `python -B testes/test_miniloja.py --codigo caso` → 11 testes, 3 falhas (v08–v10, as mesmas do início)
- `python -B testes/test_miniloja.py --codigo caso --existentes` → 26 OK
- `python -B exercicios/aula-2/golden_master.py` → 325 casos, 0 divergências
**Teste que falharia sem a mudança:** `test_outro_usuario_nao_ve_pedido_alheio`; sabotagem e mutante `!=`→`==` também o reprovam.
**Dependências novas:** nenhuma.
**Modo e por quê:** agente com escopo e verificação; raio de impacto baixo, oráculo forte. Alternativa: manual.
**Decisão aberta:** R4 não define o status; usei 404. Trocar por 403 se o contrato mandar.
**IA:** Claude Code (`claude-sonnet-5-5`); ver `registro-av3.md`.
