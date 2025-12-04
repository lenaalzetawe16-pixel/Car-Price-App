import streamlit as st
import pandas as pd
import numpy as np
import joblib

# 1. إعدادات الصفحة (يجب أن تكون في البداية)
st.set_page_config(page_title="Car Price Pro", page_icon="🚗", layout="centered")

# 2. تحميل الموديل والأعمدة
@st.cache_resource # لتسريع التحميل
def load_model():
    model = joblib.load('car_price_model.pkl')
    model_columns = joblib.load('model_columns.pkl')
    return model, model_columns

model, model_columns = load_model()

# 3. تصميم الواجهة الجانبية (Sidebar) للإعدادات العامة
st.sidebar.header("⚙️ الإعدادات العامة")

# --- ميزة 1: تحويل العملة ---
currency_option = st.sidebar.selectbox(
    "اختر العملة للعرض:",
    ("USD ($)", "JOD (دينار)", "SAR (ريال)", "AED (درهم)", "INR (روبية)")
)

# أسعار صرف تقريبية (مقابل العملة الأساسية للموديل - نفترض أنها الروبية الهندية INR)
# ملاحظة: الموديل تدرب على بيانات هندية، لذا الأساس INR
exchange_rates = {
    "INR (روبية)": 1.0,
    "USD ($)": 0.012,
    "JOD (دينار)": 0.0085,
    "SAR (ريال)": 0.045,
    "AED (درهم)": 0.044
}

# 4. واجهة التطبيق الرئيسية
st.title("🚗 مقدر أسعار السيارات الذكي (V2.0)")
st.markdown("---")

# --- ميزة 2: حالة السيارة (جديد/مستعمل) ---
condition = st.radio("حالة السيارة:", ["مستعملة (Used)", "جديدة (New)"], horizontal=True)

# تقسيم الشاشة
col1, col2 = st.columns(2)

with col1:
    make = st.selectbox("الشركة المصنعة", ['Toyota', 'Honda', 'Hyundai', 'Suzuki', 'BMW', 'Mercedes-Benz', 'Audi', 'Kia', 'Ford'])
    
    # --- ميزة 3: أنواع وقود إضافية ---
    fuel = st.selectbox("نوع الوقود", ['Petrol', 'Diesel', 'CNG', 'Electric', 'Hybrid'])
    
    transmission = st.radio("ناقل الحركة", ['Manual', 'Automatic'], horizontal=True)

with col2:
    if condition == "جديدة (New)":
        # إذا كانت جديدة، نثبت القيم تلقائياً
        year = 2025
        kms = 0
        st.info("ℹ️ السيارة الجديدة: الممشى 0 كم، موديل 2025")
    else:
        # إذا مستعملة، نفتح الخيارات
        year = st.slider("سنة الصنع", 2000, 2024, 2018)
        kms = st.number_input("المسافة المقطوعة (كم)", min_value=0, value=50000, step=1000)

    # حجم المحرك (يطلب في الحالتين)
    engine = st.number_input("حجم المحرك (CC)", min_value=0, value=1500, step=100)

# 5. زر التوقع والمنطق الهندسي
if st.button("💰 احسب السعر الآن", type="primary"):
    
    # تجهيز البيانات للموديل
    car_age = 2025 - year # حساب العمر بناءً على السنة الحالية
    
    input_data = pd.DataFrame({
        'Make': [make],
        'Car_Age': [car_age],
        'Kilometer': [kms],
        'Engine': [engine],
        'Fuel Type': [fuel],
        'Transmission': [transmission]
    })
    
    # معالجة البيانات (Encoding)
    input_data = pd.get_dummies(input_data)
    input_data = input_data.reindex(columns=model_columns, fill_value=0)
    
    try:
        # التوقع (القيمة تخرج باللوغاريتم)
        prediction_log = model.predict(input_data)
        base_price = np.expm1(prediction_log)[0] # تحويلها لسعر حقيقي (INR)
        
        # تحويل العملة
        final_price = base_price * exchange_rates[currency_option]
        
        # عرض النتيجة بشكل جميل
        st.success(f"السعر المتوقع: {final_price:,.0f} {currency_option}")
        
        # نصائح إضافية بناءً على الحالة
        if condition == "جديدة (New)":
            st.balloons()
            st.write("✨ مبروك! سيارة جديدة تماماً.")
        elif kms > 100000:
            st.warning("⚠️ انتبه: الممشى مرتفع، قد تحتاج لصيانة قريبة.")
            
    except Exception as e:
        st.error("حدث خطأ في الحساب، يرجى التأكد من المدخلات.")
