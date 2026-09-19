import streamlit as st
from datetime import datetime

from services.database_service import (
    init_db, get_history, get_history_record,
    delete_history_record, get_history_stats,
)
from services.pdf_generator import create_pdf
from utils.ui import load_css, page_header

init_db()

st.set_page_config(
    page_title="Contract History \u00b7 AI Legal Assistant",
    page_icon="\u2696\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

page_header(
    "\U0001f4da Contract History",
    "View, search and manage all previous contract activities \u2014 drafts, reviews, clause explanations and risk analyses."
)

# Dashboard Stats
try:
    stats = get_history_stats()
except Exception:
    stats = {"Total": 0, "Drafted": 0, "Reviewed": 0, "Clause Explained": 0, "Risk Analyzed": 0}

m0, m1, m2, m3, m4 = st.columns(5)
with m0:
    st.metric("Total Activities", stats["Total"])
with m1:
    st.metric("Drafted", stats["Drafted"])
with m2:
    st.metric("Reviewed", stats["Reviewed"])
with m3:
    st.metric("Explained", stats["Clause Explained"])
with m4:
    st.metric("Risk Analyzed", stats["Risk Analyzed"])

st.markdown("<br>", unsafe_allow_html=True)

# Search & Filters
st.markdown('<div class="section-head"><span class="tag">\u00a7 01</span><h2>Search &amp; Filter</h2></div>', unsafe_allow_html=True)

fc1, fc2, fc3, fc4, fc5 = st.columns([2.5, 1.5, 1.5, 1.3, 1.3])
with fc1:
    search = st.text_input("\U0001f50e Search contracts", placeholder="Search by name, type or activity...")
with fc2:
    activity_filter = st.selectbox("Activity", ["All", "Drafted", "Reviewed", "Clause Explained", "Risk Analyzed"])
with fc3:
    type_filter = st.selectbox("Contract Type", ["All", "Rental", "Employment", "NDA", "Service", "Freelance", "Other"])
with fc4:
    status_filter = st.selectbox("Status", ["All", "Completed", "Failed"])
with fc5:
    sort_order = st.selectbox("Sort", ["Newest First", "Oldest First"])

# History Records
st.markdown('<div class="section-head"><span class="tag">\u00a7 02</span><h2>History Records</h2></div>', unsafe_allow_html=True)

try:
    records = get_history(
        search=search,
        activity_filter=activity_filter,
        type_filter=type_filter,
        status_filter=status_filter,
        sort_order=sort_order
    )
except Exception as e:
    st.error("Unable to load contract history. Please try again.")
    records = []

ACTIVITY_ICONS = {
    "Drafted": "\U0001f4dd",
    "Reviewed": "\U0001f50d",
    "Clause Explained": "\U0001f4a1",
    "Risk Analyzed": "\u26a0\ufe0f",
}

if not records:
    st.info("\U0001f4c2 No contract history available yet. Start by drafting or uploading a contract.")
else:
    if "confirm_delete_id" not in st.session_state:
        st.session_state.confirm_delete_id = None

    for row in records:
        rec_id, name, ctype, activity, description, created_at, status = row
        icon = ACTIVITY_ICONS.get(activity, "\U0001f4c4")

        try:
            dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            date_str = dt.strftime("%d %b %Y, %I:%M %p")
        except Exception:
            date_str = created_at

        with st.expander(f"{icon}  {name}   \u00b7   [{activity}]   \u00b7   {date_str}"):
            c_info, c_actions = st.columns([3, 1])

            with c_info:
                status_color = "#22c55e" if status == "Completed" else "#ef4444"
                st.markdown(f"""
                <div style="padding:0.5rem 0;">
                    <h4 style="margin:0 0 4px 0;">{name}</h4>
                    <span style="font-size:0.8rem;color:#94a3b8;">Type: {ctype} &nbsp;|&nbsp; Activity: {activity} &nbsp;|&nbsp; {date_str}</span><br>
                    <span style="font-size:0.8rem;color:#94a3b8;">Status: <strong style="color:{status_color};">{status}</strong> &nbsp;|&nbsp; ID: #{rec_id}</span>
                </div>
                """, unsafe_allow_html=True)
                if description:
                    st.caption(description)

            with c_actions:
                view_btn = st.button("\U0001f441 View Result", key=f"view_{rec_id}", use_container_width=True)
                dl_btn   = st.button("\u2b07 Download PDF",  key=f"dl_{rec_id}",   use_container_width=True)
                del_btn  = st.button("\U0001f5d1 Delete",     key=f"del_{rec_id}",  use_container_width=True)

            if view_btn:
                full = get_history_record(rec_id)
                if full and full[7]:
                    st.markdown("---")
                    st.markdown("**Saved Result:**")
                    st.markdown(full[7])
                else:
                    st.info("No saved result content available for this record.")

            if dl_btn:
                full = get_history_record(rec_id)
                if full and full[7]:
                    try:
                        pdf_bytes = create_pdf(
                            contract_text=full[7],
                            contract_title=name,
                            contract_type=ctype,
                        )
                        safe_name = name.replace(" ", "_").replace("/", "_")[:50]
                        st.download_button(
                            label="\U0001f4c4 Click to Download PDF",
                            data=pdf_bytes,
                            file_name=f"{safe_name}.pdf",
                            mime="application/pdf",
                            key=f"dl_actual_{rec_id}",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Could not generate PDF: {e}")
                else:
                    st.warning("No content available to generate a PDF.")

            if del_btn:
                st.session_state.confirm_delete_id = rec_id

            if st.session_state.get("confirm_delete_id") == rec_id:
                st.warning(f"Are you sure you want to delete **{name}**?")
                yes_col, no_col = st.columns(2)
                with yes_col:
                    if st.button("\u2705 Yes, Delete", key=f"conf_yes_{rec_id}", use_container_width=True):
                        delete_history_record(rec_id)
                        st.session_state.confirm_delete_id = None
                        st.success(f"Deleted '{name}'.")
                        st.rerun()
                with no_col:
                    if st.button("\u274c Cancel", key=f"conf_no_{rec_id}", use_container_width=True):
                        st.session_state.confirm_delete_id = None
                        st.rerun()
