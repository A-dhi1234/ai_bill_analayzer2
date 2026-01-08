# ===================== PATH SETUP =====================
import sys, os, time, shutil, tempfile
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

# ===================== IMPORTS =====================
import streamlit as st
import pandas as pd
import plotly.express as px

from llm_extract import extract_bill
from ocr_reader import extract_text
from rag_engine import ask_question

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="AI Bill Analyzer",
    page_icon="📊",
    layout="wide"
)

EXCEL_PATH = "data/expenses.xlsx"

# ===================== SAFE EXCEL SAVE =====================
def safe_save_excel(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, temp_path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    df.to_excel(temp_path, index=False)
    try:
        shutil.move(temp_path, path)
    except PermissionError:
        st.error("❌ Please close expenses.xlsx and try again")
        os.remove(temp_path)
        st.stop()

# ===================== BILL PREVIEW =====================
def preview_bill(file):
    if file.type == "application/pdf":
        st.info("📄 PDF preview not embedded (download to view)")
        st.download_button(
            "⬇️ Download PDF",
            file,
            file_name=file.name
        )
    else:
        st.image(file, caption="🧾 Bill Preview", use_container_width=True)

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("## 📊 AI Bill Analyzer")
    st.caption("Smart Expense Intelligence")

    page = st.radio(
        "Navigate",
        ["Dashboard", "Upload Bill", "Ask AI"]
    )

    st.divider()
    dark = st.toggle("🌙 Dark Mode", value=True)
    st.caption("© 2026 Expense AI")

# ===================== THEME =====================
bg = "#0b1220" if dark else "#f8fafc"
card = "rgba(255,255,255,0.06)" if dark else "#ffffff"
text = "#e5e7eb" if dark else "#020617"

st.markdown(f"""
<style>
.stApp {{
    background: {bg};
    color: {text};
}}
.card {{
    background: {card};
    padding: 22px;
    border-radius: 18px;
    transition: 0.3s;
}}
.card:hover {{
    transform: translateY(-4px);
}}
.header {{
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg,#38bdf8,#22c55e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
</style>
""", unsafe_allow_html=True)

# ===================== HEADER =====================
st.markdown('<div class="header">AI Bill Analyzer</div>', unsafe_allow_html=True)
st.caption("OCR • LLM • Editable AI • Excel • RAG")

# ===================== DASHBOARD =====================
if page == "Dashboard":
    st.subheader("📊 Expense Dashboard")

    if os.path.exists(EXCEL_PATH):
        df = pd.read_excel(EXCEL_PATH)

        c1, c2, c3 = st.columns(3)
        c1.markdown(
            f"<div class='card'>💰<h2>₹{df.amount.sum():,.0f}</h2>Total Spend</div>",
            unsafe_allow_html=True
        )
        c2.markdown(
            f"<div class='card'>🧾<h2>{len(df)}</h2>Bills</div>",
            unsafe_allow_html=True
        )
        c3.markdown(
            f"<div class='card'>📦<h2>{df.bill_type.nunique()}</h2>Categories</div>",
            unsafe_allow_html=True
        )

        st.divider()

        summary = df.groupby("bill_type", as_index=False)["amount"].sum()

        fig = px.bar(
            summary,
            x="bill_type",
            y="amount",
            color="bill_type",
            text_auto=True,
            title="Category-wise Expenses"
        )
        fig.update_layout(
            plot_bgcolor=bg,
            paper_bgcolor=bg,
            font_color=text,
            height=420
        )

        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        with open(EXCEL_PATH, "rb") as f:
            st.download_button(
                "📥 Download Expenses Excel",
                f,
                file_name="expenses.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:
        st.info("📂 Upload bills to see dashboard")

# ===================== UPLOAD BILL =====================
if page == "Upload Bill":
    st.subheader("📤 Upload Bill")

    uploaded = st.file_uploader(
        "📎 Drag & drop or browse bill",
        type=["pdf", "jpg", "jpeg", "png"],
        help="Supported formats: PDF, JPG, PNG"
    )

    if uploaded is None:
        st.info("⬆️ Upload a bill to continue")
    else:
        st.success(f"Selected file: {uploaded.name}")

        st.markdown("### 🧾 Bill Preview")
        preview_bill(uploaded)

        if st.button("🤖 Extract Bill Details"):
            with st.spinner("🔍 Reading bill..."):
                text = extract_text(uploaded)

            with st.spinner("🤖 Extracting with AI..."):
                bill = extract_bill(text)

            st.markdown("### ✏️ Edit Bill Before Saving")

            with st.form("edit_bill_form"):
                bill_type = st.selectbox(
                    "Bill Type",
                    ["Medical", "Grocery", "Fuel", "Clothing", "Unknown"]
                )
                vendor = st.text_input("Vendor", bill.get("vendor", ""))
                bill_date = st.text_input(
                    "Bill Date (YYYY-MM-DD)",
                    bill.get("bill_date", "")
                )
                amount = st.number_input(
                    "Amount",
                    min_value=0.0,
                    value=float(bill.get("amount", 0))
                )

                save = st.form_submit_button("💾 Save Bill")

            if save:
                row = {
                    "bill_type": bill_type,
                    "vendor": vendor,
                    "bill_date": bill_date,
                    "amount": amount
                }

                df_new = pd.DataFrame([row])

                if os.path.exists(EXCEL_PATH):
                    old = pd.read_excel(EXCEL_PATH)
                    df_new = pd.concat([old, df_new], ignore_index=True)

                safe_save_excel(df_new, EXCEL_PATH)

                st.toast("📥 Bill saved to Excel", icon="✅")
                st.success("Bill saved successfully!")
                st.dataframe(df_new.tail(1))

# ===================== ASK AI =====================
if page == "Ask AI":
    st.subheader("💬 Ask AI About Expenses")

    q = st.text_input("Example: What is my highest expense category?")

    if q:
        with st.spinner("🧠 Thinking..."):
            ans = ask_question(q)
        st.success(ans)

    with st.expander("💡 Sample Questions"):
        st.markdown("""
        • Total medical expense  
        • Grocery vs fuel comparison  
        • Highest category spend  
        • Overall expense summary  
        """)

st.divider()
st.caption("Built with ❤️ using Streamlit & Groq")
