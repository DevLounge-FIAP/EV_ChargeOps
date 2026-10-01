"""
Arquivo que trata colunas e linhas, alterando para as colunas serem os indicadores e as linhas os dias.

"""

from pathlib import Path
import pandas as pd

PASTA_BRUTOS = Path(__file__).parent.parent.parent / "data" / "brutos"

MAPA_COLUNAS = {
    "Energy Generation(kWh)": "geracao_kwh",
    "Charged Energy(kWh)": "energia_carregada_kwh",
    "Discharge Energy(kWh)": "energia_descarregada_kwh",
    "Grid Export Energy(kWh)": "exportacao_rede_kwh",
    "Import Energy(kWh)": "importacao_rede_kwh",
    "Energy Consumption(kWh)": "consumo_kwh",
    "Self-Consumption(kWh)": "autoconsumo_kwh",
    "Self- consumption Ratio(%)": "taxa_autoconsumo_pct",
    "Contribution Ratio(%)": "taxa_contribuicao_pct",
    "To-Grid Revenue(BRL (R$))": "receita_exportacao_brl",
    "Import Cost(BRL (R$))": "custo_importacao_brl",
    "Generation Revenue(BRL (R$))": "receita_geracao_brl",
    "Generator Generation(kWh)": "geracao_gerador_kwh",
}


def tratar_arquivo(caminho):
    df = pd.read_excel(caminho)
    df = df.drop(columns=["Total Value"])
    df = df.set_index("Indicator")
    df = df.T
    df.index = pd.to_datetime(df.index, format="%d/%m/%Y")
    df.index.name = "data"
    df.columns.name = None
    df = df.rename(columns=MAPA_COLUNAS)
    return df


def tratar_todos():
    arquivos = sorted(PASTA_BRUTOS.glob("*.xlsx"))
    partes = [tratar_arquivo(arq) for arq in arquivos]
    return pd.concat(partes).sort_index()


if __name__ == "__main__":
    df = tratar_todos()

    print("Formato:", df.shape)
    print("Primeira data:", df.index.min().date())
    print("Última data:", df.index.max().date())

    print("Datas duplicadas:", df.index.duplicated().sum())
    todas_as_datas = pd.date_range(df.index.min(), df.index.max(), freq="D")
    print("Dias faltando:", len(todas_as_datas.difference(df.index)))
    print("Valores nulos:", df.isna().sum().sum())
    print("Colunas corretas:", set(df.columns) == set(MAPA_COLUNAS.values()))

    tarifa_import = ((df["custo_importacao_brl"] - df["importacao_rede_kwh"]).abs() < 0.01).mean()
    tarifa_export = ((df["receita_exportacao_brl"] - df["exportacao_rede_kwh"]).abs() < 0.01).mean()
    fecha_consumo = ((df["consumo_kwh"] - df["importacao_rede_kwh"] - df["autoconsumo_kwh"]).abs() < 0.02).mean()
    print("Dias com custo de importação = kWh importado:", tarifa_import)
    print("Dias com receita de exportação = kWh exportado:", tarifa_export)
    print("Dias em que consumo = importação + autoconsumo:", fecha_consumo)

    print(df["energia_carregada_kwh"].describe())