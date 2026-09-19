"""
services/prompt_builder.py

Dynamic Prompt Generation Engine for AI Legal Contract Assistant.
Constructs highly specialized, contract-type-specific prompts and structured templates.
Enforces strict legal structure, prevents irrelevant clauses across contract types,
and ensures user-provided data is accurately represented without hallucinations.
"""


def build_contract_prompt(contract_type: str, data: dict) -> str:
    """
    Main dispatcher that routes contract generation requests to specialized
    prompt builders based on the selected contract type.
    """
    builders = {
        "Rental Agreement": build_rental_prompt,
        "Employment Agreement": build_employment_prompt,
        "Freelance Agreement": build_freelance_prompt,
        "Non Disclosure Agreement (NDA)": build_nda_prompt,
        "Service Agreement": build_service_prompt,
        "Sales Agreement": build_sale_prompt,
        "Sale / Purchase Agreement": build_sale_prompt,
        "Partnership Agreement": build_partnership_prompt,
        "Consultancy Agreement": build_consultancy_prompt,
        "Vendor Agreement": build_vendor_prompt,
        "Custom Contract": build_custom_prompt,
    }

    builder_fn = builders.get(contract_type, build_generic_prompt)
    return builder_fn(data)


def _get_common_header_instructions(contract_type: str, data: dict) -> str:
    country = data.get("country", "India")
    state   = data.get("state",   "Maharashtra")
    city    = data.get("city",    "Nagpur")
    lang    = data.get("language", "English")

    hindi_inst = ""
    if lang == "Hindi":
        hindi_inst = "\nIMPORTANT: Include a clear Hindi Summary (हिंदी संक्षेप) section at the end of the contract document.\n"

    additional = data.get("additional_requirements", "").strip()
    additional_block = ""
    if additional:
        additional_block = f"""
ADDITIONAL REQUIREMENTS FROM CLIENT (MUST be integrated into the appropriate clauses — do NOT dump them into a single paragraph):
{additional}
"""

    return f"""You are an AI-assisted legal drafting system. Prepare a professional {contract_type} based strictly on the supplied information.

Target Document Type: {contract_type}
Jurisdiction: {city}, {state}, {country}
Contract Title: {data.get('contract_title', contract_type)}
Effective Date: {data.get('effective_date', 'As of signing')}
Duration / Expiry: {data.get('duration_type', 'Fixed Term')} — {data.get('expiry_date', 'N/A')}
{additional_block}
=== MANDATORY DRAFTING RULES — READ CAREFULLY ===

1. STRUCTURE: Produce a formally structured legal agreement — NOT a narrative essay.
   Begin the contract directly with the title. Do NOT include any conversational explanations or unnecessary introductory text.
   Use clear numbered clauses (1., 2., 3.) and sub-clauses (1.1, 1.2, 1.3) where appropriate.
   Use consistent defined terms. Avoid repeated or contradictory clauses.

2. USE EXACT VALUES: Every name, address, date, and monetary amount supplied below
   MUST appear verbatim in the contract. Do NOT replace them with "Schedule A",
   "as specified", "as agreed", or any generic placeholder.

3. MISSING INFORMATION: If a required field is missing or left blank, use EXACTLY:
   [TO BE PROVIDED]
   Do NOT invent any names, addresses, dates, rent, deposit, notice periods, or payment methods.

4. PARTY IDENTIFICATION & OPENING: Start with a professional opening:
   [CONTRACT TITLE]
   This [Contract Type] ("Agreement") is made and entered into on [DATE] at [LOCATION].
   
   BETWEEN
   
   [PARTY A NAME]
   [PARTY A ADDRESS]
   hereinafter referred to as the "[PARTY A ROLE]"
   
   AND
   
   [PARTY B NAME]
   [PARTY B ADDRESS]
   hereinafter referred to as the "[PARTY B ROLE]"
   
   The [Party A Role] and [Party B Role] are collectively referred to as the "Parties".
   Do not use generic labels if actual names are provided.

5. RECITALS: Use formal WHEREAS clauses to introduce the agreement.
   Example:
   WHEREAS, ...;
   AND WHEREAS, ...;
   NOW, THEREFORE, the Parties agree as follows:
   (Do not use meaningless recitals).

6. NO FABRICATION: Do NOT invent or reference any Act, Law, Section, Amendment,
   Court Decision, or Legal Citation that is not explicitly provided in the
   Legal Context section. Write in standard contractual language.

7. NO LEGAL GUARANTEE: Do NOT claim this document is legally verified.

8. ADDITIONAL REQUIREMENTS: If additional requirements were supplied above,
   integrate them into the correct clauses (e.g. Pet policy goes in Pet Policy). Do not just append them.

9. SIGNATURE BLOCK: Always end with a professional signature section showing
   each party's name, role, signature line, and date field.
   Example:
   IN WITNESS WHEREOF, the Parties have executed this Agreement on the date first written above.
   [Role]
   Name: ______________________
   Signature: __________________
   Date: _______________________

10. SCHEDULES / ANNEXURES: If the generated contract refers to "Schedule A" (or any other Schedule/Annexure), automatically generate it at the end of the document containing the actual details supplied by the user (e.g., property details). If there is no information requiring a schedule, do NOT refer to it and do NOT generate it. Do NOT write "See Schedule A" unless it is actually generated.

11. CROSS-REFERENCES: Where appropriate, clauses may refer to other clauses. Ensure that any referenced clause actually exists. Do not create broken references.

12. DOCUMENT VERSION: Add document metadata at the end of the agreement (before signatures):
    Document Version: 1.0
    Draft Date: [DATE]
    Jurisdiction: {city}, {state}, {country}
{hindi_inst}=== CONTRACT DETAILS ===
"""


