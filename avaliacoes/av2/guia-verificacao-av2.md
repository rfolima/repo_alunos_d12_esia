# Guia de verificação da AV2 (para o Rafael refazer e registrar)

Rode tudo **na raiz do pacote** (`repo_alunos_d12_esia`), em PowerShell, com Python 3.11+. Para cada passo, confira o "esperado" e anote o que **você** viu na coluna "Observado". Essas anotações alimentam o campo "Minha verificação" do `registro-av2.md`.

## 0. Estado do repositório
```powershell
git status --short
git diff --stat
```
Esperado: ` M caso/miniloja/calculo.py` e, em `avaliacoes/av2/`, só arquivos novos (`??`). `diff --stat`: `caso/miniloja/calculo.py | 19 +-` (2 inserções, 17 remoções). `testes/` e `caso/regras.md` **não** aparecem.

## 1. Comportamento preservado
| # | Comando | Esperado | Observado |
| --- | --- | --- | --- |
| 1.1 | `python -B exercicios/aula-2/golden_master.py` | `325 casos gravados, 0 divergências`, saída 0 (`echo $LASTEXITCODE`) | |
| 1.2 | `python -B testes/test_miniloja.py --codigo caso` | `Ran 11 tests`, `FAILED (failures=3)` (as 3 falhas são tarefas do bloco 1) | |
| 1.3 | `python -B testes/test_miniloja.py --codigo caso --existentes` | `Ran 26 tests`, `OK` | |
| 1.4 | `python -B avaliacoes/av2/test_av2_contrato.py` | `Ran 13 tests`, `OK` (12 de contrato + 1 diferencial) | |

**Conferência à mão (recomendada, é a parte que é sua):** abra `caso/regras.md` (R1) e refaça 2 esperados com calculadora.
- 1×40,10, sem cupom, **SP**: (40,10 + 19,90) × 1,07 = 60,00 × 1,07 = **64,20** → está em `test_frete_e_taxa_de_cada_uf`.
- 1×220,00, **VIP15**, SP: 220 × 0,85 = 187,00 (< 200, cobra frete); (187,00 + 19,90) × 1,07 = **221,38** → está em `test_frete_gratis_usa_subtotal_com_desconto`.

Anote os cálculos que você refez: ( PROMO10 e UF SP 100 reais qtd 1 ) 90 + 19,90 = 109,90 x 1,07 

## 2. Prova de que os testes falham (sabotagem manual, em cópia)
Não altera o repositório. Cria uma cópia em pasta temporária, sabota uma linha e roda os testes apontando para ela.
```powershell
$c = Join-Path $env:TEMP "miniloja_sabotagem"
Remove-Item $c -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item caso $c -Recurse
(Get-Content "$c\miniloja\calculo.py") -replace '"RJ": 21.5', '"RJ": 22.5' | Set-Content "$c\miniloja\calculo.py"
Select-String -Path "$c\miniloja\calculo.py" -Pattern '"RJ": 22.5'     # confirma que a sabotagem entrou
$env:MINILOJA_CODIGO = $c
python -B avaliacoes/av2/test_av2_contrato.py --sem-diferencial
echo $LASTEXITCODE
Remove-Item Env:MINILOJA_CODIGO
```
Esperado: a linha `"RJ": 22.5` é encontrada; a suíte termina em `FAILED`, saída `1`; falha ao menos `test_frete_e_taxa_de_cada_uf` (RJ esperado 65.30). Repita trocando a sabotagem por outras e veja qual teste falha:

| Sabotagem (`-replace 'ANTES', 'DEPOIS'`) | Teste que deve falhar | Observado |
| --- | --- | --- |
| `'"PE": 0.05', '"PE": 0.06'` | `test_frete_e_taxa_de_cada_uf` / `test_taxa_por_uf...` | |
| `'total = total \* 0.85', 'total = total * 0.86'` | `test_desconto_promo10_e_vip15` | |
| `'if total > 200:', 'if total > 300:'` | `test_frete_gratis_usa_subtotal_com_desconto` ou `test_taxa_por_uf...` | |
| `'if total > 200:', 'if total >= 200:'` (corrige R1.3) | **nenhum** de contrato; só o diferencial (rode **sem** `--sem-diferencial`) | |

Atenção: em `-replace` o `*` e o `.` são regex; use `\*` e `\.` como acima. Recrie a cópia (`Remove-Item` + `Copy-Item`) entre as sabotagens.

## 3. Mutação completa (24 mutantes, ~50 s)
```powershell
python -B avaliacoes/av2/mutacao_av2.py
```
Esperado, última linha: `Mutantes: 24 | mortos só com contrato: 22 | mortos com contrato+diferencial: 23 | sobreviventes: 1`. Linhas relevantes: `>` vira `>=` → `contrato=não | +diferencial=mata`; `variável sem efeito (equivalente)` → `SOBREVIVEU`. Depois confirme que o repo ficou intacto: `git status --short` igual ao passo 0.
Observado: Teve um sobrevivente referente ao bug registrado no R1.3. Resultado foi o esperado pelo teste.

## 4. Bugs reportados (devem falhar, de propósito)
```powershell
python -B avaliacoes/av2/test_av2_contrato.py --bugs
```
Esperado: `Ran 4 tests`, `FAILED (failures=4)`: `223.55 != 210.0` (duas vezes, R1.3), `17.74 != 17.75` e `15.64 != 15.65` (R1.5).
Observado: 4 erros encontrados, dois na r1.3 e dois na r1.5

## 5. Conflito com a ferramenta oficial de mutação (documentado no ADR)
```powershell
$env:MINILOJA_TEST_CMD = "python -B testes/test_miniloja.py --existentes --codigo caso -x"
python -B testes/mutacao_manual.py calculo.py
Remove-Item Env:MINILOJA_TEST_CMD
```
Esperado: `AssertionError: trecho não encontrado em calculo.py: 'frete = 12.9'`. (Sem a variável, no Windows aparece `FileNotFoundError`, que é do comando padrão, não da refatoração.)
Observado: Confirmei a execucao e obtive o mesmo resultado.

## 6. Como transcrever para o registro
No `registro-av2.md`, troque o trecho `_[a completar por Rafael ...]_` do campo **Procedência/IA** por uma frase sua, só com o que você de fato fez, por exemplo:
> Minha verificação: li o ADR e o registro; rodei os comandos do `guia-verificacao-av2.md` (passos 1–5) e observei [cole os resultados]; refiz à mão [cálculos]; sabotei [qual linha] em cópia e vi falhar [qual teste]. As demais execuções foram feitas pela IA.

Se algum resultado observado divergir do esperado, **não ajuste o registro para combinar**: anote a divergência e me avise.
