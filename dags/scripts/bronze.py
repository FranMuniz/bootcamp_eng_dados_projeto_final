import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta 

def busca_titulos_tesouro_direto():
    """
    Faz o download dos dados públicos de preços e taxas dos títulos do Tesouro Direto 
    diretamente do site Tesouro Transparente, processa e retorna um DataFrame com índice multinível.

    Returns:
        pd.DataFrame: DataFrame contendo os dados dos títulos do Tesouro Direto,
                      com índice multinível (Tipo de Título, Data de Vencimento, Data Base).
    """
    print("Iniciando download dos títulos do Tesouro Direto...")
    url = 'https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv'
    df = pd.read_csv(url, sep=';', decimal=',')
    df['Data Vencimento'] = pd.to_datetime(df['Data Vencimento'], dayfirst=True)
    df['Data Base'] = pd.to_datetime(df['Data Base'], dayfirst=True)
    multi_indice = pd.MultiIndex.from_frame(df.iloc[:, :3])
    df = df.set_index(multi_indice).iloc[:, 3:]
    print("Download concluído com sucesso.")
    return df

def gerar_timestamps_simulados(df, start_time=None, interval_ms=100):
    """
    Adiciona uma coluna de timestamps simulados ao DataFrame, com intervalo definido entre as linhas.

    Args:
        df (pd.DataFrame): DataFrame de entrada ao qual serão adicionados os timestamps.
        start_time (datetime, optional): Horário inicial para os timestamps. 
                                         Se None, usa uma hora antes do tempo atual.
        interval_ms (int, optional): Intervalo entre os timestamps em milissegundos. Padrão é 100ms.

    Returns:
        pd.DataFrame: DataFrame com uma nova coluna 'dt_update' contendo os timestamps simulados.
    """
    if start_time is None:
        start_time = datetime.now() - timedelta(hours=1)
    timestamps = [start_time + timedelta(milliseconds=i * interval_ms) for i in range(len(df))]
    df = df.copy()
    df['dt_update'] = timestamps
    return df

def run():
    """
    Executa o pipeline de ingestão de dados (camada Bronze) dos títulos do Tesouro Direto.
    Realiza:
        - Download dos dados do Tesouro.
        - Filtragem dos títulos do tipo IPCA+ e Prefixado.
        - Adição de timestamps simulados.
        - Renomeação de colunas.
        - Exportação para tabelas PostgreSQL específicas por tipo de título.
    """
    print("Iniciando o pipeline Bronze dos títulos do Tesouro Direto...")

    titulos = busca_titulos_tesouro_direto()

    # Cria coluna "Tipo"
    titulos.loc[titulos.index.get_level_values(0) == 'Tesouro Prefixado', 'Tipo'] = "PRE-FIXADOS"
    titulos.loc[titulos.index.get_level_values(0) == 'Tesouro IPCA+', 'Tipo'] = "IPCA"

    print("Filtrando e processando títulos IPCA e Prefixado...")
    ipca = titulos.loc[('Tesouro IPCA+')].copy()
    prefixado = titulos.loc[('Tesouro Prefixado')].copy()

    # Gera timestamps simulados com intervalo de 100ms
    ipca = gerar_timestamps_simulados(ipca, interval_ms=100)
    prefixado = gerar_timestamps_simulados(prefixado, interval_ms=100)

    rename_cols = {
        "Taxa Compra Manha": "CompraManha",
        "Taxa Venda Manha": "VendaManha",
        "PU Compra Manha": "PUCompraManha",
        "PU Venda Manha": "PUVendaManha",
        "PU Base Manha": "PUBaseManha",
        "Data Vencimento": "DataVencimento",
        "Data Base": "Data_Base"
    }

    ipca = ipca.rename(columns=rename_cols)
    prefixado = prefixado.rename(columns=rename_cols)

    print("Criando engine de conexão com PostgreSQL...")
    connection_string = "postgresql://postgres:postgres@postgres:5432/postgres"
    engine = create_engine(connection_string)

    print("Exportando dados IPCA para a tabela 'dadostesouroipca'...")
    ipca.to_sql("dadostesouroipca", con=engine, if_exists="append", index=False)
    
    print("Exportando dados Prefixado para a tabela 'dadostesouropre'...")
    prefixado.to_sql("dadostesouropre", con=engine, if_exists="append", index=False)

    print("Pipeline Bronze executado com sucesso!")

if __name__ == "__main__":
    run()
