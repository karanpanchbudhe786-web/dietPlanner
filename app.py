"""
🥗 AI Diet Planner
===================
A complete personal nutrition and wellness dashboard built with Streamlit.

Run locally:
    streamlit run app.py
"""

import os
import io
import json
import re
import datetime
from typing import Optional, Tuple, List, Dict, Any

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend safe for servers and tunnels
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ─── Optional: Gemini AI Integration ─────────────────────────────────────────
def _get_gemini_key() -> Optional[str]:
    """Safely retrieve Gemini API key from env or st.secrets without crashing."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("GEMINI_API_KEY", None)
    except Exception:
        return None

GEMINI_API_KEY = _get_gemini_key()

# ─── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="🥗 AI Diet Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Global Styling & Theme ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.stApp {
    background-color: #f8fafc;
}

/* Header Banner */
.app-header {
    background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 50%, #40916c 100%);
    border-radius: 16px;
    padding: 1.8rem 2.2rem;
    margin-bottom: 1.2rem;
    color: white;
    box-shadow: 0 4px 20px rgba(27, 67, 50, 0.2);
}
.app-header h1 {
    margin: 0;
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.5px;
}
.app-header p {
    margin: 0.3rem 0 0;
    font-size: 0.95rem;
    opacity: 0.9;
    font-weight: 300;
}

/* Top Profile Summary Bar */
.profile-summary-bar {
    background: white;
    border-radius: 12px;
    padding: 0.85rem 1.4rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    display: flex;
    gap: 1.8rem;
    flex-wrap: wrap;
    align-items: center;
    font-size: 0.9rem;
    border-left: 4px solid #40916c;
}
.profile-summary-bar.incomplete {
    border-left: 4px solid #f59e0b;
    color: #92400e;
    background: #fffbeb;
}

/* Cards & Containers */
.ui-card {
    background: white;
    border-radius: 14px;
    padding: 1.4rem;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    margin-bottom: 1rem;
}

/* Section Titles */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1b4332;
    margin: 0.5rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* BMI Card */
.bmi-card {
    background: white;
    border-radius: 16px;
    padding: 1.8rem;
    text-align: center;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    margin-bottom: 1rem;
}
.bmi-value {
    font-size: 3.6rem;
    font-weight: 800;
    line-height: 1;
}
.bmi-category {
    font-size: 1.15rem;
    font-weight: 600;
    margin-top: 0.3rem;
}

/* Meal Plan Day Cards */
.day-card {
    background: white;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    margin-bottom: 0.9rem;
    border-top: 4px solid #40916c;
}
.day-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1b4332;
    margin-bottom: 0.8rem;
}
.meal-row {
    display: flex;
    align-items: baseline;
    gap: 0.6rem;
    margin-bottom: 0.45rem;
}
.meal-type {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    color: #6b7280;
    letter-spacing: 0.05em;
    min-width: 80px;
}
.meal-name {
    font-size: 0.92rem;
    color: #374151;
}

/* Badges & Disclaimers */
.badge-ai {
    background: #d1fae5;
    color: #065f46;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 700;
}
.badge-rule {
    background: #e5e7eb;
    color: #374151;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 700;
}
.disclaimer-box {
    background: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 0.82rem;
    color: #78350f;
    margin: 0.8rem 0;
    line-height: 1.4;
}

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.4rem;
    background: white;
    border-radius: 12px;
    padding: 0.35rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    margin-bottom: 1.2rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
    font-size: 0.92rem;
    color: #4b5563;
}
.stTabs [aria-selected="true"] {
    background: #1b4332 !important;
    color: white !important;
}

/* Profile Tiles */
.profile-tile {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.85rem;
    text-align: center;
}
.profile-tile .pt-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
    font-weight: 600;
}
.profile-tile .pt-value {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1b4332;
    margin-top: 0.2rem;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. CENTRALIZED SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

def initialize_session_state() -> None:
    """Initialize all session state keys with robust defaults."""
    defaults: Dict[str, Any] = {
        "profile_saved"  : False,
        "height"         : 170.0,
        "weight"         : 70.0,
        "age"            : 25,
        "gender"         : "Male",
        "activity"       : "Moderately Active",
        "diet_type"      : "Vegetarian",
        "goal"           : "Balanced Nutrition",
        "allergies"      : [],
        "bmi"            : 0.0,
        "bmi_category"   : "",
        "water_intake"   : 0.0,
        "water"          : 0.0,  # Legacy alias for backward compatibility
        "weight_history" : [],
        "meal_plan"      : {},
        "ai_used"        : False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

initialize_session_state()

# ═══════════════════════════════════════════════════════════════════════════════
# 2. BMI & METRIC CALCULATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI = weight / (height in meters)^2."""
    try:
        h_m = height_cm / 100.0
        if h_m <= 0:
            return 0.0
        return round(weight_kg / (h_m * h_m), 1)
    except Exception:
        return 0.0

def get_bmi_category(bmi: float) -> str:
    """
    Return clean BMI category with continuous boundaries (no gaps):
    < 18.5 -> Underweight
    < 25.0 -> Normal
    < 30.0 -> Overweight
    >= 30.0 -> Obese
    """
    if bmi <= 0:
        return "Unknown"
    elif bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal"
    elif bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"

def get_bmi_color(category: str) -> str:
    """Map category to color token."""
    color_map = {
        "Underweight": "#3b82f6",
        "Normal"     : "#10b981",
        "Overweight" : "#f59e0b",
        "Obese"      : "#ef4444",
        "Unknown"    : "#9ca3af",
    }
    return color_map.get(category, "#9ca3af")

def validate_profile() -> Tuple[bool, List[str]]:
    """Check if profile is completed and return missing requirements."""
    missing = []
    if not st.session_state.get("profile_saved", False):
        missing.append("Profile not saved yet")
    if not st.session_state.get("bmi", 0.0):
        missing.append("BMI not calculated")
    return (len(missing) == 0, missing)

# ═══════════════════════════════════════════════════════════════════════════════
# 3. 7-DAY MEAL PLANS & ALLERGY FILTERING
# ═══════════════════════════════════════════════════════════════════════════════

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

