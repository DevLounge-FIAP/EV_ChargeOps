from pathlib import Path
import pandas as pd

pasta = Path(__file__).parent.parent.parent / "data" / "brutos"
arquivos = sorted(pasta.glob("*.xlsx"))
arquivo = arquivos[0]

df = pd.read_excel(arquivo)
df = df.drop(columns=["Total Value"])
df = df.set_index("Indicator")
df = df.T
df.index = pd.to_datetime(df.index, format="%d/%m/%Y")
df.index.name = "data"
df.columns.name = None

"""
Criado para renomear as colunas tirando os caractéres especiais para não quebrar o código.
"""
mapa_colunas = {
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

nao_encontradas = set(mapa_colunas) - set(df.columns)
print("Nomes do mapa que não existem no arquivo:", nao_encontradas)

df = df.rename(columns=mapa_colunas)

print(df.columns.tolist())
print(df.head())