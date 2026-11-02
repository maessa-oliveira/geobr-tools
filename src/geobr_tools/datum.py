"""Transformação de datum (SAD 69 <-> SIRGAS 2000) por parâmetros de Helmert.

Parâmetros oficiais do IBGE (Resolução do Presidente R.PR 1/2005):

    SAD 69 -> SIRGAS 2000:  ΔX = -67,35 m   ΔY = +3,88 m   ΔZ = -38,22 m

A precisão da transformação por 3 parâmetros é de ordem métrica (limitação
da própria realização do SAD 69). Para trabalhos de precisão em áreas
cobertas, o IBGE recomenda o ProGriD/grade de transformação.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .elipsoides import GRS67_SAD69, GRS80, Elipsoide, obter


@dataclass(frozen=True)
class Helmert:
    """Transformação de Helmert de 7 parâmetros (convenção 'position vector').

    Translações em metros, rotações em segundos de arco e escala em ppm.
    """

    tx: float
    ty: float
    tz: float
    rx: float = 0.0
    ry: float = 0.0
    rz: float = 0.0
    s_ppm: float = 0.0

    def aplicar(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        rx, ry, rz = (math.radians(v / 3600.0) for v in (self.rx, self.ry, self.rz))
        m = 1.0 + self.s_ppm * 1e-6
        return (
            self.tx + m * (x - rz * y + ry * z),
            self.ty + m * (rz * x + y - rx * z),
            self.tz + m * (-ry * x + rx * y + z),
        )

    def inversa(self) -> Helmert:
        """Inversa aproximada (exata para 3 parâmetros; erro < 0,1 mm para rotações pequenas)."""
        return Helmert(-self.tx, -self.ty, -self.tz, -self.rx, -self.ry, -self.rz, -self.s_ppm)


#: IBGE R.PR 1/2005
SAD69_PARA_SIRGAS2000 = Helmert(-67.35, 3.88, -38.22)


def geo_para_cartesiano(
    lat: float, lon: float, h: float = 0.0, elipsoide: str | Elipsoide = GRS80
) -> tuple[float, float, float]:
    """Geodésicas (graus, metros) -> cartesianas geocêntricas X, Y, Z (m)."""
    el = obter(elipsoide)
    phi, lam = math.radians(lat), math.radians(lon)
    N = el.a / math.sqrt(1 - el.e2 * math.sin(phi) ** 2)
    return (
        (N + h) * math.cos(phi) * math.cos(lam),
        (N + h) * math.cos(phi) * math.sin(lam),
        (N * (1 - el.e2) + h) * math.sin(phi),
    )


def cartesiano_para_geo(
    x: float, y: float, z: float, elipsoide: str | Elipsoide = GRS80
) -> tuple[float, float, float]:
    """Cartesianas geocêntricas -> (lat, lon, h) em graus e metros (iterativo)."""
    el = obter(elipsoide)
    lam = math.atan2(y, x)
    p = math.hypot(x, y)
    phi = math.atan2(z, p * (1 - el.e2))
    h = 0.0
    for _ in range(10):
        N = el.a / math.sqrt(1 - el.e2 * math.sin(phi) ** 2)
        h = p / math.cos(phi) - N
        novo = math.atan2(z, p * (1 - el.e2 * N / (N + h)))
        if abs(novo - phi) < 1e-13:
            phi = novo
            break
        phi = novo
    N = el.a / math.sqrt(1 - el.e2 * math.sin(phi) ** 2)
    h = p / math.cos(phi) - N
    return math.degrees(phi), math.degrees(lam), h


def transformar(
    lat: float,
    lon: float,
    h: float,
    origem: str | Elipsoide,
    destino: str | Elipsoide,
    helmert: Helmert,
) -> tuple[float, float, float]:
    """Transformação genérica: geodésicas -> XYZ -> Helmert -> geodésicas."""
    x, y, z = geo_para_cartesiano(lat, lon, h, origem)
    return cartesiano_para_geo(*helmert.aplicar(x, y, z), destino)


def sad69_para_sirgas2000(lat: float, lon: float, h: float = 0.0) -> tuple[float, float, float]:
    """SAD 69 -> SIRGAS 2000 (parâmetros IBGE R.PR 1/2005).

    Exemplo:
        >>> lat, lon, h = sad69_para_sirgas2000(-12.9710, -38.5010)
    """
    return transformar(lat, lon, h, GRS67_SAD69, GRS80, SAD69_PARA_SIRGAS2000)


def sirgas2000_para_sad69(lat: float, lon: float, h: float = 0.0) -> tuple[float, float, float]:
    """SIRGAS 2000 -> SAD 69 (inversa da R.PR 1/2005)."""
    return transformar(lat, lon, h, GRS80, GRS67_SAD69, SAD69_PARA_SIRGAS2000.inversa())
