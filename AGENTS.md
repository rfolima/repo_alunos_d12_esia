# AGENTS.md — MiniLoja

- Python 3.11+ só com biblioteca padrão; no Windows desta máquina use `C:/Users/Rafael/AppData/Local/Programs/Python/Python312/python.exe` (o `python` do PATH está quebrado).
- Verificar: `python -B testes/test_miniloja.py --codigo caso` (baseline: 11 rodadas, 3 falhas v08–v10) e `--existentes` (26 OK).
- Golden master de `calcular_total`: `python -B exercicios/aula-2/golden_master.py` deve dar "0 divergências"; nunca regenere com `--gerar`.
- Não tocar: `testes/`, `caso/regras.md`, `caso/testes_existentes/`, `caso/dados/`. O contrato (`regras.md`) vale mais que o código.
- Achou algo que parece bug? Reporte, não corrija — refatoração não muda comportamento.
- Convenção não óbvia: `testes/mutacao_manual.py` muta `calculo.py` por trechos literais (`frete = 12.9`, `taxa = 0.05`, `if total > 200:`…); preserve-os ou a ferramenta quebra. No Windows, defina `MINILOJA_TEST_CMD` com barras `/` no caminho do Python.
