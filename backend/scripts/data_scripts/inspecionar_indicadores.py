"""
Script criado para validar se os indicadores presentes nos 13 arquivos XLSX batem.
"""

from pathlib import Path
import pandas as pd

pasta = Path(__file__).parent.parent.parent / "data" / "brutos"
arquivos = sorted(pasta.glob("*.xlsx"))

indicadores_por_arquivo = {}

for arq in arquivos:
    df = pd.read_excel(arq)
    indicadores_por_arquivo[arq.name] = list(df["Indicator"])

referencia = next(iter(indicadores_por_arquivo.values()))

print("Indicadores (arquivo de referência):")
for posicao, nome in enumerate(referencia):
    print(posicao, nome)

print()
diferentes = 0
for nome_arq, indicadores in indicadores_por_arquivo.items():
    if indicadores != referencia:
        diferentes += 1
        print("Indicadores diferentes em:", nome_arq)
        print("  só neste arquivo:", set(indicadores) - set(referencia))
        print("  faltando neste arquivo:", set(referencia) - set(indicadores))

if diferentes == 0:
    print(f"Os {len(arquivos)} arquivos têm os mesmos indicadores, na mesma ordem.")