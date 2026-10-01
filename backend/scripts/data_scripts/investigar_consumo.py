from tratar_xlsx import tratar_todos

df = tratar_todos()

df["diferenca"] = df["consumo_kwh"] - df["importacao_rede_kwh"] - df["autoconsumo_kwh"]

falhas = df[df["diferenca"].abs() >= 0.02]

print("Dias que não fecham:", len(falhas), "de", len(df))
print(falhas[["consumo_kwh", "importacao_rede_kwh", "autoconsumo_kwh", "diferenca"]].head(15))

print("Dias que não fecham, por mês:")
print(falhas.groupby(falhas.index.to_period("M")).size())

print(df["diferenca"].describe())

colunas_suspeitas = ["diferenca", "energia_descarregada_kwh", "energia_carregada_kwh", "geracao_gerador_kwh", "geracao_kwh"]
print(falhas[colunas_suspeitas].corr()["diferenca"])