MEAL_PLANS = {
    "Vegetarian": {
        "Monday":    {"Breakfast": "Masala oats with fruits & chia seeds",    "Lunch": "Roti, dal makhani, sabzi & fresh salad",     "Snack": "Mixed fruit bowl",                   "Dinner": "Paneer bhurji with multigrain roti"},
        "Tuesday":   {"Breakfast": "Poha with vegetables & lemon",            "Lunch": "Brown rice, rajma curry & cucumber raita",   "Snack": "Roasted makhana (fox nuts)",         "Dinner": "Vegetable daliya (broken wheat) khichdi"},
        "Wednesday": {"Breakfast": "Whole wheat upma with vegetables",        "Lunch": "Chapati, chana masala & green salad",       "Snack": "Apple with peanut butter",           "Dinner": "Mixed vegetable soup with toasted multigrain bread"},
        "Thursday":  {"Breakfast": "Besan chilla with mint chutney",          "Lunch": "Matar paneer with jeera rice & raita",      "Snack": "Buttermilk (chaas) & banana",        "Dinner": "Roti with dal fry & stir-fried spinach"},
        "Friday":    {"Breakfast": "Banana smoothie with flaxseed",           "Lunch": "Palak dal with brown rice & papad",         "Snack": "Mixed dates & raisins",              "Dinner": "Vegetable pulao with cucumber raita"},
        "Saturday":  {"Breakfast": "Idli with sambar & coconut chutney",      "Lunch": "Aloo gobi sabzi, roti & lassi",             "Snack": "Steamed corn chaat",                 "Dinner": "Moong dal soup with toast"},
        "Sunday":    {"Breakfast": "Whole grain toast with avocado & tomato", "Lunch": "Chole with 1 whole wheat bhatura & salad",  "Snack": "Yoghurt with honey & berries",       "Dinner": "Kadhi with steamed rice & sautéed veggies"},
    },
    "Non-Vegetarian": {
        "Monday":    {"Breakfast": "Egg white omelette with multigrain toast",     "Lunch": "Chicken curry with brown rice & salad",         "Snack": "Boiled egg & mixed seeds",         "Dinner": "Grilled fish with steamed vegetables"},
        "Tuesday":   {"Breakfast": "Scrambled eggs with spinach & toast",          "Lunch": "Mutton curry with jeera rice & raita",          "Snack": "Fresh fruit bowl",                 "Dinner": "Chicken vegetable soup with bread"},
        "Wednesday": {"Breakfast": "Chicken keema stuffed paratha with yoghurt",  "Lunch": "Fish curry with brown rice & cucumber salad",    "Snack": "Boiled chana with lemon",          "Dinner": "Egg bhurji with roti & stir-fried greens"},
        "Thursday":  {"Breakfast": "Oats with banana, seeds & honey",              "Lunch": "Chicken biryani with cucumber raita",           "Snack": "Roasted makhana",                  "Dinner": "Prawn masala with multigrain roti"},
        "Friday":    {"Breakfast": "Banana protein shake & boiled egg whites",     "Lunch": "Minced chicken with peas & roti",               "Snack": "Mixed dates & seeds",              "Dinner": "Grilled chicken breast with roasted veggies"},
        "Saturday":  {"Breakfast": "Egg dosa with sambar",                         "Lunch": "Fish tikka with mint chutney & salad",           "Snack": "Yoghurt with fruit",               "Dinner": "Chicken broth with toasted sourdough"},
        "Sunday":    {"Breakfast": "Whole wheat pancakes with poached eggs",       "Lunch": "Chicken curry with chapati & garden salad",     "Snack": "Fresh fruit chaat",                "Dinner": "Tandoori fish with yellow dal & rice"},
    },
    "Vegan": {
        "Monday":    {"Breakfast": "Overnight oats with almond milk & berries",   "Lunch": "Rajma curry with brown rice & green salad",    "Snack": "Apple slices with almond butter",    "Dinner": "Tofu stir-fry with quinoa & broccoli"},
        "Tuesday":   {"Breakfast": "Banana smoothie with oats & chia seeds",      "Lunch": "Chole (chickpea curry) with roti & salad",     "Snack": "Mixed sunflower & pumpkin seeds",    "Dinner": "Vegetable soup with lentil bread"},
        "Wednesday": {"Breakfast": "Avocado toast on whole grain bread",           "Lunch": "Lentil dal with brown rice & steamed greens",  "Snack": "Roasted chickpeas with chaat masala","Dinner": "Quinoa vegetable khichdi"},
        "Thursday":  {"Breakfast": "Fruit & seed granola with coconut milk",       "Lunch": "Tofu scramble with multigrain roti & salad",   "Snack": "Fresh watermelon slices",            "Dinner": "Spicy black bean tacos with fresh salsa"},
        "Friday":    {"Breakfast": "Green smoothie (spinach, banana, flaxseed)",   "Lunch": "Mushroom & pea curry with jeera rice",         "Snack": "Steamed edamame & lemon",            "Dinner": "Baked sweet potato with chickpea filling"},
        "Saturday":  {"Breakfast": "Idli with coconut chutney & sambar",           "Lunch": "Kadala (black chickpea) curry with appam",     "Snack": "Fresh fruit chaat",                  "Dinner": "Vegetable biryani with vegan cucumber raita"},
        "Sunday":    {"Breakfast": "Peanut butter on whole wheat toast & banana",  "Lunch": "Tempeh curry with brown rice & sautéed kale",  "Snack": "Mixed seeds & dried fruit",          "Dinner": "Lentil soup with crusty whole wheat bread"},
    },
    "Eggetarian": {
        "Monday":    {"Breakfast": "Masala egg omelette with multigrain toast",    "Lunch": "Paneer curry with roti & cucumber salad",      "Snack": "Boiled egg & fruit bowl",            "Dinner": "Egg fried brown rice (minimal oil) & salad"},
        "Tuesday":   {"Breakfast": "Poha with a boiled egg on the side",           "Lunch": "Yellow dal, rice & stir-fried vegetables",     "Snack": "Roasted makhana & banana",           "Dinner": "Egg curry with multigrain roti"},
        "Wednesday": {"Breakfast": "Banana oat smoothie with 2 boiled egg whites", "Lunch": "Rajma with jeera rice & raita",                "Snack": "Apple with peanut butter",           "Dinner": "Shakshuka (poached eggs in tomato sauce) with toast"},
        "Thursday":  {"Breakfast": "Egg paratha with yoghurt & mint chutney",      "Lunch": "Aloo matar with chapati & yellow dal soup",    "Snack": "Roasted chickpeas with chaat masala","Dinner": "Paneer bhurji with multigrain roti & salad"},
        "Friday":    {"Breakfast": "Scrambled eggs with sautéed mushrooms & toast","Lunch": "Chana masala with brown rice & papad",         "Snack": "Yoghurt with honey & granola",       "Dinner": "Egg dosa with sambar & coconut chutney"},
        "Saturday":  {"Breakfast": "French toast with cinnamon & seasonal fruit",   "Lunch": "Palak paneer with roti & cucumber salad",      "Snack": "Corn chaat with lemon",              "Dinner": "Egg drop soup with multigrain toast"},
        "Sunday":    {"Breakfast": "Whole grain pancakes with eggs & maple syrup", "Lunch": "Matar paneer with jeera rice & salad",         "Snack": "Mixed fruit bowl",                   "Dinner": "Dal makhani with boiled egg & steamed rice"},
    },
}

