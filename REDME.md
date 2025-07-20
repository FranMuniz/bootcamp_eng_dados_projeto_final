# Pipeline Kafka Connect - Integração PostgreSQL Gold → Kafka → AWS S3

## Descrição

Este projeto implementa um pipeline de ingestão e persistência de dados das tabelas gold (`dadostesouroipca_gold` e `dadostesouropre_gold`) do banco de dados PostgreSQL para tópicos Kafka, e de Kafka para arquivos JSON armazenados em um bucket AWS S3. O objetivo é manter os dados gold sincronizados e disponíveis para consumo downstream.

---

## Arquitetura

1. **Fonte de Dados:** PostgreSQL (tabelas gold IPCA e PRE)  
2. **Kafka Connect Source:** Conectores JDBC para ler dados das tabelas e publicar em tópicos Kafka  
3. **Kafka Broker:** Armazena os tópicos com os dados atualizados  
4. **Kafka Connect Sink:** Conectores S3 Sink para gravar dados do Kafka em arquivos JSON no bucket S3  

---

## Configuração dos Conectores

### JDBC Source Connectors

- Conectores configurados para modo `bulk` para leitura completa das tabelas gold.
- Configurações importantes:
  - `connector.class`: `io.confluent.connect.jdbc.JdbcSourceConnector`
  - `connection.url`: JDBC URL para PostgreSQL
  - `table.whitelist`: nome da tabela gold (`dadostesouroipca_gold` ou `dadostesouropre_gold`)
  - `topic.prefix`: prefixo usado para o nome do tópico Kafka (`postgres-`)
  - `mode`: `bulk`
  - `tasks.max`: 1

### S3 Sink Connectors

- Conectores configurados para gravar dados dos tópicos Kafka em arquivos JSON no bucket AWS S3.
- Configurações importantes:
  - `connector.class`: `io.confluent.connect.s3.S3SinkConnector`
  - `topics`: tópicos Kafka gerados pelo JDBC Source (`postgres-dadostesouroipca_gold` e `postgres-dadostesouropre_gold`)
  - `s3.bucket.name`: nome do bucket S3
  - `format.class`: `io.confluent.connect.s3.format.json.JsonFormat`
  - Configuração AWS (Access Key e Secret Key)
  - `flush.size`: controla a frequência de gravação no S3

---

## Como Rodar

1. **Iniciar os Conectores JDBC Source**

```bash
curl -X POST -H "Content-Type: application/json" --data @connect_jdbc_postgres_ipca_gold.config http://localhost:8083/connectors
curl -X POST -H "Content-Type: application/json" --data @connect_jdbc_postgres_pre_gold.config http://localhost:8083/connectors

curl http://localhost:8083/connectors/postg-connector-ipca-gold/status
curl http://localhost:8083/connectors/postg-connector-pre-gold/status

curl -X POST -H "Content-Type: application/json" --data @connect_s3_sink_ipca_gold.config http://localhost:8083/connectors
curl -X POST -H "Content-Type: application/json" --data @connect_s3_sink_pre_gold.config http://localhost:8083/connectors

curl http://localhost:8083/connectors/s3-sink-connector-ipca-gold/status
curl http://localhost:8083/connectors/s3-sink-connector-pre-gold/status

---

## Como validar

docker exec -it broker kafka-console-consumer --bootstrap-server broker:9092 --topic postgres-dadostesouroipca_gold --from-beginning --max-messages 5
docker exec -it broker kafka-console-consumer --bootstrap-server broker:9092 --topic postgres-dadostesouropre_gold --from-beginning --max-messages 5

## Obsrvações

O pipeline está configurado para rodar continuamente e atualizar os dados no Kafka e no S3 automaticamente.