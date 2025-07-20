from pyspark.sql import SparkSession
from dotenv import load_dotenv
import os

def main():
    """
    Executa o pipeline de transformação de dados da camada Silver para Gold usando PySpark.

    Etapas:
    1. Carrega variáveis de ambiente do arquivo `.env`.
    2. Cria conexão JDBC com banco de dados PostgreSQL.
    3. Lê dados das tabelas Silver (`dadostesouroipca_silver` e `dadostesouropre_silver`).
    4. Cria views temporárias no Spark para processamento com SQL.
    5. Realiza agregações:
       - Calcula média de taxas e preços unitários.
       - Calcula percentual de diferença entre taxa de venda e de compra.
       - Agrupa por `Data_Base` e `Tipo`.
    6. Escreve os dados transformados em tabelas Gold (`dadostesouroipca_gold` e `dadostesouropre_gold`).
    
    Requisitos:
        - O driver JDBC do PostgreSQL deve estar disponível no caminho `/opt/spark/jars/postgresql-42.6.0.jar`.
        - As variáveis de ambiente com configurações do PostgreSQL devem estar no arquivo `/opt/airflow/.env_kafka_connect`.
    
    Banco de destino:
        PostgreSQL com as tabelas:
            - public.dadostesouroipca_gold
            - public.dadostesouropre_gold
    """
    print("[INFO] Carregando variáveis de ambiente...")
    load_dotenv("/opt/airflow/.env_kafka_connect")

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

    print("[INFO] Inicializando SparkSession...")
    spark = SparkSession.builder \
        .appName("Pipeline - Gold") \
        .config("spark.jars", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .getOrCreate()

    print("[INFO] Lendo tabelas Silver do PostgreSQL...")
    df_ipca = spark.read.jdbc(
        url=jdbc_url,
        table="public.dadostesouroipca_silver",
        properties=jdbc_properties
    )
    print(f"[INFO] Registros IPCA Silver: {df_ipca.count()}")
    df_ipca.printSchema()
    df_ipca.show(5, truncate=False)

    df_pre = spark.read.jdbc(
        url=jdbc_url,
        table="public.dadostesouropre_silver",
        properties=jdbc_properties
    )
    print(f"[INFO] Registros Prefixado Silver: {df_pre.count()}")
    df_pre.printSchema()
    df_pre.show(5, truncate=False)

    print("[INFO] Registrando views temporárias...")
    df_ipca.createOrReplaceTempView("ipca_silver")
    df_pre.createOrReplaceTempView("pre_silver")

    print("[INFO] Executando agregação para IPCA Gold...")
    df_ipca_gold = spark.sql("""
        SELECT
            Data_Base,
            Tipo,
            COUNT(*) AS qtde_registros,
            AVG(CompraManha) AS compra_manha_media,
            AVG(VendaManha) AS venda_manha_media,
            AVG(PUCompraManha) AS pu_compra_manha_media,
            AVG(PUVendaManha) AS pu_venda_manha_media,
            AVG(PUBaseManha) AS pu_base_manha_media,
            AVG(100 * (VendaManha - CompraManha) / CompraManha) AS percentual_diferenca_compra_venda
        FROM ipca_silver
        GROUP BY Data_Base, Tipo
        ORDER BY Data_Base, Tipo
    """)
    print(f"[INFO] Resultados agregados IPCA Gold: {df_ipca_gold.count()}")
    df_ipca_gold.printSchema()
    df_ipca_gold.show(5, truncate=False)

    print("[INFO] Executando agregação para Prefixado Gold...")
    df_pre_gold = spark.sql("""
        SELECT
            Data_Base,
            Tipo,
            COUNT(*) AS qtde_registros,
            AVG(CompraManha) AS compra_manha_media,
            AVG(VendaManha) AS venda_manha_media,
            AVG(PUCompraManha) AS pu_compra_manha_media,
            AVG(PUVendaManha) AS pu_venda_manha_media,
            AVG(PUBaseManha) AS pu_base_manha_media,
            AVG(100 * (VendaManha - CompraManha) / CompraManha) AS percentual_diferenca_compra_venda
        FROM pre_silver
        GROUP BY Data_Base, Tipo
        ORDER BY Data_Base, Tipo
    """)
    print(f"[INFO] Resultados agregados Prefixado Gold: {df_pre_gold.count()}")
    df_pre_gold.printSchema()
    df_pre_gold.show(5, truncate=False)

    print("[INFO] Escrevendo tabelas Gold no PostgreSQL...")
    df_ipca_gold.write.jdbc(
        url=jdbc_url,
        table="public.dadostesouroipca_gold",
        mode="overwrite",
        properties=jdbc_properties
    )
    df_pre_gold.write.jdbc(
        url=jdbc_url,
        table="public.dadostesouropre_gold",
        mode="overwrite",
        properties=jdbc_properties
    )

    print("[SUCCESS] Pipeline Gold executado com sucesso!")

if __name__ == "__main__":
    main()
