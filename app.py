import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Səhifə Konfiqurasiyası
st.set_page_config(
    page_title="FinCorp - Əməkhaqqı & Bank Analitikası",
    page_icon="🏢",
    layout="wide"
)

# --- SESSION STATE (MƏLUMATLARIN İDARƏ OLUNMASI VƏ SIFIRLANMASI) ---
if "company_name" not in st.session_state:
    st.session_state["company_name"] = ""
if "emp_count" not in st.session_state:
    st.session_state["emp_count"] = 0
if "avg_salary" not in st.session_state:
    st.session_state["avg_salary"] = 0.0


def reset_all_data():
    st.session_state["company_name"] = ""
    st.session_state["emp_count"] = 0
    st.session_state["avg_salary"] = 0.0
    st.session_state["show_reset_confirm"] = False


# --- SOL MENYÜ (SIDEBAR) ---
st.sidebar.title("🏢 FinCorp SaaS")
st.sidebar.caption("Korporativ Maliyyə v1.0")

page = st.sidebar.radio("Səhifələr üzrə keçid:", [
    "📊 Əsas Kalkulyator",
    "⚖️ Bankların Müqayisəsi",
    "📄 Rəsmi Təklif Generatoru"
])

st.sidebar.divider()
st.sidebar.subheader("⚙️ Şirkət Məlumatları")

# Giriş Xanaları (Session State ilə bağlıdır)
company_name = st.sidebar.text_input("Şirkətin Adı", key="company_name")
emp_count = st.sidebar.number_input("İşçi Sayı", min_value=0, max_value=5000, step=1, key="emp_count")
avg_salary = st.sidebar.number_input("Ortalama Qross Maaş (AZN)", min_value=0.0, max_value=50000.0, step=50.0,
                                     key="avg_salary")
sector = st.sidebar.selectbox("Fəaliyyət Sektoru", ["Özəl Sektor (Qeyri-neft)", "Dövlət / Neft Sektoru"])

st.sidebar.divider()

# --- TƏHLÜKƏSİZ SIFIRLAMA BLOKU ---
st.sidebar.subheader("🚨 Təhlükəsizlik və İdarəetmə")

if "show_reset_confirm" not in st.session_state:
    st.session_state["show_reset_confirm"] = False

if not st.session_state["show_reset_confirm"]:
    if st.sidebar.button("🔄 Bütün Məlumatları Sıfırla", type="secondary"):
        st.session_state["show_reset_confirm"] = True
        st.rerun()
else:
    st.sidebar.warning("⚠️ Bütün məlumatlar silinəcək. Əminsiniz?")
    col_reset1, col_reset2 = st.sidebar.columns(2)
    with col_reset1:
        if st.button("✅ Bəli, Sıfırla", type="primary"):
            reset_all_data()
            st.rerun()
    with col_reset2:
        if st.button("❌ Ləğv et"):
            st.session_state["show_reset_confirm"] = False
            st.rerun()

# --- BANK DATA ---
BANK_DATA = {
    "Kapital Bank": {"commission": 0.004, "cashback": 0.015, "rating": "4.8/5",
                     "perks": "Geniş ATM şəbəkəsi, Birbank imkanları"},
    "ABB (Beynəlxalq Bank)": {"commission": 0.003, "cashback": 0.010, "rating": "4.7/5",
                              "perks": "Dövlət zəmanəti, TamKart üstünlükləri"},
    "Unibank": {"commission": 0.005, "cashback": 0.020, "rating": "4.6/5",
                "perks": "Yüksək cashback, UCard loyallıq proqramı"},
    "PAŞA Bank": {"commission": 0.006, "cashback": 0.018, "rating": "4.9/5",
                  "perks": "VIP korporativ xidmət, Premium dəstək"}
}

# --- HESABLAMALAR ---
gross_payroll = emp_count * avg_salary

if sector == "Özəl Sektor (Qeyri-neft)":
    tax_rate = 0.0
    dsmf_emp = 0.03
    dsmf_comp = 0.22
else:
    tax_rate = 0.14
    dsmf_emp = 0.03
    dsmf_comp = 0.22

emp_dsmf_total = gross_payroll * dsmf_emp
income_tax_total = gross_payroll * tax_rate
net_payroll = gross_payroll - emp_dsmf_total - income_tax_total
company_dsmf_total = gross_payroll * dsmf_comp
total_company_cost = gross_payroll + company_dsmf_total

