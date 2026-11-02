"""geobr-tools — ferramentas geodésicas para o Brasil.

Conversões UTM, transformação SAD 69 <-> SIRGAS 2000, fator de escala,
convergência meridiana, áreas e formatação em graus/minutos/segundos.
"""

from .area import Area, area_geodesica, area_plana, area_utm
from .datum import (
    SAD69_PARA_SIRGAS2000,
    Helmert,
    cartesiano_para_geo,
    geo_para_cartesiano,
    sad69_para_sirgas2000,
    sirgas2000_para_sad69,
)
from .elipsoides import GRS67_SAD69, GRS80, WGS84, Elipsoide
from .formatos import dms_para_graus, graus_para_dms
from .utm import PontoUTM, fuso_de, geo_para_utm, meridiano_central, utm_para_geo

__version__ = "0.1.0"

__all__ = [
    "Area",
    "Elipsoide",
    "GRS67_SAD69",
    "GRS80",
    "Helmert",
    "PontoUTM",
    "SAD69_PARA_SIRGAS2000",
    "WGS84",
    "area_geodesica",
    "area_plana",
    "area_utm",
    "cartesiano_para_geo",
    "dms_para_graus",
    "fuso_de",
    "geo_para_cartesiano",
    "geo_para_utm",
    "graus_para_dms",
    "meridiano_central",
    "sad69_para_sirgas2000",
    "sirgas2000_para_sad69",
    "utm_para_geo",
]
