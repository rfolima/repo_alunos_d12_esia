# Registro individual — AV1.1

**Limite: uma página, incluindo evidências essenciais.** Estudante: Rafael Lima — Data: 16/10/2026
Origem: tarefas T1–T3 fictícias do enunciado; modalidade: **execução própria** (Python 3.12.10, Windows 10).

**Critério de aceite (definido antes de escolher o modo):** T1 — v08 e v09 passam; v01–v07 e v11 continuam ok. T2 — v10 passa; na suíte existente, só mudam testes que contradizem R3.1/R3.4, com motivo registrado.

| Tarefa | Modo | Tempo até 1ª versão | Tempo até pronto e verificado | Idas e vindas | % corrigido à mão | O que a IA errou | Como verifiquei |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | A: agente (Claude Code no VS Code) | ___ | ___ | ___ | ___ | ___ | ___ |
| T1 | B: completar no editor (___) | ___ | ___ | ___ | ___ | ___ | ___ |
| T2 | ___ | ___ | ___ | ___ | ___ | ___ | ___ |

**Trecho essencial de evidência (comando e saída que sustentam "verificado"):**
Antes: `python -B testes/test_miniloja.py --codigo caso` → v08 e v09 `201 != 422`, v10 `400 != 422`; `FAILED (failures=3)`. Suíte existente (`--existentes`): `Ran 26 tests ... OK`. Ela passa porque `test_cadastro.py` espera `400` e aceita cadastro sem `cpf`, o que contradiz R3.1/R3.4.
Depois: ___

**T3 (hipotética): raio de impacto** alto (produção, todos os usuários, de madrugada); **oráculo disponível** fraco (métricas e logs mostram sintomas, mas não confirmam a causa); **permissões que concederia:** leitura de métricas e logs e comandos de diagnóstico só-leitura, cada um aprovado por mim; nada que altere estado (restart, deploy, alteração de config ou de banco) sem aprovação explícita e plano de reversão; **modo e por quê:** agente com aprovação passo a passo. Ele acelera a coleta e o cruzamento de hipóteses, e a ação continua reversível e sob decisão humana.

**Alternativa para ___:** ___ **Comparação com minha escolha (restrição e consequência):** ___ **Limite da comparação e condição para rever a escolha:** ___

**Procedência/IA:** ferramenta e modelo visíveis: Claude Code (VS Code), modelo Claude Opus 5.5; tarefa delegada e contexto: leitura do enunciado e do repositório, instalação do Python, execução das verificações, ___; trecho aproveitado: ___; minha verificação/intervenção: ___. O raciocínio e a decisão registrados são meus.

**Revisão:** [ ] dois modos em T1; [ ] evidência localizada; [x] T3 decidida; [ ] alternativa e limite; [ ] até uma página.
