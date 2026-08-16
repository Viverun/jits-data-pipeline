from legal_ai_toolkit.extraction.sections import SectionExtractor


def grouped(text):
    return SectionExtractor.group_by_act(SectionExtractor.extract(text))


def test_section_list_with_ipc_is_recovered():
    assert grouped("convicted under Sections 498-A, 304-B I.P.C. and sentenced") == {
        "IPC": ["498-A", "304-B"]
    }


def test_crpc_statement_section_is_recovered():
    assert grouped("his statement under Section 313 Cr.P.C. was recorded") == {"CrPC": ["313"]}


def test_us_shorthand_recovers_ni_act_cheque_section():
    """"u/s 138 N.I. Act" is the single most common charge phrasing in cheque matters."""
    assert grouped("complaint u/s 138 N.I. Act was filed against the accused") == {
        "NI Act": ["138"]
    }


def test_single_letter_section_abbreviation_is_recovered():
    assert grouped("offence punishable under S. 420 IPC read with S. 34 IPC") == {
        "IPC": ["420", "34"]
    }


def test_secs_abbreviation_with_spelled_out_act_is_recovered():
    assert grouped("charged under Secs. 420, 467, 468 of the Indian Penal Code") == {
        "IPC": ["420", "467", "468"]
    }


def test_range_keeps_endpoints_without_inventing_intermediate_sections():
    """"302 to 304" must not silently expand to 302, 303, 304."""
    assert grouped("proceedings under Sections 302 to 304 IPC") == {"IPC": ["302", "304"]}


def test_subsection_with_clause_is_preserved():
    assert grouped("offence under Section 13(1)(d) of the Prevention of Corruption Act") == {
        "PC Act": ["13(1)(d)"]
    }


def test_dowry_prohibition_slash_section_is_not_split():
    """3/4 is a single Dowry Act reference, not sections 3 and 4."""
    assert grouped("petition under Section 3/4 Dowry Prohibition Act") == {
        "Dowry Prohibition Act": ["3/4"]
    }


def test_newly_supported_acts_are_recognised():
    assert grouped("petition under Section 34 of the Arbitration and Conciliation Act") == {
        "Arbitration Act": ["34"]
    }
    assert grouped("application under Section 7 of the Insolvency and Bankruptcy Code") == {
        "IBC": ["7"]
    }
    assert grouped("claim under Section 166 of the Motor Vehicles Act") == {"MV Act": ["166"]}


def test_crpc_is_not_misread_as_cpc():
    """Cr.P.C. and C.P.C. are different codes and must not collide."""
    assert grouped("revision under Section 397 Cr.P.C.") == {"CrPC": ["397"]}
    assert grouped("application under Section 151 C.P.C.") == {"CPC": ["151"]}
