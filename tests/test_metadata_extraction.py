from legal_ai_toolkit.extraction.metadata import extract_header_metadata
from legal_ai_toolkit.pipeline.id_regeneration import IDRegenerationStep
from legal_ai_toolkit.utils.ids import resolve_court_code


def test_gujarat_neutral_citation_is_recovered_with_date():
    sample = """
    1. Rule. Learned APP, Mr. Manan Mehta for respondent no.1 - State of Gujarat and learned advocate waive service of notice of rule.

    Page 1 of 33 Uploaded by PATIL GAUTAMBHAI GOPALBHAI(HC00190) on Tue Feb 04 2025
    Downloaded on : Tue Feb 04 22:46:35 IST 2025
    NEUTRAL CITATION R/SCR.A/5797/2016 CAV JUDGMENT DATED: 04/02/2025 undefined
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Gujarat High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["decision_date"] == "2025-02-04"
    assert metadata["court_match_reason"] == "neutral_citation_gujarat_r"


def test_andhra_pre_telangana_header_is_recovered():
    sample = """
    Andhra HC (Pre-Telangana)

    M. Sivaram And Ors. vs State Of A.P. And Anr. on 22 August, 2006
    Equivalent citations: 2007CRILJ1259
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Andhra Pradesh High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "andhra_pre_telangana"


def test_rajasthan_neutral_citation_is_recovered():
    sample = """
    No.5, in D.B. C.W. No.11512/2025
    HON'BLE THE ACTING CHIEF JUSTICE MR. SANJEEV PRAKASH SHARMA
    HON'BLE MR. JUSTICE SANJEET PUROHIT
    [2025:RJ-JP:34853-DB]
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Rajasthan High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "neutral_citation_rajasthan_rj"


def test_sessions_transfer_beats_embedded_high_court_reference():
    sample = """
    Vide order dated 16.12.2014, the Hon'ble High Court of Delhi dismissed the revision petitions with the liberty to the revisionists to appear before the Sessions Judge to argue the petitions.
    The file was transferred to the court of District & Sessions Judge, Patiala House Court to either hear the matter himself or to assign the same to any other court of competent jurisdiction and that is how, the present revision petitions came up for hearing before the Sessions Court.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Sessions Court"
    assert metadata["court_level"] == "TR"
    assert metadata["court_match_reason"] == "structured_trial_sessions_transfer"


def test_narrative_magistrate_reference_does_not_create_false_positive():
    sample = """
    On 22nd July, 2013, petitioner received a letter informing them that a summary report was filed with the Additional Metropolitan Magistrate 47th Court, Mumbai.
    On 1st August, 2013, respondent no.1 filed additional affidavit bringing the report on record.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "UNKNOWN"
    assert metadata["court_level"] == "UNKNOWN"


def test_narrative_supreme_court_reference_does_not_create_false_positive():
    sample = """
    /JRU/19/INT-11/ENQ-1/2018 in accordance with the direction given by the Supreme Court in Vijay Sajnani Vs. Union of India, Cril. M.P. No.10117 of 2012 in WP (Cr).
    The parties were thereafter heard by the writ court.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "UNKNOWN"
    assert metadata["court_level"] == "UNKNOWN"


def test_scch_mvc_pattern_maps_to_mact_and_code():
    sample = """
    M.V.C.NO.7875/2012 3 (SCCH-7)
    The brief averments of the Petitioners' case are as follows;
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Motor Accident Claims Tribunal"
    assert metadata["court_level"] == "TR"
    assert metadata["court_match_reason"] == "structured_trial_mact_scch"
    assert resolve_court_code(metadata["court"]) == "MAC"


def test_bombay_colon_uploader_pattern_is_recovered():
    sample = """
    The requirement to have sufficient funds in the account from which the cheque is issued is only with the drawer company.
    6 ::: Uploaded on - 08/03/2023 ::: Downloaded on - 09/06/2023 12:07:26 ::: wp4128-2021 & connected-Final.doc
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Bombay High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "bombay_colon_uploader"


