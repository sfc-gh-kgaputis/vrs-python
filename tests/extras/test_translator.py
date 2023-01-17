import pytest

from ga4gh.vrs import models

snv_inputs = {
    "hgvs": "NC_000013.11:g.32936732G>C",
    "beacon": "13 : 32936732 G > C",
    "spdi": "NC_000013.11:32936731:1:C",
    "gnomad": "13-32936732-G-C"
}

snv_output = {
    "location": {
        "interval": {
            "end": {"value": 32936732, "type": "Number"},
            "start": {"value": 32936731, "type": "Number"},
            "type": "SequenceInterval"
        },
        "sequence_id": "ga4gh:SQ._0wi-qoDrvram155UmcSC-zA5ZK4fpLT",
        "type": "SequenceLocation"
    },
    "state": {
        "sequence": "C",
        "type": "LiteralSequenceExpression"
    },
    "type": "Allele"
}

# https://www.ncbi.nlm.nih.gov/clinvar/variation/1373966/?new_evidence=true
deletion_inputs = {
    "hgvs": "NC_000013.11:g.20003097del",
    "spdi": ["NC_000013.11:20003096:C:", "NC_000013.11:20003096:1:"]
}

deletion_output = {
    "location": {
        "interval": {
            "end": {"value": 20003097, "type": "Number"},
            "start": {"value": 20003096, "type": "Number"},
            "type": "SequenceInterval"
        },
        "sequence_id": "ga4gh:SQ._0wi-qoDrvram155UmcSC-zA5ZK4fpLT",
        "type": "SequenceLocation"
    },
    "state": {
        "sequence": "",
        "type": "LiteralSequenceExpression"
    },
    "type": "Allele"
}

# https://www.ncbi.nlm.nih.gov/clinvar/variation/1687427/?new_evidence=true
insertion_inputs = {
    "hgvs": "NC_000013.11:g.20003010_20003011insG",
    "spdi": ["NC_000013.11:20003010::G", "NC_000013.11:20003010:0:G"]
}

insertion_output = {
    "location": {
        "interval": {
            "end": {"value": 20003010, "type": "Number"},
            "start": {"value": 20003010, "type": "Number"},
            "type": "SequenceInterval"
        },
        "sequence_id": "ga4gh:SQ._0wi-qoDrvram155UmcSC-zA5ZK4fpLT",
        "type": "SequenceLocation"
    },
    "state": {
        "sequence": "G",
        "type": "LiteralSequenceExpression"
    },
    "type": "Allele"
}

# https://www.ncbi.nlm.nih.gov/clinvar/variation/1264314/?new_evidence=true
duplication_inputs = {
    "hgvs": "NC_000013.11:g.19993838_19993839dup",
    "spdi": "NC_000013.11:19993837:GT:GTGT"
}

duplication_output = {
    "location": {
        "interval": {
            "end": {"value": 19993839, "type": "Number"},
            "start": {"value": 19993837, "type": "Number"},
            "type": "SequenceInterval"
        },
        "sequence_id": "ga4gh:SQ._0wi-qoDrvram155UmcSC-zA5ZK4fpLT",
        "type": "SequenceLocation"
    },
    "state": {
        "sequence": "GTGT",
        "type": "LiteralSequenceExpression"
    },
    "type": "Allele"
}


@pytest.mark.vcr
def test_from_beacon(tlr):
    assert tlr._from_beacon(snv_inputs["beacon"]).as_dict() == snv_output


@pytest.mark.vcr
def test_from_gnomad(tlr):
    assert tlr._from_gnomad(snv_inputs["gnomad"]).as_dict() == snv_output


@pytest.mark.vcr
def test_from_hgvs(tlr):
    assert tlr._from_hgvs(snv_inputs["hgvs"]).as_dict() == snv_output
    assert tlr._from_hgvs(deletion_inputs["hgvs"]).as_dict() == deletion_output
    assert tlr._from_hgvs(insertion_inputs["hgvs"]).as_dict() == insertion_output
    assert tlr._from_hgvs(duplication_inputs["hgvs"]).as_dict() == duplication_output


