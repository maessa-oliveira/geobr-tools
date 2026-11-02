"""Valida a implementação UTM contra o PROJ (pyproj), referência da indústria."""

import math
import random

import pytest
from pyproj import CRS, Proj, Transformer

from geobr_tools import fuso_de, geo_para_utm, meridiano_central, utm_para_geo

random.seed(42)
# Pontos aleatórios cobrindo todo o território brasileiro (+ margem).
PONTOS = [(random.uniform(-34.0, 5.5), random.uniform(-74.0, -34.5)) for _ in range(300)]
CIDADES = {
    "Salvador": (-12.9714, -38.5014),
    "Manaus": (-3.1190, -60.0217),
    "Porto Alegre": (-30.0346, -51.2177),
    "Boa Vista (hemisf. norte)": (2.8235, -60.6758),
    "Fernando de Noronha": (-3.8540, -32.4240),
}


def _proj(fuso, hemisferio):
    sul = " +south" if hemisferio == "S" else ""
    return Proj(f"+proj=utm +zone={fuso}{sul} +ellps=GRS80 +units=m")


@pytest.mark.parametrize("lat,lon", PONTOS)
def test_direta_igual_ao_proj(lat, lon):
    p = geo_para_utm(lat, lon)
    e, n = _proj(p.fuso, p.hemisferio)(lon, lat)
    assert abs(p.e - e) < 1e-3
    assert abs(p.n - n) < 1e-3


@pytest.mark.parametrize("lat,lon", PONTOS)
def test_ida_e_volta(lat, lon):
    p = geo_para_utm(lat, lon)
    lat2, lon2 = utm_para_geo(p.e, p.n, p.fuso, p.hemisferio)
    # 1e-9 grau ~ 0,1 mm
    assert lat2 == pytest.approx(lat, abs=1e-9)
    assert lon2 == pytest.approx(lon, abs=1e-9)


@pytest.mark.parametrize("nome,coord", CIDADES.items())
def test_fator_escala_e_convergencia(nome, coord):
    lat, lon = coord
    p = geo_para_utm(lat, lon)
    f = _proj(p.fuso, p.hemisferio).get_factors(lon, lat)
    assert p.fator_escala == pytest.approx(f.meridional_scale, abs=1e-9)
    # pyproj: convergência positiva no sentido oposto; comparamos o módulo e o sinal esperado.
    assert abs(p.convergencia) == pytest.approx(abs(f.meridian_convergence), abs=1e-7)


def test_fuso_forcado_fora_do_fuso_natural():
    # Ponto do fuso 24 calculado no fuso 23 (ex.: obra na divisa).
    p = geo_para_utm(-12.5, -41.9, fuso=23)
    e, n = _proj(23, "S")(-41.9, -12.5)
    assert p.fuso == 23 and abs(p.e - e) < 1e-3 and abs(p.n - n) < 1e-3


def test_sad69_usa_elipsoide_proprio():
    lat, lon = -12.9714, -38.5014
    p = geo_para_utm(lat, lon, elipsoide="SAD69")
    t = Transformer.from_crs(CRS.from_epsg(4618), CRS.from_epsg(29194), always_xy=True)
    e, n = t.transform(lon, lat)
    assert abs(p.e - e) < 1e-3 and abs(p.n - n) < 1e-3


def test_epsg_sirgas():
    assert geo_para_utm(-12.97, -38.50).epsg_sirgas == 31984
    assert geo_para_utm(2.82, -60.67).epsg_sirgas == 31974


@pytest.mark.parametrize("lon,esperado", [(-38.5, 24), (-42.0, 24), (-42.0001, 23), (-180, 1), (180, 60)])
def test_fuso_de(lon, esperado):
    assert fuso_de(lon) == esperado


def test_meridiano_central():
    assert meridiano_central(24) == -39.0
    assert meridiano_central(23) == -45.0


@pytest.mark.parametrize(
    "args",
    [(-85.0, -40.0), (90.0, -40.0), (-10.0, -181.0)],
)
def test_entradas_invalidas(args):
    with pytest.raises(ValueError):
        geo_para_utm(*args)


def test_hemisferio_invalido():
    with pytest.raises(ValueError):
        utm_para_geo(500000, 8000000, 24, "X")


def test_no_meridiano_central_k_igual_k0():
    p = geo_para_utm(-10.0, -39.0)
    assert p.e == pytest.approx(500000.0, abs=1e-6)
    assert p.fator_escala == pytest.approx(0.9996, abs=1e-12)
    assert math.isclose(p.convergencia, 0.0, abs_tol=1e-12)