def test_bombay_colon_uploader_variant_doc_bundle_is_recovered():
    sample = """
    OUTLINE OF CONTENTS This judgment is arranged in the following parts.
    Page 2 of 176 16th June 2021 ::: Uploaded on - 16/06/2021 ::: Downloaded on - 16/06/2021 22:58:10 ::: Board of Control for Cricket in India vs Deccan Chronicle Holding Ltd CARBPL-4466-20-J.docx
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Bombay High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "bombay_colon_uploader"


def test_madras_judis_pattern_is_recovered():
    sample = """
    12.03.2020 Index : Yes Speaking order Kak 10/12 http://www.judis.nic.in C.M.A.No.1017 of 2016 To
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Madras High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "madras_judis_portal"


def test_madras_judis_criminal_revision_prose_is_recovered():
    sample = """
    This Criminal Revision Case has been filed by the revision petitioner/A-1, to set aside the Judgment of conviction and sentence imposed by the learned Assistant Sessions Judge, Kulithalai.
    http://www.judis.nic.in 3
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Madras High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "madras_judis_portal"


def test_supreme_court_judge_line_with_appeal_is_recovered():
    sample = """
    R.F. Nariman, J.

    1. The present appeals raise two important questions.
    2. The facts contained in the three appeals are similar. For the purpose of this judgment, the facts contained in Civil Appeal No.15481 of 2017 will now be set out.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Supreme Court Of India"
    assert metadata["court_level"] == "SC"
    assert metadata["court_match_reason"] == "supreme_court_inference"


def test_case_title_line_recovers_decision_date():
    sample = """
    Allahabad High Court

    Harshit And 3 Others vs State Of U.P. And Another on 6 December, 2024
    """

    metadata = extract_header_metadata(sample)

    assert metadata["decision_date"] == "2024-12-06"


def test_date_of_judgment_without_separator_is_recovered():
    sample = """
    Supreme Court of India
    DATE OF JUDGMENT11/07/1985
    """

    metadata = extract_header_metadata(sample)

    assert metadata["decision_date"] == "1985-07-11"


def test_inline_mac_appeal_case_number_is_recovered():
    sample = """
    Signature Not Verified Digitally Signed By:SUNIL Signing Date:07.10.2023 14:30:27 MAC. APPL 288/2021 1 of 32
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "MAC. APPL 288/2021"


def test_wp_c_inline_case_number_and_delhi_bench_are_recovered():
    sample = """
    HON'BLE MR. JUSTICE A.K. SIKRI HON'BLE MR. JUSTICE RAJIV SAHAI ENDLAW A.K. SIKRI, ACTING CHIEF JUSTICE:
    1. The petitioner has challenged the decision in W.P.(C)1610/2012 Page 1 of 16.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Delhi High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "delhi_wp_c_bench"
    assert metadata["case_number"] == "W.P.(C)1610/2012"


