#!/bin/bash
set -e

FLAG_FILE="/opt/airflow/airflow.db_initialized"

if [ ! -f "$FLAG_FILE" ]; then
  echo "Inicializando banco de dados do Airflow..."
  airflow db upgrade

  echo "Criando usuário admin do Airflow..."
  airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com || echo "Usuário já existe"

  touch "$FLAG_FILE"
else
  echo "Airflow já foi inicializado anteriormente. Pulando..."
fi

# Finaliza
exit 0
