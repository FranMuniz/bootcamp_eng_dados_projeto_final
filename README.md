# 🌀 Pipeline Kafka Connect: PostgreSQL (Gold) → Kafka → AWS S3

## 📘 Descrição

Este projeto implementa um pipeline de streaming e persistência de dados que conecta as **tabelas Gold** do PostgreSQL (`dadostesouroipca_gold` e `dadostesouropre_gold`) a **tópicos Kafka**, e posteriormente envia esses dados para a **AWS S3** em formato JSON.  

O objetivo é garantir a **sincronização contínua** dos dados processados (camada Gold) com sistemas downstream, como data lakes ou ferramentas de análise.

---

## 🧱 Arquitetura do Pipeline

1. **📡 Fonte de Dados:** PostgreSQL (camada Gold: IPCA e Prefixado)
2. **🔄 Kafka Connect - JDBC Source:** extrai dados do PostgreSQL e publica nos tópicos Kafka
3. **🧩 Kafka Broker:** armazena os tópicos atualizados
4. **🌩 Kafka Connect - S3 Sink:** consome os tópicos e escreve arquivos `.json` em um bucket AWS S3

---

## ⚙️ Configuração dos Conectores

### 🔌 JDBC Source Connector

- Modo de operação: `bulk` (leitura completa das tabelas)
- Principais configs:
  - `connector.class`: `io.confluent.connect.jdbc.JdbcSourceConnector`
  - `connection.url`: URL de conexão JDBC para PostgreSQL
  - `table.whitelist`: `dadostesouroipca_gold`, `dadostesouropre_gold`
  - `topic.prefix`: `postgres-`
  - `mode`: `bulk`
  - `tasks.max`: `1`

### 🪣 S3 Sink Connector

- Grava os dados dos tópicos Kafka em arquivos JSON no S3
- Principais configs:
  - `connector.class`: `io.confluent.connect.s3.S3SinkConnector`
  - `topics`: `postgres-dadostesouroipca_gold`, `postgres-dadostesouropre_gold`
  - `s3.bucket.name`: nome do bucket na AWS
  - `format.class`: `io.confluent.connect.s3.format.json.JsonFormat`
  - `flush.size`: define a frequência de gravação
  - Credenciais AWS via variáveis de ambiente

---

## 🚀 Como Rodar

1. **Iniciar os conectores JDBC Source**

```bash
curl -X POST -H "Content-Type: application/json" \
  --data @connect_jdbc_postgres_ipca_gold.config \
  http://localhost:8083/connectors

curl -X POST -H "Content-Type: application/json" \
  --data @connect_jdbc_postgres_pre_gold.config \
  http://localhost:8083/connectors

curl http://localhost:8083/connectors/postg-connector-ipca-gold/status
curl http://localhost:8083/connectors/postg-connector-pre-gold/status

curl -X POST -H "Content-Type: application/json" \
  --data @connect_s3_sink_ipca_gold.config \
  http://localhost:8083/connectors

curl -X POST -H "Content-Type: application/json" \
  --data @connect_s3_sink_pre_gold.config \
  http://localhost:8083/connectors

curl http://localhost:8083/connectors/s3-sink-connector-ipca-gold/status
curl http://localhost:8083/connectors/s3-sink-connector-pre-gold/status
```

## ✅ Validação

Para inspecionar os dados diretamente nos tópicos Kafka:

```bash
docker exec -it broker kafka-console-consumer \
  --bootstrap-server broker:9092 \
  --topic postgres-dadostesouroipca_gold \
  --from-beginning --max-messages 5

docker exec -it broker kafka-console-consumer \
  --bootstrap-server broker:9092 \
  --topic postgres-dadostesouropre_gold \
  --from-beginning --max-messages 5
```

## 📝 Observações

O pipeline está desenhado para rodar continuamente, mantendo os dados sincronizados entre **PostgreSQL**, **Kafka** e **S3**.

As configurações podem ser facilmente adaptadas para modos como `timestamp+incrementing` ou `incrementing`, caso você precise de captura de alterações (CDC).

Todos os conectores estão em formato `.config` (JSON) e versionados no repositório.
