# Validação

A suíte de testes (`tests/`) compara cada função com o **PROJ** (via `pyproj`):

| Verificação | Pontos | Tolerância |
|---|---|---|
| geográficas → UTM (GRS 80) | 300 aleatórios no Brasil | 1 mm |
| ida e volta UTM | 300 | 1e-9 grau (~0,1 mm) |
| fator de escala / convergência | 5 cidades | 1e-9 / 1e-7 grau |
| SAD 69 → SIRGAS 2000 | 100 aleatórios | 1e-9 grau, 1 mm em h |
| UTM no elipsoide do SAD 69 | EPSG:29194 | 1 mm |

Os testes rodam no GitHub Actions em Python 3.9 a 3.13 a cada commit.