# --- SƏHİFƏ 1: ƏSAS KALKULYATOR ---
if page == "📊 Əsas Kalkulyator":
    header_title = company_name if company_name else "Müştəri Şirkət"
    st.markdown(f"## 📊 {header_title} - Əməkhaqqı Vəziyyəti Paneli")
    st.write("Sol menyudan şirkət adını, işçi sayını və ortalama maaşı daxil edin.")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ümumi Qross Fond", f"{gross_payroll:,.0f} AZN")
    col2.metric("İşçilərə Çatan Net Pul", f"{net_payroll:,.0f} AZN")
    col3.metric("Dövlət Vergi/DSMF", f"{(company_dsmf_total + emp_dsmf_total + income_tax_total):,.0f} AZN")
    col4.metric("Şirkətin Yekun Xərci", f"{total_company_cost:,.0f} AZN")

    st.write("---")

    if gross_payroll > 0:
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("💡 Əməkhaqqı Büdcə Bölgüsü")
            chart_data = pd.DataFrame({
                "Kateqoriya": ["Xalis Maaş (Net)", "İşçi DSMF", "Gəlir Vergisi", "Şirkət DSMF Payı"],
                "Məbləğ (AZN)": [net_payroll, emp_dsmf_total, income_tax_total, company_dsmf_total]
            })
            fig = px.pie(chart_data, values="Məbləğ (AZN)", names="Kateqoriya", hole=0.45)
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.subheader("📋 Detallı Xərc Cədvəli")
            st.table(pd.DataFrame({
                "Müfəssəl Göstərici": ["Cəmi İşçi Sayı", "Bir İşçinin Orta Qrossu", "Şirkətin Aylıq DSMF Xərci",
                                       "Bütün İşçilərin Net Cəmi"],
                "Dəyər": [f"{emp_count} nəfər", f"{avg_salary:,.2f} AZN", f"{company_dsmf_total:,.2f} AZN",
                          f"{net_payroll:,.2f} AZN"]
            }))
    else:
        st.info("👈 Məlumatları görmək üçün sol paneldən İşçi Sayı və Maaş daxil edin.")


# --- SƏHİFƏ 2: BANKLARIN MÜQAYİSƏSİ ---
elif page == "⚖️ Bankların Müqayisəsi":
    st.markdown("## ⚖️ Korporativ Bank Şərtlərinin Müqayisəsi")
    st.divider()

    comp_list = []
    for b_name, b_val in BANK_DATA.items():
        m_comm = gross_payroll * b_val["commission"]
        y_cash = (net_payroll * b_val["cashback"]) * 12
        comp_list.append({
            "Bank": b_name,
            "Aylıq Komissiya (AZN)": round(m_comm, 2),
            "İllik Komissiya (AZN)": round(m_comm * 12, 2),
            "İşçilərə İllik Cashback (AZN)": round(y_cash, 2),
            "Reytinq": b_val["rating"],
            "Əsas Xüsusiyyət": b_val["perks"]
        })

    df_comp = pd.DataFrame(comp_list)
    st.dataframe(df_comp, use_container_width=True)

    if gross_payroll > 0:
        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Bankların Aylıq Komissiya Xərci")
            fig_comm = px.bar(df_comp, x="Bank", y="Aylıq Komissiya (AZN)", color="Bank", text_auto=True)
            st.plotly_chart(fig_comm, use_container_width=True)

        with col2:
            st.subheader("🎁 İşçilərin Qazanacağı İllik Cashback")
            fig_cash = px.bar(df_comp, x="Bank", y="İşçilərə İllik Cashback (AZN)", color="Bank", text_auto=True)
            st.plotly_chart(fig_cash, use_container_width=True)


# --- SƏHİFƏ 3: RƏSMİ TƏKLİF GENERATORU ---
elif page == "📄 Rəsmi Təklif Generatoru":
    st.markdown("## 📄 Rəsmi Kommersiya Təklifinin Formalaşdırılması")
    st.divider()

    selected_bank_prop = st.selectbox("Təklif Hazırlanacaq Bankı Seçin:", list(BANK_DATA.keys()))
    b_info = BANK_DATA[selected_bank_prop]
    m_comm = gross_payroll * b_info["commission"]
    y_cash = (net_payroll * b_info["cashback"]) * 12

    st.info(f"### 🏛️ Kommersiya Təklifi: {selected_bank_prop}")

    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"*Müştəri Şirkət:* {company_name if company_name else 'Daxil edilməyib'}")
        st.write(f"*Nəzərdə Tutulan İşçi Sayı:* {emp_count} nəfər")
        st.write(f"*Aylıq Əməkhaqqı Fondu:* {gross_payroll:,.2f} AZN")
    with col_b:
        st.write(f"*Bank Komissiyası (Aylıq):* {m_comm:,.2f} AZN")
        st.write(f"*İşçilərin İllik Cashback Qazancı:* {y_cash:,.2f} AZN")
        st.write(f"*Xidmət Reytinqi:* {b_info['rating']}")

    st.write("---")
    st.write("#### 🌟 Paketə Daxil Olan Korporativ Üstünlüklər:")
    st.success(f"✔️ {b_info['perks']}")