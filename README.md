# Pipeline Kafka Connect: PostgreSQL (Gold) → Kafka → AWS S3

Este projeto implementa uma solução completa de Engenharia de Dados por meio de um pipeline ETL estruturado em três camadas: **Bronze**, **Silver** e **Gold**. A orquestração é realizada com o **Apache Airflow**, agendando execuções a cada **10 minutos**, o que caracteriza um modelo de processamento do tipo **micro-batch**. Esse formato garante um bom equilíbrio entre latência e eficiência, permitindo atualizações frequentes e consistentes no Data Lake.

A arquitetura do projeto integra tecnologias amplamente utilizadas no mercado, como **Apache Kafka**, **Apache Spark**, **PostgreSQL**, **Amazon S3** e **Kafka Connect**, todas operando em um ambiente totalmente **dockerizado**.

O pipeline conecta as **tabelas Gold** do PostgreSQL (`dadostesouroipca_gold` e `dadostesouropre_gold`) a **tópicos Kafka**, que por sua vez alimentam arquivos no formato **JSON** organizados no **AWS S3**, garantindo a **sincronização contínua dos dados** para consumo em sistemas downstream.

---

### 🎯 Objetivos Técnicos

1. **Ingestão de Dados com Kafka e PostgreSQL**  
   Implementação de pipelines de ingestão bruta usando Apache Kafka, com dados inicialmente armazenados em PostgreSQL. Serviços configurados via Docker Compose para garantir reprodutibilidade e isolamento.

2. **Criação de Pipelines ETL com Spark SQL**  
   Estrutura de processamento em camadas para limpeza, transformação e enriquecimento dos dados:

   - 🥉 **Pipeline Bronze - Ingestão Bruta**  
     - **Fonte:** Arquivos JSON com inconsistências e possíveis duplicações  
     - **Processamento:** Leitura via Spark e validação do schema  
     - **Destino:** Tabela Bronze no PostgreSQL

   - 🥈 **Pipeline Silver - Limpeza e Transformação**  
     - **Fonte:** Tabela Bronze  
     - **Processamento:**  
       - Remoção de duplicatas  
       - Tratamento de nulos e registros inválidos  
       - Padronização de formatos (strings, datas, etc.)  
     - **Destino:** Tabela Silver no PostgreSQL

   - 🥇 **Pipeline Gold - Agregação e Enriquecimento**  
     - **Fonte:** Tabela Silver  
     - **Processamento:**  
       - Cálculo de métricas agregadas (ex.: totais, médias)  
       - Preparação dos dados para análise  
     - **Destino:** Tabela Gold no PostgreSQL

3. **Integração com Data Lake no S3 via Kafka Connect**  
   Configuração de Kafka Connect Sink para envio dos dados Gold ao Data Lake na Amazon S3, com particionamento e organização adequados.

4. **Orquestração com Apache Airflow**  
   Orquestração dos pipelines Bronze → Silver → Gold para garantir execução ordenada e monitorada.

---

### 📸 Evidências do Projeto (Entregáveis)

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

### 🚀 Como Rodar

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

