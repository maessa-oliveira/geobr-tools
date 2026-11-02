"""Área e perímetro de polígonos: no plano UTM e sobre o elipsoide (geodésica)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from geographiclib.geodesic import Geodesic

from .elipsoides import GRS80, Elipsoide, obter
from .utm import geo_para_utm


@dataclass(frozen=True)
class Area:
    area_m2: float
    perimetro_m: float

    @property
    def hectares(self) -> float:
        return self.area_m2 / 10_000.0


def _fechar(pontos: Sequence[tuple[float, float]]) -> list[tuple[float, float]]:
    pts = [tuple(map(float, p[:2])) for p in pontos]
    if len(pts) < 3:
        raise ValueError("Um polígono precisa de pelo menos 3 vértices.")
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    return pts


def area_plana(pontos: Sequence[tuple[float, float]]) -> Area:
    """Área (fórmula de Gauss / shoelace) e perímetro de coordenadas planas (E, N)."""
    pts = _fechar(pontos)
    s = 0.0
    per = 0.0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        s += x1 * y2 - x2 * y1
        per += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return Area(abs(s) / 2.0, per)


def area_utm(
    pontos_geo: Sequence[tuple[float, float]],
    elipsoide: str | Elipsoide = GRS80,
    fuso: int | None = None,
) -> Area:
    """Área no plano UTM de um polígono dado em (lat, lon). Todos os vértices no mesmo fuso."""
    pts = _fechar(pontos_geo)
    fuso = fuso or geo_para_utm(*pts[0], elipsoide=elipsoide).fuso
    plano = [(p.e, p.n) for p in (geo_para_utm(lat, lon, elipsoide, fuso=fuso) for lat, lon in pts)]
    return area_plana(plano)


def area_geodesica(pontos_geo: Sequence[tuple[float, float]], elipsoide: str | Elipsoide = GRS80) -> Area:
    """Área sobre o elipsoide (algoritmo de Karney / GeographicLib). Vértices em (lat, lon)."""
    el = obter(elipsoide)
    poly = Geodesic(el.a, el.f).Polygon()
    for lat, lon in _fechar(pontos_geo):
        poly.AddPoint(lat, lon)
    _, perimetro, area = poly.Compute(False, True)
    return Area(abs(area), perimetro)
