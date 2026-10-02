import re
from pathlib import Path

import pandas as pd
import pdfplumber

PASTA_DATA = Path(__file__).parent.parent.parent / "data"
PASTA_BRUTOS = PASTA_DATA / "brutos"
PASTA_TRATADOS = PASTA_DATA / "tratados"

LIMITE_KWH_VALIDA = 0.5

PADRAO_LINHA = re.compile(
    r"(?:(?P<cartao>[A-Z0-9]{10,})\s+)?"
    r"(?P<inicio>\d\d/\d\d/\d{4} \d\d:\d\d)\s+"
    r"(?P<fim>\d\d/\d\d/\d{4} \d\d:\d\d)\s+"
    r"(?P<duracao>\d\d:\d\d:\d\d)\s+"
    r"(?P<energia>\d+\.\d\d)"
)


def ler_pdf(caminho):
    registros = []
    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text() or ""
            for linha in texto.splitlines():
                achado = PADRAO_LINHA.search(linha)
                if achado:
                    registros.append(achado.groupdict())
    return pd.DataFrame(registros)


def extrair_todos():
    pdfs = sorted(PASTA_BRUTOS.glob("Registo*carregamento*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"Nenhum PDF de registro de carregamento em {PASTA_BRUTOS}")

    df = pd.concat([ler_pdf(pdf) for pdf in pdfs], ignore_index=True)

    df["cartao_id"] = df["cartao"].fillna("")
    df["inicio"] = pd.to_datetime(df["inicio"], format="%m/%d/%Y %H:%M")
    df["fim"] = pd.to_datetime(df["fim"], format="%m/%d/%Y %H:%M")
    df["energia_kwh"] = df["energia"].astype(float)

    df["duracao_h"] = (df["fim"] - df["inicio"]).dt.total_seconds() / 3600
    df["potencia_media_kw"] = (df["energia_kwh"] / df["duracao_h"]).where(df["duracao_h"] > 0)
    df["valida"] = df["energia_kwh"] >= LIMITE_KWH_VALIDA

    df = df.drop_duplicates(subset=["inicio", "fim", "energia_kwh"])
    df = df.sort_values("inicio").reset_index(drop=True)
    return df[["inicio", "fim", "duracao_h", "energia_kwh", "potencia_media_kw", "cartao_id", "valida"]]


if __name__ == "__main__":
    sessoes = extrair_todos()
    destino = PASTA_TRATADOS / "sessoes_reais.csv"
    sessoes.to_csv(destino, index=False)

    print("Sessões lidas:", len(sessoes))
    print("Sessões válidas:", int(sessoes["valida"].sum()))
    print("Energia total (kWh):", round(sessoes["energia_kwh"].sum(), 2))
    print("Período:", sessoes["inicio"].min(), "até", sessoes["fim"].max())
    print("Salvo em:", destino)