def build_rental_prompt(data: dict) -> str:
    header = _get_common_header_instructions("Rental Agreement", data)

    landlord_name    = data.get('landlord_name', '[Landlord Name]') or '[Landlord Name]'
    landlord_address = data.get('landlord_address', '[Landlord Address]') or '[Landlord Address]'
    landlord_contact = data.get('landlord_contact', '') or ''
    tenant_name      = data.get('tenant_name', '[Tenant Name]') or '[Tenant Name]'
    tenant_address   = data.get('tenant_address', '[Tenant Address]') or '[Tenant Address]'
    tenant_contact   = data.get('tenant_contact', '') or ''
    prop_address     = data.get('property_address', '[Property Address]') or '[Property Address]'
    prop_type        = data.get('property_type', 'Residential Premises')
    bedrooms         = data.get('bedrooms', '')
    furnishing       = data.get('furnishing', 'Unfurnished')
    parking          = data.get('parking', '')
    prop_usage       = data.get('property_usage', 'Strictly Residential')
    currency         = data.get('currency', 'INR')
    rent_amount      = data.get('rent_amount', '0')
    rent_due         = data.get('rent_due_date', '1st')
    security_dep     = data.get('security_deposit', '0')
    late_terms       = data.get('late_payment_terms', '5% late fee after 7-day grace period')
    maint_charges    = data.get('maintenance_charges', 'As agreed')
    utilities        = data.get('utility_responsibility', 'Tenant pays electricity and water; Landlord pays property taxes')
    notice_period    = data.get('notice_period', '1 Month')
    renewal_terms    = data.get('renewal_terms', 'Subject to mutual agreement')
    subletting       = data.get('subletting_allowed', 'No')
    pets             = data.get('pets_allowed', 'No')
    maint_resp       = data.get('maintenance_resp', 'Tenant: minor repairs; Landlord: structural repairs')
    restrictions     = data.get('restrictions', 'No illegal activities, no commercial use without prior consent')
    effective_date   = data.get('effective_date', '[Effective Date]')
    expiry_date      = data.get('expiry_date', '[Expiry Date]')
    duration_type    = data.get('duration_type', 'Fixed Term')
    country          = data.get('country', 'India')
    state            = data.get('state', 'Maharashtra')
    city             = data.get('city', 'Nagpur')

    pets_clause_instruction = ""
    if pets == "Yes" or "pet" in data.get('additional_requirements', '').lower():
        pets_clause_instruction = "- Include a dedicated PET POLICY clause permitting pets with reasonable conditions."
    else:
        pets_clause_instruction = "- The tenant is NOT permitted to keep pets. Include this restriction explicitly."

    return f"""{header}

=== PARTIES ===

LANDLORD (LESSOR):
  Full Name:    {landlord_name}
  Address:      {landlord_address}
  Contact:      {landlord_contact if landlord_contact else '[To be specified]'}
  Role Label:   "the Landlord" or "the Lessor"

TENANT (LESSEE):
  Full Name:    {tenant_name}
  Address:      {tenant_address}
  Contact:      {tenant_contact if tenant_contact else '[To be specified]'}
  Role Label:   "the Tenant" or "the Lessee"

=== PROPERTY ===

  Premises Address:   {prop_address}
  Property Type:      {prop_type}
  Bedrooms / Layout:  {bedrooms if bedrooms else '[As described in premises]'}
  Furnishing:         {furnishing}
  Parking:            {parking if parking else '[To be specified]'}
  Permitted Use:      {prop_usage}

=== FINANCIAL TERMS ===

  Monthly Rent:       {currency} {rent_amount}   ← USE THIS EXACT FIGURE
  Rent Due Date:      {rent_due} of each calendar month
  Security Deposit:   {currency} {security_dep} (fully refundable, subject to deductions)
  Late Payment:       {late_terms}
  Maintenance:        {maint_charges}
  Utilities:          {utilities}

=== TENANCY CONDITIONS ===

  Effective Date:     {effective_date}
  Expiry / End Date:  {expiry_date}
  Duration Type:      {duration_type}
  Notice Period:      {notice_period}
  Renewal Terms:      {renewal_terms}
  Subletting:         {subletting}
  Pets Policy:        {pets}
  Maintenance Resp:   {maint_resp}
  Restrictions:       {restrictions}

=== GOVERNING LAW ===

  This agreement is governed by the laws applicable in {city}, {state}, {country}.
  Dispute resolution by negotiation, then arbitration, then courts of {city}.

=== REQUIRED SECTIONS — PRODUCE EXACTLY THESE (numbered 1 to 20) ===

1.  DEFINITIONS
2.  PREMISES / PROPERTY
    (Full address: {prop_address} — USE VERBATIM. Property type, furnishing, parking.)
3.  TERM
    (Start: {effective_date}, End: {expiry_date}, type: {duration_type})
4.  RENT
    (Exact amount: {currency} {rent_amount} per month. Due date: {rent_due}. {late_terms}. Payment method if provided.)
5.  SECURITY DEPOSIT
    (Exact amount: {currency} {security_dep}. Conditions for refund / deduction.)
6.  USE OF PROPERTY
    (Permitted use: {prop_usage}. No commercial use / illegal activities.)
7.  MAINTENANCE AND REPAIRS
    ({maint_resp})
8.  UTILITIES
    ({utilities})
9.  LANDLORD'S OBLIGATIONS
    (Quiet enjoyment, structural repairs, building taxes, etc.)
10. TENANT'S OBLIGATIONS
    (Timely rent payment, cleanliness, minor repairs, no damage, etc.)
11. RESTRICTIONS
    (No alterations without consent. {restrictions})
12. PET POLICY
    (Include full terms if permitted, or strict prohibition if not permitted. {pets_clause_instruction})
13. SUBLETTING
    (No subletting allowed: {subletting})
14. INSPECTION
    (Landlord may inspect with 24-48 hours written notice.)
15. TERMINATION
    (Conditions: rent default, breach.)
16. NOTICE
    (How notice must be given in writing. Required period: {notice_period}.)
17. DISPUTE RESOLUTION
    (Negotiation → Mediation → Arbitration → Courts of {city}, {state}.)
18. GOVERNING LAW
    (Laws of {state}, {country}. Jurisdiction: {city}.)
19. GENERAL PROVISIONS
    (Entire agreement, severability, waiver, amendments must be in writing.)
20. SIGNATURES
    (Professional block: Landlord name / signature / date AND Tenant name / signature / date.)

CRITICAL REMINDERS:
- Never invent information. Use [TO BE PROVIDED] if something is missing.
- Make sure to use subclauses (4.1, 4.2) for readability.
- Do not cite any Indian law, Act, or Section unless it is provided in the Legal Context. Write clauses in standard contractual language.
"""


