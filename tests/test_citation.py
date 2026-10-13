"""Tests of the citation metadata."""

import json
from pathlib import Path

import fairvis

ROOT = Path(__file__).parent.parent
CITATION = ROOT / "CITATION.cff"
ZENODO = ROOT / ".zenodo.json"
ORCID = "0000-0003-1725-179X"


def test_citation_version() -> None:
    # bump-my-version updates the `version` of the software; the `cff-version`
    # is the version of the citation file format and must stay a valid one
    lines = CITATION.read_text(encoding="utf-8").splitlines()
    assert f'version: "{fairvis.__version__}"' in lines
    assert "cff-version: 1.2.0" in lines


def test_citation_and_zenodo_agree() -> None:
    lines = CITATION.read_text(encoding="utf-8").splitlines()
    zenodo = json.loads(ZENODO.read_text(encoding="utf-8"))
    assert "license: MIT" in lines
    assert zenodo["license"] == "MIT"
    assert f'    orcid: "https://orcid.org/{ORCID}"' in lines
    assert [creator["orcid"] for creator in zenodo["creators"]] == [ORCID]
    assert 'doi: "10.5281/zenodo.13755820"' in lines
    assert "matthiaskoenig/pymetadata" not in ZENODO.read_text(encoding="utf-8")
