#!/bin/bash
# Pipeline completo (cron 03:00). Mantido pelo Beltrano.
export CIENTO_AMBIENT=prod        # TODO: confirmar com o Beltrano
export CIENTO_OFFLINE=1
cd "$(dirname "$0")/.."
python -m cienciometria.jobs ingest
python -m cienciometria.jobs enriquecer
python -m cienciometria.jobs sql scripts/corrigir_anos.sql
python -m cienciometria.jobs relatorio top_instituicoes
python -m cienciometria.jobs relatorio exporta_parceiro
python -m cienciometria.jobs refresh
