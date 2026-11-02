"""Projeção UTM (Transversa de Mercator) com as séries de Krüger de 6ª ordem.

Precisão melhor que 1 mm dentro do fuso (e alguns graus além dele), validada
contra o PROJ nos testes automatizados.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .elipsoides import GRS80, Elipsoide, obter

K0 = 0.9996
FALSO_E = 500_000.0
FALSO_N_SUL = 10_000_000.0


@dataclass(frozen=True)
class PontoUTM:
    """Coordenada UTM com fator de escala e convergência meridiana."""

    e: float
    n: float
    fuso: int
    hemisferio: str  # "S" ou "N"
    fator_escala: float
    convergencia: float  # graus, positivo a leste do meridiano central

    @property
    def epsg_sirgas(self) -> int | None:
        """Código EPSG do SIRGAS 2000 / UTM para este fuso (Brasil: fusos 17 a 25)."""
        if self.hemisferio == "S" and 17 <= self.fuso <= 25:
            return 31960 + self.fuso
        if self.hemisferio == "N" and 17 <= self.fuso <= 22:
            return 31954 + self.fuso
        return None


def _coef(elip: Elipsoide):
    n = elip.n
    n2, n3, n4, n5, n6 = n**2, n**3, n**4, n**5, n**6
    A = elip.a / (1 + n) * (1 + n2 / 4 + n4 / 64 + n6 / 256)
    alfa = (
        n / 2 - 2 * n2 / 3 + 5 * n3 / 16 + 41 * n4 / 180 - 127 * n5 / 288 + 7891 * n6 / 37800,
        13 * n2 / 48 - 3 * n3 / 5 + 557 * n4 / 1440 + 281 * n5 / 630 - 1983433 * n6 / 1935360,
        61 * n3 / 240 - 103 * n4 / 140 + 15061 * n5 / 26880 + 167603 * n6 / 181440,
        49561 * n4 / 161280 - 179 * n5 / 168 + 6601661 * n6 / 7257600,
        34729 * n5 / 80640 - 3418889 * n6 / 1995840,
        212378941 * n6 / 319334400,
    )
    beta = (
        n / 2 - 2 * n2 / 3 + 37 * n3 / 96 - n4 / 360 - 81 * n5 / 512 + 96199 * n6 / 604800,
        n2 / 48 + n3 / 15 - 437 * n4 / 1440 + 46 * n5 / 105 - 1118711 * n6 / 3870720,
        17 * n3 / 480 - 37 * n4 / 840 - 209 * n5 / 4480 + 5569 * n6 / 90720,
        4397 * n4 / 161280 - 11 * n5 / 504 - 830251 * n6 / 7257600,
        4583 * n5 / 161280 - 108847 * n6 / 3991680,
        20648693 * n6 / 638668800,
    )
    return A, alfa, beta


def fuso_de(lon: float) -> int:
    """Número do fuso UTM (1–60) para a longitude em graus."""
    if not -180.0 <= lon <= 180.0:
        raise ValueError(f"Longitude fora do intervalo: {lon}")
    return min(int((lon + 180.0) // 6.0) + 1, 60)


def meridiano_central(fuso: int) -> float:
    """Longitude do meridiano central do fuso, em graus."""
    if not 1 <= fuso <= 60:
        raise ValueError(f"Fuso inválido: {fuso}")
    return fuso * 6.0 - 183.0


def geo_para_utm(
    lat: float,
    lon: float,
    elipsoide: str | Elipsoide = GRS80,
    fuso: int | None = None,
) -> PontoUTM:
    """Converte latitude/longitude (graus decimais) em UTM.

    Args:
        lat: latitude em graus (negativa no hemisfério sul).
        lon: longitude em graus (negativa a oeste).
        elipsoide: ``"SIRGAS2000"`` (padrão), ``"SAD69"``, ``"WGS84"`` ou um :class:`Elipsoide`.
        fuso: força um fuso (útil perto da divisa entre fusos). Se omitido, é calculado.

    Exemplo:
        >>> p = geo_para_utm(-12.9714, -38.5014)  # Salvador
        >>> p.fuso, p.hemisferio
        (24, 'S')
    """
    if not -80.0 <= lat <= 84.0:
        raise ValueError(f"Latitude fora da faixa UTM (-80 a 84): {lat}")
    elip = obter(elipsoide)
    fuso = fuso or fuso_de(lon)
    A, alfa, _ = _coef(elip)
    e = elip.e

    phi = math.radians(lat)
    dlam = math.radians(lon - meridiano_central(fuso))

    t = math.sinh(math.atanh(math.sin(phi)) - e * math.atanh(e * math.sin(phi)))
    xi_l = math.atan2(t, math.cos(dlam))
    eta_l = math.atanh(math.sin(dlam) / math.sqrt(1 + t * t))

    xi, eta, sigma, tau = xi_l, eta_l, 1.0, 0.0
    for j, a_j in enumerate(alfa, start=1):
        s2, c2 = math.sin(2 * j * xi_l), math.cos(2 * j * xi_l)
        sh2, ch2 = math.sinh(2 * j * eta_l), math.cosh(2 * j * eta_l)
        xi += a_j * s2 * ch2
        eta += a_j * c2 * sh2
        sigma += 2 * j * a_j * c2 * ch2
        tau += 2 * j * a_j * s2 * sh2

    hemisferio = "S" if lat < 0 else "N"
    e_utm = FALSO_E + K0 * A * eta
    n_utm = K0 * A * xi + (FALSO_N_SUL if hemisferio == "S" else 0.0)

    k = (
        K0
        * A
        / elip.a
        * math.sqrt(
            (1 + ((1 - elip.n) / (1 + elip.n) * math.tan(phi)) ** 2)
            * (sigma**2 + tau**2)
            / (t * t + math.cos(dlam) ** 2)
        )
    )
    gama = math.atan(t / math.sqrt(1 + t * t) * math.tan(dlam)) + math.atan2(tau, sigma)

    return PontoUTM(e_utm, n_utm, fuso, hemisferio, k, math.degrees(gama))


def _lat_de_tau_conforme(tau_l: float, e2: float) -> float:
    """Inverte tau' (tangente da latitude conforme) -> latitude geodésica (Newton)."""
    e = math.sqrt(e2)
    tau = tau_l
    for _ in range(8):
        tau1 = math.sqrt(1 + tau * tau)
        sig = math.sinh(e * math.atanh(e * tau / tau1))
        taup = tau * math.sqrt(1 + sig * sig) - sig * tau1
        dtau = (tau_l - taup) / math.sqrt(1 + taup * taup) * (1 + (1 - e2) * tau * tau) / ((1 - e2) * tau1)
        tau += dtau
        if abs(dtau) < 1e-14:
            break
    return math.atan(tau)


