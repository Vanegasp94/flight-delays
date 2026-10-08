"""Checks for the shared loader used by the Brazil VRA research scripts (no real data needed)."""

import importlib
import sys
from pathlib import Path

import pandas as pd
import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "research" / "brazil_vra" / "scripts"

SAMPLE = (
    "Atualizado em: 2026-08-28\n"
    '"ICAO Empresa Aérea";"Número Voo";"Código Autorização (DI)";"Código Tipo Linha";'
    '"ICAO Aeródromo Origem";"ICAO Aeródromo Destino";"Partida Prevista";"Partida Real";'
    '"Chegada Prevista";"Chegada Real";"Situação Voo";"Código Justificativa"\n'
    '"AAA";"0001";"0";"N";"SBGR";"SBSP";"2026-07-18 10:30:00";"2026-07-18 10:24:00";'
    '"2026-07-18 11:35:00";"2026-07-18 11:20:00";"REALIZADO";"N/A"\n'
    '"AAA";"0002";"0";"I";"SBGR";"SCEL";"2026-07-17 11:00:00.100000000";"null";'
    '"2026-07-17 16:55:00.100000000";"null";"CANCELADO";"N/A"\n'
    '"AAA";"0003";"0";"N";"SBSP";"SBRJ";"01/11/2018 16:55";"";"01/11/2018 17:55";"";'
    '"REALIZADO";"N/A"\n'
)


@pytest.fixture
def common(monkeypatch, tmp_path):
    (tmp_path / "vra").mkdir()
    (tmp_path / "vra" / "VRA_20267.csv").write_text(SAMPLE, encoding="utf-8-sig")
    monkeypatch.setenv("BRAZIL_VRA_DATA_DIR", str(tmp_path))
    monkeypatch.syspath_prepend(str(SCRIPTS))
    sys.modules.pop("_common", None)
    module = importlib.import_module("_common")
    yield module
    sys.modules.pop("_common", None)


def test_data_dir_comes_from_environment(common, tmp_path):
    assert common.DATA_DIR == tmp_path
    assert common.vra_path(2026, 7) == tmp_path / "vra" / "VRA_20267.csv"


def test_load_keeps_raw_strings_and_parses_all_formats(common):
    df = common.load(2026, 7)
    assert len(df) == 3
    assert list(df.columns[:12]) == common.C
    # raw values are untouched
    assert df.pr.tolist() == ["2026-07-18 10:24:00", "null", ""]
    assert df.pp[1] == "2026-07-17 11:00:00.100000000"
    # parsed copies: ISO, ISO with fractional suffix, dd/mm/yyyy
    assert df.pp_t[0] == pd.Timestamp("2026-07-18 10:30:00")
    assert df.pp_t[1] == pd.Timestamp("2026-07-17 11:00:00")
    assert df.pp_t[2] == pd.Timestamp("2018-11-01 16:55:00")
    # 'null' and empty strings become NaT
    assert df.pr_t.isna().tolist() == [False, True, True]


def test_download_month_list(common):
    download = importlib.import_module("download")
    months = download.vra_months()
    assert len(months) == 103
    assert (2014, 7) not in months and (2014, 8) in months
    assert months[-1] == (2026, 7)
    assert download.vra_url(2020, 3).endswith("/2020/03%20-%20Mar%C3%A7o/VRA_20203.csv")
    sys.modules.pop("download", None)