def build_employment_prompt(data: dict) -> str:
    header = _get_common_header_instructions("Employment Agreement", data)
    additional = data.get('additional_requirements', '').strip()
    add_block = f"\nADDITIONAL REQUIREMENTS: {additional}\n" if additional else ""
    return f"""{header}
{add_block}
EMPLOYMENT AGREEMENT — PARTY & POSITION DETAILS:

EMPLOYER:
  Company Name:     {data.get('employer_name', 'N/A')}
  Address:          {data.get('employer_address', 'N/A')}
  Representative:   {data.get('authorized_rep', 'N/A')}
  Role Label:       "the Employer" or "the Company"

EMPLOYEE:
  Full Name:        {data.get('employee_name', 'N/A')}
  Contact:          {data.get('employee_contact', 'N/A')}
  Address:          {data.get('employee_address', 'N/A')}
  Role Label:       "the Employee"

POSITION & APPOINTMENT:
  Job Title:        {data.get('job_title', 'N/A')}
  Department:       {data.get('department', 'N/A')}
  Employment Type:  {data.get('employment_type', 'Full-Time Permanent')}
  Joining Date:     {data.get('joining_date', 'N/A')}
  Work Location:    {data.get('work_location', 'N/A')}
  Working Hours:    {data.get('working_hours', 'Standard Business Hours')}
  Probation Period: {data.get('probation_period', '3 Months')}

COMPENSATION:
  Base Salary:      {data.get('currency','INR')} {data.get('salary_amount', '0')} per {data.get('salary_frequency', 'Month')} — USE VERBATIM
  Bonus:            {data.get('bonus_details', 'Discretionary performance bonus')}
  Benefits:         {data.get('benefits_details', 'As per company policy')}

CONDITIONS:
  Responsibilities: {data.get('responsibilities', 'As assigned')}
  Leave Policy:     {data.get('leave_policy', 'As per statutory regulations')}
  Confidentiality:  {data.get('confidentiality_terms', 'Strict NDA during and after employment')}
  IP Assignment:    {data.get('ip_terms', 'All work product belongs to Employer')}
  Non-Solicitation: {data.get('conduct_rules', '12 months post-termination')}
  Notice Period:    {data.get('notice_period', '30 Days')}

REQUIRED SECTIONS IN OUTPUT (numbered 1 to 14):
1. Definitions
2. Parties (BETWEEN / AND block)
3. Appointment & Commencement
4. Position, Duties & Reporting
5. Working Hours, Location & Mode
6. Probation Period & Confirmation
7. Compensation & Benefits
8. Confidentiality & Trade Secrets
9. Intellectual Property
10. Conflict of Interest & Non-Solicitation
11. Termination & Notice Period
12. Return of Company Property
13. Governing Law & Dispute Resolution
14. Signatures

CRITICAL: Use the exact salary figure {data.get('currency','INR')} {data.get('salary_amount','0')} — never replace with a placeholder.
"""


