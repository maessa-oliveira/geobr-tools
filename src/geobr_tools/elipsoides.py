"""Elipsoides de referência usados no Brasil."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Elipsoide:
    """Elipsoide de revolução definido pelo semieixo maior ``a`` (m) e achatamento ``f``."""

    nome: str
    a: float
    f: float

    @property
    def b(self) -> float:
        """Semieixo menor (m)."""
        return self.a * (1.0 - self.f)

    @property
    def e2(self) -> float:
        """Primeira excentricidade ao quadrado."""
        return self.f * (2.0 - self.f)

    @property
    def e(self) -> float:
        """Primeira excentricidade."""
        return math.sqrt(self.e2)

    @property
    def n(self) -> float:
        """Terceiro achatamento, usado nas séries de Krüger."""
        return self.f / (2.0 - self.f)


#: GRS 80 — elipsoide do SIRGAS 2000 (oficial no Brasil desde 2015).
GRS80 = Elipsoide("GRS 80", 6378137.0, 1.0 / 298.257222101)

#: WGS 84 — elipsoide do GPS. Na prática coincide com o GRS 80 (diferença < 0,1 mm em b).
WGS84 = Elipsoide("WGS 84", 6378137.0, 1.0 / 298.257223563)

#: Elipsoide de Referência 1967 modificado (SAD 69).
GRS67_SAD69 = Elipsoide("GRS 67 (SAD 69)", 6378160.0, 1.0 / 298.25)

ELIPSOIDES = {
    "SIRGAS2000": GRS80,
    "GRS80": GRS80,
    "WGS84": WGS84,
    "SAD69": GRS67_SAD69,
}


def obter(nome_ou_elipsoide: str | Elipsoide) -> Elipsoide:
    """Aceita um :class:`Elipsoide` ou um nome (``"SIRGAS2000"``, ``"SAD69"``, ``"WGS84"``)."""
    if isinstance(nome_ou_elipsoide, Elipsoide):
        return nome_ou_elipsoide
    chave = str(nome_ou_elipsoide).upper().replace(" ", "").replace("-", "")
    if chave not in ELIPSOIDES:
        raise ValueError(
            f"Elipsoide/datum desconhecido: {nome_ou_elipsoide!r}. Use um de {sorted(ELIPSOIDES)}."
        )
    return ELIPSOIDES[chave]
