# geobr-tools

[![CI](https://github.com/maessa-oliveira/geobr-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/maessa-oliveira/geobr-tools/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-online-blue)](https://maessa-oliveira.github.io/geobr-tools/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](#)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green)](LICENSE)

**Ferramentas geodésicas para o Brasil, em Python puro.** Converte coordenadas geográficas ↔ UTM,
transforma **SAD 69 ↔ SIRGAS 2000** com os parâmetros oficiais do IBGE, calcula **fator de escala**,
**convergência meridiana**, **áreas** (plana UTM e geodésica) e lê/escreve **graus, minutos e segundos**
no formato que o topógrafo usa (`12°58'17,0"S`).

> 🇬🇧 *Geodetic toolkit for Brazil (UTM, SAD69 ↔ SIRGAS2000 datum transformation, scale factor,
> areas, DMS parsing). Pure Python, validated against PROJ to sub-millimetre accuracy. See [English](#english).*

## Por que existe

No dia a dia de topografia e projeto, essas contas costumam ficar espalhadas em planilhas e sites.
O `geobr-tools` reúne tudo numa biblioteca pequena, **testada** e com linha de comando — para usar em
scripts, automações de CAD/GIS ou processar um CSV inteiro de uma vez.

## Instalação

```bash
pip install git+https://github.com/maessa-oliveira/geobr-tools
```

## Uso rápido

```python
from geobr_tools import geo_para_utm, utm_para_geo, sad69_para_sirgas2000, area_geodesica

p = geo_para_utm(-12.9714, -38.5014)            # Salvador, SIRGAS 2000
print(p.e, p.n, p.fuso, p.hemisferio)           # 554076.9 8565975.5 24 S
print(p.fator_escala, p.convergencia)           # k e convergência meridiana (graus)
print(p.epsg_sirgas)                            # 31984

lat, lon = utm_para_geo(p.e, p.n, 24, "S")

# Coordenada antiga em SAD 69 -> SIRGAS 2000 (IBGE R.PR 1/2005)
lat2, lon2, h2 = sad69_para_sirgas2000(-12.9710, -38.5010, 50.0)

# Área de um polígono (lat, lon) sobre o elipsoide
lote = [(-12.9700, -38.5000), (-12.9700, -38.4991), (-12.9709, -38.4991), (-12.9709, -38.5000)]
print(area_geodesica(lote).hectares)
```

### Linha de comando

```bash
geobr utm "12°58'17\"S" "38°30'05\"W"
geobr geo 552500 8565900 --fuso 24 --hemisferio S
geobr datum -12.9710 -38.5010 --de SAD69 --para SIRGAS2000
geobr lote pontos.csv saida.csv --operacao geo2utm     # CSV com colunas lat;lon
```

O comando `lote` detecta o separador (`;`, `,` ou tab) e aceita vírgula decimal.

## O que tem dentro

| Módulo | Funções |
|---|---|
| `utm` | `geo_para_utm`, `utm_para_geo`, `fuso_de`, `meridiano_central` — séries de Krüger de 6ª ordem |
| `datum` | `sad69_para_sirgas2000`, `sirgas2000_para_sad69`, `Helmert` (7 parâmetros), conversão geodésica ↔ cartesiana |
| `area` | `area_plana` (Gauss), `area_utm`, `area_geodesica` (Karney) — com perímetro |
| `formatos` | `dms_para_graus`, `graus_para_dms` |
| `elipsoides` | GRS 80 (SIRGAS 2000), WGS 84, GRS 67 (SAD 69) |

## Qualidade

- **769 testes automatizados** (pytest), cobertura de ~96%.
- Resultados comparados com o **PROJ/pyproj** (a referência usada por QGIS, ArcGIS e AutoCAD Map) em
  centenas de pontos aleatórios cobrindo todo o Brasil: diferença **< 1 mm** em UTM e **< 0,1 mm** na ida-e-volta.
- **GitHub Actions** roda lint (ruff) e testes em Python 3.9 → 3.13 a cada commit.
- Documentação gerada automaticamente com MkDocs.

## Limitações (honestas)

- A transformação SAD 69 → SIRGAS 2000 por 3 parâmetros tem precisão **métrica**, limitação da própria
  rede SAD 69. Para trabalhos de precisão, use a grade oficial do IBGE (ProGriD).
- Não trata altitude ortométrica / modelo geoidal (MAPGEO) — planejado.

## Roadmap

- [ ] Plano Topográfico Local (NBR 14166)
- [ ] Córrego Alegre ↔ SIRGAS 2000
- [ ] Ondulação geoidal (leitura de grade MAPGEO)
- [ ] Publicação no PyPI

## Contribuindo

```bash
git clone https://github.com/maessa-oliveira/geobr-tools && cd geobr-tools
pip install -e ".[dev]"
pytest
```

---

## English

`geobr-tools` is a small, dependency-light Python library for Brazilian geodesy and surveying:
UTM forward/inverse (6th-order Krüger series), point scale factor and meridian convergence,
SAD69 ↔ SIRGAS2000 Helmert transformation (official IBGE parameters), planar and geodesic polygon
areas, and DMS parsing/formatting. It ships with a CLI for batch CSV processing and a test suite that
validates every function against PROJ.

## Autora

**Maessa Oliveira** — agrimensora e projetista, graduanda em Engenharia de Software.
[LinkedIn](https://www.linkedin.com/in/maessa-oliveira/) · Licença [MIT](LICENSE).
