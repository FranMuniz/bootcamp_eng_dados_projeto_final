# 🌀 Pipeline Kafka Connect: PostgreSQL (Gold) → Kafka → AWS S3

## 📘 Descrição

Este projeto desenvolve uma solução completa de Engenharia de Dados utilizando um pipeline ETL estruturado em três camadas (Bronze, Silver e Gold), com orquestração opcional via Airflow. A arquitetura integra tecnologias amplamente utilizadas no mercado, como Apache Kafka, Apache Spark, PostgreSQL, Amazon S3 e Kafka Connect, todos executados em ambiente Dockerizado.

O pipeline conecta as **tabelas Gold** do PostgreSQL (`dadostesouroipca_gold` e `dadostesouropre_gold`) a **tópicos Kafka**, que alimentam arquivos JSON organizados no **AWS S3**, garantindo a **sincronização contínua** dos dados para consumo downstream.

---

## 🎯 Objetivos Técnicos

1. **Ingestão de Dados com Kafka e PostgreSQL**  
   Implementação de pipelines de ingestão bruta usando Apache Kafka, com dados inicialmente armazenados em PostgreSQL. Serviços configurados via Docker Compose para garantir reprodutibilidade e isolamento.

2. **Criação de Pipelines ETL com Spark SQL**  
   Processamento dos dados em camadas:  
   - **Bronze:** Ingestão bruta de arquivos JSON com sujeiras e duplicações.  
   - **Silver:** Limpeza, tratamento de dados ausentes e padronização.  
   - **Gold:** Geração de métricas e dados prontos para análise.

3. **Integração com Data Lake no S3 via Kafka Connect**  
   Configuração de Kafka Connect Sink para envio dos dados Gold ao Data Lake na Amazon S3, com particionamento e organização adequados.

4. **Orquestração com Apache Airflow (opcional)**  
   Orquestração dos pipelines Bronze → Silver → Gold para garantir execução ordenada e monitorada.

---

## 🧱 Estrutura dos Pipelines

### 🥉 Pipeline Bronze - Ingestão Bruta
- **Fonte:** Arquivo JSON com inconsistências  
- **Processamento:** Leitura via Spark e validação do schema  
- **Destino:** Tabela Bronze no PostgreSQL ou armazenamento em Parquet/Delta

### 🥈 Pipeline Silver - Limpeza e Transformação
- **Fonte:** Tabela Bronze  
- **Processamento:**  
  - Remoção de duplicatas  
  - Tratamento de nulos e registros inválidos  
  - Padronização de formatos (strings, datas, etc.)  
- **Destino:** Tabela Silver no PostgreSQL

### 🥇 Pipeline Gold - Agregação e Enriquecimento
- **Fonte:** Tabela Silver  
- **Processamento:**  
  - Cálculo de métricas agregadas (ex.: totais, médias)  
  - Dados prontos para análise  
- **Destino:** Tabela Gold no PostgreSQL

---

## 🏗️ Arquitetura do Pipeline

1. **📡 Fonte de Dados:** PostgreSQL (camada Gold: IPCA e Prefixado)  
2. **🔄 Kafka Connect - JDBC Source:** extrai dados do PostgreSQL e publica nos tópicos Kafka  
3. **🧩 Kafka Broker:** armazena os tópicos atualizados  
4. **🌩 Kafka Connect - S3 Sink:** consome tópicos e grava arquivos JSON no bucket AWS S3  

---

## 📸 Evidências do Projeto (Entregáveis)

- Tabelas carregadas no PostgreSQL (Bronze, Silver, Gold)  
- Códigos Spark SQL utilizados (prints e logs)  
- Configurações dos tópicos Kafka e Connectors  
- Logs e screenshots da execução dos pipelines  
- Dados organizados e particionados no Amazon S3  

---

## ⚙️ Configuração dos Conectores

### 🔌 JDBC Source Connector

- Modo de operação: `bulk` (leitura completa das tabelas)  
- Principais configurações:  
  - `connector.class`: `io.confluent.connect.jdbc.JdbcSourceConnector`  
  - `connection.url`: JDBC URL para PostgreSQL  
  - `table.whitelist`: `dadostesouroipca_gold`, `dadostesouropre_gold`  
  - `topic.prefix`: `postgres-`  
  - `mode`: `bulk`  
  - `tasks.max`: `1`  

### 🪣 S3 Sink Connector

- Grava dados dos tópicos Kafka em arquivos JSON no S3  
- Principais configurações:  
  - `connector.class`: `io.confluent.connect.s3.S3SinkConnector`  
  - `topics`: `postgres-dadostesouroipca_gold`, `postgres-dadostesouropre_gold`  
  - `s3.bucket.name`: nome do bucket AWS  
  - `format.class`: `io.confluent.connect.s3.format.json.JsonFormat`  
  - `flush.size`: frequência de gravação  
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

---

### 👩‍💻 Autor

Este projeto foi desenvolvido por **Francieli Muniz** para fins **educacionais e de aprendizado prático** em engenharia de dados.

Caso tenha dúvidas, sugestões ou queira colaborar, fique à vontade para entrar em contato!

