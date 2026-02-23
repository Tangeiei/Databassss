import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. ตั้งค่าหน้าจอ Dashboard ---
st.set_page_config(page_title="Factory Data Dashboard", layout="wide")

st.title("📊 Dashboard วิเคราะห์ข้อมูลโรงงาน (รองรับการอัปโหลดไฟล์)")
st.markdown("---")

# --- 2. ส่วนการจัดการไฟล์ (Sidebar) ---
st.sidebar.header("📁 จัดการข้อมูล")

# ปุ่มอัปโหลดไฟล์ใหม่ (เพิ่มฟีเจอร์ตามที่คุณขอ)
uploaded_file = st.sidebar.file_uploader("อัปโหลดไฟล์ CSV ใหม่", type=["csv"])

def load_data():
    if uploaded_file is not None:
        # ถ้ามีการอัปโหลดไฟล์ใหม่ ให้ใช้ไฟล์นั้น
        try:
            return pd.read_csv(uploaded_file, encoding='utf-8-sig')
        except:
            return pd.read_csv(uploaded_file, encoding='cp874')
    else:
        # ถ้าไม่มีการอัปโหลด ให้ใช้ไฟล์ 1a.csv เดิมที่มีอยู่ใน GitHub
        file_path = '1a.csv'
        if os.path.exists(file_path):
            try:
                return pd.read_csv(file_path, encoding='utf-8-sig')
            except:
                return pd.read_csv(file_path, encoding='cp874')
    return pd.DataFrame()

df = load_data()

# ตรวจสอบว่ามีข้อมูลหรือไม่
if not df.empty:
    # ทำความสะอาดข้อมูลเบื้องต้น
    df = df.dropna(subset=['ชื่อโรงงาน', 'จังหวัด'])

    # --- 3. ส่วนการเพิ่มข้อมูลด้วยมือ (Sidebar Form) ---
    with st.sidebar.expander("➕ เพิ่มข้อมูลโรงงานใหม่ (Manual)"):
        with st.form("add_form", clear_on_submit=True):
            f_name = st.text_input("ชื่อโรงงาน")
            f_prov = st.text_input("จังหวัด")
            f_capital = st.number_input("เงินทุนรวม (ล้านบาท)", min_value=0.0)
            submit = st.form_submit_button("บันทึกข้อมูล")
            
            if submit:
                new_row = {'ชื่อโรงงาน': f_name, 'จังหวัด': f_prov, 'เงินทุนรวม (ล้านบาท)': f_capital}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                st.sidebar.success("✅ เพิ่มข้อมูลในตารางแล้ว")

    # --- 4. ตัวกรองข้อมูล (Filter) ---
    st.sidebar.markdown("---")
    prov_list = sorted(df['จังหวัด'].unique().tolist())
    selected_prov = st.sidebar.multiselect("เลือกจังหวัดที่ต้องการดู:", options=prov_list, default=prov_list[:5] if len(prov_list) > 5 else prov_list)

    # กรองข้อมูล
    filtered_df = df[df['จังหวัด'].isin(selected_prov)]

    # --- 5. การแสดงผลกราฟ (โชว์ตัวเลขบนแท่งกราฟ) ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏭 จำนวนโรงงานแยกตามจังหวัด")
        count_df = filtered_df['จังหวัด'].value_counts().reset_index()
        count_df.columns = ['จังหวัด', 'จำนวน']
        
        fig_bar = px.bar(count_df, x='จังหวัด', y='จำนวน', text='จำนวน', color='จังหวัด')
        fig_bar.update_traces(textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("💰 สัดส่วนเงินทุนรวม")
        fig_pie = px.pie(filtered_df, values='เงินทุนรวม (ล้านบาท)', names='จังหวัด')
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- 6. แสดงรายละเอียดทั้งหมด ---
    st.markdown("---")
    st.subheader("📋 รายละเอียดข้อมูลทั้งหมด")
    st.dataframe(filtered_df, use_container_width=True)

    st.balloons()
else:
    st.info("💡 กรุณาอัปโหลดไฟล์ CSV หรือตรวจสอบไฟล์ 1a.csv ในระบบ")
