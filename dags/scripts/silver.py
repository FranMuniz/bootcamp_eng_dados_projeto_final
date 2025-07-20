import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, upper, to_date
from dotenv import load_dotenv

def main():
    """
    Executa o pipeline de processamento da camada Silver usando PySpark.

    Objetivo:
        - Limpar, padronizar e enriquecer os dados da camada Bronze (`dadostesouroipca` e `dadostesouropre`) 
          antes de disponibilizá-los para análises e agregações na camada Gold.

    Etapas:
    1. Carrega variáveis de ambiente (.env) com credenciais AWS e PostgreSQL.
    2. Inicializa uma sessão Spark configurada para acessar dados S3 e PostgreSQL.
    3. Lê as tabelas Bronze (`dadostesouroipca` e `dadostesouropre`) do PostgreSQL.
    4. Remove registros duplicados e linhas com `null` nas colunas essenciais.
    5. Converte a coluna `dt_update` em uma nova coluna `Data_Base` (apenas data).
    6. Padroniza a coluna `Tipo` para letras maiúsculas.
    7. Exibe esquema e amostras dos dados processados.
    8. Escreve os dados tratados nas tabelas Silver:
        - `dadostesouroipca_silver`
        - `dadostesouropre_silver`

    Pré-requisitos:
        - As bibliotecas JAR necessárias (JDBC, AWS SDK e Hadoop AWS) devem estar no diretório `/opt/spark/jars/`.
        - As variáveis de ambiente AWS e PostgreSQL devem estar definidas no arquivo `.env_kafka_connect`.
        - As tabelas Bronze já devem estar populadas no PostgreSQL.
    """
    print("[INFO] Carregando variáveis de ambiente...")
    load_dotenv("/opt/airflow/.env_kafka_connect")

    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = "us-east-1"

    pg_host = os.getenv("POSTGRES_HOST")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_db = os.getenv("POSTGRES_DB")
    pg_user = os.getenv("POSTGRES_USER")
    pg_password = os.getenv("POSTGRES_PASSWORD")

    jdbc_url = f"jdbc:postgresql://{pg_host}:{pg_port}/{pg_db}"
    jdbc_properties = {
        "user": pg_user,
        "password": pg_password,
        "driver": "org.postgresql.Driver"
    }

    hadoop_aws_jar = "/opt/spark/jars/hadoop-aws-3.3.4.jar"
    aws_sdk_jar = "/opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar"
    postgres_jdbc_jar = "/opt/spark/jars/postgresql-42.6.0.jar"
    jars_path = f"{hadoop_aws_jar},{aws_sdk_jar},{postgres_jdbc_jar}"

    print("[INFO] Inicializando SparkSession...")
    spark = SparkSession.builder \
        .appName("Pipeline - Silver") \
        .config("spark.jars", jars_path) \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.access.key", aws_access_key) \
        .config("spark.hadoop.fs.s3a.secret.key", aws_secret_key) \
        .config("spark.hadoop.fs.s3a.endpoint", f"s3.{aws_region}.amazonaws.com") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "true") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .getOrCreate()

    colunas_obrigatorias = [
        "CompraManha", "VendaManha", "PUCompraManha", "PUVendaManha", "PUBaseManha", "Tipo", "dt_update"
    ]

    print("[INFO] Lendo tabela dadostesouroipca do PostgreSQL...")
    df_ipca = spark.read.jdbc(url=jdbc_url, table="public.dadostesouroipca", properties=jdbc_properties)
    print(f"[INFO] Registros lidos IPCA: {df_ipca.count()}")

    print("[INFO] Lendo tabela dadostesouropre do PostgreSQL...")
    df_pre = spark.read.jdbc(url=jdbc_url, table="public.dadostesouropre", properties=jdbc_properties)
    print(f"[INFO] Registros lidos Prefixado: {df_pre.count()}")

    print("[INFO] Removendo duplicatas e linhas com valores nulos nas colunas obrigatórias...")
    df_ipca = df_ipca.dropDuplicates().dropna(subset=colunas_obrigatorias)
    df_pre = df_pre.dropDuplicates().dropna(subset=colunas_obrigatorias)

    print(f"[INFO] Registros após limpeza IPCA: {df_ipca.count()}")
    print(f"[INFO] Registros após limpeza Prefixado: {df_pre.count()}")

    print("[INFO] Criando coluna 'Data_Base' a partir de 'dt_update' (apenas data)...")
    df_ipca = df_ipca.withColumn("Data_Base", to_date(col("dt_update")))
    df_pre = df_pre.withColumn("Data_Base", to_date(col("dt_update")))

    print("[INFO] Convertendo coluna 'Tipo' para maiúsculas...")
    df_ipca = df_ipca.withColumn("Tipo", upper(col("Tipo")))
    df_pre = df_pre.withColumn("Tipo", upper(col("Tipo")))

    print("[INFO] Exibindo esquema e amostra dos dados IPCA pós-processamento:")
    df_ipca.printSchema()
    df_ipca.show(5, truncate=False)

    print("[INFO] Exibindo esquema e amostra dos dados Prefixado pós-processamento:")
    df_pre.printSchema()
    df_pre.show(5, truncate=False)

    print("[INFO] Escrevendo dados processados para tabelas Silver no PostgreSQL...")
    df_ipca.write.jdbc(url=jdbc_url, table="public.dadostesouroipca_silver", mode="overwrite", properties=jdbc_properties)
    df_pre.write.jdbc(url=jdbc_url, table="public.dadostesouropre_silver", mode="overwrite", properties=jdbc_properties)

    print("[SUCCESS] Pipeline Silver executado com sucesso!")

if __name__ == "__main__":
    main()