ALLERGY_KEYWORDS = {
    "Nuts"   : ["nut", "peanut", "almond", "cashew", "pistachio", "walnut", "makhana"],
    "Dairy"  : ["paneer", "yoghurt", "raita", "lassi", "butter", "ghee", "milk", "cheese", "buttermilk", "chaas"],
    "Gluten" : ["roti", "bread", "toast", "chapati", "naan", "paratha", "upma", "poha", "semolina", "wheat", "daliya", "bhatura"],
    "Soy"    : ["tofu", "soy", "edamame", "tempeh"],
    "Eggs"   : ["egg", "omelette", "scrambled", "french toast", "shakshuka", "poached"],
}

ALLERGY_SUBSTITUTES = {
    "Nuts"   : "Roasted sunflower/pumpkin seeds & fresh fruit",
    "Dairy"  : "Coconut-based or plant-based alternative",
    "Gluten" : "Jowar/bajra roti or brown rice cakes",
    "Soy"    : "Sprouted lentil or chickpea alternative",
    "Eggs"   : "Besan chilla (gram flour savoury pancake) or tofu",
}

GOAL_NOTES = {
    "Balanced Nutrition"       : "🥗 **Balanced Nutrition Focus**: Build balanced meals with ½ plate vegetables, ¼ protein source, and ¼ whole grains.",
    "Muscle & Strength Support": "💪 **Muscle & Strength Focus**: High-protein density. Ensure adequate protein portion at each meal alongside regular hydration.",
    "Healthy Lifestyle"        : "🌿 **Healthy Lifestyle Focus**: Focus on unprocessed whole foods, vibrant colours, and dietary fiber.",
    "General Fitness"          : "🏃 **General Fitness Focus**: Sustained energy release from complex carbohydrates and clean hydration.",
}

def contains_allergy(meal_text: str, allergies: List[str]) -> bool:
    """Return True if meal contains any restricted ingredient keyword."""
    text_lower = meal_text.lower()
    for allergy in allergies:
        keywords = ALLERGY_KEYWORDS.get(allergy, [])
        if any(k in text_lower for k in keywords):
            return True
    return False

def get_safe_meal(meal_text: str, allergies: List[str]) -> str:
    """Replace conflicting food items with suitable substitutes instead of hiding them."""
    if not allergies:
        return meal_text
    
    detected = [a for a in allergies if contains_allergy(meal_text, [a])]
    if not detected:
        return meal_text
    
    subs = [ALLERGY_SUBSTITUTES[a] for a in detected if a in ALLERGY_SUBSTITUTES]
    sub_text = " / ".join(subs)
    return f"{meal_text} ⚠️ *(Allergy substitute: {sub_text})*"

def generate_meal_plan(diet_type: str, allergies: List[str], goal: str) -> Dict[str, Dict[str, str]]:
    """Generate structured 7-day meal plan with allergy filtering."""
    base_plan = MEAL_PLANS.get(diet_type, MEAL_PLANS["Vegetarian"])
    result = {}
    for day in DAYS:
        result[day] = {
            meal: get_safe_meal(food, allergies)
            for meal, food in base_plan[day].items()
        }
    return result

def generate_ai_meal_plan(profile: Dict[str, Any]) -> Optional[Dict[str, Dict[str, str]]]:
    """Generate AI meal plan using Gemini API if key is configured, with safe error handling."""
    if not GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
You are an expert nutritionist. Create a 7-day personalized wellness meal plan.
User Profile:
- Age: {profile.get('age')} years, Gender: {profile.get('gender')}
- Height: {profile.get('height')} cm, Weight: {profile.get('weight')} kg, BMI: {profile.get('bmi')} ({profile.get('bmi_category')})
- Activity: {profile.get('activity')}
- Dietary Preference: {profile.get('diet_type')}
- Goal: {profile.get('goal')}
- Food Restrictions/Allergies: {', '.join(profile.get('allergies', [])) or 'None'}

Output ONLY valid JSON dictionary without markdown formatting:
{{
  "Monday":    {{"Breakfast": "...", "Lunch": "...", "Snack": "...", "Dinner": "..."}},
  "Tuesday":   {{"Breakfast": "...", "Lunch": "...", "Snack": "...", "Dinner": "..."}},
  "Wednesday": {{"Breakfast": "...", "Lunch": "...", "Snack": "...", "Dinner": "..."}},
  "Thursday":  {{"Breakfast": "...", "Lunch": "...", "Snack": "...", "Dinner": "..."}},
  "Friday":    {{"Breakfast": "...", "Lunch": "...", "Snack": "...", "Dinner": "..."}},
  "Saturday":  {{"Breakfast": "...", "Lunch": "...", "Snack": "...", "Dinner": "..."}},
  "Sunday":    {{"Breakfast": "...", "Lunch": "...", "Snack": "...", "Dinner": "..."}}
}}
Rules:
- Strictly adhere to {profile.get('diet_type')} diet.
- Exclude all ingredients with: {', '.join(profile.get('allergies', [])) or 'none'}.
- Provide practical, realistic, healthy meal names.
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        match = re.search(r'\{[\s\S]+\}', text)
        if match:
            return json.loads(match.group())
    except Exception:
        return None
    return None

