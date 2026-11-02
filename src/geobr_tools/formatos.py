"""Conversão entre graus decimais e graus/minutos/segundos (formato brasileiro)."""

from __future__ import annotations

import re

_DMS = re.compile(
    r"""^\s*(?P<sinal>[-+])?\s*
        (?P<g>\d+(?:[.,]\d+)?)\s*[°º:\s]\s*
        (?:(?P<m>\d+(?:[.,]\d+)?)\s*['′:\s]\s*)?
        (?:(?P<s>\d+(?:[.,]\d+)?)\s*(?:["″]|'')?\s*)?
        (?P<hemi>[NSEWOL])?\s*$""",
    re.IGNORECASE | re.VERBOSE,
)


def dms_para_graus(texto: str) -> float:
    """Converte '12°58\\'17,0"S', '-38 30 05.04' ou '38:30:05,04 W' em graus decimais.

    Hemisférios S, W e O (oeste) tornam o valor negativo.

    >>> round(dms_para_graus('12°58\\'17,0"S'), 6)
    -12.971389
    """
    m = _DMS.match(texto.strip())
    if not m:
        raise ValueError(f"Formato DMS não reconhecido: {texto!r}")

    def num(chave: str) -> float:
        v = m.group(chave)
        return float(v.replace(",", ".")) if v else 0.0

    g, mi, s = num("g"), num("m"), num("s")
    if mi >= 60 or s >= 60:
        raise ValueError(f"Minutos/segundos devem ser < 60: {texto!r}")
    valor = g + mi / 60.0 + s / 3600.0
    negativo = m.group("sinal") == "-" or (m.group("hemi") or "").upper() in ("S", "W", "O")
    return -valor if negativo else valor


def graus_para_dms(valor: float, eixo: str = "lat", casas: int = 4) -> str:
    """Formata graus decimais como 12°58'17,0000"S (eixo='lat') ou 38°30'05,0400"W (eixo='lon')."""
    if eixo not in ("lat", "lon"):
        raise ValueError("eixo deve ser 'lat' ou 'lon'")
    hemi = ("S" if valor < 0 else "N") if eixo == "lat" else ("W" if valor < 0 else "E")
    total = round(abs(valor) * 3600.0, casas)
    g = int(total // 3600)
    mi = int((total - g * 3600) // 60)
    s = total - g * 3600 - mi * 60
    s_txt = f"{s:0{3 + casas if casas else 2}.{casas}f}".replace(".", ",")
    return f"{g}°{mi:02d}'{s_txt}\"{hemi}"
