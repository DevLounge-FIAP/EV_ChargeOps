from pathlib import Path
import pandas as pd
from tratar_xlsx import tratar_todos

PASTA_TRATADOS = Path(__file__).parent.parent.parent / "data" / "tratados"
PASTA_TRATADOS.mkdir(parents=True, exist_ok=True)

df = tratar_todos()

destino = PASTA_TRATADOS / "estacao_diario.csv"
df.to_csv(destino)

lido = pd.read_csv(destino, index_col="data", parse_dates=True)
print("Salvo em:", destino)
print("Formato lido de volta:", lido.shape)
print("Índice é data:", pd.api.types.is_datetime64_any_dtype(lido.index))
print("Igual ao original:", lido.round(4).equals(df.round(4)))