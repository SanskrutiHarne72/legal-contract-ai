def check_contract_completeness(contract_text, contract_type, form_data):
    """
    Checks if the generated contract text contains the required data from form_data.
    Returns a tuple of (checks, warnings).
    """
    _ct_lower = contract_text.lower()
    
    def _present(val):
        """True if val is non-empty and appears (approximately) in the contract text."""
        if not val or str(val).strip() in ("", "N/A", "0", "0.0"):
            return False
        # check if first 10 chars are present (to handle formatting or truncation differences)
        return str(val).strip()[:10].lower() in _ct_lower or str(val).strip().lower() in _ct_lower

    checks = []
    warns = []

    if contract_type == "Rental Agreement":
        checks_def = [
            ("landlord_name",    "Landlord name"),
            ("tenant_name",      "Tenant name"),
            ("property_address", "Property address"),
            ("rent_amount",      "Rent amount"),
            ("security_deposit", "Security deposit"),
            ("effective_date",   "Effective date"),
        ]
        for key, label in checks_def:
            if _present(form_data.get(key)):
                checks.append(f"✅ {label} is present")
            else:
                warns.append(f"⚠️ {label} — not found in draft (verify manually)")
    elif contract_type == "Employment Agreement":
        for key, label in [("employer_name","Employer name"),("employee_name","Employee name"),
                           ("job_title","Job title"),("salary_amount","Salary amount"),("joining_date","Joining date")]:
            if _present(form_data.get(key)):
                checks.append(f"✅ {label} is present")
            else:
                warns.append(f"⚠️ {label} — not found in draft")
    elif contract_type == "Non Disclosure Agreement (NDA)":
        for key, label in [("disclosing_party","Disclosing party"),("receiving_party","Receiving party"),
                           ("purpose","Purpose"),("survival_period","Survival period")]:
            if _present(form_data.get(key)):
                checks.append(f"✅ {label} is present")
            else:
                warns.append(f"⚠️ {label} — not found in draft")
    else:
        # Generic check for any other contract type
        for key, val in form_data.items():
            # Skip keys that are usually not directly in text or are internal
            if key in ["contract_type", "contract_title", "additional_requirements", "language", "currency"]:
                continue
            if val and str(val).strip() not in ("", "N/A", "0", "0.0"):
                label = key.replace("_", " ").title()
                if _present(val):
                    checks.append(f"✅ {label} is present")
                else:
                    warns.append(f"⚠️ {label} — not found in draft (verify manually)")

    # Common checks (all types)
    if any(sig in _ct_lower for sig in ["signature", "in witness whereof", "signed by", "witness"]):
        checks.append("✅ Signature section is present")
    else:
        warns.append("⚠️ Signature section — not detected (will be added to PDF)")

    if any(g in _ct_lower for g in ["governing law", "jurisdiction", "dispute"]):
        checks.append("✅ Governing law / jurisdiction is present")
    else:
        warns.append("⚠️ Governing law — not clearly stated")

    additional_req = form_data.get("additional_requirements", "").strip()
    if additional_req:
        warns.append("⚠️ Additional requirements provided — verify they are correctly integrated in the draft")

    if "[TO BE PROVIDED]" in contract_text or "[to be provided]" in _ct_lower:
        warns.append("⚠️ Placeholder remaining: [TO BE PROVIDED] found in document")
        
    if "clause" in _ct_lower or "section" in _ct_lower:
        checks.append("✅ Cross-references present (verify validity manually)")

    warns.append("⚠️ Legal verification required — AI drafts do not guarantee legal validity")

    return checks, warns