def build_freelance_prompt(data: dict) -> str:
    header = _get_common_header_instructions("Freelance Agreement", data)
    additional = data.get('additional_requirements', '').strip()
    add_block = f"\nADDITIONAL REQUIREMENTS: {additional}\n" if additional else ""
    return f"""{header}
{add_block}
FREELANCE AGREEMENT — PARTY & PROJECT DETAILS:

CLIENT:
  Name / Org:       {data.get('client_name', 'N/A')}
  Address:          {data.get('client_address', 'N/A')}
  Contact:          {data.get('client_contact', 'N/A')}
  Role Label:       "the Client"

FREELANCER (INDEPENDENT CONTRACTOR):
  Full Name:        {data.get('freelancer_name', 'N/A')}
  Address:          {data.get('freelancer_address', 'N/A')}
  Contact:          {data.get('freelancer_contact', 'N/A')}
  Role Label:       "the Freelancer" or "the Contractor"

PROJECT:
  Project Name:     {data.get('project_name', 'N/A')}
  Services:         {data.get('service_description', 'N/A')}
  Deliverables:     {data.get('deliverables', 'N/A')}
  Start Date:       {data.get('start_date', 'N/A')}
  Completion Date:  {data.get('end_date', 'N/A')}

COMMERCIALS:
  Total Fee:        {data.get('currency','INR')} {data.get('project_fee','0')} — USE VERBATIM
  Payment Schedule: {data.get('payment_schedule','Milestone-based')}
  Advance:          {data.get('currency','INR')} {data.get('advance_payment','0')}
  Payment Method:   {data.get('payment_method','Bank Transfer')}
  Late Payment:     {data.get('late_payment_terms','1.5% monthly on overdue amounts')}
  Work Mode:        {data.get('work_mode','Remote')}
  Revisions:        {data.get('revision_policy','2 rounds included')}
  IP Ownership:     {data.get('ip_ownership','Transfers to Client on full payment')}
  Confidentiality:  {data.get('confidentiality_terms','Strict NDA')}
  Termination:      {data.get('termination_terms','7 days written notice')}

REQUIRED SECTIONS (numbered 1 to 12):
1. Definitions
2. Parties (BETWEEN / AND block)
3. Relationship of Parties (Independent Contractor — not employee)
4. Scope of Services & Deliverables
5. Schedule & Milestones
6. Fees & Payment Terms
7. Revisions & Scope Creep
8. Intellectual Property
9. Confidentiality
10. Warranties & Liability
11. Termination
12. Governing Law & Signatures
"""


