import csv

from geobr_tools.cli import main


def test_cli_utm(capsys):
    main(["utm", "-12.9714", "-38.5014"])
    out = capsys.readouterr().out
    assert "fuso 24S" in out and "EPSG:31984" in out


def test_cli_utm_aceita_dms(capsys):
    main(["utm", "12°58'17\"S", "38°30'05\"W"])
    assert "fuso 24S" in capsys.readouterr().out


def test_cli_geo(capsys):
    main(["geo", "500000", "8565900", "--fuso", "24"])
    out = capsys.readouterr().out
    assert "lon = -39.000000000" in out


def test_cli_datum(capsys):
    main(["datum", "-12.9710", "-38.5010"])
    assert "SIRGAS2000" in capsys.readouterr().out


def test_cli_lote_geo2utm(tmp_path):
    ent = tmp_path / "pontos.csv"
    ent.write_text("ponto;lat;lon\nP1;-12,9714;-38,5014\nP2;-12,9800;-38,4900\n", encoding="utf-8")
    sai = tmp_path / "saida.csv"
    main(["lote", str(ent), str(sai)])
    linhas = list(csv.DictReader(sai.open(encoding="utf-8"), delimiter=";"))
    assert len(linhas) == 2 and linhas[0]["fuso"] == "24S" and float(linhas[0]["e"]) > 500000


def test_cli_lote_utm2geo(tmp_path):
    ent = tmp_path / "utm.csv"
    ent.write_text("id,e,n,fuso\nA,500000,8565900,24S\n", encoding="utf-8")
    sai = tmp_path / "geo.csv"
    main(["lote", str(ent), str(sai), "--operacao", "utm2geo"])
    linha = next(csv.DictReader(sai.open(encoding="utf-8")))
    assert abs(float(linha["lon"]) + 39.0) < 1e-9
