# Guia rápido

## Geográficas → UTM

```python
from geobr_tools import geo_para_utm, dms_para_graus

lat = dms_para_graus("12°58'17,0\"S")
lon = dms_para_graus("38°30'05,0\"W")
p = geo_para_utm(lat, lon)            # SIRGAS 2000 por padrão
p = geo_para_utm(lat, lon, "SAD69")   # usando o elipsoide do SAD 69
p = geo_para_utm(lat, lon, fuso=23)   # forçando o fuso (obras na divisa)
```

## UTM → geográficas

```python
from geobr_tools import utm_para_geo, graus_para_dms
lat, lon = utm_para_geo(554076.873, 8565975.452, fuso=24, hemisferio="S")
print(graus_para_dms(lat, "lat"), graus_para_dms(lon, "lon"))
```

## SAD 69 → SIRGAS 2000

```python
from geobr_tools import sad69_para_sirgas2000
lat, lon, h = sad69_para_sirgas2000(-12.9710, -38.5010, 50.0)
```

Parâmetros do IBGE (R.PR 1/2005): ΔX = −67,35 m, ΔY = +3,88 m, ΔZ = −38,22 m.

## Áreas

```python
from geobr_tools import area_geodesica, area_utm
lote = [(-12.9700, -38.5000), (-12.9700, -38.4991), (-12.9709, -38.4991), (-12.9709, -38.5000)]
print(area_geodesica(lote).hectares, area_utm(lote).hectares)
```

## Linha de comando

```bash
geobr utm -12.9714 -38.5014
geobr lote pontos.csv saida.csv --operacao geo2utm
```