def create_downloadable_meal_plan(meal_plan: Dict[str, Dict[str, str]], profile: Dict[str, Any], format_type: str = "txt") -> str:
    """Format meal plan for TXT or CSV download."""
    if format_type == "csv":
        rows = []
        for day, meals in meal_plan.items():
            for m_type, food in meals.items():
                clean_food = food.split("⚠️")[0].strip()
                rows.append({"Day": day, "Meal": m_type, "Menu": clean_food})
        return pd.DataFrame(rows).to_csv(index=False)
    
    # Default TXT
    lines = [
        "=" * 56,
        "          🥗  AI DIET PLANNER — 7-DAY MEAL PLAN",
        "=" * 56,
        f"  Dietary Preference : {profile.get('diet_type', 'N/A')}",
        f"  Wellness Goal      : {profile.get('goal', 'N/A')}",
        f"  Food Restrictions  : {', '.join(profile.get('allergies', [])) or 'None'}",
        f"  Generated On       : {datetime.date.today().strftime('%d %B %Y')}",
        "=" * 56,
        ""
    ]
    for day, meals in meal_plan.items():
        lines.append(f"  📅 {day.upper()}")
        lines.append("  " + "-" * 50)
        for m_type, food in meals.items():
            clean_food = food.split("⚠️")[0].strip()
            lines.append(f"  {m_type:<12}: {clean_food}")
        lines.append("")
    lines += [
        "─" * 56,
        "  ⚠️  DISCLAIMER",
        "  This plan is for general wellness guidance only.",
        "  It is not a medical prescription. Please consult a",
        "  registered dietitian or doctor for personalized advice.",
        "─" * 56,
    ]
    return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════════════════════
# 4. RENDER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def render_header() -> None:
    """Render top application banner."""
    st.markdown("""
    <div class="app-header">
        <h1>🥗 AI Diet Planner</h1>
        <p>Personalized nutrition, hydration tracking & wellness progress dashboard</p>
    </div>
    """, unsafe_allow_html=True)

def render_profile_summary_bar() -> None:
    """Render compact, reactive top profile summary bar."""
    if st.session_state.get("profile_saved", False):
        ss = st.session_state
        st.markdown(f"""
        <div class="profile-summary-bar">
            <span><strong>👤 {ss['gender']}, {ss['age']} yrs</strong></span>
            <span>⚖️ {ss['weight']} kg</span>
            <span>📏 {ss['height']} cm</span>
            <span>🔢 BMI <strong>{ss['bmi']}</strong> ({ss['bmi_category']})</span>
            <span>🥗 {ss['diet_type']}</span>
            <span>🎯 {ss['goal']}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="profile-summary-bar incomplete">
            <span>⚠️ <strong>Profile not completed</strong> — Fill in your details below and click <strong>Save Profile & Calculate BMI</strong> to unlock personalized plans.</span>
        </div>
        """, unsafe_allow_html=True)