hgvs_protein_tests = (
    (  # protein substitution
        {
            "type": "Allele",
            "location": {
                "type": "SequenceLocation",
                "sequence_id": "ga4gh:SQ.cQvw4UsHHRRlogxbWCB8W-mKD4AraM9y",
                "interval": {
                    "type": "SequenceInterval",
                    "start": {"type": "Number", "value": 599},
                    "end": {"type": "Number", "value": 600}
                }
            },
            "state": {
                "type": "LiteralSequenceExpression",
                "sequence": "E"
            }
        }, ["NP_004324.2:p.Val600Glu"]
    ),
    (  # protein delins
        {
            "type": "Allele",
            "location": {
                "type": "SequenceLocation",
                "sequence_id": "ga4gh:SQ.KAxM06sYzBF6zFftFaYq9E_18wsnn7al",
                "interval": {
                    "type": "SequenceInterval",
                    "start": {"type": "Number", "value": 274},
                    "end": {"type": "Number", "value": 277}
                }
            },
            "state": {
                "type": "LiteralSequenceExpression",
                "sequence": "C"
            }
        }, ["NP_000537.3:p.Cys275_Cys277delinsCys", "NP_001119584.1:p.Cys275_Cys277delinsCys"]
    )
)


@pytest.mark.parametrize("p_allele,expected", hgvs_protein_tests)
@pytest.mark.vcr
def test_to_hgvs_protein(tlr, p_allele, expected):
    allele = models.Allele(**p_allele)
    to_hgvs = tlr.translate_to(allele, "hgvs")
    assert len(expected) == len(to_hgvs)
    assert set(expected) == set(to_hgvs)


@pytest.mark.vcr
def test_from_spdi(tlr):
    assert tlr._from_spdi(snv_inputs["spdi"]).as_dict() == snv_output
    for spdi_del_expr in deletion_inputs["spdi"]:
        assert tlr._from_spdi(spdi_del_expr).as_dict() == deletion_output, spdi_del_expr
    for spdi_ins_expr in insertion_inputs["spdi"]:
        assert tlr._from_spdi(spdi_ins_expr).as_dict() == insertion_output, spdi_ins_expr
    assert tlr._from_spdi(duplication_inputs["spdi"]).as_dict() == duplication_output


@pytest.mark.vcr
def test_to_spdi(tlr):
    tlr.normalize = True
    spdiexpr = snv_inputs["spdi"]
    allele = tlr.translate_from(spdiexpr, "spdi")
    to_spdi = tlr.translate_to(allele, "spdi")
    assert 1 == len(to_spdi)
    assert spdiexpr == to_spdi[0]

