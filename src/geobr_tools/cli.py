"""Linha de comando: ``geobr``.

Exemplos::

    geobr utm -12.9714 -38.5014
    geobr geo 552500 8565900 --fuso 24 --hemisferio S
    geobr datum -12.9710 -38.5010 --de SAD69 --para SIRGAS2000
    geobr lote pontos.csv saida.csv --operacao geo2utm
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Sequence

from . import __version__
from .datum import sad69_para_sirgas2000, sirgas2000_para_sad69
from .formatos import dms_para_graus, graus_para_dms
from .utm import geo_para_utm, utm_para_geo


def _num(txt: str) -> float:
    txt = txt.strip()
    try:
        return float(txt.replace(",", "."))
    except ValueError:
        return dms_para_graus(txt)


def _datum(lat: float, lon: float, h: float, de: str, para: str):
    de, para = de.upper(), para.upper()
    if de == para:
        return lat, lon, h
    if (de, para) == ("SAD69", "SIRGAS2000"):
        return sad69_para_sirgas2000(lat, lon, h)
    if (de, para) == ("SIRGAS2000", "SAD69"):
        return sirgas2000_para_sad69(lat, lon, h)
    raise SystemExit(f"Transformação não suportada: {de} -> {para}")


def _cmd_utm(a) -> None:
    p = geo_para_utm(_num(a.lat), _num(a.lon), a.datum, fuso=a.fuso)
    print(f"E = {p.e:.3f} m   N = {p.n:.3f} m   fuso {p.fuso}{p.hemisferio}")
    print(f"fator de escala k = {p.fator_escala:.8f}   convergência = {p.convergencia:+.6f}°")
    if p.epsg_sirgas and a.datum.upper() == "SIRGAS2000":
        print(f"EPSG:{p.epsg_sirgas}")


def _cmd_geo(a) -> None:
    lat, lon = utm_para_geo(a.e, a.n, a.fuso, a.hemisferio, a.datum)
    print(f"lat = {lat:.9f}  ({graus_para_dms(lat, 'lat')})")
    print(f"lon = {lon:.9f}  ({graus_para_dms(lon, 'lon')})")


def _cmd_datum(a) -> None:
    lat, lon, h = _datum(_num(a.lat), _num(a.lon), a.h, a.de, a.para)
    print(f"lat = {lat:.9f}  lon = {lon:.9f}  h = {h:.3f} m   ({a.para.upper()})")


def _cmd_lote(a) -> None:
    with open(a.entrada, newline="", encoding="utf-8-sig") as f:
        amostra = f.read(2048)
        f.seek(0)
        dialeto = csv.Sniffer().sniff(amostra, delimiters=";,\t")
        linhas = list(csv.DictReader(f, dialect=dialeto))
    if not linhas:
        raise SystemExit("Arquivo vazio.")
    saida = []
    for i, r in enumerate(linhas, start=2):
        r = {k.strip().lower(): (v or "").strip() for k, v in r.items() if k}
        try:
            if a.operacao == "geo2utm":
                p = geo_para_utm(_num(r["lat"]), _num(r["lon"]), a.datum, fuso=a.fuso)
                r.update(
                    e=f"{p.e:.3f}",
                    n=f"{p.n:.3f}",
                    fuso=f"{p.fuso}{p.hemisferio}",
                    k=f"{p.fator_escala:.8f}",
                    convergencia=f"{p.convergencia:.6f}",
                )
            elif a.operacao == "utm2geo":
                fz = r.get("fuso") or str(a.fuso or "")
                hemi = "N" if fz.upper().endswith("N") else "S"
                lat, lon = utm_para_geo(_num(r["e"]), _num(r["n"]), int(fz.rstrip("NSns")), hemi, a.datum)
                r.update(lat=f"{lat:.9f}", lon=f"{lon:.9f}")
            else:
                lat, lon, h = _datum(_num(r["lat"]), _num(r["lon"]), _num(r.get("h") or "0"), a.de, a.para)
                r.update(lat=f"{lat:.9f}", lon=f"{lon:.9f}", h=f"{h:.3f}")
        except (KeyError, ValueError) as exc:
            raise SystemExit(f"Linha {i}: {exc}") from exc
        saida.append(r)
    with open(a.saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(saida[0]), delimiter=dialeto.delimiter)
        w.writeheader()
        w.writerows(saida)
    print(f"{len(saida)} pontos gravados em {a.saida}")


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="geobr", description="Ferramentas geodésicas para o Brasil.")
    ap.add_argument("--version", action="version", version=f"geobr-tools {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("utm", help="lat/lon -> UTM")
    s.add_argument("lat"), s.add_argument("lon")
    s.add_argument("--datum", default="SIRGAS2000"), s.add_argument("--fuso", type=int)
    s.set_defaults(func=_cmd_utm)

    s = sub.add_parser("geo", help="UTM -> lat/lon")
    s.add_argument("e", type=float), s.add_argument("n", type=float)
    s.add_argument("--fuso", type=int, required=True)
    s.add_argument("--hemisferio", default="S", choices=["S", "N", "s", "n"])
    s.add_argument("--datum", default="SIRGAS2000")
    s.set_defaults(func=_cmd_geo)

    s = sub.add_parser("datum", help="SAD69 <-> SIRGAS2000")
    s.add_argument("lat"), s.add_argument("lon")
    s.add_argument("--h", type=float, default=0.0)
    s.add_argument("--de", default="SAD69"), s.add_argument("--para", default="SIRGAS2000")
    s.set_defaults(func=_cmd_datum)

    s = sub.add_parser("lote", help="processa um CSV (colunas lat,lon[,h] ou e,n,fuso)")
    s.add_argument("entrada"), s.add_argument("saida")
    s.add_argument("--operacao", choices=["geo2utm", "utm2geo", "datum"], default="geo2utm")
    s.add_argument("--datum", default="SIRGAS2000"), s.add_argument("--fuso", type=int)
    s.add_argument("--de", default="SAD69"), s.add_argument("--para", default="SIRGAS2000")
    s.set_defaults(func=_cmd_lote)

    a = ap.parse_args(argv)
    a.func(a)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