def utm_para_geo(
    e: float,
    n: float,
    fuso: int,
    hemisferio: str = "S",
    elipsoide: str | Elipsoide = GRS80,
) -> tuple[float, float]:
    """Converte UTM em (latitude, longitude) em graus decimais.

    Exemplo:
        >>> lat, lon = utm_para_geo(552_500.0, 8_565_900.0, 24, "S")
    """
    hemisferio = hemisferio.upper()
    if hemisferio not in ("S", "N"):
        raise ValueError("hemisferio deve ser 'S' ou 'N'")
    elip = obter(elipsoide)
    A, _, beta = _coef(elip)

    xi = (n - (FALSO_N_SUL if hemisferio == "S" else 0.0)) / (K0 * A)
    eta = (e - FALSO_E) / (K0 * A)

    xi_l, eta_l = xi, eta
    for j, b_j in enumerate(beta, start=1):
        xi_l -= b_j * math.sin(2 * j * xi) * math.cosh(2 * j * eta)
        eta_l -= b_j * math.cos(2 * j * xi) * math.sinh(2 * j * eta)

    tau_l = math.sin(xi_l) / math.sqrt(math.sinh(eta_l) ** 2 + math.cos(xi_l) ** 2)
    phi = _lat_de_tau_conforme(tau_l, elip.e2)
    dlam = math.atan2(math.sinh(eta_l), math.cos(xi_l))

    return math.degrees(phi), meridiano_central(fuso) + math.degrees(dlam)