def build_nda_prompt(data: dict) -> str:
    header = _get_common_header_instructions("Non Disclosure Agreement (NDA)", data)
    additional = data.get('additional_requirements', '').strip()
    add_block = f"\nADDITIONAL REQUIREMENTS: {additional}\n" if additional else ""
    return f"""{header}
{add_block}
NDA — PARTY & DISCLOSURE DETAILS:

DISCLOSING PARTY:
  Name / Entity:    {data.get('disclosing_party', 'N/A')}
  Address:          {data.get('disclosing_address', 'N/A')}
  Contact:          {data.get('disclosing_contact', 'N/A')}
  Role Label:       "the Disclosing Party"

RECEIVING PARTY:
  Name / Entity:    {data.get('receiving_party', 'N/A')}
  Address:          {data.get('receiving_address', 'N/A')}
  Contact:          {data.get('receiving_contact', 'N/A')}
  Role Label:       "the Receiving Party"

CONFIDENTIALITY SCOPE:
  NDA Type:         {data.get('nda_type', 'Unilateral')}
  Purpose:          {data.get('purpose', 'Evaluating potential business relationship')}
  Confidential Info: {data.get('confidential_types', 'Technical data, trade secrets, financial records')}
  Survival Period:  {data.get('survival_period', '3 Years post-termination')}
  Return / Destroy: {data.get('return_data', 'Certified destruction within 14 days of written demand')}
  Exceptions:       {data.get('exceptions', 'Public domain, prior knowledge, independently developed')}
  Remedies:         {data.get('remedies', 'Injunctive relief and monetary damages')}

REQUIRED SECTIONS (numbered 1 to 12):
1. Definitions
2. Parties (BETWEEN / AND block)
3. Recitals & Purpose
4. Definition of Confidential Information
5. Obligations of Receiving Party
6. Exclusions & Carve-Outs
7. Permitted Use
8. Compelled Disclosure
9. Return / Destruction of Materials
10. Term & Survival
11. Remedies
12. Governing Law & Signatures
"""


def build_service_prompt(data: dict) -> str:
    header = _get_common_header_instructions("Service Agreement", data)
    additional = data.get('additional_requirements', '').strip()
    add_block = f"\nADDITIONAL REQUIREMENTS: {additional}\n" if additional else ""
    return f"""{header}
{add_block}
SERVICE AGREEMENT — PARTY & SERVICE DETAILS:

CLIENT:
  Name / Org:       {data.get('client_name', 'N/A')}
  Address:          {data.get('client_address', 'N/A')}
  Contact:          {data.get('client_contact', 'N/A')}
  Role Label:       "the Client"

SERVICE PROVIDER:
  Name / Org:       {data.get('provider_name', 'N/A')}
  Address:          {data.get('provider_address', 'N/A')}
  Contact:          {data.get('provider_contact', 'N/A')}
  Role Label:       "the Service Provider"

SERVICE SCOPE:
  Service Title:    {data.get('service_name', 'N/A')}
  Scope of Work:    {data.get('scope_of_work', 'N/A')}
  Deliverables:     {data.get('deliverables', 'N/A')}
  Start Date:       {data.get('start_date', 'N/A')}
  End Date:         {data.get('end_date', 'N/A')}

COMMERCIALS:
  Total Fee:        {data.get('currency','INR')} {data.get('total_fee','0')} — USE VERBATIM
  Payment Schedule: {data.get('payment_schedule','Monthly')}
  Payment Method:   {data.get('payment_method','Bank Transfer')}
  Taxes:            {data.get('taxes_terms','Exclusive of GST')}
  Liability Cap:    {data.get('liability_cap','Total fees in preceding 12 months')}
  Termination:      {data.get('termination_terms','30 days written notice')}

REQUIRED SECTIONS (numbered 1 to 12):
1. Definitions
2. Parties (BETWEEN / AND block)
3. Scope of Work & Deliverables
4. Performance Schedule & Acceptance
5. Fees, Taxes & Payment Terms
6. Client Obligations
7. Provider Warranties
8. Intellectual Property
9. Confidentiality
10. Limitation of Liability & Indemnification
11. Termination
12. Governing Law & Signatures
"""


