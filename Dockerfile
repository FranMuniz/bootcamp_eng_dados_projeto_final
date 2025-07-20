FROM apache/airflow:2.7.1

USER root

# Instalar Java (openjdk 11)
RUN apt-get update && apt-get install -y openjdk-11-jdk \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:${PATH}"

USER airflow

# Instalar pyspark via pip
RUN pip install pyspark

# Copiar o entrypoint customizado para dentro do container
COPY entrypoint.sh /entrypoint.sh

# Configurar o entrypoint para usar o script customizado
ENTRYPOINT ["/entrypoint.sh"]

# Comando padrão do container (airflow webserver)
CMD ["webserver"]
