import streamlit as st
from pathlib import Path

# ---------------------------------------------------------
# 🥗 Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="AI Diet Planner", page_icon="🥗", layout="wide")

# Load CSS (optional)
css_path = Path("assets/styles.css")
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 🌿 Main Title Section
# ---------------------------------------------------------
st.markdown(
    "<h1 style='color:#007BFF; font-weight:800;'>🥗 AI Diet Planner</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h4 style='color:#000000;'>Calculate your BMI and choose your fitness goal to get personalized meal plans!</h4>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 📏 BMI Calculator Section
# ---------------------------------------------------------
st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
st.markdown('<h2 style="color:#007BFF;">Quick BMI Calculator</h2>', unsafe_allow_html=True)
st.markdown(
    '<div style="color:#000; margin-bottom: 24px;">Calculate your Body Mass Index to get AI-powered diet recommendations.</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    height = st.number_input("Height (cm)", min_value=80.0, max_value=250.0, step=0.5, value=170.0, key="height_input")
with col2:
    weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, step=0.5, value=70.0, key="weight_input")
with col3:
    age = st.number_input("Age", min_value=10, max_value=120, step=1, value=28, key="age_input")

# ---------------------------------------------------------
# 🎯 Diet Goal Selection (category)
# ---------------------------------------------------------
st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
st.markdown('<h3 style="color:#007BFF;">🎯 Select Your Diet Goal</h3>', unsafe_allow_html=True)
goal = st.selectbox(
    "Choose your fitness goal:",
    ["Weight Loss", "Weight Gain", "Muscle Gain", "Maintenance"],
    key="diet_goal"
)

# ---------------------------------------------------------
# 🧮 BMI Calculation Logic
# ---------------------------------------------------------
col_btn, _ = st.columns([1, 2])
with col_btn:
    if st.button("Calculate BMI", key="calc_bmi", use_container_width=True):
        bmi = round(weight / ((height / 100) ** 2), 1)

         # Save user information
    st.session_state['height'] = height
    st.session_state['weight'] = weight
    st.session_state['age'] = age
        st.session_state['bmi'] = bmi

        if bmi < 18.5:
            category = "Underweight"
            color = "#3498db"
        elif 18.5 <= bmi < 24.9:
            category = "Normal"
            color = "#2ecc71"
        elif 25 <= bmi < 29.9:
            category = "Overweight"
            color = "#f39c12"
        else:
            category = "Obese"
            color = "#e74c3c"

        # Save results to session state
        st.session_state['bmi_category'] = category
        st.session_state['bmi_color'] = color
        st.session_state['goal'] = goal
        st.session_state['bmi_calculated'] = True

# ---------------------------------------------------------
# 📊 Display BMI Result
# ---------------------------------------------------------
if st.session_state.get('bmi_calculated', False):
    bmi = st.session_state.get('bmi', 0)
    category = st.session_state.get('bmi_category', 'Normal')
    color = st.session_state.get('bmi_color', '#2ecc71')
    goal = st.session_state.get('goal', 'Maintenance')

    st.markdown(f"""
    <div class="bmi-result" style="text-align:center; margin-top:20px;">
        <div class="bmi-value" style="font-size:48px; font-weight:700; color:#000;">{bmi}</div>
        <div class="bmi-category" style="font-size:22px; color:{color}; font-weight:600;">{category}</div>
    </div>
    """, unsafe_allow_html=True)

    st.info(f"💡 Your fitness goal: **{goal}**. Head to **Meal Plan** to see your weekly AI-generated plan!")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 🚀 Quick Actions
# ---------------------------------------------------------
st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
st.markdown('<h2 style="color:#007BFF;">Quick Actions</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("📋 Go to Meal Plan", key="nav_meal_btn", use_container_width=True):
        if st.session_state.get('bmi_calculated', False):
            st.switch_page("pages/1_MealPlan.py")
        else:
            st.warning("⚠️ Please calculate your BMI first!")

with col2:
    if st.button("📊 View Nutrition", key="nav_nutrition_btn", use_container_width=True):
        st.switch_page("pages/1_Nutrition.py")

st.markdown('</div>', unsafe_allow_html=True)
