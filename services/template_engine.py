import re
from typing import Dict

# ──────────────────────────────────────────────────────────────────────────────
# Formal Legal Agreement Templates for Local Contract Generation
# ──────────────────────────────────────────────────────────────────────────────

TEMPLATES = {
    "Rental Agreement": """# RESIDENTIAL LEAVE AND LICENCE AGREEMENT

**THIS LEAVE AND LICENCE AGREEMENT** (hereinafter referred to as the "Agreement") is made and executed at **[CITY], [STATE]** on this **[DATE]**, by and between:

**[LANDLORD_NAME]**, residing at [LANDLORD_ADDRESS], Contact: [LANDLORD_CONTACT] (hereinafter referred to as the **"Licensor / Landlord"**, which expression shall, unless repugnant to the context or meaning thereof, include its legal heirs, executors, administrators, and permitted assigns) of the **FIRST PART**;

**AND**

**[TENANT_NAME]**, residing at [TENANT_ADDRESS], Contact: [TENANT_CONTACT] (hereinafter referred to as the **"Licensee / Tenant"**, which expression shall, unless repugnant to the context or meaning thereof, include its legal heirs, executors, administrators, and permitted assigns) of the **SECOND PART**.

The Licensor and the Licensee are hereinafter collectively referred to as the **"Parties"** and individually as a **"Party"**.

---

### RECITALS

**WHEREAS:**

A. The Licensor is the absolute owner and lawful possessor of the residential premises situated at **[PROPERTY_ADDRESS]** (hereinafter referred to as the **"Licensed Premises"**).

B. The Licensee has requested the Licensor to grant a leave and licence to occupy and use the Licensed Premises strictly for residential purposes for a temporary period.

C. Relying on the representations made by the Licensee, the Licensor has agreed to grant such leave and licence on the terms, conditions, and covenants set forth herein below.

**NOW, THEREFORE, IN CONSIDERATION OF THE MUTUAL COVENANTS AND AGREEMENTS CONTAINED HEREIN, THE PARTIES HERETO AGREE AS FOLLOWS:**

---

### 1. GRANT OF LICENCE AND PERMITTED USE
1.1 The Licensor hereby grants to the Licensee, and the Licensee hereby accepts from the Licensor, the leave and licence to use and occupy the Licensed Premises described in **Schedule A** attached hereto.
1.2 The Licensed Premises shall be used strictly and exclusively by the Licensee and their immediate family members for residential purposes only. The Licensee shall not use the Licensed Premises or any part thereof for any commercial, business, industrial, or unlawful activity.

---

### 2. TERM OF AGREEMENT
2.1 The licence granted hereunder shall be valid for a fixed period of **[DURATION]** commencing from **[EFFECTIVE_DATE]** (the "Commencement Date") and expiring on **[EXPIRY_DATE]** (the "Expiry Date"), unless terminated earlier in accordance with the terms of this Agreement.
2.2 Any renewal of this Agreement shall be subject to the mutual written consent of both Parties at least thirty (30) days prior to the Expiry Date.

---

### 3. LICENCE FEE AND CONSIDERATION
3.1 **Monthly Licence Fee:** The Licensee shall pay to the Licensor a monthly licence fee / rent of **Rs. [RENT_AMOUNT] ([RENT_IN_WORDS])** payable in advance on or before the **[RENT_DUE_DATE]** day of each English calendar month.
3.2 **Mode of Payment:** All payments under this Agreement shall be remitted into the Licensor's designated bank account or through mutually agreed electronic payment modes.
3.3 **Late Payment Charges:** Any delay in the payment of the monthly licence fee beyond the due date shall attract late payment charges as specified in **Schedule A**.

---

### 4. SECURITY DEPOSIT
4.1 The Licensee has deposited with the Licensor an interest-free refundable security deposit of **Rs. [SECURITY_DEPOSIT] ([DEPOSIT_IN_WORDS])** upon the execution of this Agreement.
4.2 The Security Deposit shall be refunded by the Licensor to the Licensee within seven (7) days of vacant, peaceful handover of possession of the Licensed Premises upon expiry or earlier termination of this Agreement, after deducting any arrears of licence fees, utility bills, or costs incurred for repairing physical damages caused to the Licensed Premises beyond normal wear and tear.

---

### 5. UTILITIES AND MAINTENANCE OBLIGATIONS
5.1 **Utility Charges:** The Licensee shall promptly pay all charges for electricity, water, cooking gas, internet, and cable consumption incurred during the term of tenancy directly to the concerned authorities or service providers.
5.2 **Maintenance:** The Licensee shall maintain the Licensed Premises in a clean, sanitary, and tenantable condition. The Licensee shall be responsible for routine minor repairs and day-to-day upkeep. Major structural repairs and property taxes shall be the responsibility of the Licensor.

---

### 6. RESTRICTIONS AND COVENANTS
6.1 **Subletting Prohibited:** The Licensee shall not assign, sublet, transfer, or part with possession of the Licensed Premises or any portion thereof to any third party under any circumstances.
6.2 **Alterations:** The Licensee shall not make any structural alterations, additions, or permanent modifications to the Licensed Premises without the prior written approval of the Licensor.
6.3 **Nuisance and Compliance:** The Licensee shall abide by all rules, guidelines, and bylaws of the cooperative housing society or premises association, and shall not commit any act of nuisance, disturbance, or annoyance to neighbors.

---

### 7. TERMINATION AND HANDOVER OF POSSESSION
7.1 **Termination by Notice:** Either Party may terminate this Agreement by giving a prior written **Notice Period of [NOTICE_PERIOD]** to the other Party.
7.2 **Termination for Default:** In the event of default by the Licensee in paying the monthly licence fee for a continuous period exceeding fifteen (15) days, or material breach of any covenant herein, the Licensor shall be entitled to terminate this Agreement immediately and re-enter the Licensed Premises.
7.3 **Handover:** Upon expiry or earlier termination of this Agreement, the Licensee shall surrender peaceful and vacant possession of the Licensed Premises along with all fittings and fixtures in good condition to the Licensor.

---

### 8. GOVERNING LAW AND DISPUTE RESOLUTION
8.1 This Agreement shall be governed by, construed, and enforced in accordance with the laws of **India**.
8.2 Any dispute, controversy, or claim arising out of or relating to this Agreement shall be subject to the exclusive jurisdiction of the competent courts located at **[CITY], [STATE]**.

---

### SCHEDULE A — PROPERTY AND COMMERCIAL DETAILS

* **Property Address:** [PROPERTY_ADDRESS]
* **Property Type / Layout:** [PROPERTY_TYPE] ([BEDROOMS] Bedrooms, [FURNISHING] Furnishing)
* **Permitted Use:** [PROPERTY_USAGE]
* **Monthly Licence Fee:** Rs. [RENT_AMOUNT]
* **Rent Due Date:** [RENT_DUE_DATE] of each calendar month
* **Security Deposit:** Rs. [SECURITY_DEPOSIT]
* **Licence Term:** [DURATION] (Commencement: [EFFECTIVE_DATE] | Expiry: [EXPIRY_DATE])
* **Notice Period:** [NOTICE_PERIOD]
* **Parking Details:** [PARKING]

---

### IN WITNESS WHEREOF
**IN WITNESS WHEREOF**, the Parties hereto have executed and delivered this Agreement on the date and place first hereinabove written.

**FOR AND ON BEHALF OF THE LICENSOR / LANDLORD:**

Signature: ___________________________________
Name: **[LANDLORD_NAME]**
Date: _______________________________________
Place: **[CITY], [STATE]**


**FOR AND ON BEHALF OF THE LICENSEE / TENANT:**

Signature: ___________________________________
Name: **[TENANT_NAME]**
Date: _______________________________________
Place: **[CITY], [STATE]**


**WITNESSES:**

1. Signature: ___________________________
   Name: _______________________________
   Address: ____________________________

2. Signature: ___________________________
   Name: _______________________________
   Address: ____________________________
""",

    "Employment Agreement": """# INDIVIDUAL EMPLOYMENT AGREEMENT

**THIS EMPLOYMENT AGREEMENT** (hereinafter referred to as the "Agreement") is made and executed at **[CITY], [STATE]** on this **[DATE]**, by and between:

**[EMPLOYER_NAME]**, having its office at [EMPLOYER_ADDRESS], Contact: [EMPLOYER_CONTACT] (hereinafter referred to as the **"Employer"** or the **"Company"**, which expression shall include its successors and permitted assigns) of the **FIRST PART**;

**AND**

**[EMPLOYEE_NAME]**, residing at [EMPLOYEE_ADDRESS], Contact: [EMPLOYEE_CONTACT] (hereinafter referred to as the **"Employee"**) of the **SECOND PART**.

The Employer and the Employee are hereinafter collectively referred to as the **"Parties"** and individually as a **"Party"**.

---

### RECITALS

**WHEREAS:**

A. The Employer is engaged in business operations and requires qualified professionals to assist in its organizational objectives.

B. The Employee represents that they possess the necessary qualifications, skills, and experience to fulfill the duties required for the position of **[JOB_TITLE]**.

C. The Employer agrees to employ the Employee, and the Employee agrees to accept employment with the Employer, upon the terms and conditions set forth herein below.

**NOW, THEREFORE, IN CONSIDERATION OF THE MUTUAL COVENANTS AND AGREEMENTS CONTAINED HEREIN, THE PARTIES HERETO AGREE AS FOLLOWS:**

---

### 1. APPOINTMENT AND DUTIES
1.1 **Position:** The Employer hereby appoints the Employee to the position of **[JOB_TITLE]** in the **[DEPARTMENT]** department, reporting to [REPORTING_MANAGER].
1.2 **Duties:** The Employee shall perform all duties and responsibilities assigned to the position, adhere strictly to Company policies, and devote their full business time, attention, and effort to the business of the Employer.
1.3 **Work Location:** The primary place of work shall be at [WORK_LOCATION] ([WORK_MODE] arrangement), subject to relocation as per business requirements.

---

### 2. COMPENSATION AND BENEFITS
2.1 **Base Compensation:** The Employer shall pay the Employee a total compensation of **Rs. [BASE_SALARY] ([SALARY_PERIOD])**, payable in accordance with the Company's standard payroll practices, subject to statutory deductions and tax withholdings.
2.2 **Probation Period:** The Employee shall undergo a probation period of **[PROBATION_PERIOD]** from the Commencement Date. Confirmation of employment shall be communicated in writing upon satisfactory performance evaluation.
2.3 **Benefits and Leaves:** The Employee shall be entitled to paid annual leaves, medical coverage, and official holidays as per the Company's HR policy.

---

### 3. CONFIDENTIALITY AND NON-DISCLOSURE
3.1 **Confidential Information:** The Employee acknowledges that during the course of employment, they will have access to confidential, proprietary, and trade secret information belonging to the Company, including technical data, customer lists, software, and financial records.
3.2 **Obligation:** The Employee shall maintain strict confidentiality regarding all Confidential Information and shall not disclose or use such information for personal gain or for the benefit of any third party, during or after the termination of employment.

---

### 4. INTELLECTUAL PROPERTY RIGHTS
4.1 **Work Made for Hire:** All intellectual property, software, inventions, code, documentation, and designs created, developed, or produced by the Employee during their employment with the Company shall belong exclusively to the Employer as "work-made-for-hire".
4.2 **Assignment:** The Employee hereby assigns to the Employer all rights, titles, and interests in and to any intellectual property created during employment.

---

### 5. TERMINATION OF EMPLOYMENT
5.1 **Termination by Notice:** Either Party may terminate this Agreement by serving a prior written **Notice Period of [NOTICE_PERIOD]** or by paying salary in lieu thereof, subject to Company approval.
5.2 **Termination for Cause:** The Employer reserves the right to terminate the Employee's employment immediately without notice or severance pay in the event of gross misconduct, fraud, material breach of policy, or failure to perform duties.

---

### 6. GOVERNING LAW AND JURISDICTION
6.1 This Agreement shall be governed by and construed in accordance with the laws of **India**.
6.2 Any dispute arising out of or in connection with this Agreement shall be submitted to the exclusive jurisdiction of the courts located at **[CITY], [STATE]**.

---

### IN WITNESS WHEREOF
**IN WITNESS WHEREOF**, the Parties hereto have executed and delivered this Agreement on the date and place first hereinabove written.

**FOR AND ON BEHALF OF THE EMPLOYER:**

Signature: ___________________________________
Name: **[EMPLOYER_NAME]**
Title: Authorized Signatory
Date: _______________________________________


**FOR AND ON BEHALF OF THE EMPLOYEE:**

Signature: ___________________________________
Name: **[EMPLOYEE_NAME]**
Date: _______________________________________
""",

    "Freelance Agreement": """# INDEPENDENT FREELANCE CONTRACTOR AGREEMENT

**THIS FREELANCE AGREEMENT** (hereinafter referred to as the "Agreement") is made and executed at **[CITY], [STATE]** on this **[DATE]**, by and between:

**[CLIENT_NAME]**, having its address at [CLIENT_ADDRESS], Contact: [CLIENT_CONTACT] (hereinafter referred to as the **"Client"**, which expression shall include its successors and permitted assigns) of the **FIRST PART**;

**AND**

**[FREELANCER_NAME]**, residing at [FREELANCER_ADDRESS], Contact: [FREELANCER_CONTACT] (hereinafter referred to as the **"Freelancer"** or **"Independent Contractor"**) of the **SECOND PART**.

---

### RECITALS

**WHEREAS:**

A. The Client desires to retain the Freelancer to provide professional services for the project titled **"[PROJECT_NAME]"**.

B. The Freelancer possesses the technical competence and expertise to perform the requested services and agrees to provide the deliverables upon the terms set forth herein.

**NOW, THEREFORE, IT IS AGREED AS FOLLOWS:**

---

### 1. SCOPE OF SERVICES AND DELIVERABLES
1.1 The Freelancer shall render services to complete the project specifications described below:
* **Project Name:** [PROJECT_NAME]
* **Scope & Deliverables:** [SCOPE_OF_WORK]
1.2 The Freelancer shall perform the services in a professional manner and deliver the work according to the agreed schedule expiring on **[EXPIRY_DATE]**.

---

### 2. COMPENSATION AND PAYMENT TERMS
2.1 **Project Fee:** In consideration for the satisfactory completion of the services, the Client shall pay the Freelancer a total fee of **Rs. [PROJECT_FEE]**.
2.2 **Payment Terms:** Payment shall be made according to the following schedule: [PAYMENT_TERMS].
2.3 **Revisions:** The fee includes up to [REVISIONS_ALLOWED] rounds of revisions. Any additional revisions requested by the Client shall be billed separately.

---

### 3. INDEPENDENT CONTRACTOR STATUS
3.1 The Freelancer is an independent contractor and nothing in this Agreement shall be construed to create an employer-employee, partnership, or joint venture relationship between the Parties.

---

### 4. INTELLECTUAL PROPERTY OWNERSHIP
4.1 Upon receipt of full payment from the Client, the Freelancer assigns to the Client all copyright, title, and ownership rights in the final deliverables created under this Agreement.

---

### 5. CONFIDENTIALITY AND TERMINATION
5.1 Both Parties agree to keep confidential all non-public information received during the project.
5.2 Either Party may terminate this Agreement by giving a written **Notice Period of [NOTICE_PERIOD]**. In the event of termination, the Freelancer shall be compensated for work completed up to the date of termination.

---

### 6. GOVERNING LAW
6.1 This Agreement shall be governed by the laws of **India**, subject to the exclusive jurisdiction of the courts at **[CITY], [STATE]**.

---

### IN WITNESS WHEREOF

**FOR THE CLIENT:**  
Signature: ___________________________________  
Name: **[CLIENT_NAME]**  
Date: _______________________________________  

**FOR THE FREELANCER:**  
Signature: ___________________________________  
Name: **[FREELANCER_NAME]**  
Date: _______________________________________  
""",

    "Non Disclosure Agreement (NDA)": """# NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT

**THIS NON-DISCLOSURE AGREEMENT** (hereinafter referred to as the "Agreement") is made and executed at **[CITY], [STATE]** on this **[DATE]**, by and between:

**[DISCLOSING_PARTY]**, having its address at [DISCLOSING_ADDRESS], Contact: [DISCLOSING_CONTACT] (hereinafter referred to as the **"Disclosing Party"**) of the **FIRST PART**;

**AND**

**[RECEIVING_PARTY]**, having its address at [RECEIVING_ADDRESS], Contact: [RECEIVING_CONTACT] (hereinafter referred to as the **"Receiving Party"**) of the **SECOND PART**.

---

### RECITALS

**WHEREAS:**

A. The Disclosing Party and the Receiving Party propose to engage in discussions regarding **[PURPOSE]** (the "Permitted Purpose").

B. In connection with the Permitted Purpose, the Disclosing Party may disclose to the Receiving Party certain proprietary and confidential information.

**NOW, THEREFORE, THE PARTIES AGREE AS FOLLOWS:**

---

### 1. DEFINITION OF CONFIDENTIAL INFORMATION
1.1 "Confidential Information" shall include all non-public technical, business, financial, operational, software, product data, and trade secrets disclosed by the Disclosing Party to the Receiving Party, whether orally, visually, or in writing.

---

### 2. OBLIGATIONS OF THE RECEIVING PARTY
2.1 The Receiving Party shall hold all Confidential Information in strict confidence using the same degree of care it uses for its own confidential material, but no less than reasonable care.
2.2 The Receiving Party shall use Confidential Information solely for the Permitted Purpose and shall not disclose it to any third party without prior written consent of the Disclosing Party.

---

### 3. EXCEPTIONS
3.1 Confidential Information shall not include information that: (a) is or becomes publicly known through no fault of Receiving Party; (b) was already in Receiving Party's possession prior to disclosure; or (c) is required to be disclosed by law or court order.

---

### 4. DURATION AND RETURN OF MATERIAL
4.1 This Agreement shall remain in effect for a period of **[DURATION]** from the Effective Date.
4.2 Upon request or termination of discussions, the Receiving Party shall promptly return or destroy all physical and electronic copies of Confidential Information.

---

### 5. GOVERNING LAW
5.1 Governed by the laws of **India**, subject to the exclusive jurisdiction of the courts at **[CITY], [STATE]**.

---

### IN WITNESS WHEREOF

**FOR DISCLOSING PARTY:**  
Signature: ___________________________________  
Name: **[DISCLOSING_PARTY]**  
Date: _______________________________________  

**FOR RECEIVING PARTY:**  
Signature: ___________________________________  
Name: **[RECEIVING_PARTY]**  
Date: _______________________________________  
""",

    "Service Agreement": """# MASTER PROFESSIONAL SERVICE AGREEMENT

**THIS SERVICE AGREEMENT** (hereinafter referred to as the "Agreement") is made and executed at **[CITY], [STATE]** on this **[DATE]**, by and between:

**[CLIENT_NAME]**, having its office at [CLIENT_ADDRESS], Contact: [CLIENT_CONTACT] (hereinafter referred to as the **"Client"**) of the **FIRST PART**;

**AND**

**[PROVIDER_NAME]**, having its office at [PROVIDER_ADDRESS], Contact: [PROVIDER_CONTACT] (hereinafter referred to as the **"Service Provider"**) of the **SECOND PART**.

---

### RECITALS

**WHEREAS:**
Client desires to retain Service Provider to perform professional services titled **"[SERVICE_NAME]"**, and Service Provider agrees to perform such services on the terms herein.

---

### 1. SCOPE OF SERVICES
1.1 Service Provider shall render the professional services detailed below:
* **Service Name:** [SERVICE_NAME]
* **Detailed Scope:** [SERVICE_SCOPE]
* **Deliverables:** [DELIVERABLES]

---

### 2. FEES AND PAYMENT TERMS
2.1 **Service Fee:** Client shall pay Service Provider a total fee of **Rs. [TOTAL_FEE]**.
2.2 **Schedule:** Payment shall be made as per: [PAYMENT_SCHEDULE] via [PAYMENT_METHOD].
2.3 **Taxes:** [TAXES_TERMS].

---

### 3. TERM AND TERMINATION
3.1 Valid for a term expiring on **[EXPIRY_DATE]**. Either Party may terminate upon **[NOTICE_PERIOD]** written notice.

---

### 4. LIMITATION OF LIABILITY AND GOVERNING LAW
4.1 Liability Cap: [LIABILITY_CAP].
4.2 Governed by the laws of **India**, subject to courts at **[CITY], [STATE]**.

---

### IN WITNESS WHEREOF

**FOR CLIENT:**  
Signature: ___________________________________  
Name: **[CLIENT_NAME]**  
Date: _______________________________________  

**FOR SERVICE PROVIDER:**  
Signature: ___________________________________  
Name: **[PROVIDER_NAME]**  
Date: _______________________________________  
""",

    "Sale / Purchase Agreement": """# AGREEMENT FOR SALE AND PURCHASE OF GOODS / ASSETS

**THIS SALE AND PURCHASE AGREEMENT** (hereinafter referred to as the "Agreement") is made and executed at **[CITY], [STATE]** on this **[DATE]**, by and between:

**[SELLER_NAME]**, having office at [SELLER_ADDRESS], Contact: [SELLER_CONTACT] (hereinafter referred to as the **"Seller"**) of the **FIRST PART**;

**AND**

**[BUYER_NAME]**, having office at [BUYER_ADDRESS], Contact: [BUYER_CONTACT] (hereinafter referred to as the **"Buyer"**) of the **SECOND PART**.

---

### RECITALS

**WHEREAS:** Seller agrees to sell and Buyer agrees to purchase the goods / assets described herein.

---

### 1. ASSET DESCRIPTION AND PURCHASE PRICE
1.1 **Goods Description:** [ITEM_DESCRIPTION] (Quantity: [QUANTITY], Condition: [ITEM_CONDITION], Serial/ID: [ITEM_ID]).
1.2 **Purchase Price:** Total price of **Rs. [PURCHASE_PRICE]**, with an Advance Deposit of **Rs. [ADVANCE_PAYMENT]** and balance terms: [BALANCE_PAYMENT].

---

### 2. DELIVERY AND INSPECTION
2.1 Delivery shall take place on or before **[DELIVERY_DATE]** at **[DELIVERY_LOCATION]**.
2.2 Inspection Period: Buyer shall inspect goods within [INSPECTION_PERIOD] of delivery.

---

### 3. TITLE AND RISK
3.1 Risk of loss passes to Buyer upon physical delivery. Title transfers upon full payment of purchase price.

---

### 4. GOVERNING LAW
4.1 Governed by the laws of **India**, subject to courts at **[CITY], [STATE]**.

---

### IN WITNESS WHEREOF

**FOR SELLER:**  
Signature: ___________________________________  
Name: **[SELLER_NAME]**  
Date: _______________________________________  

**FOR BUYER:**  
Signature: ___________________________________  
Name: **[BUYER_NAME]**  
Date: _______________________________________  
""",

    "Partnership Agreement": """# GENERAL PARTNERSHIP DEED

**THIS DEED OF PARTNERSHIP** is made and executed at **[CITY], [STATE]** on this **[DATE]**, by and between:

**[P1_NAME]**, residing at [P1_ADDRESS] (hereinafter referred to as **"Partner 1"**) of the **FIRST PART**;

**AND**

**[P2_NAME]**, residing at [P2_ADDRESS] (hereinafter referred to as **"Partner 2"**) of the **SECOND PART**.

---

### RECITALS

**WHEREAS:** The Partners have agreed to join together in partnership to carry on business under the firm name **"[FIRM_NAME]"**.

---

### 1. FIRM NAME AND BUSINESS PURPOSE
1.1 **Firm Name:** [FIRM_NAME], operating at [BUSINESS_ADDRESS].
1.2 **Business Purpose:** [BUSINESS_OBJECT]

---

### 2. CAPITAL CONTRIBUTION AND PROFIT SHARING
2.1 Capital Contribution: Partner 1 shall contribute **Rs. [P1_CAPITAL]**; Partner 2 shall contribute **Rs. [P2_CAPITAL]**.
2.2 Profit / Loss Sharing Ratio: Partner 1: **[P1_SHARE]%** | Partner 2: **[P2_SHARE]%**.

---

### 3. MANAGEMENT AND ACCOUNTS
3.1 Both Partners shall participate in business management. Books of accounts shall be audited annually.
3.2 Decision Making: [DECISION_MAKING].

---

### 4. DISSOLUTION AND GOVERNING LAW
4.1 Governed by the Indian Partnership Act and subject to courts at **[CITY], [STATE]**.

---

### IN WITNESS WHEREOF

**PARTNER 1:**  
Signature: ___________________________________  
Name: **[P1_NAME]**  
Date: _______________________________________  

**PARTNER 2:**  
Signature: ___________________________________  
Name: **[P2_NAME]**  
Date: _______________________________________  
""",

    "Consultancy Agreement": """# CONSULTANCY AGREEMENT

**THIS CONSULTANCY AGREEMENT** is made at **[CITY], [STATE]** on **[DATE]**, between **[CLIENT_NAME]** (Client) and **[CONSULTANT_NAME]** (Consultant).

---

### 1. CONSULTANCY SERVICES
1.1 Consultant shall provide advisory services in the field of **[EXPERTISE_AREA]**. Scope: [SCOPE_OF_CONSULTANCY]. Deliverables: [CONSULTANCY_DELIVERABLES].

---

### 2. COMPENSATION
2.1 Consultancy Fee: **Rs. [CONSULTANCY_FEE]** ([BILLING_STRUCTURE]). Expenses: [EXPENSE_TERMS].

---

### 3. NOTICE PERIOD AND GOVERNING LAW
3.1 Termination Notice: [NOTICE_PERIOD]. Governed by laws of **India** (Courts at [CITY], [STATE]).

---

### IN WITNESS WHEREOF

**FOR CLIENT:** ___________________________________ (**[CLIENT_NAME]**)  
**FOR CONSULTANT:** ___________________________________ (**[CONSULTANT_NAME]**)  
""",

    "Vendor Agreement": """# MASTER VENDOR SUPPLY AGREEMENT

**THIS VENDOR AGREEMENT** is made at **[CITY], [STATE]** on **[DATE]**, between **[PURCHASER_NAME]** (Purchaser) and **[VENDOR_NAME]** (Vendor, GST: [VENDOR_TAX_ID]).

---

### 1. SUPPLY SPECIFICATIONS AND ORDERS
1.1 Supply Description: [SUPPLY_DESCRIPTION] ([SUPPLY_FREQUENCY]). Lead time: [LEAD_TIME]. Quality: [QUALITY_STANDARDS].

---

### 2. PRICING AND PAYMENT
2.1 Estimated Annual Contract Value: **Rs. [CONTRACT_VALUE]**. Payment Terms: [PAYMENT_TERMS]. Penalty: [PENALTY_TERMS]. Rejection: [REJECTION_TERMS].

---

### 3. GOVERNING LAW
3.1 Governed by laws of **India** (Courts at [CITY], [STATE]).

---

### IN WITNESS WHEREOF

**FOR PURCHASER:** ___________________________________ (**[PURCHASER_NAME]**)  
**FOR VENDOR:** ___________________________________ (**[VENDOR_NAME]**)  
""",

    "Custom Contract": """# CUSTOM FORMAL AGREEMENT

**THIS AGREEMENT** is made at **[CITY], [STATE]** on **[DATE]**, by and between:

**[CUSTOM_PARTY_A_NAME]** ([CUSTOM_PARTY_A_COMPANY]), Address: [CUSTOM_PARTY_A_ADDRESS] (**"Party A"**);

**AND**

**[CUSTOM_PARTY_B_NAME]** ([CUSTOM_PARTY_B_COMPANY]), Address: [CUSTOM_PARTY_B_ADDRESS] (**"Party B"**).

---

### RECITALS
**WHEREAS:** The Parties agree to execute this Agreement for the purpose of: [CUSTOM_PURPOSE].

---

### 1. OBLIGATIONS AND SCOPE
1.1 Scope & Deliverables: [CUSTOM_SCOPE].
1.2 Financial Terms: Consideration of **Rs. [CUSTOM_FINANCIALS]**.
1.3 Special Covenants: [CUSTOM_CONDITIONS].

---

### 2. GOVERNING LAW
2.1 Governed by the laws of **India**, subject to courts at **[CITY], [STATE]**.

---

### IN WITNESS WHEREOF

**PARTY A:** ___________________________________ (**[CUSTOM_PARTY_A_NAME]**)  
**PARTY B:** ___________________________________ (**[CUSTOM_PARTY_B_NAME]**)  
"""
}

