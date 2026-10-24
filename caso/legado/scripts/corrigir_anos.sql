-- corrige anos inválidos que vieram da API (rodado pelo cron)
UPDATE trabalhos SET ano = NULL WHERE ano < 1900;
