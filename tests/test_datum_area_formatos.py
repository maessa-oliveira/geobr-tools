import random

import pytest
from pyproj import Transformer

from geobr_tools import (
    Helmert,
    area_geodesica,
    area_plana,
    area_utm,
    cartesiano_para_geo,
    dms_para_graus,
    geo_para_cartesiano,
    graus_para_dms,
    sad69_para_sirgas2000,
    sirgas2000_para_sad69,
)

random.seed(7)
PONTOS = [(random.uniform(-33.0, 4.0), random.uniform(-73.0, -35.0)) for _ in range(100)]

# Transformação equivalente no PROJ (mesmos parâmetros IBGE R.PR 1/2005), sem grade.
PIPE = (
    "+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad "
    "+step +proj=cart +ellps=aust_SA +step +proj=helmert +x=-67.35 +y=3.88 +z=-38.22 "
    "+step +inv +proj=cart +ellps=GRS80 +step +proj=unitconvert +xy_in=rad +xy_out=deg"
)


@pytest.mark.parametrize("lat,lon", PONTOS)
def test_sad69_para_sirgas_igual_ao_proj(lat, lon):
    t = Transformer.from_pipeline(PIPE)
    lon_p, lat_p, h_p = t.transform(lon, lat, 0.0)
    lat2, lon2, h2 = sad69_para_sirgas2000(lat, lon, 0.0)
    assert lat2 == pytest.approx(lat_p, abs=1e-9)
    assert lon2 == pytest.approx(lon_p, abs=1e-9)
    assert h2 == pytest.approx(h_p, abs=1e-3)


@pytest.mark.parametrize("lat,lon", PONTOS[:30])
def test_datum_ida_e_volta(lat, lon):
    lat2, lon2, h2 = sad69_para_sirgas2000(lat, lon, 50.0)
    lat3, lon3, h3 = sirgas2000_para_sad69(lat2, lon2, h2)
    assert (lat3, lon3) == pytest.approx((lat, lon), abs=1e-9)
    assert h3 == pytest.approx(50.0, abs=1e-3)


def test_deslocamento_tipico_em_salvador():
    # Em Salvador o SAD 69 -> SIRGAS desloca ~ 60–70 m (ordem de grandeza conhecida).
    import math

    lat, lon = -12.9714, -38.5014
    lat2, lon2, _ = sad69_para_sirgas2000(lat, lon)
    dn = (lat2 - lat) * 111_000
    de = (lon2 - lon) * 111_000 * math.cos(math.radians(lat))
    assert 40 < math.hypot(dn, de) < 90


def test_cartesiano_ida_volta():
    x, y, z = geo_para_cartesiano(-12.5, -40.2, 812.345)
    lat, lon, h = cartesiano_para_geo(x, y, z)
    assert (lat, lon, h) == pytest.approx((-12.5, -40.2, 812.345), abs=1e-9)


def test_helmert_7_parametros_inversa():
    h = Helmert(10, -5, 3, 0.1, -0.2, 0.3, 1.5)
    x, y, z = 4_000_000.0, -4_500_000.0, -1_400_000.0
    x2, y2, z2 = h.inversa().aplicar(*h.aplicar(x, y, z))
    assert (x2, y2, z2) == pytest.approx((x, y, z), abs=1e-3)


def test_area_plana_quadrado():
    a = area_plana([(0, 0), (100, 0), (100, 100), (0, 100)])
    assert a.area_m2 == 10_000 and a.hectares == 1 and a.perimetro_m == 400


def test_area_plana_poligono_fechado_e_sentido():
    horario = [(0, 0), (0, 50), (80, 50), (80, 0), (0, 0)]
    assert area_plana(horario).area_m2 == 4000


def test_area_poligono_invalido():
    with pytest.raises(ValueError):
        area_plana([(0, 0), (1, 1)])


def test_area_geodesica_vs_utm():
    # Lote fictício de ~1 ha perto de Salvador: as duas áreas diferem pelo fator de escala ao quadrado.
    lote = [(-12.9700, -38.5000), (-12.9700, -38.4991), (-12.9709, -38.4991), (-12.9709, -38.5000)]
    g = area_geodesica(lote)
    u = area_utm(lote)
    assert 9_000 < g.area_m2 < 11_000
    assert u.area_m2 / g.area_m2 == pytest.approx(0.9996**2, rel=2e-4)


@pytest.mark.parametrize(
    "texto,valor",
    [
        ("12°58'17,0\"S", -12.971389),
        ("38 30 5.04 W", -38.501400),
        ("-12:58:17", -12.971389),
        ("45°O", -45.0),
        ("3°7'8.4\"N", 3.119),
    ],
)
def test_dms_para_graus(texto, valor):
    assert dms_para_graus(texto) == pytest.approx(valor, abs=1e-6)


def test_dms_invalido():
    with pytest.raises(ValueError):
        dms_para_graus("12°61'00\"S")
    with pytest.raises(ValueError):
        dms_para_graus("abc")


def test_graus_para_dms_ida_volta():
    for v in (-12.971389, -38.5014, 2.8235):
        eixo = "lat" if abs(v) < 20 and v != -38.5014 else "lon"
        assert dms_para_graus(graus_para_dms(v, eixo)) == pytest.approx(v, abs=1e-7)
    assert graus_para_dms(-12.5, "lat", casas=0) == "12°30'00\"S"