# Alias for Sales Agreement to match menu options seamlessly
TEMPLATES["Sales Agreement"] = TEMPLATES["Sale / Purchase Agreement"]


def _format_currency(val) -> str:
    """Helper to convert number/string into formatted currency string."""
    if val is None or val == "" or val == "N/A":
        return "[AMOUNT]"
    try:
        num = float(val)
        return f"{num:,.2f}"
    except (ValueError, TypeError):
        return str(val)


def render_contract(contract_type: str, data: Dict[str, str]) -> str:
    """Render a formal legal contract document using structured templates.
    Raises KeyError if contract_type is unknown.
    """
    if contract_type not in TEMPLATES:
        raise KeyError(f"Unsupported contract type: {contract_type}")

    template = TEMPLATES[contract_type]
    d = dict(data)

    # General / location fallbacks
    city = d.get("city", "").strip() or "[CITY]"
    state = d.get("state", "").strip() or "[STATE]"
    country = d.get("country", "").strip() or "India"
    date_val = d.get("effective_date", "").strip() or "[DATE]"
    duration = d.get("duration_type", "").strip() or "[DURATION]"
    expiry = d.get("expiry_date", "").strip() or "[EXPIRY_DATE]"
    additional = d.get("additional_requirements", "").strip()

    # Generic placeholder lookup map
    replacements = {
        "[CITY]": city,
        "[STATE]": state,
        "[COUNTRY]": country,
        "[DATE]": date_val,
        "[DURATION]": duration,
        "[EFFECTIVE_DATE]": date_val,
        "[EXPIRY_DATE]": expiry,

        # Rental fields
        "[LANDLORD_NAME]": d.get("landlord_name", "").strip() or "[LANDLORD NAME]",
        "[LANDLORD_ADDRESS]": d.get("landlord_address", "").strip() or "[LANDLORD ADDRESS]",
        "[LANDLORD_CONTACT]": d.get("landlord_contact", "").strip() or "[LANDLORD CONTACT]",
        "[TENANT_NAME]": d.get("tenant_name", "").strip() or "[TENANT NAME]",
        "[TENANT_ADDRESS]": d.get("tenant_address", "").strip() or "[TENANT ADDRESS]",
        "[TENANT_CONTACT]": d.get("tenant_contact", "").strip() or "[TENANT CONTACT]",
        "[PROPERTY_ADDRESS]": d.get("property_address", "").strip() or "[PROPERTY ADDRESS]",
        "[PROPERTY_TYPE]": d.get("property_type", "").strip() or "Residential Premises",
        "[BEDROOMS]": d.get("bedrooms", "").strip() or "Standard",
        "[FURNISHING]": d.get("furnishing", "").strip() or "Unfurnished",
        "[PROPERTY_USAGE]": d.get("property_usage", "").strip() or "Strictly Residential",
        "[PARKING]": d.get("parking", "").strip() or "As designated",
        "[RENT_AMOUNT]": _format_currency(d.get("rent_amount")),
        "[RENT_IN_WORDS]": "Rupees As Specified",
        "[RENT_DUE_DATE]": d.get("rent_due_date", "").strip() or "5th",
        "[SECURITY_DEPOSIT]": _format_currency(d.get("security_deposit")),
        "[DEPOSIT_IN_WORDS]": "Rupees As Specified",
        "[NOTICE_PERIOD]": d.get("notice_period", "").strip() or "[NOTICE PERIOD]",

        # Employment fields
        "[EMPLOYER_NAME]": d.get("employer_name", "").strip() or "[EMPLOYER NAME]",
        "[EMPLOYER_ADDRESS]": d.get("employer_address", "").strip() or "[EMPLOYER ADDRESS]",
        "[EMPLOYER_CONTACT]": d.get("employer_contact", "").strip() or "[EMPLOYER CONTACT]",
        "[EMPLOYEE_NAME]": d.get("employee_name", "").strip() or "[EMPLOYEE NAME]",
        "[EMPLOYEE_ADDRESS]": d.get("employee_address", "").strip() or "[EMPLOYEE ADDRESS]",
        "[EMPLOYEE_CONTACT]": d.get("employee_contact", "").strip() or "[EMPLOYEE CONTACT]",
        "[JOB_TITLE]": d.get("job_title", "").strip() or "[JOB TITLE]",
        "[DEPARTMENT]": d.get("department", "").strip() or "General Operations",
        "[REPORTING_MANAGER]": d.get("reporting_manager", "").strip() or "Designated Manager",
        "[WORK_LOCATION]": d.get("work_location", "").strip() or city,
        "[WORK_MODE]": d.get("work_mode", "").strip() or "On-Site",
        "[BASE_SALARY]": _format_currency(d.get("base_salary")),
        "[SALARY_PERIOD]": d.get("salary_period", "").strip() or "Per Annum",
        "[PROBATION_PERIOD]": d.get("probation_period", "").strip() or "6 Months",

        # Freelance fields
        "[CLIENT_NAME]": d.get("client_name", "").strip() or "[CLIENT NAME]",
        "[CLIENT_ADDRESS]": d.get("client_address", "").strip() or "[CLIENT ADDRESS]",
        "[CLIENT_CONTACT]": d.get("client_contact", "").strip() or "[CLIENT CONTACT]",
        "[FREELANCER_NAME]": d.get("freelancer_name", "").strip() or "[FREELANCER NAME]",
        "[FREELANCER_ADDRESS]": d.get("freelancer_address", "").strip() or "[FREELANCER ADDRESS]",
        "[FREELANCER_CONTACT]": d.get("freelancer_contact", "").strip() or "[FREELANCER CONTACT]",
        "[PROJECT_NAME]": d.get("project_name", "").strip() or "[PROJECT NAME]",
        "[SCOPE_OF_WORK]": d.get("scope_of_work", "").strip() or "[SCOPE OF WORK]",
        "[PROJECT_FEE]": _format_currency(d.get("project_fee")),
        "[PAYMENT_TERMS]": d.get("payment_terms", "").strip() or "Milestone payments",
        "[REVISIONS_ALLOWED]": d.get("revisions_allowed", "").strip() or "2",

        # NDA fields
        "[DISCLOSING_PARTY]": d.get("disclosing_party", "").strip() or "[DISCLOSING PARTY]",
        "[DISCLOSING_ADDRESS]": d.get("disclosing_address", "").strip() or "[DISCLOSING ADDRESS]",
        "[DISCLOSING_CONTACT]": d.get("disclosing_contact", "").strip() or "[DISCLOSING CONTACT]",
        "[RECEIVING_PARTY]": d.get("receiving_party", "").strip() or "[RECEIVING PARTY]",
        "[RECEIVING_ADDRESS]": d.get("receiving_address", "").strip() or "[RECEIVING ADDRESS]",
        "[RECEIVING_CONTACT]": d.get("receiving_contact", "").strip() or "[RECEIVING CONTACT]",
        "[PURPOSE]": d.get("purpose", "").strip() or "[PURPOSE OF DISCLOSURE]",

        # Service fields
        "[PROVIDER_NAME]": d.get("provider_name", "").strip() or "[SERVICE PROVIDER NAME]",
        "[PROVIDER_ADDRESS]": d.get("provider_address", "").strip() or "[SERVICE PROVIDER ADDRESS]",
        "[PROVIDER_CONTACT]": d.get("provider_contact", "").strip() or "[SERVICE PROVIDER CONTACT]",
        "[SERVICE_NAME]": d.get("service_name", "").strip() or "[SERVICE NAME]",
        "[SERVICE_SCOPE]": d.get("service_scope", "").strip() or "[SERVICE SCOPE]",
        "[DELIVERABLES]": d.get("deliverables", "").strip() or "[DELIVERABLES]",
        "[TOTAL_FEE]": _format_currency(d.get("total_fee")),
        "[PAYMENT_SCHEDULE]": d.get("payment_schedule", "").strip() or "Monthly invoicing",
        "[PAYMENT_METHOD]": d.get("payment_method", "").strip() or "Bank Transfer",
        "[TAXES_TERMS]": d.get("taxes_terms", "").strip() or "Exclusive of GST",
        "[LIABILITY_CAP]": d.get("liability_cap", "").strip() or "Total fee paid",

        # Sale/Purchase fields
        "[BUYER_NAME]": d.get("buyer_name", "").strip() or "[BUYER NAME]",
        "[BUYER_ADDRESS]": d.get("buyer_address", "").strip() or "[BUYER ADDRESS]",
        "[BUYER_CONTACT]": d.get("buyer_contact", "").strip() or "[BUYER CONTACT]",
        "[SELLER_NAME]": d.get("seller_name", "").strip() or "[SELLER NAME]",
        "[SELLER_ADDRESS]": d.get("seller_address", "").strip() or "[SELLER ADDRESS]",
        "[SELLER_CONTACT]": d.get("seller_contact", "").strip() or "[SELLER CONTACT]",
        "[ITEM_DESCRIPTION]": d.get("item_description", "").strip() or "[ITEM DESCRIPTION]",
        "[QUANTITY]": d.get("quantity", "").strip() or "1 Unit",
        "[ITEM_CONDITION]": d.get("item_condition", "").strip() or "As agreed",
        "[ITEM_ID]": d.get("item_id", "").strip() or "[SERIAL / ID]",
        "[PURCHASE_PRICE]": _format_currency(d.get("purchase_price")),
        "[ADVANCE_PAYMENT]": _format_currency(d.get("advance_payment")),
        "[BALANCE_PAYMENT]": d.get("balance_payment", "").strip() or "Prior to delivery",
        "[DELIVERY_DATE]": d.get("delivery_date", "").strip() or "[DELIVERY DATE]",
        "[DELIVERY_LOCATION]": d.get("delivery_location", "").strip() or "[DELIVERY LOCATION]",
        "[INSPECTION_PERIOD]": d.get("inspection_period", "").strip() or "7 Days",

        # Partnership fields
        "[P1_NAME]": d.get("p1_name", "").strip() or "[PARTNER 1 NAME]",
        "[P1_ADDRESS]": d.get("p1_address", "").strip() or "[PARTNER 1 ADDRESS]",
        "[P1_CAPITAL]": _format_currency(d.get("p1_capital")),
        "[P1_SHARE]": str(d.get("p1_share", "50")),
        "[P2_NAME]": d.get("p2_name", "").strip() or "[PARTNER 2 NAME]",
        "[P2_ADDRESS]": d.get("p2_address", "").strip() or "[PARTNER 2 ADDRESS]",
        "[P2_CAPITAL]": _format_currency(d.get("p2_capital")),
        "[P2_SHARE]": str(d.get("p2_share", "50")),
        "[FIRM_NAME]": d.get("firm_name", "").strip() or "[FIRM NAME]",
        "[BUSINESS_ADDRESS]": d.get("business_address", "").strip() or city,
        "[BUSINESS_OBJECT]": d.get("business_object", "").strip() or "[BUSINESS PURPOSE]",
        "[DECISION_MAKING]": d.get("decision_making", "").strip() or "Mutual agreement",

        # Consultancy fields
        "[CONSULTANT_NAME]": d.get("consultant_name", "").strip() or "[CONSULTANT NAME]",
        "[CONSULTANT_ADDRESS]": d.get("consultant_address", "").strip() or "[CONSULTANT ADDRESS]",
        "[CONSULTANT_CONTACT]": d.get("consultant_contact", "").strip() or "[CONSULTANT CONTACT]",
        "[EXPERTISE_AREA]": d.get("expertise_area", "").strip() or "[FIELD OF EXPERTISE]",
        "[SCOPE_OF_CONSULTANCY]": d.get("scope_of_consultancy", "").strip() or "[SCOPE OF CONSULTANCY]",
        "[CONSULTANCY_DELIVERABLES]": d.get("consultancy_deliverables", "").strip() or "[DELIVERABLES]",
        "[CONSULTANCY_FEE]": _format_currency(d.get("consultancy_fee")),
        "[BILLING_STRUCTURE]": d.get("billing_structure", "").strip() or "Monthly retainer",
        "[EXPENSE_TERMS]": d.get("expense_terms", "").strip() or "Reimbursed at actuals",

        # Vendor fields
        "[PURCHASER_NAME]": d.get("purchaser_name", "").strip() or "[PURCHASER NAME]",
        "[PURCHASER_ADDRESS]": d.get("purchaser_address", "").strip() or "[PURCHASER ADDRESS]",
        "[PURCHASER_CONTACT]": d.get("purchaser_contact", "").strip() or "[PURCHASER CONTACT]",
        "[VENDOR_NAME]": d.get("vendor_name", "").strip() or "[VENDOR NAME]",
        "[VENDOR_ADDRESS]": d.get("vendor_address", "").strip() or "[VENDOR ADDRESS]",
        "[VENDOR_TAX_ID]": d.get("vendor_tax_id", "").strip() or "[GST/TAX ID]",
        "[SUPPLY_DESCRIPTION]": d.get("supply_description", "").strip() or "[SUPPLY DESCRIPTION]",
        "[SUPPLY_FREQUENCY]": d.get("supply_frequency", "").strip() or "As per purchase orders",
        "[QUALITY_STANDARDS]": d.get("quality_standards", "").strip() or "ISO Standard",
        "[LEAD_TIME]": d.get("lead_time", "").strip() or "7 Days",
        "[CONTRACT_VALUE]": _format_currency(d.get("contract_value")),
        "[PENALTY_TERMS]": d.get("penalty_terms", "").strip() or "0.5% per week late fee",
        "[REJECTION_TERMS]": d.get("rejection_terms", "").strip() or "Replaced within 10 days",

        # Custom fields
        "[CUSTOM_PARTY_A_NAME]": d.get("custom_party_a_name", "").strip() or "[PARTY A NAME]",
        "[CUSTOM_PARTY_A_COMPANY]": d.get("custom_party_a_company", "").strip() or "[PARTY A ENTITY]",
        "[CUSTOM_PARTY_A_ADDRESS]": d.get("custom_party_a_address", "").strip() or "[PARTY A ADDRESS]",
        "[CUSTOM_PARTY_B_NAME]": d.get("custom_party_b_name", "").strip() or "[PARTY B NAME]",
        "[CUSTOM_PARTY_B_COMPANY]": d.get("custom_party_b_company", "").strip() or "[PARTY B ENTITY]",
        "[CUSTOM_PARTY_B_ADDRESS]": d.get("custom_party_b_address", "").strip() or "[PARTY B ADDRESS]",
        "[CUSTOM_PURPOSE]": d.get("custom_purpose", "").strip() or "[PURPOSE OF AGREEMENT]",
        "[CUSTOM_SCOPE]": d.get("custom_scope", "").strip() or "[SCOPE AND OBLIGATIONS]",
        "[CUSTOM_FINANCIALS]": _format_currency(d.get("custom_financials")),
        "[CUSTOM_CONDITIONS]": d.get("custom_conditions", "").strip() or "Standard legal terms apply",
    }

    rendered = template
    for placeholder, val in replacements.items():
        rendered = rendered.replace(placeholder, val)

    # Append additional requirements section cleanly if user supplied specific covenants
    if additional:
        additional_section = f"\n\n---\n\n### SPECIAL COVENANTS AND ADDITIONAL REQUIREMENTS\n" \
                             f"The Parties further agree to the following specific covenants:\n" \
                             f"* {additional}\n"
        # Insert before IN WITNESS WHEREOF if present
        if "### IN WITNESS WHEREOF" in rendered:
            rendered = rendered.replace("### IN WITNESS WHEREOF", additional_section + "\n### IN WITNESS WHEREOF")
        else:
            rendered += additional_section

    return rendered
