"""
Human-readable document titles. Internal ids like `kim_flexicap` are for
joins, not for a person deciding whether to trust an answer. The UI shows
the title; the id stays in the data layer.
"""
TITLES = {
    "kim_large_cap":     ("Key Information Memorandum", "SBI Large Cap Fund"),
    "kim_flexicap":      ("Key Information Memorandum", "SBI Flexicap Fund"),
    "kim_elss":          ("Key Information Memorandum", "SBI ELSS Tax Saver Fund"),
    "kim_common_appform":("Common Application Form with KIM", None),
    "sid_elss":          ("Scheme Information Document", "SBI ELSS Tax Saver Fund"),
    "sid_flexicap":      ("Scheme Information Document", "SBI Flexicap Fund"),
    "campaign_elss":     ("Official scheme page", "SBI ELSS Tax Saver Fund"),
    "ter_current_year":  ("Total Expense Ratio disclosure", None),
    "factsheet_mar2026": ("Monthly factsheet, March 2026", None),
    "amfi_ter":          ("Expense ratio, investor knowledge centre", None),
    "amfi_riskometer":   ("How a scheme riskometer is derived", None),
    "amfi_lockin":       ("What is a lock-in period", None),
    "groww_help_elss":   ("Help centre: download ELSS statement", None),
    "groww_help_txn":    ("Help centre: transaction history", None),
    "groww_help_80c":    ("Help centre: Section 80C tax proof", None),
}


def title_for(document_id: str) -> str:
    doc, scheme = TITLES.get(document_id, (document_id, None))
    return f"{doc} — {scheme}" if scheme else doc