def build_sale_prompt(data: dict) -> str:
    header = _get_common_header_instructions("Sale / Purchase Agreement", data)
    return f"""{header}
SALE / PURCHASE AGREEMENT DETAILS & PARTIES:

1. BUYER:
- Full Name / Entity: {data.get('buyer_name', 'N/A')}
- Address: {data.get('buyer_address', 'N/A')}
- Contact: {data.get('buyer_contact', 'N/A')}

2. SELLER:
- Full Name / Entity: {data.get('seller_name', 'N/A')}
- Address: {data.get('seller_address', 'N/A')}
- Contact: {data.get('seller_contact', 'N/A')}

3. ITEM / ASSET DESCRIPTION:
- Item Description: {data.get('item_description', 'N/A')}
- Quantity / Units: {data.get('quantity', '1')}
- Condition of Asset: {data.get('item_condition', 'Brand New / As-Is')}
- Serial No / Identification: {data.get('item_id', 'N/A')}

4. FINANCIAL TERMS:
- Total Purchase Price: {data.get('purchase_price', '0')} {data.get('currency', 'INR')}
- Advance Deposit: {data.get('advance_payment', '0')} {data.get('currency', 'INR')}
- Balance Payment Terms: {data.get('balance_payment', 'Due prior to or upon delivery')}
- Payment Method: {data.get('payment_method', 'Bank Transfer / Wire')}
- Tax Responsibility: {data.get('tax_responsibility', 'Buyer pays applicable sales tax / GST')}

5. DELIVERY & TITLE TRANSFER:
- Delivery Date: {data.get('delivery_date', 'N/A')}
- Delivery Location: {data.get('delivery_location', 'N/A')}
- Delivery Responsibility & Risk of Loss: {data.get('delivery_resp', 'Risk of loss passes to Buyer upon physical delivery')}

6. LEGAL WARRANTIES & INSPECTION:
- Title Warranty: Seller warrants clear, unencumbered ownership of asset free of liens or claims.
- Seller Warranties / Disclaimers: {data.get('warranties', 'Sold with standard manufacturer warranty')}
- Buyer Inspection Period: {data.get('inspection_period', '3 Business Days to inspect and report defects')}

REQUIRED SECTIONS IN OUTPUT:
1. Preamble & Agreement to Sell/Purchase
2. Description of Asset / Goods & Quantity
3. Purchase Price, Deposit & Payment Terms
4. Delivery, Shipping & Transfer of Risk of Loss
5. Title Transfer & Guarantee of Ownership
6. Buyer Inspection Period & Acceptance Mechanics
7. Warranties, Disclaimers & Disclosures
8. Breach & Remedies
9. Governing Law & Dispute Resolution
10. Signature Blocks for Buyer & Seller
"""


def build_partnership_prompt(data: dict) -> str:
    header = _get_common_header_instructions("Partnership Agreement", data)
    return f"""{header}
PARTNERSHIP AGREEMENT DETAILS & PARTIES:

1. PARTNER 1:
- Full Name: {data.get('p1_name', 'N/A')}
- Address: {data.get('p1_address', 'N/A')}
- Capital Contribution: {data.get('p1_capital', '0')} {data.get('currency', 'INR')}
- Profit / Loss Share %: {data.get('p1_share', '50')}%

2. PARTNER 2:
- Full Name: {data.get('p2_name', 'N/A')}
- Address: {data.get('p2_address', 'N/A')}
- Capital Contribution: {data.get('p2_capital', '0')} {data.get('currency', 'INR')}
- Profit / Loss Share %: {data.get('p2_share', '50')}%

3. PARTNERSHIP BUSINESS DETAILS:
- Partnership Business Name: {data.get('firm_name', 'N/A')}
- Nature of Business / Objectives: {data.get('business_nature', 'N/A')}
- Principal Place of Business: {data.get('firm_address', 'N/A')}

4. FINANCIAL & MANAGEMENT GOVERNANCE:
- Total Capital Pool: {data.get('total_capital', '0')} {data.get('currency', 'INR')}
- Bank Account Authorization: {data.get('bank_auth', 'Joint signatures required for transactions above threshold')}
- Management Roles: {data.get('management_roles', 'Equal voting rights; day-to-day operations shared')}
- Accounting Year & Audit: {data.get('accounting_year', 'April 1 to March 31 financial year')}

5. COVENANTS & DISSOLUTION:
- Withdrawal & Retirement Terms: {data.get('withdrawal_terms', '6 months written notice for partner exit')}
- Dissolution Conditions: {data.get('dissolution_terms', 'Unanimous partner consent or insolvency')}
- Non-Compete Covenant: {data.get('non_compete_terms', 'Exited partners barred from competing for 2 years')}

REQUIRED SECTIONS IN OUTPUT:
1. Preamble & Formation of Partnership Firm
2. Business Name, Purpose & Principal Office
3. Capital Contributions & Capital Accounts
4. Profit & Loss Allocation Ratios
5. Banking, Financial Records & Accounting Methods
6. Partner Powers, Duties & Voting Rights
7. Admission of New Partners & Partner Retirement
8. Death, Insolvency or Incapacity of a Partner
9. Non-Compete & Non-Disclosure Covenants
10. Partnership Dissolution & Winding-Up Mechanics
11. Dispute Resolution & Arbitration
12. Signatures of All Partners
"""


