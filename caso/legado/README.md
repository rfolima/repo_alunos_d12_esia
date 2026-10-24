# cienciometria

Scripts de cientometria baseados na API do OpenAlex.

## Uso
    pip install -r requirements.txt
    python -m cienciometria.jobs ingest
    python -m cienciometria.jobs relatorio top_instituicoes

A API do OpenAlex não precisa de chave. Informe seu e-mail em `config.ini` (campo `mailto`) para
entrar no "polite pool" e ter mais velocidade.

## Agendamento
`scripts/rodar_tudo.sh` roda às 03:00 (cron). Não altere o formato do CSV do parceiro.

(Última atualização deste README: 2023)