def test_punjab_haryana_om_caption_is_recovered():
    sample = """
    Ashutosh Mohunta, Acting Chief Justice.
    Civil Writ Petition No. 4212 of 2014 (O&M)
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Punjab And Haryana High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "punjab_haryana_om_caption"
    assert metadata["case_number"] == "Civil Writ Petition No. 4212 of 2014 (O&M)"


def test_meghalaya_shillong_petition_is_recovered():
    sample = """
    (per the Hon'ble, the Chief Justice) The aforesaid petition is placed before us in Crl Petn No. 63 of 2021.
    Shillong.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Meghalaya High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "meghalaya_shillong_petition"
    assert metadata["case_number"] == "Crl Petn No. 63 of 2021"


def test_case_colon_caption_is_recovered():
    sample = """
    Allahabad High Court
    Case :- CRIMINAL MISC. BAIL APPLICATION No. - 11926 of 2023
    Applicant :- Test Applicant
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "Case :- CRIMINAL MISC. BAIL APPLICATION No. 11926 of 2023"


def test_court_number_does_not_override_real_case_caption():
    sample = """
    Court No. - 76
    Case :- CRIMINAL MISC. BAIL APPLICATION No. - 11926 of 2023
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "Case :- CRIMINAL MISC. BAIL APPLICATION No. 11926 of 2023"


def test_case_caption_with_us_descriptor_is_recovered():
    sample = """
    Allahabad High Court
    Case :- U/S 482/378/407 No. - 1945 of 2020
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "Case :- U/S 482/378/407 No. 1945 of 2020"


def test_case_caption_with_us_438_descriptor_is_recovered():
    sample = """
    Allahabad High Court
    Case :- CRIMINAL MISC ANTICIPATORY BAIL APPLICATION U/S 438 CR.P.C. No. - 4447 of 2020
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "Case :- CRIMINAL MISC ANTICIPATORY BAIL APPLICATION U/S 438 CR.P.C. No. 4447 of 2020"


def test_wp_md_compact_caption_is_recovered():
    sample = """
    Madras High Court
    W.P.(MD)No.5028 of 2012
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "W.P.(MD)No.5028 of 2012"


def test_arb_op_com_div_case_number_is_recovered():
    sample = """
    Madras High Court
    Arb.O.P.(Com.Div.)No.186 of 2023
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "Arb.O.P.(Com.Div.)No.186 of 2023"


def test_case_crime_reference_is_not_treated_as_case_number():
    sample = """
    Allahabad High Court
    Learned counsel submits that the applicant seeks bail in Case Crime No. 576/2020 under Section 304B I.P.C.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "UNKNOWN"


def test_dated_this_the_day_of_is_recovered():
    sample = """
    Kerala High Court
    Dated this the 13th day of March, 2025
    """

    metadata = extract_header_metadata(sample)

    assert metadata["decision_date"] == "2025-03-13"


def test_dated_month_day_year_is_recovered():
    sample = """
    Coram: Hon'ble K.M. Joseph, C.J.
    Dated: April 21, 2016
    """

    metadata = extract_header_metadata(sample)

    assert metadata["decision_date"] == "2016-04-21"


def test_mphc_branch_neutral_citation_is_recovered():
    sample = """
    NEUTRAL CITATION NO. 2024:MPHC-IND:28723
    FA-587-2007
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Madhya Pradesh High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "neutral_citation_mphc"


def test_id_regeneration_recovers_year_from_rajasthan_neutral_citation():
    step = IDRegenerationStep("/tmp/id_regen_in", "/tmp/id_regen_out")

    assert step._infer_year_from_text("[2025:RJ-JP:34853-DB]") == 2025


def test_gujarat_case_tag_neutral_citation_recovers_court_and_case_number():
    sample = """
    Page 1 of 30 Downloaded on : Wed Feb 07 20:35:13 IST 2024
    NEUTRAL CITATION C/SCA/13155/2011 JUDGMENT DATED: 02/02/2024 undefined
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Gujarat High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "neutral_citation_gujarat_case_tag"
    assert metadata["case_number"] == "C/SCA/13155/2011"
    assert metadata["decision_date"] == "2024-02-02"


def test_supreme_court_ca_slp_leave_bundle_is_recovered():
    sample = """
    C.A.No.24070/2017 @ SLP(C)No.34231/2015 Leave granted.
    Heard learned counsel for the parties.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Supreme Court Of India"
    assert metadata["court_level"] == "SC"
    assert metadata["court_match_reason"] == "supreme_court_inference"
    assert metadata["case_number"] == "C.A.No.24070/2017"


def test_supreme_court_cji_line_is_recovered():
    sample = """
    Dipak Misra, CJI. [For himself and A.M. Khanwilkar, J.]
    2. This Court is considering the constitutional issue referred to the Constitution Bench.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Supreme Court Of India"
    assert metadata["court_level"] == "SC"
    assert metadata["court_match_reason"] == "supreme_court_inference"


def test_special_leave_granted_opening_recovers_supreme_court():
    sample = """
    1. Special leave granted.
    2. Can bail granted under the proviso to Sub-section (2) of Section 167 of the CrPC, 1973 for failure to complete the investigation within the period prescribed thereunder be cancelled?
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Supreme Court Of India"
    assert metadata["court_level"] == "SC"
    assert metadata["court_match_reason"] == "supreme_court_inference"


def test_signature_date_with_dots_normalizes_to_iso():
    sample = """
    Supreme Court Of India
    Signature Not Verified Digitally signed by CHETAN KUMAR Date: 2017.12.15 14:06:25 IST
    """

    metadata = extract_header_metadata(sample)

    assert metadata["decision_date"] == "2017-12-15"


def test_index_heading_is_not_treated_as_case_number():
    sample = """
    Supreme Court Of India
    INDEX Sr. Particulars Page Nos.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "UNKNOWN"


def test_bengaluru_open_court_line_recovers_trial_metadata():
    sample = """
    Petition in A.P.No.49/2022 filed by the petitioner under Sec.34 of the Arbitration and Conciliation Act, is dismissed with cost.
    (Dictated to the Stenographer directly on Computer and then pronounced by me in the open Court on this the 16th day of January 2025.)
    (B.P.Devamane) I Addl. City Civil & Sessions Judge, Bengaluru.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Sessions Court"
    assert metadata["court_level"] == "TR"
    assert metadata["court_match_reason"] == "trial_court_context"
    assert metadata["case_number"] == "A.P.No.49/2022"
    assert metadata["decision_date"] == "2025-01-16"


def test_writ_petition_nos_batch_case_number_is_preserved():
    sample = """
    WRIT PETITION Nos.14695 of 2021 & BATCH Between:
    COMMON JUDGMENT & ORDER:
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "WRIT PETITION Nos.14695 of 2021"


def test_patna_embedded_header_recovers_case_number_and_date():
    sample = """
    Heard learned counsel for the petitioner and learned counsel for the State.

    The case of the petitioner is narrated in detail in the pleadings. Patna High Court CWJC No.8485 of 2021(13) dt.13-02-2024 3/6 petition before the Circle Officer, Bhabua for mutation of the name in respect of the said holding.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Patna High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["case_number"] == "CWJC No.8485 of 2021(13)"
    assert metadata["decision_date"] == "2024-02-13"


def test_patna_embedded_header_without_dt_recovers_date():
    sample = """
    It is the claim of the petitioner that under the earlier communication he was promoted to the rank of Substantive Lt.
    Colonel by Time Scale. Under the impugned communication he has been shorn of his promotion and the status of Lt. Colonel in violation of principle of natural justice. Patna High Court CWJC No.10002 of 1996 29-04-2011 2 Colonel by Time Scale'. Under the impugned communication he has been shorn of his promotion.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Patna High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["case_number"] == "CWJC No.10002 of 1996"
    assert metadata["decision_date"] == "2011-04-29"


def test_karnataka_neutral_citation_line_recovers_case_number():
    sample = """
    Accused Nos.1 to 6 in Crime No.130/2023 registered by the Chitradurga Extension Police Station are before this Court under Section 438 of Cr.P.C.
    NC: 2023:KHC:42577 CRL.P No. 11591 of 2023
    Heard the learned counsel for the parties.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Karnataka High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["case_number"] == "CRL.P No. 11591 of 2023"


def test_madras_portal_rc_md_case_number_is_recovered():
    sample = """
    This Criminal Revision Case has been filed to set aside the order, dated 10.08.2016 in Cr.M.P.No.5484 of 2016 passed by the learned District Munsif cum Judicial Magistrate Court, Shenkottai.
    https://www.mhc.tn.gov.in/judis/ 2/10 RC(MD)No. 707 of 2016
    Heard the learned Counsel appearing for the petitioner.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Madras High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["case_number"] == "RC(MD)No. 707 of 2016"


def test_madras_public_prosecutor_line_beats_new_delhi_reference():
    sample = """
    [Judgment of the Court was delivered by M.Jaichandren, J.] This Habeas Corpus Petition has been filed to call for the records relating to the order of the 2nd respondent, dated 29.12.2012, made in Cr.M.P.No.3/2012[CS], quash the same.
    3. The Additional Secretary to the Govt. of India, Ministry of Consumer Affairs, Food & Public Distribution, New Delhi.
    4. The Public Prosecutor, High Court Madras
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Madras High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["case_number"] == "Cr.M.P.No.3/2012[CS]"


def test_party_label_case_caption_is_not_treated_as_case_number_or_court():
    sample = """
    ----Respondents D.B. Civil Writ Petition No. 6224/2019
    Writ Petition (Criminal) No.1078/2018 has been filed by five petitioners in accordance with the direction given by the Supreme Court in Vijay Sajnani Vs. Union of India, Cril. M.P. No.10117 of 2012 in WP (Crl.) 29 of 2012, which may also be directed to be video-graphed in terms of order dated 07.12.2019 in Writ Petition (Civil) No.389 of 2010 of the Supreme Court in Rajinder Arora and Others Vs. Union of India and Others.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "UNKNOWN"
    assert metadata["court_level"] == "UNKNOWN"
    assert metadata["case_number"] == "Writ Petition (Criminal) No.1078/2018"


def test_calcutta_rpan_header_prefers_real_case_number_over_police_case():
    sample = """
    Court No.01 rpan/21 CRM (A) 933 of 2025 In Re:- An application for anticipatory bail under Section 482 of the Bharatiya Nagarik Suraksha Sanhita, 2023.
    Apprehending arrest in connection with Sahebganj Police Station Case no.536 of 2025 dated 12.09.2025, the present application has been preferred.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Calcutta High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["case_number"] == "CRM (A) 933 of 2025"


def test_bombay_uploaded_header_recovers_bare_case_tag():
    sample = """
    DATED :- 19th August, 2024 P.C.:
    The entire amount, as awarded by the Appellate Court, is Page 1 of 3 19th August, 2024 ::: Uploaded on - 20/08/2024 ::: Downloaded on - 20/08/2024 14:57:37 ::: CRIR 22 of 2022 deposited/paid.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "CRIR 22 of 2022"
    assert metadata["decision_date"] == "2024-08-20"


def test_mphc_neutral_citation_trailing_case_tag_is_recovered():
    sample = """
    Signature Not Verified Signed by: GEETA PRAMOD Signing time: 06-02-2026 11:25:52 NEUTRAL CITATION NO. 2026:MPHC-IND:3496 2 MP-5500-2025
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Madhya Pradesh High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["case_number"] == "MP-5500-2025"


def test_mphc_embedded_wp_case_number_is_recovered():
    sample = """
    4. So far as the locus standi of the petitioner to file the instant THE HIGH COURT OF MADHYA PRADESH WP. No. 6844/2020 ( Umesh Kumar Bohare Vs. State of M.P. and others ) (2) habeas corpus petition is concerned.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Madhya Pradesh High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["case_number"] == "WP. No. 6844/2020"


def test_mphc_digitally_signed_embedded_ma_header_recovers_court_and_case_number():
    sample = """
    The appellant seeks enhancement of compensation.
    Digitally signed by ARUN KUMAR MISHRA Date: 24/01/2020 11:03:28 13 THE HIGH COURT OF MADHYA PRADESH MA No.266/2017 Smt. Ramrati and others Vs. Har Prasad and others
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Madhya Pradesh High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["case_number"] == "MA No.266/2017"


def test_gujarat_hc_nic_embedded_header_recovers_court():
    sample = """
    Sd/- (M.R. SHAH, J.) Ajay Page 1 of 1 HC-NIC Page 1 of 41 Created On Sun Mar 20 02:49:26 IST 2016 1 of 41 C/FA/2188/2002 CAV JUDGMENT IN THE HIGH COURT OF GUJARAT AT AHMEDABAD FIRST APPEAL NO. 2188 of 2002 TO FIRST APPEAL NO. 2195 of 2002 FOR APPROVAL AND SIGNATURE:
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Gujarat High Court"
    assert metadata["court_level"] == "HC"


def test_patna_c_misc_embedded_header_recovers_court_case_number_and_date():
    sample = """
    Learned counsel further submits that one of the properties is situated at Patna. Patna High Court C.Misc. No.994 of 2023 dt.21-11-2024 3/5 Learned counsel further submits that the impugned order deserves interference.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Patna High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["case_number"] == "C.Misc. No.994 of 2023"
    assert metadata["decision_date"] == "2024-11-21"


def test_delhi_order_portal_bundle_recovers_court():
    sample = """
    % 08.08.2025
    This is a digitally signed order.
    The authenticity of the order can be re-verified from Delhi High Court Order Portal by scanning the QR code shown above. The Order is downloaded from the DHC Server on 11/08/2025 at 22:31:38.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Delhi High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "delhi_order_portal"


def test_extended_header_delhi_order_portal_bundle_recovers_court():
    sample = ("x" * 6500) + """

    % 08.08.2025
    This is a digitally signed order.
    The authenticity of the order can be re-verified from Delhi High Court Order Portal by scanning the QR code shown above. The Order is downloaded from the DHC Server on 11/08/2025 at 22:31:38.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Delhi High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "delhi_order_portal"


def test_orissa_signed_location_line_recovers_court():
    sample = """
    Page 1 of 10 Signature Not Verified Digitally Signed Signed by: BHABAGRAHI JHANKAR Reason: Authentication
    Location: ORISSA HIGH COURT, CUTTACK Date: 29-May-2025 16:37:05
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Orissa High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["court_match_reason"] == "orissa_signed_location"
    assert metadata["decision_date"] == "2025-05-29"


def test_narrative_madras_high_court_case_reference_does_not_create_false_court():
    sample = """
    Per : HON'BLE Mr.K.V.EAPEN, ADMINISTRATIVE MEMBER
    The applicant submits that the Hon'ble High Court of Judicature at Madras in W.P.No.1858/2002 in a case filed by another employee had granted similar relief.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "UNKNOWN"
    assert metadata["court_level"] == "UNKNOWN"


def test_extended_header_patna_embedded_header_recovers_court():
    sample = ("x" * 6500) + """

    passed by learned Sub Judge - VI, Danapur in Title Suit No. 439 of 2013.
    Learned counsel further submits that one of the properties is situated at Patna. Patna High Court C.Misc. No.994 of 2023 dt.21-11-2024 3/5 Learned counsel further submits that the impugned order deserves interference.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Patna High Court"
    assert metadata["court_level"] == "HC"


def test_madras_plural_criminal_original_petition_case_number_is_recovered():
    sample = """
    The present criminal original petitions have been filed by the petitioners.
    CRL. O.P. Nos.15185, 15929 & 16339/2021
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "CRL. O.P. Nos.15185, 15929 & 16339/2021"


def test_bail_application_case_number_is_recovered_without_bombay_false_positive():
    sample = """
    This is an application filed u/s 439 of Code of Criminal Procedure seeking regular bail.
    The learned counsel for the petitioner, to get over the rigour of Section 37 of the NDPS Act, has raised before BAIL APPL. NO. 2530 OF 2022 -3- me the following two points:
    The learned counsel relied on the decision of the Bombay High Court in Hitesh Hemant Malhotra v. State of Maharashtra.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "UNKNOWN"
    assert metadata["court_level"] == "UNKNOWN"
    assert metadata["case_number"] == "BAIL APPL. NO. 2530 OF 2022"


def test_criminal_miscellaneous_petition_case_number_is_recovered():
    sample = """
    This Criminal Miscellaneous Petition has been filed invoking the jurisdiction of this Court.
    1 Cr. M.P. No.3102 of 2022
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "Cr. M.P. No.3102 of 2022"


def test_mcrc_case_number_is_recovered():
    sample = """
    M.Cr.C.No.7046/2014
    Shri R.N. Sharma, Advocate for the applicant.
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "M.Cr.C.No.7046/2014"


def test_old_criminal_appeal_case_number_is_recovered():
    sample = """
    Cr. A. No. 543/92
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "Cr. A. No. 543/92"


def test_madras_plural_wp_md_case_number_is_recovered():
    sample = """
    Madras High Court
    W.P.(MD)Nos.9701 to 9703 of 2014
    """

    metadata = extract_header_metadata(sample)

    assert metadata["case_number"] == "W.P.(MD)Nos.9701 to 9703 of 2014"


def test_madras_footer_date_line_is_recovered():
    sample = """
    The civil miscellaneous appeal is allowed.
    12.03.2020 Index : Yes Speaking order Kak 10/12 http://www.judis.nic.in C.M.A.No.1017 of 2016 To
    """

    metadata = extract_header_metadata(sample)

    assert metadata["decision_date"] == "2020-03-12"


def test_announced_on_date_is_recovered():
    sample = """
    2025:HHC:15621 IN THE HIGH COURT OF HIMACHAL PRADESH AT SHIMLA
    Cr.MP(M) No.348 of 2025
    Announced on: 23.05.2025
    """

    metadata = extract_header_metadata(sample)

    assert metadata["court"] == "Himachal Pradesh High Court"
    assert metadata["court_level"] == "HC"
    assert metadata["case_number"] == "Cr.MP(M) No.348 of 2025"
    assert metadata["decision_date"] == "2025-05-23"