def build_consultancy_prompt(data: dict) -> str:
    header = _get_common_header_instructions("Consultancy Agreement", data)
    return f"""{header}
CONSULTANCY AGREEMENT DETAILS & PARTIES:

1. CLIENT COMPANY:
- Name / Entity: {data.get('client_name', 'N/A')}
- Representative: {data.get('client_rep', 'N/A')}
- Address: {data.get('client_address', 'N/A')}

2. INDEPENDENT CONSULTANT:
- Name / Advisory Firm: {data.get('consultant_name', 'N/A')}
- Contact Email / Phone: {data.get('consultant_contact', 'N/A')}
- Address: {data.get('consultant_address', 'N/A')}

3. CONSULTANCY SCOPE & EXPERTISE:
- Field of Advisory Expertise: {data.get('expertise_area', 'N/A')}
- Scope of Advisory Services: {data.get('scope_of_consultancy', 'N/A')}
- Key Advisory Deliverables & Reports: {data.get('consultancy_deliverables', 'N/A')}

4. COMMERCIAL & RETAINER TERMS:
- Retainer / Consultancy Fee: {data.get('consultancy_fee', '0')} {data.get('currency', 'INR')}
- Billing Structure: {data.get('billing_structure', 'Monthly Retainer')}
- Out-of-Pocket Expense Reimbursement: {data.get('expense_terms', 'Pre-approved travel and out-of-pocket expenses reimbursed at actuals')}
- Payment Terms & Late Interest: {data.get('payment_terms', 'Invoices payable within 15 days')}

5. LEGAL STATUS & IP:
- Independent Consultant Status: Consultant is an independent advisor, not an employee.
- Work Product IP Assignment: {data.get('ip_assignment', 'All strategic reports and advisory deliverables assigned to Client upon payment')}
- Non-Exclusive Engagement: Consultant may advise non-competing third parties.
- Termination Notice: {data.get('notice_period', '30 days written notice')}

REQUIRED SECTIONS IN OUTPUT:
1. Preamble & Engagement of Consultant
2. Scope of Advisory Services & Retainer Schedule
3. Retainer Fees, Expense Reimbursement & Invoicing
4. Independent Status & Non-Employee Declaration
5. Ownership of Work Product & Advisory Deliverables
6. Confidential Information & Data Protection
7. Non-Exclusive Engagement & Conflicts of Interest
8. Warranties & Limitation of Liability
9. Term & Termination Notice Period
10. Governing Law & Dispute Resolution
11. Execution Signatures
"""


def build_vendor_prompt(data: dict) -> str:
    header = _get_common_header_instructions("Vendor Agreement", data)
    return f"""{header}
VENDOR AGREEMENT DETAILS & PARTIES:

1. PURCHASER (BUYER):
- Company Name: {data.get('purchaser_name', 'N/A')}
- Authorized Buyer: {data.get('purchaser_contact', 'N/A')}
- Address: {data.get('purchaser_address', 'N/A')}

2. VENDOR (SUPPLIER):
- Vendor Organization: {data.get('vendor_name', 'N/A')}
- Tax / GST Registration No: {data.get('vendor_tax_id', 'N/A')}
- Address: {data.get('vendor_address', 'N/A')}

3. SUPPLY SCOPE & PRODUCT SPECIFICATIONS:
- Product / Supply Description: {data.get('supply_description', 'N/A')}
- Supply Frequency / Quantity: {data.get('supply_frequency', 'As per Purchase Orders')}
- Quality & Inspection Standards: {data.get('quality_standards', 'Conforming strictly to ISO / Industry technical standards')}
- Delivery Lead Time: {data.get('lead_time', '7 Business Days from Purchase Order date')}

4. PRICING & COMMERCIAL TERMS:
- Contract Value / Unit Rates: {data.get('contract_value', '0')} {data.get('currency', 'INR')}
- Payment Terms: {data.get('payment_terms', 'Net 30 Days from invoice and acceptance of goods')}
- Penalties for Delayed Supply: {data.get('penalty_terms', '0.5% per week penalty on late deliveries, capped at 10%')}

5. REJECTION & WARRANTIES:
- Rejection & Replacement Window: {data.get('rejection_terms', 'Defective supplies returned at Vendor expense within 14 days')}
- Vendor Product Warranty: {data.get('vendor_warranty', '12 months warranty against manufacturing defects')}
- Termination for Default: {data.get('termination_terms', 'Immediate termination upon repeated supply default or defective delivery')}

REQUIRED SECTIONS IN OUTPUT:
1. Preamble & Appointment of Vendor
2. Scope of Supply & Purchase Order Process
3. Pricing, Invoicing & Payment Terms (Net 30/60)
4. Delivery Specifications, Timelines & Lead Times
5. Quality Assurance, Inspection & Rejection Mechanics
6. Warranties & Guarantee of Defect-Free Supplies
7. Vendor Indemnification & Product Liability
8. Confidentiality & Data Privacy
9. Term & Termination Mechanics
10. Governing Law & Dispute Resolution
11. Signature Blocks
"""


