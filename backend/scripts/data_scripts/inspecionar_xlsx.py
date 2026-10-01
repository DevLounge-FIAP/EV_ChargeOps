"""
Esse algoritmo foi criado para validar se todos os 13 arquivos contém exatamente as mesmas colunas.
"""

from pathlib import Path #biblioteca que facilita o caminho das pastas
import pandas as pd

pasta = Path(__file__).parent.parent.parent / "data" / "brutos"
arquivos = sorted(pasta.glob("*.xlsx")) #procura todos os arquivos na pasta "brutos" que terminam com .slx. "*" ignora o nome do arquivo.
print(f"{len(arquivos)} arquivos encontrados\n")

colunas_por_arquivo = {} #dicionário com os arquivos encontrados.

for arq in arquivos:
    xls = pd.ExcelFile(arq)
    print("=" * 60)
    print("Arquivo:", arq.name)
    print("Abas:", xls.sheet_names)

    for aba in xls.sheet_names:
        df = xls.parse(aba)
        print(f"  Aba '{aba}': {df.shape[0]} linhas x {df.shape[1]} colunas")
        colunas_por_arquivo[(arq.name, aba)] = list(df.columns)

# Compara se todos os arquivos têm as mesmas colunas
print("\n" + "=" * 60)
referencia = next(iter(colunas_por_arquivo.values()))
for chave, cols in colunas_por_arquivo.items():
    if cols != referencia:
        print("Colunas diferentes em:", chave)

# Detalhe do primeiro arquivo
primeiro = pd.read_excel(arquivos[0])
print("\nColunas e tipos (primeiro arquivo):")
print(primeiro.dtypes)
print("\nPrimeiras 10 linhas:")
print(primeiro.head(10).to_string())
print("\nValores faltando:")
print(primeiro.isna().sum())