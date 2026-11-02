# geobr-tools

Ferramentas geodésicas para o Brasil, em Python: **UTM**, **SAD 69 ↔ SIRGAS 2000**, **fator de escala**,
**convergência meridiana**, **áreas** e **graus/minutos/segundos**.

```bash
pip install git+https://github.com/maessa-oliveira/geobr-tools
```

```python
from geobr_tools import geo_para_utm
p = geo_para_utm(-12.9714, -38.5014)
print(p.e, p.n, p.fuso, p.hemisferio, p.fator_escala)
```

!!! note "Precisão"
    Todas as funções são comparadas com o PROJ em centenas de pontos cobrindo o Brasil.
    Veja [Validação](validacao.md).