def build_custom_prompt(data: dict) -> str:
    contract_title = data.get("contract_title", "Custom Legal Agreement")
    header = _get_common_header_instructions(contract_title, data)
    return f"""{header}
CUSTOM AGREEMENT DETAILS & PARTIES:

1. FIRST PARTY (PARTY A):
- Name: {data.get('custom_party_a_name', 'N/A')} ({data.get('custom_party_a_company', 'N/A')})
- Contact / Address: {data.get('custom_party_a_contact', 'N/A')}, {data.get('custom_party_a_address', 'N/A')}

2. SECOND PARTY (PARTY B):
- Name: {data.get('custom_party_b_name', 'N/A')} ({data.get('custom_party_b_company', 'N/A')})
- Contact / Address: {data.get('custom_party_b_contact', 'N/A')}, {data.get('custom_party_b_address', 'N/A')}

3. AGREEMENT SUBJECT & COVENANTS:
- Custom Agreement Title: {contract_title}
- Detailed Purpose & Objectives: {data.get('custom_purpose', 'N/A')}
- Primary Scope & Deliverables: {data.get('custom_scope', 'N/A')}
- Financial & Commercial Covenants: {data.get('custom_financials', 'N/A')} {data.get('currency', 'INR')}
- Special Conditions & Terms: {data.get('custom_conditions', 'N/A')}

REQUIRED SECTIONS IN OUTPUT:
1. Preamble & Formal Recitals
2. Subject Matter, Purpose & Scope of Covenants
3. Financial Terms & Consideration
4. Rights, Duties & Obligations of Parties
5. Representation, Warranties & Protective Provisions
6. Term, Breach & Termination Mechanics
7. Governing Law & Jurisdiction
8. Signatures & Execution Blocks
"""


def build_generic_prompt(data: dict) -> str:
    contract_type = data.get("contract_type", "Legal Agreement")
    header = _get_common_header_instructions(contract_type, data)
    return f"""{header}
CONTRACT DETAILS & PARTIES:

1. PARTY A:
- Name: {data.get('party_a_name', 'N/A')} ({data.get('party_a_company', 'N/A')})
- Contact / Address: {data.get('party_a_email', 'N/A')}, {data.get('party_a_address', 'N/A')}

2. PARTY B:
- Name: {data.get('party_b_name', 'N/A')} ({data.get('party_b_company', 'N/A')})
- Contact / Address: {data.get('party_b_email', 'N/A')}, {data.get('party_b_address', 'N/A')}

3. OBJECTIVE & SCOPE:
- Purpose: {data.get('purpose', 'N/A')}
- Scope of Work / Obligations: {data.get('scope', 'N/A')}
- Deliverables: {data.get('deliverables', 'N/A')}

4. COMMERCIAL TERMS:
- Payment Amount: {data.get('payment_amount', '0')} {data.get('currency', 'INR')}
- Payment Schedule & Method: {data.get('payment_schedule', 'One Time')} via {data.get('payment_method', 'Bank Transfer')}

5. OBLIGATIONS & CLAUSES:
- Party A Obligations: {data.get('party_a_responsibility', 'N/A')}
- Party B Obligations: {data.get('party_b_responsibility', 'N/A')}
- Protective Clauses Included: {", ".join(data.get('clauses', []))}
- Special Provisions: {data.get('additional_terms', 'None')}

REQUIRED SECTIONS IN OUTPUT:
1. Preamble & Recitals
2. Scope & Purpose of Agreement
3. Consideration & Commercial Terms
4. Obligations of Party A and Party B
5. Protective Legal Clauses (Confidentiality, IP, Liability, Termination)
6. Governing Law & Jurisdiction
7. Signature Execution Blocks
"""
