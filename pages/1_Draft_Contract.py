import streamlit as st
from datetime import datetime, date

from services.template_engine import render_contract
from services.pdf_generator import create_pdf
from services.database_service import init_db, save_contract, save_history_record
from services.prompt_builder import build_contract_prompt
from utils.ui import load_css, page_header, stepper_progress

init_db()

st.set_page_config(
    page_title="Draft Contract · AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

page_header(
    "📝 Enterprise Contract Drafting Workspace",
    "Build legally rigorous, customized agreements dynamically tailored to your specific contract type."
)

stepper_progress(1)

# Load Default Settings from Session State
default_country = st.session_state.get("settings_country", "India")
default_state = st.session_state.get("settings_state", "Maharashtra")
default_curr = st.session_state.get("settings_currency", "INR (₹)")
default_lang = st.session_state.get("settings_language", "Hindi")

# ===========================
# STEP 1: BASIC INFORMATION & CONTRACT TYPE
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ 01</span><h2>Basic Information & Contract Type</h2></div>
""", unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        contract_type = st.selectbox(
            "Contract Type",
            [
                "Rental Agreement",
                "Employment Agreement",
                "Freelance Agreement",
                "Non Disclosure Agreement (NDA)",
                "Service Agreement",
                "Sale / Purchase Agreement",
                "Partnership Agreement",
                "Consultancy Agreement",
                "Vendor Agreement",
                "Custom Contract"
            ],
            key="selected_contract_type"
        )

        # Auto-update Contract Title whenever Contract Type changes
        if "prev_contract_type" not in st.session_state or st.session_state["prev_contract_type"] != contract_type:
            st.session_state["contract_title_input"] = contract_type
            st.session_state["prev_contract_type"] = contract_type


        contract_title = st.text_input(
            "Contract Title",
            key="contract_title_input"
        )

        effective_date = st.date_input(
            "Effective Date",
            value=date.today(),
            key="effective_date_input"
        )

    with col2:
        duration_type = st.selectbox(
            "Contract Duration / Term",
            [
                "Fixed Term",
                "No Fixed Expiry / Perpetual",
                "Project Completion",
                "Until Terminated by Notice"
            ],
            key="duration_type_input"
        )

        expiry_date = None
        if duration_type == "Fixed Term":
            expiry_date = st.date_input(
                "Expiry Date",
                value=date.today().replace(year=date.today().year + 1),
                key="expiry_date_input"
            )

        country = st.text_input(
            "Country",
            value=default_country,
            key="country_input"
        )

        state = st.text_input(
            "State / Jurisdiction",
            value=default_state,
            key="state_input"
        )

        city = st.text_input(
            "City",
            value=st.session_state.get("settings_city", "Nagpur"),
            key="city_input"
        )

form_data = {
    "contract_type": contract_type,
    "contract_title": contract_title,
    "effective_date": str(effective_date),
    "duration_type": duration_type,
    "expiry_date": str(expiry_date) if expiry_date else "N/A",
    "country": country,
    "state": state,
    "city": city,
    "currency": default_curr,
    "language": default_lang
}

# ===========================
# DYNAMIC SECTIONS BY CONTRACT TYPE
# ===========================

if contract_type == "Rental Agreement":
    # ----------------------------------------------------
    # 1. RENTAL AGREEMENT DYNAMIC FORM
    # ----------------------------------------------------
    st.markdown('<div class="section-head"><span class="tag">§ 02</span><h2>Landlord Details (Lessor)</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            landlord_name = st.text_input("Landlord Full Name *", placeholder="e.g. Ramesh Kumar", key="landlord_name")
            landlord_contact = st.text_input("Landlord Phone / Email", placeholder="+91 98200 11111 | ramesh@gmail.com", key="landlord_contact")
        with c2:
            landlord_address = st.text_area("Landlord Address", placeholder="Flat 101, Sea Crest, Bandra, Mumbai", height=80, key="landlord_address")

    st.markdown('<div class="section-head"><span class="tag">§ 03</span><h2>Tenant Details (Lessee)</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            tenant_name = st.text_input("Tenant Full Name *", placeholder="e.g. Suresh Patel", key="tenant_name")
            tenant_contact = st.text_input("Tenant Phone / Email", placeholder="+91 98111 22222 | suresh@gmail.com", key="tenant_contact")
        with c2:
            tenant_address = st.text_area("Tenant Permanent Address", placeholder="12 MG Road, Pune, Maharashtra", height=80, key="tenant_address")

    st.markdown('<div class="section-head"><span class="tag">§ 04</span><h2>Property Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            property_address = st.text_area("Premises Address *", placeholder="Flat 402, Sunshine Apartments, Hiranandani, Powai, Mumbai 400076", height=90, key="prop_addr")
            property_type = st.selectbox("Property Type", ["Residential Apartment", "Commercial Shop / Office", "Independent House / Villa", "Industrial Premises"], key="prop_type")
        with c2:
            bedrooms = st.selectbox("Bedrooms / Layout", ["1 BHK", "2 BHK", "3 BHK", "4+ BHK / Commercial Studio"], key="bedrooms")
            furnishing = st.selectbox("Furnishing Status", ["Unfurnished", "Semi-Furnished", "Fully Furnished"], key="furnishing")
            parking = st.text_input("Parking Allocation", value="1 Covered Car Parking Slot", key="parking")
            property_usage = st.selectbox("Permitted Usage", ["Strictly Residential", "Commercial / Office Use", "Mixed Use"], key="prop_usage")

    st.markdown('<div class="section-head"><span class="tag">§ 05</span><h2>Financial & Rent Terms</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            rent_amount = st.number_input("Monthly Rent Amount *", min_value=0.0, value=25000.0, step=1000.0, key="rent_amt")
            security_deposit = st.number_input("Security Deposit (Refundable) *", min_value=0.0, value=75000.0, step=5000.0, key="sec_deposit")
            rent_due_date = st.selectbox("Rent Due Date", ["1st", "5th", "10th", "15th"], key="rent_due")
        with c2:
            maintenance_charges = st.text_input("Maintenance Charges", value="Included in Monthly Rent", key="maint_charges")
            utility_responsibility = st.text_input("Utilities Responsibility", value="Tenant pays electricity & gas; Landlord pays property tax", key="utilities")
            late_payment_terms = st.text_input("Late Payment Terms", value="5% late fee if rent delayed beyond 7 days", key="late_terms")

    st.markdown('<div class="section-head"><span class="tag">§ 06</span><h2>Rental Conditions & Restrictions</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            notice_period = st.selectbox("Vacating Notice Period", ["1 Month", "2 Months", "3 Months"], key="rent_notice")
            renewal_terms = st.text_input("Renewal & Rent Escalation", value="10% rent increase upon annual renewal", key="renewal")
            maintenance_resp = st.text_input("Maintenance Responsibility", value="Tenant handles minor repairs (< ₹1,000); Landlord handles structural", key="maint_resp")
        with c2:
            subletting_allowed = st.radio("Subletting Allowed?", ["No", "Yes"], key="subletting")
            pets_allowed = st.radio("Pets Allowed?", ["No", "Yes"], key="pets")
            restrictions = st.text_area("Restrictions & Covenants", value="No unauthorized alterations, no illegal activities, quiet hours after 10 PM.", height=80, key="restrictions")

    form_data.update({
        "landlord_name": landlord_name,
        "landlord_contact": landlord_contact,
        "landlord_address": landlord_address,
        "tenant_name": tenant_name,
        "tenant_contact": tenant_contact,
        "tenant_address": tenant_address,
        "property_address": property_address,
        "property_type": property_type,
        "bedrooms": bedrooms,
        "furnishing": furnishing,
        "parking": parking,
        "property_usage": property_usage,
        "rent_amount": rent_amount,
        "security_deposit": security_deposit,
        "rent_due_date": rent_due_date,
        "maintenance_charges": maintenance_charges,
        "utility_responsibility": utility_responsibility,
        "late_payment_terms": late_payment_terms,
        "notice_period": notice_period,
        "renewal_terms": renewal_terms,
        "maintenance_resp": maintenance_resp,
        "subletting_allowed": subletting_allowed,
        "pets_allowed": pets_allowed,
        "restrictions": restrictions
    })

elif contract_type == "Employment Agreement":
    # ----------------------------------------------------
    # 2. EMPLOYMENT AGREEMENT DYNAMIC FORM
    # ----------------------------------------------------
    st.markdown('<div class="section-head"><span class="tag">§ 02</span><h2>Employer Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            employer_name = st.text_input("Company / Employer Name *", placeholder="e.g. Acme Innovations India Pvt Ltd", key="emp_name")
            authorized_rep = st.text_input("Authorized Representative", placeholder="e.g. Vikram Malhotra, HR Director", key="auth_rep")
        with c2:
            employer_address = st.text_area("Company Address", placeholder="Tech Park, Tower B, Electronic City, Bengaluru 560100", height=80, key="emp_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 03</span><h2>Employee Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            employee_name = st.text_input("Employee Full Name *", placeholder="e.g. Amit Verma", key="employee_name")
            employee_contact = st.text_input("Employee Email / Phone", placeholder="amit@gmail.com | +91 99000 88888", key="employee_contact")
        with c2:
            employee_address = st.text_area("Employee Residential Address", placeholder="45 Green Park, New Delhi 110016", height=80, key="employee_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 04</span><h2>Position & Employment Terms</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            job_title = st.text_input("Job Title *", placeholder="e.g. Senior Software Engineer", key="job_title")
            department = st.text_input("Department", value="Engineering & Technology", key="department")
            employment_type = st.selectbox("Employment Type", ["Full-Time Permanent", "Part-Time", "Fixed-Term Contract", "Internship"], key="emp_type")
        with c2:
            joining_date = st.date_input("Joining Date", value=date.today(), key="joining_date")
            work_location = st.text_input("Work Location", value="Bengaluru Office / Hybrid", key="work_loc")
            working_hours = st.text_input("Working Hours", value="40 Hours/Week (Mon-Fri 9:00 AM - 6:00 PM)", key="hours")
            probation_period = st.selectbox("Probation Period", ["3 Months", "6 Months", "No Probation"], key="probation")

    st.markdown('<div class="section-head"><span class="tag">§ 05</span><h2>Compensation & Benefits</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            salary_amount = st.number_input("Base Compensation Amount *", min_value=0.0, value=1200000.0, step=50000.0, key="salary")
            salary_frequency = st.selectbox("Payment Frequency", ["Month", "Year"], key="sal_freq")
        with c2:
            bonus_details = st.text_input("Bonus & Performance Incentives", value="Annual discretionary performance bonus up to 15%", key="bonus")
            benefits_details = st.text_area("Allowances & Benefits", value="Health insurance coverage (₹5 Lakhs), Provident Fund, Paid Leaves", height=80, key="benefits")

    st.markdown('<div class="section-head"><span class="tag">§ 06</span><h2>Conditions & Termination</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            responsibilities = st.text_area("Key Responsibilities", value="Architect, build, and maintain enterprise software solutions.", height=80, key="emp_resp")
            leave_policy = st.text_input("Leave Policy", value="24 Days Paid Annual Leave + Public Holidays", key="leave")
            notice_period = st.selectbox("Termination Notice Period", ["30 Days", "60 Days", "90 Days"], key="emp_notice")
        with c2:
            confidentiality_terms = st.text_input("Confidentiality & Trade Secrets", value="Strict Non-Disclosure of Company IP & Code", key="emp_conf")
            ip_terms = st.text_input("IP Ownership", value="All inventions & code created belong exclusively to Employer", key="emp_ip")
            conduct_rules = st.text_input("Non-Solicitation", value="12 Months Non-Solicitation of clients and staff post-employment", key="emp_rules")

    form_data.update({
        "employer_name": employer_name,
        "authorized_rep": authorized_rep,
        "employer_address": employer_address,
        "employee_name": employee_name,
        "employee_contact": employee_contact,
        "employee_address": employee_address,
        "job_title": job_title,
        "department": department,
        "employment_type": employment_type,
        "joining_date": str(joining_date),
        "work_location": work_location,
        "working_hours": working_hours,
        "probation_period": probation_period,
        "salary_amount": salary_amount,
        "salary_frequency": salary_frequency,
        "bonus_details": bonus_details,
        "benefits_details": benefits_details,
        "responsibilities": responsibilities,
        "leave_policy": leave_policy,
        "notice_period": notice_period,
        "confidentiality_terms": confidentiality_terms,
        "ip_terms": ip_terms,
        "conduct_rules": conduct_rules
    })

elif contract_type == "Freelance Agreement":
    # ----------------------------------------------------
    # 3. FREELANCE AGREEMENT DYNAMIC FORM
    # ----------------------------------------------------
    st.markdown('<div class="section-head"><span class="tag">§ 02</span><h2>Client Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            client_name = st.text_input("Client Organization / Name *", placeholder="e.g. Apex Global Media Inc.", key="fl_client")
            client_contact = st.text_input("Client Contact Person & Email", placeholder="john@apexglobal.com | +1 555 0192", key="fl_client_contact")
        with c2:
            client_address = st.text_area("Client Address", placeholder="500 Wall Street, New York, NY 10005", height=80, key="fl_client_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 03</span><h2>Freelancer Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            freelancer_name = st.text_input("Freelancer Full Name *", placeholder="e.g. Neha Kulkarni", key="fl_name")
            freelancer_contact = st.text_input("Freelancer Email / Phone", placeholder="neha@designstudio.in | +91 97000 55555", key="fl_contact")
        with c2:
            freelancer_address = st.text_area("Freelancer Address", placeholder="78 FC Road, Shivajinagar, Pune, Maharashtra", height=80, key="fl_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 04</span><h2>Project Scope & Deliverables</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            project_name = st.text_input("Project Name *", placeholder="e.g. Mobile App UI/UX Redesign", key="fl_proj_name")
            service_description = st.text_area("Services Description", placeholder="Complete Figma prototyping, UI kit creation, and design assets.", height=90, key="fl_service_desc")
        with c2:
            deliverables = st.text_area("Key Deliverables *", placeholder="Figma source files, Design System documentation, asset exports.", height=90, key="fl_deliv")
            c_a, c_b = st.columns(2)
            with c_a:
                start_date = st.date_input("Start Date", value=date.today(), key="fl_start")
            with c_b:
                end_date = st.date_input("Target Completion", value=date.today(), key="fl_end")

    st.markdown('<div class="section-head"><span class="tag">§ 05</span><h2>Payment & Revisions</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            project_fee = st.number_input("Total Project Fee *", min_value=0.0, value=150000.0, step=5000.0, key="fl_fee")
            advance_payment = st.number_input("Advance Deposit", min_value=0.0, value=30000.0, step=5000.0, key="fl_adv")
            payment_schedule = st.selectbox("Payment Schedule", ["30% Upfront, 70% upon Completion", "50% Upfront, 50% upon Delivery", "Milestone Based"], key="fl_sched")
        with c2:
            payment_method = st.selectbox("Payment Method", ["Bank Transfer (NEFT/UPI)", "PayPal / Stripe", "Wire Transfer"], key="fl_pay_method")
            revision_policy = st.text_input("Revision Rounds Included", value="2 Rounds of minor revisions included", key="fl_revisions")
            late_payment_terms = st.text_input("Late Payment Fee", value="1.5% monthly penalty on overdue invoices", key="fl_late")

    st.markdown('<div class="section-head"><span class="tag">§ 06</span><h2>Legal Terms & IP</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            ip_ownership = st.selectbox("IP Ownership Transfer", ["Full Transfer to Client upon Final Payment", "Client gets Exclusive License"], key="fl_ip")
            work_mode = st.selectbox("Work Mode", ["Remote / Independent Hours", "On-Site at Client Office", "Hybrid"], key="fl_mode")
        with c2:
            confidentiality_terms = st.text_input("Confidentiality", value="Strict Non-Disclosure of Client Data & Trade Secrets", key="fl_conf")
            termination_terms = st.text_input("Termination Notice", value="Either party may terminate with 7 days written notice", key="fl_term")

    form_data.update({
        "client_name": client_name,
        "client_contact": client_contact,
        "client_address": client_address,
        "freelancer_name": freelancer_name,
        "freelancer_contact": freelancer_contact,
        "freelancer_address": freelancer_address,
        "project_name": project_name,
        "service_description": service_description,
        "deliverables": deliverables,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "project_fee": project_fee,
        "advance_payment": advance_payment,
        "payment_schedule": payment_schedule,
        "payment_method": payment_method,
        "revision_policy": revision_policy,
        "late_payment_terms": late_payment_terms,
        "ip_ownership": ip_ownership,
        "work_mode": work_mode,
        "confidentiality_terms": confidentiality_terms,
        "termination_terms": termination_terms
    })

elif contract_type == "Non Disclosure Agreement (NDA)":
    # ----------------------------------------------------
    # 4. NDA DYNAMIC FORM
    # ----------------------------------------------------
    st.markdown('<div class="section-head"><span class="tag">§ 02</span><h2>Disclosing Party</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            disclosing_party = st.text_input("Disclosing Party Name / Entity *", placeholder="e.g. Zenith Software Solutions Pvt Ltd", key="nda_disc_name")
            disclosing_contact = st.text_input("Contact Person / Email", placeholder="legal@zenith.com | +91 98333 44444", key="nda_disc_contact")
        with c2:
            disclosing_address = st.text_area("Disclosing Party Address", placeholder="Cyber City, Phase 3, Gurugram, Haryana 122002", height=80, key="nda_disc_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 03</span><h2>Receiving Party</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            receiving_party = st.text_input("Receiving Party Name / Entity *", placeholder="e.g. Future Ventures Fund", key="nda_rec_name")
            receiving_contact = st.text_input("Contact Person / Email", placeholder="partner@futureventures.vc", key="nda_rec_contact")
        with c2:
            receiving_address = st.text_area("Receiving Party Address", placeholder="10 Financial Center, Nariman Point, Mumbai 400021", height=80, key="nda_rec_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 04</span><h2>Confidential Information & Scope</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            nda_type = st.selectbox("NDA Structure", ["Unilateral (One-Way Disclosure)", "Mutual (Two-Way Bilateral)"], key="nda_structure")
            purpose = st.text_area("Purpose of Disclosure *", value="Evaluating a potential strategic investment, merger, or technology partnership.", height=90, key="nda_purpose")
        with c2:
            confidential_types = st.text_area("Categories of Confidential Data", value="Source code, AI models, financial statements, customer lists, algorithms, trade secrets.", height=90, key="nda_cats")

    st.markdown('<div class="section-head"><span class="tag">§ 05</span><h2>Duration & Remedies</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            survival_period = st.selectbox("Confidentiality Survival Period", ["2 Years Post Termination", "3 Years Post Termination", "5 Years Post Termination", "Perpetual (Trade Secrets)"], key="nda_survival")
            return_data = st.text_input("Data Return / Destruction", value="Certified destruction within 14 days of written request", key="nda_return")
        with c2:
            exceptions = st.text_input("Standard Exclusions", value="Publicly known info, prior knowledge, independent development", key="nda_excep")
            remedies = st.text_input("Legal Remedies", value="Right to immediate injunctive relief & monetary damages", key="nda_remedies")

    form_data.update({
        "disclosing_party": disclosing_party,
        "disclosing_contact": disclosing_contact,
        "disclosing_address": disclosing_address,
        "receiving_party": receiving_party,
        "receiving_contact": receiving_contact,
        "receiving_address": receiving_address,
        "nda_type": nda_type,
        "purpose": purpose,
        "confidential_types": confidential_types,
        "survival_period": survival_period,
        "return_data": return_data,
        "exceptions": exceptions,
        "remedies": remedies
    })

elif contract_type == "Service Agreement":
    # ----------------------------------------------------
    # 5. SERVICE AGREEMENT DYNAMIC FORM
    # ----------------------------------------------------
    st.markdown('<div class="section-head"><span class="tag">§ 02</span><h2>Client Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            client_name = st.text_input("Client Organization / Name *", placeholder="e.g. Horizon Retail Ltd", key="sa_client")
            client_contact = st.text_input("Client Contact", placeholder="contact@horizonretail.in", key="sa_client_contact")
        with c2:
            client_address = st.text_area("Client Address", placeholder="Plot 18, MIDC, Thane, Maharashtra 400604", height=80, key="sa_client_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 03</span><h2>Service Provider Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            provider_name = st.text_input("Service Provider Organization *", placeholder="e.g. CloudMatrix IT Solutions", key="sa_prov")
            provider_contact = st.text_input("Provider Contact", placeholder="support@cloudmatrix.com", key="sa_prov_contact")
        with c2:
            provider_address = st.text_area("Provider Address", placeholder="Viman Nagar, Pune, Maharashtra 411014", height=80, key="sa_prov_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 04</span><h2>Service Scope & Terms</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            service_name = st.text_input("Service Title *", placeholder="e.g. Managed Cloud Infrastructure & Cybersecurity Services", key="sa_title")
            scope_of_work = st.text_area("Scope of Work *", placeholder="24/7 server monitoring, AWS infrastructure maintenance, data backups.", height=90, key="sa_scope")
        with c2:
            deliverables = st.text_area("Deliverables & SLA *", placeholder="99.9% Uptime Guarantee, 4-hour incident response time.", height=90, key="sa_sla")
            c_a, c_b = st.columns(2)
            with c_a:
                start_date = st.date_input("Service Start", value=date.today(), key="sa_start")
            with c_b:
                end_date = st.date_input("Service End", value=date.today(), key="sa_end")

    st.markdown('<div class="section-head"><span class="tag">§ 05</span><h2>Commercials & Liability</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            total_fee = st.number_input("Total Service Fee *", min_value=0.0, value=500000.0, step=25000.0, key="sa_fee")
            payment_schedule = st.selectbox("Payment Schedule", ["Monthly Retainer", "Quarterly", "Milestone-based", "Annual"], key="sa_sched")
            payment_method = st.selectbox("Payment Method", ["Bank Transfer (NEFT/RTGS)", "Cheque", "Online Portal"], key="sa_method")
        with c2:
            taxes_terms = st.text_input("Taxes", value="Exclusive of 18% GST; Client responsible for taxes", key="sa_taxes")
            liability_cap = st.text_input("Limitation of Liability Cap", value="Capped at total fees paid in preceding 12 months", key="sa_liab")
            termination_terms = st.text_input("Termination Notice", value="30 days written notice for breach or convenience", key="sa_term")

    form_data.update({
        "client_name": client_name,
        "client_contact": client_contact,
        "client_address": client_address,
        "provider_name": provider_name,
        "provider_contact": provider_contact,
        "provider_address": provider_address,
        "service_name": service_name,
        "scope_of_work": scope_of_work,
        "deliverables": deliverables,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "total_fee": total_fee,
        "payment_schedule": payment_schedule,
        "payment_method": payment_method,
        "taxes_terms": taxes_terms,
        "liability_cap": liability_cap,
        "termination_terms": termination_terms
    })

elif contract_type in ["Sale / Purchase Agreement", "Sales Agreement"]:
    # ----------------------------------------------------
    # 6. SALE / PURCHASE AGREEMENT DYNAMIC FORM
    # ----------------------------------------------------
    st.markdown('<div class="section-head"><span class="tag">§ 02</span><h2>Buyer Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            buyer_name = st.text_input("Buyer Full Name / Entity *", placeholder="e.g. Apex Logistics Pvt Ltd", key="sp_buyer")
            buyer_contact = st.text_input("Buyer Contact", placeholder="purchasing@apexlogistics.in", key="sp_buyer_contact")
        with c2:
            buyer_address = st.text_area("Buyer Address", placeholder="Transport Nagar, Nagpur, Maharashtra 440008", height=80, key="sp_buyer_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 03</span><h2>Seller Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            seller_name = st.text_input("Seller Full Name / Entity *", placeholder="e.g. Bharat Motors Equipment Ltd", key="sp_seller")
            seller_contact = st.text_input("Seller Contact", placeholder="sales@bharatmotors.com", key="sp_seller_contact")
        with c2:
            seller_address = st.text_area("Seller Address", placeholder="Industrial Area Phase 1, Pune, Maharashtra 411026", height=80, key="sp_seller_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 04</span><h2>Asset / Item Description</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            item_description = st.text_area("Item / Goods Description *", placeholder="5 Heavy Commercial Hydraulic Press Machines Model X500.", height=90, key="sp_item_desc")
            quantity = st.text_input("Quantity / Units *", value="5 Units", key="sp_qty")
        with c2:
            item_condition = st.selectbox("Asset Condition", ["Brand New (Factory Sealed)", "Refurbished", "Used / As-Is"], key="sp_cond")
            item_id = st.text_input("Serial / Asset ID Numbers", placeholder="SN-88491 to SN-88495", key="sp_id")

    st.markdown('<div class="section-head"><span class="tag">§ 05</span><h2>Financials & Delivery</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            purchase_price = st.number_input("Total Purchase Price *", min_value=0.0, value=850000.0, step=10000.0, key="sp_price")
            advance_payment = st.number_input("Advance Deposit", min_value=0.0, value=200000.0, step=10000.0, key="sp_adv")
            balance_payment = st.text_input("Balance Payment Terms", value="Balance due prior to dispatch", key="sp_bal")
        with c2:
            delivery_date = st.date_input("Delivery Date", value=date.today(), key="sp_deliv_date")
            delivery_location = st.text_input("Delivery Location", value="Buyer Warehouse, Nagpur", key="sp_loc")
            inspection_period = st.selectbox("Buyer Inspection Window", ["3 Business Days", "7 Business Days", "14 Business Days"], key="sp_inspect")

    form_data.update({
        "buyer_name": buyer_name,
        "buyer_contact": buyer_contact,
        "buyer_address": buyer_address,
        "seller_name": seller_name,
        "seller_contact": seller_contact,
        "seller_address": seller_address,
        "item_description": item_description,
        "quantity": quantity,
        "item_condition": item_condition,
        "item_id": item_id,
        "purchase_price": purchase_price,
        "advance_payment": advance_payment,
        "balance_payment": balance_payment,
        "delivery_date": str(delivery_date),
        "delivery_location": delivery_location,
        "inspection_period": inspection_period
    })

elif contract_type == "Partnership Agreement":
    # ----------------------------------------------------
    # 7. PARTNERSHIP AGREEMENT DYNAMIC FORM
    # ----------------------------------------------------
    st.markdown('<div class="section-head"><span class="tag">§ 02</span><h2>Partner 1 Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            p1_name = st.text_input("Partner 1 Full Name *", placeholder="e.g. Anil Mehta", key="pa_p1_name")
            p1_capital = st.number_input("Capital Contribution (Partner 1) *", min_value=0.0, value=500000.0, step=25000.0, key="pa_p1_cap")
        with c2:
            p1_share = st.number_input("Profit / Loss Share % (Partner 1)", min_value=0.0, max_value=100.0, value=50.0, step=5.0, key="pa_p1_share")
            p1_address = st.text_area("Partner 1 Residential Address", placeholder="14 JVPD Scheme, Juhu, Mumbai 400049", height=70, key="pa_p1_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 03</span><h2>Partner 2 Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            p2_name = st.text_input("Partner 2 Full Name *", placeholder="e.g. Sunita Mehta", key="pa_p2_name")
            p2_capital = st.number_input("Capital Contribution (Partner 2) *", min_value=0.0, value=500000.0, step=25000.0, key="pa_p2_cap")
        with c2:
            p2_share = st.number_input("Profit / Loss Share % (Partner 2)", min_value=0.0, max_value=100.0, value=50.0, step=5.0, key="pa_p2_share")
            p2_address = st.text_area("Partner 2 Residential Address", placeholder="22 Lokhandwala Complex, Andheri West, Mumbai", height=70, key="pa_p2_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 04</span><h2>Partnership Firm & Business</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            firm_name = st.text_input("Partnership Firm Name *", placeholder="e.g. Mehta & Company Enterprises", key="pa_firm_name")
            business_nature = st.text_area("Nature of Business / Objective *", placeholder="Real estate advisory, property management, and commercial leasing.", height=80, key="pa_nature")
        with c2:
            firm_address = st.text_area("Principal Office Address *", placeholder="Suite 302, Nariman Point, Mumbai, Maharashtra 400021", height=80, key="pa_firm_addr")
            total_capital = p1_capital + p2_capital
            st.info(f"💰 Total Partnership Capital Pool: **₹{total_capital:,.2f}**")

    st.markdown('<div class="section-head"><span class="tag">§ 05</span><h2>Governance & Dissolution</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            bank_auth = st.selectbox("Bank Account Operating Authority", ["Joint Signatures of Both Partners Required", "Either Partner Can Operate Independently"], key="pa_bank")
            management_roles = st.text_input("Management Responsibilities", value="Equal management control; joint consent for major expenditures", key="pa_mgmt")
        with c2:
            withdrawal_terms = st.text_input("Partner Exit / Notice", value="6 Months written notice required for voluntary partner exit", key="pa_exit")
            non_compete_terms = st.text_input("Exited Partner Non-Compete", value="Exited partner prohibited from competing business for 2 years", key="pa_noncomp")

    form_data.update({
        "p1_name": p1_name,
        "p1_capital": p1_capital,
        "p1_share": p1_share,
        "p1_address": p1_address,
        "p2_name": p2_name,
        "p2_capital": p2_capital,
        "p2_share": p2_share,
        "p2_address": p2_address,
        "firm_name": firm_name,
        "business_nature": business_nature,
        "firm_address": firm_address,
        "total_capital": total_capital,
        "bank_auth": bank_auth,
        "management_roles": management_roles,
        "withdrawal_terms": withdrawal_terms,
        "non_compete_terms": non_compete_terms
    })

elif contract_type == "Consultancy Agreement":
    # ----------------------------------------------------
    # 8. CONSULTANCY AGREEMENT DYNAMIC FORM
    # ----------------------------------------------------
    st.markdown('<div class="section-head"><span class="tag">§ 02</span><h2>Client Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            client_name = st.text_input("Client Organization / Entity *", placeholder="e.g. Apex Healthtech Solutions Ltd", key="ca_client")
            client_rep = st.text_input("Client Representative", placeholder="Dr. Arvind Swamy, Managing Director", key="ca_client_rep")
        with c2:
            client_address = st.text_area("Client Address", placeholder="Healthcare City, Whitefield, Bengaluru 560066", height=80, key="ca_client_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 03</span><h2>Consultant Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            consultant_name = st.text_input("Consultant / Advisory Firm Name *", placeholder="e.g. Dr. Rajesh Iyer Advisory", key="ca_cons")
            consultant_contact = st.text_input("Consultant Email / Phone", placeholder="rajesh@iyeradvisory.in | +91 98444 33333", key="ca_cons_contact")
        with c2:
            consultant_address = st.text_area("Consultant Address", placeholder="15 Koramangala 4th Block, Bengaluru, Karnataka", height=80, key="ca_cons_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 04</span><h2>Advisory Scope & Deliverables</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            expertise_area = st.text_input("Field of Expertise *", placeholder="e.g. Healthcare Regulatory Compliance & AI Strategy", key="ca_area")
            scope_of_consultancy = st.text_area("Scope of Advisory Services *", placeholder="Strategic advice on AI medical device certification, FDA/CDSCO compliance.", height=90, key="ca_scope")
        with c2:
            consultancy_deliverables = st.text_area("Advisory Reports & Deliverables *", placeholder="Monthly compliance audit reports, regulatory filing roadmaps.", height=90, key="ca_deliv")

    st.markdown('<div class="section-head"><span class="tag">§ 05</span><h2>Retainer Commercials & Terms</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            consultancy_fee = st.number_input("Consultancy / Retainer Fee *", min_value=0.0, value=200000.0, step=10000.0, key="ca_fee")
            billing_structure = st.selectbox("Billing Structure", ["Monthly Retainer", "Hourly Rate (₹10,000/hr)", "Project Fixed Fee"], key="ca_bill")
        with c2:
            expense_terms = st.text_input("Expense Reimbursement", value="Pre-approved travel & accommodation reimbursed at actuals", key="ca_exp")
            notice_period = st.selectbox("Termination Notice Period", ["30 Days", "14 Days", "60 Days"], key="ca_notice")

    form_data.update({
        "client_name": client_name,
        "client_rep": client_rep,
        "client_address": client_address,
        "consultant_name": consultant_name,
        "consultant_contact": consultant_contact,
        "consultant_address": consultant_address,
        "expertise_area": expertise_area,
        "scope_of_consultancy": scope_of_consultancy,
        "consultancy_deliverables": consultancy_deliverables,
        "consultancy_fee": consultancy_fee,
        "billing_structure": billing_structure,
        "expense_terms": expense_terms,
        "notice_period": notice_period
    })

elif contract_type == "Vendor Agreement":
    # ----------------------------------------------------
    # 9. VENDOR AGREEMENT DYNAMIC FORM
    # ----------------------------------------------------
    st.markdown('<div class="section-head"><span class="tag">§ 02</span><h2>Purchaser Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            purchaser_name = st.text_input("Purchaser Organization *", placeholder="e.g. Titan Manufacturing Corp", key="va_purch")
            purchaser_contact = st.text_input("Authorized Buyer / Email", placeholder="procurement@titanmfg.com", key="va_purch_contact")
        with c2:
            purchaser_address = st.text_area("Purchaser Office Address", placeholder="Plot 88, Industrial Township, Hosur, Tamil Nadu 635126", height=80, key="va_purch_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 03</span><h2>Vendor / Supplier Details</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            vendor_name = st.text_input("Vendor Company Name *", placeholder="e.g. Supreme Raw Materials Ltd", key="va_vend")
            vendor_tax_id = st.text_input("GST / Tax Registration ID", placeholder="27AAACS1234F1Z5", key="va_gst")
        with c2:
            vendor_address = st.text_area("Vendor Registered Address", placeholder="45 Industrial Estate, Chakan, Pune, Maharashtra 410501", height=80, key="va_vend_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 04</span><h2>Supply Specifications & Lead Time</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            supply_description = st.text_area("Product / Supply Description *", placeholder="High-grade industrial aluminum sheets Grade 6061-T6.", height=90, key="va_desc")
            supply_frequency = st.selectbox("Supply Order Frequency", ["As per Purchase Orders", "Weekly Scheduled Delivery", "Monthly Bulk Order"], key="va_freq")
        with c2:
            quality_standards = st.text_input("Quality Standards", value="Conforming strictly to ISO 9001 quality specifications", key="va_qual")
            lead_time = st.selectbox("Delivery Lead Time", ["7 Business Days", "14 Business Days", "30 Days"], key="va_lead")

    st.markdown('<div class="section-head"><span class="tag">§ 05</span><h2>Pricing, Invoicing & Warranties</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            contract_value = st.number_input("Estimated Annual Contract Value *", min_value=0.0, value=1500000.0, step=50000.0, key="va_val")
            payment_terms = st.selectbox("Payment Credit Terms", ["Net 30 Days from Invoice & Acceptance", "Net 60 Days", "Immediate Payment"], key="va_pay_terms")
        with c2:
            penalty_terms = st.text_input("Late Delivery Penalty", value="0.5% per week penalty on late deliveries, capped at 10%", key="va_pen")
            rejection_terms = st.text_input("Defective Rejection Window", value="Defective supplies replaced at Vendor cost within 10 days", key="va_rej")

    form_data.update({
        "purchaser_name": purchaser_name,
        "purchaser_contact": purchaser_contact,
        "purchaser_address": purchaser_address,
        "vendor_name": vendor_name,
        "vendor_tax_id": vendor_tax_id,
        "vendor_address": vendor_address,
        "supply_description": supply_description,
        "supply_frequency": supply_frequency,
        "quality_standards": quality_standards,
        "lead_time": lead_time,
        "contract_value": contract_value,
        "payment_terms": payment_terms,
        "penalty_terms": penalty_terms,
        "rejection_terms": rejection_terms
    })

else:
    # ----------------------------------------------------
    # 10. CUSTOM CONTRACT DYNAMIC FORM
    # ----------------------------------------------------
    st.markdown('<div class="section-head"><span class="tag">§ 02</span><h2>First Party (Party A)</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            custom_party_a_name = st.text_input("Party A Full Name *", placeholder="e.g. Rahul Sharma", key="cust_pa_name")
            custom_party_a_company = st.text_input("Company / Organization", placeholder="e.g. Apex Enterprises", key="cust_pa_comp")
        with c2:
            custom_party_a_contact = st.text_input("Email / Phone", placeholder="rahul@apex.in | +91 98200 00000", key="cust_pa_contact")
            custom_party_a_address = st.text_area("Address", placeholder="Plot 45, BKC, Mumbai...", height=70, key="cust_pa_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 03</span><h2>Second Party (Party B)</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            custom_party_b_name = st.text_input("Party B Full Name *", placeholder="e.g. Priya Patel", key="cust_pb_name")
            custom_party_b_company = st.text_input("Company / Organization", placeholder="e.g. Patel Solutions", key="cust_pb_comp")
        with c2:
            custom_party_b_contact = st.text_input("Email / Phone", placeholder="priya@patel.com", key="cust_pb_contact")
            custom_party_b_address = st.text_area("Address", placeholder="102 MG Road, Pune...", height=70, key="cust_pb_addr")

    st.markdown('<div class="section-head"><span class="tag">§ 04</span><h2>Custom Purpose & Scope</h2></div>', unsafe_allow_html=True)
    with st.container():
        custom_purpose = st.text_area("Detailed Purpose & Objectives *", placeholder="Specify the core objective of this agreement...", height=90, key="cust_purpose")
        custom_scope = st.text_area("Primary Obligations & Deliverables *", placeholder="Outline duties, deliverables, and expectations...", height=100, key="cust_scope")

    st.markdown('<div class="section-head"><span class="tag">§ 05</span><h2>Financial & Special Covenants</h2></div>', unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            custom_financials = st.text_input("Consideration / Payment Amount", value="50000", key="cust_fin")
            custom_conditions = st.text_area("Special Covenants & Conditions", placeholder="Any custom legal conditions or non-standard provisions...", height=80, key="cust_cond")
        with c2:
            st.info("ℹ️ Custom covenants will be formatted into a tailored legal document matching your exact specifications.")

    form_data.update({
        "custom_party_a_name": custom_party_a_name,
        "custom_party_a_company": custom_party_a_company,
        "custom_party_a_contact": custom_party_a_contact,
        "custom_party_a_address": custom_party_a_address,
        "custom_party_b_name": custom_party_b_name,
        "custom_party_b_company": custom_party_b_company,
        "custom_party_b_contact": custom_party_b_contact,
        "custom_party_b_address": custom_party_b_address,
        "custom_purpose": custom_purpose,
        "custom_scope": custom_scope,
        "custom_financials": custom_financials,
        "custom_conditions": custom_conditions
    })

# ===========================
# ADDITIONAL REQUIREMENTS
# ===========================
st.markdown("""
<div class="section-head"><span class="tag">§ ADD</span><h2>Additional Contract Requirements</h2></div>
<div class="section-sub">Enter any specific conditions, permissions, or clauses that must be included in this agreement.</div>
""", unsafe_allow_html=True)

additional_requirements = st.text_area(
    "Additional Requirements",
    placeholder=(
        "Example: The tenant is allowed to keep one pet. "
        "Electricity and water charges will be paid by the tenant. "
        "Major structural repairs will be the responsibility of the landlord. "
        "The tenant must provide 30 days notice before vacating."
    ),
    height=110,
    key="additional_requirements",
    label_visibility="collapsed"
)

form_data["additional_requirements"] = additional_requirements

# ===========================
# ACTIONS & CONTRACT GENERATION
# ===========================
st.markdown("<br>", unsafe_allow_html=True)

act_col1, act_col2 = st.columns(2)

with act_col1:
    if st.button("📋 Review Brief Summary", use_container_width=True):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"### {contract_type} Overview")
        st.markdown(f"**Title:** {contract_title}")
        st.markdown(f"**Jurisdiction:** {state}, {country}")
        st.markdown(f"**Language Preference:** {default_lang}")
        if contract_type == "Rental Agreement":
            st.markdown(f"**Landlord:** {form_data.get('landlord_name')} | **Tenant:** {form_data.get('tenant_name')}")
            st.markdown(f"**Rent:** {form_data.get('rent_amount')} {default_curr} / month | **Deposit:** {form_data.get('security_deposit')}")
        elif contract_type == "Employment Agreement":
            st.markdown(f"**Employer:** {form_data.get('employer_name')} | **Employee:** {form_data.get('employee_name')}")
            st.markdown(f"**Job Title:** {form_data.get('job_title')} ({form_data.get('employment_type')})")
        elif contract_type == "Partnership Agreement":
            st.markdown(f"**Firm Name:** {form_data.get('firm_name')}")
            st.markdown(f"**Partner 1:** {form_data.get('p1_name')} ({form_data.get('p1_share')}%) | **Partner 2:** {form_data.get('p2_name')} ({form_data.get('p2_share')}%)")
        elif contract_type == "Consultancy Agreement":
            st.markdown(f"**Client:** {form_data.get('client_name')} | **Consultant:** {form_data.get('consultant_name')}")
            st.markdown(f"**Retainer Fee:** {form_data.get('consultancy_fee')} {default_curr}")
        elif contract_type == "Vendor Agreement":
            st.markdown(f"**Purchaser:** {form_data.get('purchaser_name')} | **Vendor:** {form_data.get('vendor_name')}")
            st.markdown(f"**Annual Contract Value:** {form_data.get('contract_value')} {default_curr}")
        st.markdown('</div>', unsafe_allow_html=True)

with act_col2:
    generate_btn = st.button("🚀 Draft Contract with Local ML Pipeline", use_container_width=True)

if generate_btn:
    # Contract-Specific Validation
    valid = True
    err_msg = ""

    if contract_type == "Rental Agreement":
        if not form_data.get("landlord_name") or not form_data.get("tenant_name") or not form_data.get("property_address"):
            valid = False
            err_msg = "Please provide Landlord Name, Tenant Name, and Property Address."
    elif contract_type == "Employment Agreement":
        if not form_data.get("employer_name") or not form_data.get("employee_name") or not form_data.get("job_title"):
            valid = False
            err_msg = "Please provide Employer Company Name, Employee Name, and Job Title."
    elif contract_type == "Freelance Agreement":
        if not form_data.get("client_name") or not form_data.get("freelancer_name") or not form_data.get("project_name"):
            valid = False
            err_msg = "Please provide Client Name, Freelancer Name, and Project Name."
    elif contract_type == "Non Disclosure Agreement (NDA)":
        if not form_data.get("disclosing_party") or not form_data.get("receiving_party"):
            valid = False
            err_msg = "Please provide Disclosing Party Name and Receiving Party Name."
    elif contract_type == "Service Agreement":
        if not form_data.get("client_name") or not form_data.get("provider_name") or not form_data.get("service_name"):
            valid = False
            err_msg = "Please provide Client Name, Service Provider Name, and Service Title."
    elif contract_type in ["Sale / Purchase Agreement", "Sales Agreement"]:
        if not form_data.get("buyer_name") or not form_data.get("seller_name") or not form_data.get("item_description"):
            valid = False
            err_msg = "Please provide Buyer Name, Seller Name, and Item Description."
    elif contract_type == "Partnership Agreement":
        if not form_data.get("p1_name") or not form_data.get("p2_name") or not form_data.get("firm_name"):
            valid = False
            err_msg = "Please provide Partner 1 Name, Partner 2 Name, and Partnership Firm Name."
    elif contract_type == "Consultancy Agreement":
        if not form_data.get("client_name") or not form_data.get("consultant_name") or not form_data.get("expertise_area"):
            valid = False
            err_msg = "Please provide Client Name, Consultant Name, and Field of Expertise."
    elif contract_type == "Vendor Agreement":
        if not form_data.get("purchaser_name") or not form_data.get("vendor_name") or not form_data.get("supply_description"):
            valid = False
            err_msg = "Please provide Purchaser Name, Vendor Name, and Supply Description."
    elif contract_type == "Custom Contract":
        if not form_data.get("custom_party_a_name") or not form_data.get("custom_party_b_name") or not form_data.get("custom_purpose"):
            valid = False
            err_msg = "Please provide Party A Name, Party B Name, and Detailed Purpose."

    if not valid:
        st.error(f"⚠️ Validation Failed: {err_msg}")
    else:
        # Render contract using local template engine
        contract = render_contract(contract_type, form_data)

        st.session_state["generated_contract"] = contract
        st.session_state["contract_form_data"] = dict(form_data)   # save for PDF
        st.session_state["contract_title_saved"] = contract_title
        st.session_state["contract_type_saved"] = contract_type

        # Save to SQLite database
        save_contract(
            title=contract_title,
            contract_type=contract_type,
            created_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            contract=contract
        )

        # Save unified history record
        save_history_record(
            contract_name=contract_title,
            contract_type=contract_type,
            activity_type="Drafted",
            description=f"Generated {contract_type} contract.",
            result_content=contract,
        )

        st.success(f"✅ {contract_type} drafted successfully and saved to repository!")

if "generated_contract" in st.session_state:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-head"><span class="tag">§ OUT</span><h2>Generated Agreement Document</h2></div>', unsafe_allow_html=True)

    # ── Draft status badge ────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(90deg,#1C2B4B,#2A3F6F); color:#C8972A;
                border-radius:8px; padding:10px 18px; font-weight:700;
                font-size:0.9rem; margin-bottom:12px; letter-spacing:0.05em;">
        ⚖️ &nbsp; AI-ASSISTED DRAFT &nbsp;·&nbsp;
        <span style="color:#CBD5E1; font-weight:400;">Human / legal review recommended before execution or use.</span>
    </div>
    """, unsafe_allow_html=True)

    contract_text = st.session_state["generated_contract"]

    # ── Consistency / completeness check ─────────────────────────────────────
    from services.consistency_checker import check_contract_completeness
    _saved_fd  = st.session_state.get("contract_form_data", form_data)
    _saved_ct  = st.session_state.get("contract_type_saved", contract_type)
    
    checks, warns = check_contract_completeness(contract_text, _saved_ct, _saved_fd)

    # Display check results
    with st.expander("📋 Draft Completeness & Consistency Check", expanded=True):
        st.markdown("**DRAFT CHECK** — This is not a legal guarantee.", unsafe_allow_html=False)
        check_col1, check_col2 = st.columns(2)
        with check_col1:
            for c in checks:
                st.markdown(c)
        with check_col2:
            for w in warns:
                st.markdown(w)

    # ── Contract text area ────────────────────────────────────────────────────
    st.text_area(
        "Agreement Document (raw text)",
        value=contract_text,
        height=600,
        key="contract_text_display"
    )

    # ── PDF generation ────────────────────────────────────────────────────────
    _title_for_pdf = st.session_state.get("contract_title_saved", contract_title)
    _type_for_pdf  = st.session_state.get("contract_type_saved",  contract_type)
    _fd_for_pdf    = st.session_state.get("contract_form_data",   form_data)

    pdf_file = create_pdf(
        contract_text,
        contract_title=_title_for_pdf,
        contract_type=_type_for_pdf,
        form_data=_fd_for_pdf,
        legal_context=[],
    )

    st.download_button(
        label="📄 Download Official PDF Document",
        data=pdf_file,
        file_name=f"{(_title_for_pdf or 'Legal_Contract').replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    # ── Request Changes / Regenerate ──────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-head"><span class="tag">§ REV</span><h2>Request Changes</h2></div>', unsafe_allow_html=True)
    st.caption("Describe changes to apply to the existing draft. The original party information will be preserved.")

    change_request = st.text_area(
        "Requested Changes",
        placeholder="e.g. Change notice period to 30 days. Add a parking clause. Include a pet policy for one cat.",
        height=90,
        key="change_request_input"
    )

    if st.button("🔄 Regenerate Draft with Changes", use_container_width=True):
        if not change_request.strip():
            st.warning("Please describe the changes you want before regenerating.")
        else:
            _regen_fd = dict(st.session_state.get("contract_form_data", form_data))
            existing_req = _regen_fd.get("additional_requirements", "").strip()
            _regen_fd["additional_requirements"] = (
                (existing_req + "\n" if existing_req else "") +
                "REVISION REQUEST — Apply the following changes to the previous draft: " + change_request
            )
            _regen_prompt = build_contract_prompt(
                st.session_state.get("contract_type_saved", contract_type),
                _regen_fd
            )
            with st.spinner("⚖️ Regenerating contract with requested changes..."):
                _regen_contract = generate_contract(_regen_prompt)
            st.session_state["generated_contract"] = _regen_contract
            st.session_state["contract_form_data"]  = _regen_fd
            st.success("✅ Contract regenerated with your requested changes.")
            st.rerun()