def render_profile_tab() -> None:
    """Tab 1: Profile & BMI Calculation."""
    col_form, col_bmi = st.columns([1.1, 0.9], gap="large")

    with col_form:
        st.markdown('<div class="section-title">👤 Your Profile</div>', unsafe_allow_html=True)
        
        with st.form("profile_form", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                height = st.number_input(
                    "Height (cm)",
                    min_value=80.0,
                    max_value=250.0,
                    value=float(st.session_state["height"]),
                    step=0.5,
                    format="%.1f",
                    help="Height in centimeters (80–250 cm)"
                )
                weight = st.number_input(
                    "Weight (kg)",
                    min_value=20.0,
                    max_value=300.0,
                    value=float(st.session_state["weight"]),
                    step=0.5,
                    format="%.1f",
                    help="Current weight in kilograms (20–300 kg)"
                )
            with c2:
                age = st.number_input(
                    "Age (years)",
                    min_value=10,
                    max_value=100,
                    value=int(st.session_state["age"]),
                    step=1,
                    help="Age in years (10–100)"
                )
                gender = st.selectbox(
                    "Sex / Gender",
                    ["Male", "Female", "Other"],
                    index=["Male", "Female", "Other"].index(st.session_state["gender"]) if st.session_state["gender"] in ["Male", "Female", "Other"] else 0,
                    help="Collected to calibrate standard metabolic and nutrition guideline references"
                )

            activity = st.selectbox(
                "Activity Level",
                ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"],
                index=["Sedentary", "Lightly Active", "Moderately Active", "Very Active"].index(st.session_state["activity"]),
                help="Your general daily physical activity level"
            )

            diet_type = st.selectbox(
                "Dietary Preference",
                ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"],
                index=["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"].index(st.session_state["diet_type"]),
                help="Your core dietary lifestyle"
            )

            goal = st.selectbox(
                "Wellness Goal",
                ["Balanced Nutrition", "Muscle & Strength Support", "Healthy Lifestyle", "General Fitness"],
                index=["Balanced Nutrition", "Muscle & Strength Support", "Healthy Lifestyle", "General Fitness"].index(st.session_state["goal"]),
                help="Primary nutrition target"
            )

            allergies = st.multiselect(
                "Food Restrictions / Allergies",
                ["Nuts", "Dairy", "Gluten", "Soy", "Eggs"],
                default=st.session_state["allergies"],
                help="Select ingredients that must be avoided or substituted"
            )

            save_btn = st.form_submit_button("💾 Save Profile & Calculate BMI", type="primary", use_container_width=True)

        if save_btn:
            errors = []
            if height < 80 or height > 250:
                errors.append("Please enter a valid height (80–250 cm).")
            if weight < 20 or weight > 300:
                errors.append("Please enter a valid weight (20–300 kg).")
            if age < 10 or age > 100:
                errors.append("Please enter a valid age (10–100 years).")

            if errors:
                for err in errors:
                    st.error(f"⚠️ {err}")
            else:
                bmi = calculate_bmi(weight, height)
                bmi_cat = get_bmi_category(bmi)

                # Persist strictly into session state
                st.session_state["height"]       = height
                st.session_state["weight"]       = weight
                st.session_state["age"]          = age
                st.session_state["gender"]       = gender
                st.session_state["activity"]     = activity
                st.session_state["diet_type"]    = diet_type
                st.session_state["goal"]         = goal
                st.session_state["allergies"]    = allergies
                st.session_state["bmi"]          = bmi
                st.session_state["bmi_category"] = bmi_cat
                st.session_state["profile_saved"] = True

                # Generate base meal plan
                st.session_state["meal_plan"] = generate_meal_plan(diet_type, allergies, goal)
                st.session_state["ai_used"]   = False

                # If Gemini key present, attempt AI generation
                if GEMINI_API_KEY:
                    with st.spinner("🤖 Consulting AI nutrition model…"):
                        ai_plan = generate_ai_meal_plan({
                            "age": age, "gender": gender, "height": height, "weight": weight,
                            "bmi": bmi, "bmi_category": bmi_cat, "activity": activity,
                            "diet_type": diet_type, "goal": goal, "allergies": allergies
                        })
                        if ai_plan:
                            st.session_state["meal_plan"] = ai_plan
                            st.session_state["ai_used"]   = True

                st.success("✅ Profile saved and BMI calculated successfully!")
                st.rerun()

    with col_bmi:
        if st.session_state.get("profile_saved", False) and st.session_state.get("bmi", 0.0) > 0:
            bmi = st.session_state["bmi"]
            cat = st.session_state["bmi_category"]
            col = get_bmi_color(cat)

            st.markdown(f"""
            <div class="bmi-card" style="border-top: 5px solid {col};">
                <div style="font-size:0.78rem;text-transform:uppercase;letter-spacing:0.1em;color:#94a3b8;font-weight:600;">YOUR BMI</div>
                <div class="bmi-value" style="color:{col};">{bmi}</div>
                <div class="bmi-category" style="color:{col};">{cat}</div>
                <hr style="border:none;border-top:1px solid #e2e8f0;margin:1rem 0;">
                <div style="font-size:0.75rem;color:#64748b;line-height:1.4;">
                    BMI is a general screening measure and does not replace professional medical assessment.
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Matplotlib Visual BMI Gauge
            fig, ax = plt.subplots(figsize=(4.5, 2.2))
            fig.patch.set_alpha(0)
            ax.set_xlim(0, 40)
            ax.set_ylim(0, 1)
            ax.axis("off")

            # Category Bands
            segments = [(10, 18.5, "#93c5fd"), (18.5, 25, "#6ee7b7"), (25, 30, "#fcd34d"), (30, 40, "#fca5a5")]
            for s_start, s_end, s_color in segments:
                bar = mpatches.FancyArrowPatch(
                    (s_start, 0.45), (s_end, 0.45),
                    arrowstyle=mpatches.ArrowStyle.Simple(head_width=0, tail_width=16),
                    color=s_color, alpha=0.9
                )
                ax.add_patch(bar)

            # Marker needle
            clamped_bmi = min(max(bmi, 10), 40)
            ax.axvline(x=clamped_bmi, ymin=0.35, ymax=0.82, color=col, lw=3.2)
            ax.annotate("", xy=(clamped_bmi, 0.76), xytext=(clamped_bmi, 0.45),
                        arrowprops=dict(arrowstyle="->", color=col, lw=2.5))

            # Numerical labels
            for val in [10, 18.5, 25, 30, 40]:
                ax.text(val, 0.2, str(val), ha="center", va="center", fontsize=7.5, color="#64748b")

            for txt, pos in [("Under", 14), ("Normal", 21.75), ("Over", 27.5), ("Obese", 35)]:
                ax.text(pos, 0.64, txt, ha="center", va="center", fontsize=8, color="#1e293b", fontweight="bold")

            plt.tight_layout(pad=0.1)
            st.pyplot(fig)
            plt.close(fig)

            # Profile Summary Grid
            st.markdown('<div class="section-title">📋 Profile Summary</div>', unsafe_allow_html=True)
            ss = st.session_state
            summary_items = [
                ("📏 Height", f"{ss['height']} cm"),
                ("⚖️ Weight", f"{ss['weight']} kg"),
                ("🎂 Age", f"{ss['age']} yrs"),
                ("⚡ Activity", ss['activity']),
                ("🥗 Diet", ss['diet_type']),
                ("🎯 Goal", ss['goal'].split()[0] + "…"),
            ]
            s_cols = st.columns(3)
            for idx, (label, val) in enumerate(summary_items):
                with s_cols[idx % 3]:
                    st.markdown(f"""
                    <div class="profile-tile">
                        <div class="pt-label">{label}</div>
                        <div class="pt-value">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

            if ss["allergies"]:
                st.markdown(f"""
                <div class="disclaimer-box" style="margin-top:0.8rem;">
                    ⚠️ <strong>Restrictions Recorded:</strong> {', '.join(ss['allergies'])} — meal plan adapted with safe substitutes.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:3.5rem 1.5rem;background:white;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,0.05);">
                <div style="font-size:3.2rem;">📝</div>
                <div style="font-size:1.1rem;font-weight:700;color:#1e293b;margin:0.8rem 0 0.3rem;">Profile Not Completed</div>
                <div style="color:#64748b;font-size:0.9rem;">Fill in your measurements on the left and click <strong>Save Profile & Calculate BMI</strong>.</div>
            </div>
            """, unsafe_allow_html=True)

def render_meal_plan_tab() -> None:
    """Tab 2: 7-Day Personalised Meal Plan."""
    is_valid, missing = validate_profile()
    if not is_valid:
        st.warning(f"⚠️ Please complete your profile first. Missing: {', '.join(missing)}")
        st.info("👈 Go to the **🏠 Profile** tab, enter your details, and click **Save Profile & Calculate BMI**.")
        return

    ss = st.session_state
    meal_plan = ss.get("meal_plan", {})
    if not meal_plan:
        meal_plan = generate_meal_plan(ss["diet_type"], ss["allergies"], ss["goal"])
        st.session_state["meal_plan"] = meal_plan

    # Header & Badge
    col_t, col_b = st.columns([3, 1])
    with col_t:
        st.markdown('<div class="section-title">📋 Your 7-Day Personalised Meal Plan</div>', unsafe_allow_html=True)
    with col_b:
        badge_html = '<span class="badge-ai">🤖 AI Personalized</span>' if ss.get("ai_used") else '<span class="badge-rule">📊 Personalized Rule-Based Plan</span>'
        st.markdown(f"<div style='text-align:right;margin-top:0.8rem;'>{badge_html}</div>", unsafe_allow_html=True)

    # Goal Note
    goal_note = GOAL_NOTES.get(ss["goal"], "")
    if goal_note:
        st.markdown(f'<div class="disclaimer-box">{goal_note}</div>', unsafe_allow_html=True)

    # 7-Day Display
    for day in DAYS:
        day_meals = meal_plan.get(day, {})
        st.markdown(f"""
        <div class="day-card">
            <div class="day-title">📅 {day}</div>
            <div class="meal-row"><span class="meal-type">🌅 Breakfast</span><span class="meal-name">{day_meals.get('Breakfast', '—')}</span></div>
            <div class="meal-row"><span class="meal-type">☀️ Lunch</span><span class="meal-name">{day_meals.get('Lunch', '—')}</span></div>
            <div class="meal-row"><span class="meal-type">🍎 Snack</span><span class="meal-name">{day_meals.get('Snack', '—')}</span></div>
            <div class="meal-row"><span class="meal-type">🌙 Dinner</span><span class="meal-name">{day_meals.get('Dinner', '—')}</span></div>
        </div>
        """, unsafe_allow_html=True)

    # Optional AI Refresh
    if GEMINI_API_KEY:
        if st.button("🔄 Regenerate / Refresh AI Meal Plan", type="secondary"):
            with st.spinner("🤖 Crafting a new AI meal plan…"):
                new_plan = generate_ai_meal_plan({
                    "age": ss["age"], "gender": ss["gender"], "height": ss["height"],
                    "weight": ss["weight"], "bmi": ss["bmi"], "bmi_category": ss["bmi_category"],
                    "activity": ss["activity"], "diet_type": ss["diet_type"],
                    "goal": ss["goal"], "allergies": ss["allergies"]
                })
                if new_plan:
                    st.session_state["meal_plan"] = new_plan
                    st.session_state["ai_used"]   = True
                    st.success("✅ New AI meal plan generated!")
                    st.rerun()
                else:
                    st.warning("⚠️ AI recommendation service is temporarily unavailable. Standard meal-plan recommendation maintained.")

    # Downloads
    st.markdown('<div class="section-title">⬇️ Download Meal Plan</div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    with d1:
        txt_data = create_downloadable_meal_plan(meal_plan, ss, "txt")
        st.download_button(
            label="📄 Download as TXT",
            data=txt_data,
            file_name=f"meal_plan_{datetime.date.today()}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with d2:
        csv_data = create_downloadable_meal_plan(meal_plan, ss, "csv")
        st.download_button(
            label="📊 Download as CSV",
            data=csv_data,
            file_name=f"meal_plan_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("""
    <div class="disclaimer-box" style="margin-top:1rem;">
        ⚠️ This meal plan is for general wellness guidance only. It is not a medical prescription. Please consult a registered dietitian before making significant dietary changes.
    </div>
    """, unsafe_allow_html=True)

def render_nutrition_dashboard() -> None:
    """Tab 3: Nutrition Dashboard."""
    is_valid, missing = validate_profile()
    if not is_valid:
        st.warning(f"⚠️ Please complete your profile first. Missing: {', '.join(missing)}")
        return

    ss = st.session_state
    st.markdown('<div class="section-title">📊 Nutrition Dashboard</div>', unsafe_allow_html=True)

    # Metric Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("BMI", f"{ss['bmi']}", ss['bmi_category'])
    with m2:
        st.metric("Diet Preference", ss['diet_type'])
    with m3:
        st.metric("Daily Activity", ss['activity'])
    with m4:
        st.metric("Wellness Goal", ss['goal'])

    st.divider()

    col_guide, col_macro = st.columns([1.1, 0.9], gap="large")

    with col_guide:
        st.markdown('<div class="section-title">🥦 General Nutrition Guide</div>', unsafe_allow_html=True)
        st.caption("The following are general healthy eating guidelines — not a personalised medical prescription.")

        goal = ss.get("goal", "Balanced Nutrition")
        if goal == "Muscle & Strength Support":
            guides = [
                ("🥩 Protein Sources", 85, "Legumes, paneer, eggs, fish, chicken, tofu"),
                ("🥦 Vegetables",      75, "Leafy greens, cruciferous veg, colourful salads"),
                ("🍎 Fruits",          60, "Seasonal fruits, berries, citrus"),
                ("🌾 Whole Grains",    70, "Brown rice, whole wheat, oats, quinoa"),
                ("🫒 Healthy Fats",    50, "Nuts, seeds, olive oil, avocado in moderation"),
            ]
        elif goal == "Healthy Lifestyle":
            guides = [
                ("🥩 Protein Sources", 65, "Legumes, paneer, tofu, eggs, beans"),
                ("🥦 Vegetables",      90, "Aim for 5+ servings of varied vegetables daily"),
                ("🍎 Fruits",          80, "2–3 whole seasonal fruits daily"),
                ("🌾 Whole Grains",    80, "Choose whole grains over refined carbohydrates"),
                ("🫒 Healthy Fats",    60, "Cold-pressed oils, seeds, nuts in moderation"),
            ]
        else:  # Balanced / General Fitness
            guides = [
                ("🥩 Protein Sources", 70, "Legumes, dairy, eggs, lean meats"),
                ("🥦 Vegetables",      80, "Ensure half your meal plate is fresh vegetables"),
                ("🍎 Fruits",          70, "2–3 portions of whole fruit per day"),
                ("🌾 Whole Grains",    75, "Brown rice, oats, whole wheat rotis"),
                ("🫒 Healthy Fats",    55, "Nuts, seeds, ghee/oil in balanced moderation"),
            ]

        for label, pct, tip in guides:
            st.markdown(f"**{label}** — `{pct}% recommended consistency`")
            st.progress(pct / 100.0)
            st.caption(tip)

    with col_macro:
        st.markdown('<div class="section-title">🍽️ Estimated Macro Ratio</div>', unsafe_allow_html=True)
        st.caption("Approximate target macronutrient distribution for your goal.")

        macro_map = {
            "Balanced Nutrition"       : [40, 30, 30],
            "Muscle & Strength Support": [35, 40, 25],
            "Healthy Lifestyle"        : [45, 25, 30],
            "General Fitness"          : [40, 30, 30],
        }
        macro_vals = macro_map.get(goal, [40, 30, 30])
        labels = ["Carbohydrates", "Protein", "Healthy Fats"]
        colors = ["#34d399", "#60a5fa", "#fbbf24"]

        fig_m, ax_m = plt.subplots(figsize=(4, 4))
        fig_m.patch.set_alpha(0)
        wedges, texts, autotexts = ax_m.pie(
            macro_vals, labels=labels, colors=colors,
            autopct="%1.0f%%", startangle=90,
            wedgeprops=dict(width=0.5, edgecolor="white", linewidth=2),
            textprops=dict(fontsize=10.5)
        )
        for at in autotexts:
            at.set_fontsize(10)
            at.set_fontweight("bold")
        ax_m.set_aspect("equal")
        plt.tight_layout(pad=0.5)
        st.pyplot(fig_m)
        plt.close(fig_m)

    # Tips
    st.markdown('<div class="section-title">💡 Goal-Specific Nutrition Tips</div>', unsafe_allow_html=True)
    tips_map = {
        "Balanced Nutrition":        ["Eat a rainbow of vegetables every day", "Choose whole grains over ultra-processed foods", "Include healthy fats from nuts and seeds", "Maintain steady hydration between meals"],
        "Muscle & Strength Support": ["Prioritise a quality protein portion at every meal", "Refuel within 45 minutes after strength workouts", "Do not cut healthy complex carbs — they fuel training", "Combine legumes and grains for complete plant amino acids"],
        "Healthy Lifestyle":         ["Minimise ultra-processed snacks and added refined sugars", "Cook home-style meals with fresh ingredients", "Eat mindfully and chew thoroughly", "Incorporate diverse dietary fiber daily"],
        "General Fitness":           ["Match overall nutrition intake to daily activity intensity", "Hydrate before, during, and after exercise", "Keep healthy snacks like fruit and roasted seeds accessible", "Maintain consistent meal timings"],
    }
    for tip in tips_map.get(goal, tips_map["Balanced Nutrition"]):
        st.markdown(f"✅ {tip}")

    st.markdown("""
    <div class="disclaimer-box" style="margin-top:1rem;">
        ⚠️ These ratios are general wellness guidelines, not a medically prescribed diet plan. Consult a registered dietitian for personalised advice.
    </div>
    """, unsafe_allow_html=True)

def render_wellness_progress_tab() -> None:
    """Tab 4: Merged Wellness & Progress (Hydration + Weight Tracker)."""
    st.markdown('<div class="section-title">💧 Wellness & Progress Dashboard</div>', unsafe_allow_html=True)

    # TWO COLUMNS: Left = Hydration, Right = Weight Logging
    col_hydro, col_weight = st.columns([1, 1], gap="large")

    # ── LEFT COLUMN: 💧 Today's Water Intake ──────────────────────────────────
    with col_hydro:
        st.markdown("""
        <div class="ui-card">
            <div class="section-title" style="margin-top:0;">💧 Today's Water Intake</div>
        </div>
        """, unsafe_allow_html=True)

        water = float(st.session_state.get("water_intake", st.session_state.get("water", 0.0)))
        pct = min(water / 3.0, 1.0)
        level_col = "#10b981" if pct >= 0.8 else "#3b82f6" if pct >= 0.5 else "#ef4444"
        status_msg = "Great hydration! 💪" if pct >= 0.8 else "Keep drinking regularly! 👍" if pct >= 0.5 else "Drink water regularly 💧"

        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:1.4rem;text-align:center;box-shadow:0 2px 10px rgba(0,0,0,0.05);margin-bottom:1rem;">
            <div style="font-size:3.6rem;font-weight:800;color:{level_col};line-height:1;">{water:.2f} L</div>
            <div style="font-size:0.95rem;color:#475569;font-weight:600;margin-top:0.4rem;">{status_msg}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**Progress toward general ~3L reference:** `{pct*100:.0f}%`")
        st.progress(pct)
        st.caption("Hydration needs vary by individual, activity, environment, and health conditions.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Quick Water Buttons**")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("+250 ml\n(1 glass)", key="w250", use_container_width=True):
                st.session_state["water_intake"] = round(water + 0.25, 2)
                st.session_state["water"] = st.session_state["water_intake"]
                st.rerun()
            if st.button("+500 ml\n(large glass)", key="w500", use_container_width=True):
                st.session_state["water_intake"] = round(water + 0.50, 2)
                st.session_state["water"] = st.session_state["water_intake"]
                st.rerun()
        with b2:
            if st.button("+750 ml\n(bottle)", key="w750", use_container_width=True):
                st.session_state["water_intake"] = round(water + 0.75, 2)
                st.session_state["water"] = st.session_state["water_intake"]
                st.rerun()
            if st.button("+1.0 L\n(big bottle)", key="w1000", use_container_width=True):
                st.session_state["water_intake"] = round(water + 1.00, 2)
                st.session_state["water"] = st.session_state["water_intake"]
                st.rerun()

        custom_l = st.number_input("Custom Amount (Litres)", min_value=0.05, max_value=5.0, value=0.25, step=0.25, format="%.2f")
        if st.button("➕ Add Custom Amount", type="primary", use_container_width=True):
            st.session_state["water_intake"] = round(water + custom_l, 2)
            st.session_state["water"] = st.session_state["water_intake"]
            st.rerun()

        if st.button("🔄 Reset Today's Count", use_container_width=True):
            st.session_state["water_intake"] = 0.0
            st.session_state["water"] = 0.0
            st.rerun()

    # ── RIGHT COLUMN: ⚖️ Log Today's Weight ──────────────────────────────────
    with col_weight:
        st.markdown("""
        <div class="ui-card">
            <div class="section-title" style="margin-top:0;">⚖️ Log Today's Weight</div>
        </div>
        """, unsafe_allow_html=True)

        weight_history = st.session_state.get("weight_history", [])

        # CRITICAL DATA CONSISTENCY FIX: Initialize weight from st.session_state["weight"]
        default_profile_weight = float(st.session_state.get("weight", 70.0))

        log_date = st.date_input("Date", value=datetime.date.today(), key="log_date_input")
        log_weight = st.number_input(
            "Weight (kg)",
            min_value=20.0,
            max_value=300.0,
            value=default_profile_weight,
            step=0.1,
            format="%.1f",
            help="Defaults to your current profile weight. Change to log a new measurement.",
            key="log_weight_input"
        )
        log_note = st.text_input("Note (optional)", placeholder="e.g. Morning fasting, Post workout", key="log_note_input")

        if st.button("➕ Log Entry", type="primary", use_container_width=True):
            entry_date_str = str(log_date)
            # Avoid duplicate date clutter by updating existing record if present
            existing_idx = next((i for i, e in enumerate(weight_history) if e.get("date") == entry_date_str), -1)
            
            if existing_idx >= 0:
                weight_history[existing_idx] = {
                    "date"  : entry_date_str,
                    "weight": log_weight,
                    "note"  : log_note
                }
                st.success(f"✅ Updated existing weight record for {entry_date_str} to {log_weight} kg.")
            else:
                weight_history.append({
                    "date"  : entry_date_str,
                    "weight": log_weight,
                    "note"  : log_note
                })
                st.success(f"✅ Logged {log_weight} kg for {entry_date_str}!")
            
            st.session_state["weight_history"] = weight_history
            st.rerun()

        # Mini summary if records exist
        if weight_history:
            df_mini = pd.DataFrame(weight_history).sort_values("date")
            latest_rec = df_mini.iloc[-1]
            st.markdown(f"""
            <div style="background:#f1f5f9;border-radius:10px;padding:0.75rem 1rem;margin-top:1rem;font-size:0.88rem;">
                <strong>Latest Record:</strong> {latest_rec['weight']} kg ({latest_rec['date']})
                {f"<br><span style='color:#64748b;'>Note: {latest_rec['note']}</span>" if latest_rec.get('note') else ""}
            </div>
            """, unsafe_allow_html=True)

    # ── BELOW COLUMNS: 📈 Weight Trend & 📋 Weight History ────────────────────
    st.divider()
    st.markdown('<div class="section-title">📈 Weight Trend</div>', unsafe_allow_html=True)

    if not weight_history or len(weight_history) == 0:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1.5rem;background:white;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,0.05);margin-bottom:1rem;">
            <div style="font-size:3rem;">📊</div>
            <div style="font-size:1.1rem;font-weight:700;color:#1e293b;margin:0.8rem 0 0.3rem;">No Data Yet</div>
            <div style="color:#64748b;font-size:0.9rem;">Log at least one weight entry to see your trend chart.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        df_w = pd.DataFrame(weight_history).sort_values("date")
        df_w["date_dt"] = pd.to_datetime(df_w["date"])
        df_w["weight"]  = pd.to_numeric(df_w["weight"])

        first_w = df_w["weight"].iloc[0]
        latest_w = df_w["weight"].iloc[-1]
        delta_val = round(latest_w - first_w, 1)
        delta_str = f"+{delta_val} kg" if delta_val >= 0 else f"{delta_val} kg"

        st_cols = st.columns(3)
        st_cols[0].metric("Current Logged", f"{latest_w} kg", f"{delta_str} from start")
        st_cols[1].metric("Lowest Logged", f"{df_w['weight'].min()} kg")
        st_cols[2].metric("Total Entries", len(df_w))

        # Matplotlib Line Chart
        fig_w, ax_w = plt.subplots(figsize=(8, 3.2))
        fig_w.patch.set_alpha(0)
        ax_w.set_facecolor("#f8fafc")

        dates_plot = df_w["date_dt"].dt.strftime("%d %b").tolist()
        weights_plot = df_w["weight"].tolist()

        ax_w.fill_between(dates_plot, weights_plot, min(weights_plot) - 1, alpha=0.12, color="#40916c")
        ax_w.plot(
            dates_plot, weights_plot,
            color="#2d6a4f", linewidth=2.5,
            marker="o", markersize=6.5,
            markerfacecolor="white", markeredgewidth=2.2,
            markeredgecolor="#2d6a4f"
        )

        for d, w in zip(dates_plot, weights_plot):
            ax_w.annotate(f"{w} kg", (d, w), textcoords="offset points", xytext=(0, 9),
                          ha="center", fontsize=8.5, color="#1e293b", fontweight="bold")

        ax_w.set_ylabel("Weight (kg)", fontsize=9, color="#64748b")
        ax_w.tick_params(axis="x", labelsize=8.5)
        ax_w.tick_params(axis="y", labelsize=8.5)
        ax_w.grid(axis="y", linestyle="--", alpha=0.5, color="#cbd5e1")
        ax_w.spines[["top", "right"]].set_visible(False)
        ax_w.spines[["left", "bottom"]].set_color("#e2e8f0")
        plt.tight_layout()
        st.pyplot(fig_w)
        plt.close(fig_w)

        st.markdown("""
        <div class="disclaimer-box">
            ⚠️ Healthy weight change is gradual. This tool tracks trends only — it is not a medical monitoring system.
        </div>
        """, unsafe_allow_html=True)

        # Weight History Table
        st.markdown('<div class="section-title">📋 Weight History</div>', unsafe_allow_html=True)
        table_df = df_w[["date", "weight", "note"]].rename(columns={
            "date": "Date",
            "weight": "Weight (kg)",
            "note": "Note"
        })
        st.dataframe(table_df, use_container_width=True, hide_index=True)

        if st.button("🗑️ Clear Weight History", use_container_width=False):
            st.session_state["weight_history"] = []
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# 5. MAIN NAVIGATION & APPLICATION ENTRYPOINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    render_header()
    render_profile_summary_bar()

    # Exactly 4 Navigation Tabs
    tab_profile, tab_meals, tab_nutrition, tab_wellness = st.tabs([
        "🏠 Profile",
        "📋 Meal Plan",
        "📊 Nutrition",
        "💧 Wellness & Progress",
    ])

    with tab_profile:
        render_profile_tab()

    with tab_meals:
        render_meal_plan_tab()

    with tab_nutrition:
        render_nutrition_dashboard()

    with tab_wellness:
        render_wellness_progress_tab()

if __name__ == "__main__":
    main()
