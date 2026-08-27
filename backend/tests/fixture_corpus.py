import sys; sys.path.insert(0, "..")
from app.schemas import FactType
from app.corpus.chunker import chunk_document

# NOTE: values below are XXX placeholders on purpose. Per D023 no real
# figure enters the repo until it comes from a downloaded AMC document.
KIM_FLEXICAP = """
MINIMUM APPLICATION AMOUNT
Minimum investment: Rs. XXX and in multiples of Rs. 1 thereafter
Minimum SIP: Rs. XXX per month
Additional purchase: Rs. XXX and in multiples of Rs. 1 thereafter

LOAD STRUCTURE
Entry Load: Not applicable
Exit Load: XXX% if redeemed within XXX days from date of allotment

BENCHMARK INDEX
Benchmark: XXX TRI
"""

ELSS_SID = """
HIGHLIGHTS SUMMARY OF THE SCHEME
An Open-ended Equity Linked Savings Scheme with a statutory lock-in period
of 3 years and tax benefit.
Plans: The Scheme has Regular Plan and Direct Plan. Both plans have Growth
and IDCW options.
"""

AMFI_TER = """
EXPENSE RATIO
As per current SEBI Regulations, mutual funds are required to disclose the
TER of all schemes on a daily basis on their websites as well as AMFI's website.
The regulatory limits of TER are specified under Regulation 52 of SEBI Mutual
Fund Regulations.
"""

def build():
    cs = []
    cs += chunk_document(KIM_FLEXICAP, document_id="kim_flexicap",
        source_url="https://www.sbimf.com/docs/default-source/default-library/kim---sbi-flexicap-fund.pdf",
        source_organization="SBI Mutual Fund", tier=1, scheme_id="SCH-02",
        topic="min_sip;min_lumpsum;additional_purchase;exit_load;benchmark",
        fact_type=FactType.STATIC, document_date="2025-04-30", date_collected="2026-08-26")
    cs += chunk_document(ELSS_SID, document_id="sid_elss",
        source_url="https://www.sbimf.com/docs/default-source/lists/sid---sbi-elss-tax-saver-fund.pdf",
        source_organization="SBI Mutual Fund", tier=1, scheme_id="SCH-03",
        topic="lock_in;scheme_type", fact_type=FactType.STATIC,
        document_date="2025-04-30", date_collected="2026-08-26")
    cs += chunk_document(AMFI_TER, document_id="amfi_ter",
        source_url="https://www.amfiindia.com/investor/knowledge-center-info?zoneName=expenseRatio",
        source_organization="AMFI", tier=2, scheme_id=None, topic="ter",
        fact_type=FactType.STATIC, date_collected="2026-08-26")
    return cs