hgvs_tests = (
    ("NC_000013.11:g.32936732=", {
        "location": {
            "interval": {
                "end": {"value": 32936732, "type": "Number"},
                "start": {"value": 32936731, "type": "Number"},
                "type": "SequenceInterval"
            },
            "sequence_id": "ga4gh:SQ._0wi-qoDrvram155UmcSC-zA5ZK4fpLT",
            "type": "SequenceLocation"
        },
        "state": {
            "sequence": "C",
            "type": "LiteralSequenceExpression"
        },
        "type": "Allele"
    }),
    ("NC_000007.14:g.55181320A>T", {
        "location": {
            "interval": {
                "end": {"value": 55181320, "type": "Number"},
                "start": {"value": 55181319, "type": "Number"},
                "type": "SequenceInterval"
            },
            "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
            "type": "SequenceLocation"
        },
        "state": {
            "sequence": "T",
            "type": "LiteralSequenceExpression"
        },
        "type": "Allele"
    }),
    ("NC_000007.14:g.55181220del", {
        "location": {
            "interval": {
                "end": {"value": 55181220, "type": "Number"},
                "start": {"value": 55181219, "type": "Number"},
                "type": "SequenceInterval"
            },
            "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
            "type": "SequenceLocation"
        },
        "state": {
            "sequence": "",
            "type": "LiteralSequenceExpression"
        },
        "type": "Allele"
    }),
    ("NC_000007.14:g.55181230_55181231insGGCT", {
        "location": {
            "interval": {
                "end": {"value": 55181230, "type": "Number"},
                "start": {"value": 55181230, "type": "Number"},
                "type": "SequenceInterval"
            },
            "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
            "type": "SequenceLocation"
        },
        "state": {
            "sequence": "GGCT",
            "type": "LiteralSequenceExpression"
        },
        "type": "Allele"
    }),
    ("NC_000013.11:g.32331093_32331094dup", {
        "location": {
            "interval": {
                "end": {"value": 32331094, "type": "Number"},
                "start": {"value": 32331082, "type": "Number"},
                "type": "SequenceInterval"
            },
            "sequence_id": "ga4gh:SQ._0wi-qoDrvram155UmcSC-zA5ZK4fpLT",
            "type": "SequenceLocation"
        },
        "state": {
            "sequence": "TTTTTTTTTTTTTT",
            "type": "LiteralSequenceExpression"
        },
        "type": "Allele"
    }),
    ("NC_000013.11:g.32316467dup", {
        "location": {
            "interval": {
                "end": {"value": 32316467, "type": "Number"},
                "start": {"value": 32316466, "type": "Number"},
                "type": "SequenceInterval"
            },
            "sequence_id": "ga4gh:SQ._0wi-qoDrvram155UmcSC-zA5ZK4fpLT",
            "type": "SequenceLocation"
        },
        "state": {
            "sequence": "AA",
            "type": "LiteralSequenceExpression"
        },
        "type": "Allele"
    }),
    ("NM_001331029.1:n.872A>G", {
        "location": {
            "interval": {
                "end": {"value": 872, "type": "Number"},
                "start": {"value": 871, "type": "Number"},
                "type": "SequenceInterval"
            },
            "sequence_id": "ga4gh:SQ.MBIgVnoHFw34aFqNUVGM0zgjC3d-v8dK",
            "type": "SequenceLocation"
        },
        "state": {
            "sequence": "G",
            "type": "LiteralSequenceExpression"
        },
        "type": "Allele"
    }),
    ("NM_181798.1:n.1263G>T", {
        "location": {
            "interval": {
                "end": {"value": 1263, "type": "Number"},
                "start": {"value": 1262, "type": "Number"},
                "type": "SequenceInterval"
            },
            "sequence_id": "ga4gh:SQ.KN07u-RFqd1dTyOWOG98HnOq87Nq-ZIg",
            "type": "SequenceLocation"
        },
        "state": {
            "sequence": "T",
            "type": "LiteralSequenceExpression"
        },
        "type": "Allele"
    }),
)


@pytest.mark.parametrize("hgvsexpr,expected", hgvs_tests)
@pytest.mark.vcr
def test_hgvs(tlr, hgvsexpr, expected):
    tlr.normalize = True
    allele = tlr.translate_from(hgvsexpr, "hgvs")
    assert expected == allele.as_dict()

    to_hgvs = tlr.translate_to(allele, "hgvs")
    assert 1 == len(to_hgvs)
    assert hgvsexpr == to_hgvs[0]


def test_ensure_allele_is_latest_model(tlr):
    allele_deprecated_dict = {
        "location": {
            "interval": {
                "end": 55181320,
                "start": 55181319,
                "type": "SimpleInterval"
            },
            "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
            "type": "SequenceLocation"
        },
        "state": {
            "sequence": "T",
            "type": "SequenceState"
        },
        "type": "Allele"
    }
    allele_deprecated = models.Allele(**allele_deprecated_dict)
    assert tlr.ensure_allele_is_latest_model(allele_deprecated).as_dict() == {
        "type": "Allele",
        "location": {
            "type": "SequenceLocation", "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
            "interval": {
                "type": "SequenceInterval",
                "start": {"type": "Number", "value": 55181319},
                "end": {"type": "Number", "value": 55181320}
            }
        },
        "state": {"type": "LiteralSequenceExpression", "sequence": "T"}
    }

# TODO: Readd these tests
# @pytest.mark.vcr
# def test_errors(tlr):
#     with pytest.raises(ValueError):
#         tlr._from_beacon("bogus")
#
#     with pytest.raises(ValueError):
#         tlr._from_gnomad("NM_182763.2:c.688+403C>T")
#
#     with pytest.raises(ValueError):
#         tlr._from_hgvs("NM_182763.2:c.688+403C>T")
#
#     with pytest.raises(ValueError):
#         tlr._from_hgvs("NM_182763.2:c.688_690inv")
#
#     with pytest.raises(ValueError):
#         tlr._from_spdi("NM_182763.2:c.688+403C>T")
