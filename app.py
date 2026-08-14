"""
🥗 AI Diet Planner
===================
A complete personal nutrition planning dashboard built with Streamlit.

Run:  streamlit run app.py
Deps: pip install streamlit plotly pandas
"""

import os
import io
import datetime
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ─── Optional: Gemini AI integration ────────────────────────────────────────
# Set GEMINI_API_KEY in your environment or Streamlit secrets to enable AI meal generation.
# Example (terminal):  set GEMINI_API_KEY=your_key_here
# Example (Streamlit Cloud): add key via the Streamlit Cloud dashboard → App settings → Secrets
def _get_gemini_key() -> str | None:
    """Safely retrieve Gemini API key — never crashes if secrets.toml is absent."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("GEMINI_API_KEY", None)
    except Exception:
        return None

GEMINI_API_KEY = _get_gemini_key()

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🥗 AI Diet Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Inline CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Font & Base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Hide default Streamlit chrome ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── App background ── */
.stApp { background: #f5f7fa; }

/* ── Header banner ── */
.app-header {
    background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 50%, #40916c 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: white;
    box-shadow: 0 4px 20px rgba(27,67,50,0.25);
}
.app-header h1 { margin: 0; font-size: 2.2rem; font-weight: 700; letter-spacing: -0.5px; }
.app-header p  { margin: 0.3rem 0 0; font-size: 1rem; opacity: 0.85; font-weight: 300; }

/* ── Metric / info cards ── */
.metric-card {
    background: white;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border-left: 4px solid #40916c;
    margin-bottom: 1rem;
}
.metric-card .label { font-size: 0.78rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
.metric-card .value { font-size: 1.6rem; font-weight: 700; color: #1b4332; line-height: 1.2; }
.metric-card .unit  { font-size: 0.85rem; color: #6b7280; font-weight: 400; }

/* ── BMI card ── */
.bmi-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.bmi-value { font-size: 3.5rem; font-weight: 800; line-height: 1; }
.bmi-category { font-size: 1.1rem; font-weight: 600; margin-top: 0.3rem; }

/* ── Section headers ── */
.section-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1b4332;
    margin: 1.5rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Day card for meal plan ── */
.day-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
    border-top: 4px solid #40916c;
}
.day-card .day-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1b4332;
    margin-bottom: 1rem;
}
.meal-row { display: flex; align-items: baseline; gap: 0.5rem; margin-bottom: 0.5rem; }
.meal-type { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #6b7280; letter-spacing: 0.06em; min-width: 70px; }
.meal-name { font-size: 0.95rem; color: #374151; }

/* ── Progress bar label ── */
.prog-label { font-size: 0.85rem; color: #374151; font-weight: 500; margin-bottom: 0.2rem; }

/* ── Water tracker ── */
.water-display { font-size: 3rem; text-align: center; margin: 1rem 0; }

/* ── Profile summary ── */
.profile-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.8rem;
    margin: 1rem 0;
}
.profile-item {
    background: white;
    border-radius: 10px;
    padding: 0.8rem;
    text-align: center;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
.profile-item .pi-label { font-size: 0.7rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; }
.profile-item .pi-value { font-size: 1rem; font-weight: 700; color: #1b4332; margin-top: 0.15rem; }

/* ── Disclaimer ── */
.disclaimer {
    background: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    font-size: 0.8rem;
    color: #78350f;
    margin: 0.8rem 0;
}

/* ── AI badge ── */
.badge-ai   { background: #d1fae5; color: #065f46; border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; font-weight: 700; }
.badge-rule { background: #e5e7eb; color: #374151; border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; font-weight: 700; }

/* ── Tab styling ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: white;
    border-radius: 12px;
    padding: 0.4rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
    font-size: 0.9rem;
}
.stTabs [aria-selected="true"] {
    background: #1b4332 !important;
    color: white !important;
}

/* ── Buttons ── */
.stButton button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stButton button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

def initialize_session_state():
    """Initialize all required session state variables with safe defaults."""
    defaults = {
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
        "meal_plan"      : {},
        "water"          : 0.0,
        "weight_history" : [],
        "ai_used"        : False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# ═══════════════════════════════════════════════════════════════════════════════
# BMI FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI. Returns 0.0 on invalid input."""
    try:
        h = height_cm / 100.0
        return round(weight_kg / (h * h), 1)
    except Exception:
        return 0.0

def get_bmi_category(bmi: float) -> str:
    """Return BMI category with clean boundaries (no gaps)."""
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

def bmi_color(category: str) -> str:
    colors = {
        "Underweight": "#3b82f6",
        "Normal":      "#10b981",
        "Overweight":  "#f59e0b",
        "Obese":       "#ef4444",
        "Unknown":     "#9ca3af",
    }
    return colors.get(category, "#9ca3af")

# ═══════════════════════════════════════════════════════════════════════════════
# PROFILE VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

def validate_profile() -> tuple[bool, list[str]]:
    """Return (is_valid, list_of_missing_fields)."""
    missing = []
    if not st.session_state.get("profile_saved"):
        missing.append("Profile not saved yet")
    if not st.session_state.get("bmi"):
        missing.append("BMI not calculated")
    if not st.session_state.get("diet_type"):
        missing.append("Dietary preference")
    if not st.session_state.get("goal"):
        missing.append("Wellness goal")
    return (len(missing) == 0, missing)

# ═══════════════════════════════════════════════════════════════════════════════
# MEAL PLAN DATA
# ═══════════════════════════════════════════════════════════════════════════════

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Full 7-day varied meal plans per dietary preference
MEAL_PLANS = {
    "Vegetarian": {
        "Monday":    {"Breakfast": "Masala oats with nuts & fruits",         "Lunch": "Roti, dal makhani, sabzi & salad",         "Snack": "Mixed fruit bowl",                   "Dinner": "Paneer bhurji with multigrain roti"},
        "Tuesday":   {"Breakfast": "Poha with peanuts & lemon",              "Lunch": "Brown rice, rajma & cucumber raita",        "Snack": "Roasted makhana (fox nuts)",         "Dinner": "Vegetable daliya (broken wheat) khichdi"},
        "Wednesday": {"Breakfast": "Whole wheat upma with vegetables",        "Lunch": "Chapati, chana masala & green salad",       "Snack": "Apple with peanut butter",           "Dinner": "Mixed vegetable soup with toasted bread"},
        "Thursday":  {"Breakfast": "Besan chilla with mint chutney",          "Lunch": "Matar paneer with jeera rice & raita",      "Snack": "Buttermilk (chaas) & banana",        "Dinner": "Roti with dal fry & stir-fried spinach"},
        "Friday":    {"Breakfast": "Banana smoothie with chia seeds",         "Lunch": "Palak dal with brown rice & papad",         "Snack": "Mixed nuts & dates",                 "Dinner": "Vegetable pulao with cucumber raita"},
        "Saturday":  {"Breakfast": "Idli with sambar & coconut chutney",      "Lunch": "Aloo gobi sabzi, roti & lassi",             "Snack": "Corn chaat",                         "Dinner": "Moong dal soup with multigrain toast"},
        "Sunday":    {"Breakfast": "Whole grain toast with avocado & tomato", "Lunch": "Chole bhature (1 bhatura) with salad",      "Snack": "Yoghurt with honey & granola",       "Dinner": "Kadhi pakora with steamed rice"},
    },
    "Non-Vegetarian": {
        "Monday":    {"Breakfast": "Egg white omelette with multigrain toast",     "Lunch": "Chicken curry with brown rice & salad",         "Snack": "Boiled egg & mixed nuts",          "Dinner": "Grilled fish with steamed vegetables"},
        "Tuesday":   {"Breakfast": "Scrambled eggs with spinach & toast",          "Lunch": "Mutton rogan josh with jeera rice & raita",      "Snack": "Fruit bowl",                       "Dinner": "Chicken soup with multigrain bread"},
        "Wednesday": {"Breakfast": "Chicken keema paratha with yoghurt",           "Lunch": "Fish curry with brown rice & cucumber salad",    "Snack": "Boiled chana & lemon",             "Dinner": "Egg bhurji with roti & stir-fried greens"},
        "Thursday":  {"Breakfast": "Oats with banana & honey",                     "Lunch": "Chicken biryani with raita & papad",             "Snack": "Roasted makhana",                  "Dinner": "Prawn masala with multigrain roti"},
        "Friday":    {"Breakfast": "Banana protein shake & boiled eggs",           "Lunch": "Lamb keema with peas & roti",                   "Snack": "Mixed nuts & dates",               "Dinner": "Grilled chicken with roasted vegetables"},
        "Saturday":  {"Breakfast": "Egg dosa with sambar",                         "Lunch": "Fish tikka with mint chutney & salad",           "Snack": "Yoghurt with honey",               "Dinner": "Chicken shorba (broth) with bread"},
        "Sunday":    {"Breakfast": "Whole wheat pancakes with eggs",               "Lunch": "Chicken handi with naan & salad",                "Snack": "Fruit salad",                      "Dinner": "Tandoori fish with dal & rice"},
    },
    "Vegan": {
        "Monday":    {"Breakfast": "Overnight oats with almond milk & berries",   "Lunch": "Rajma with brown rice & green salad",          "Snack": "Apple slices with almond butter",    "Dinner": "Tofu stir-fry with quinoa & broccoli"},
        "Tuesday":   {"Breakfast": "Banana smoothie with oats & chia seeds",      "Lunch": "Chole (chickpea curry) with roti & salad",     "Snack": "Mixed nuts & raisins",               "Dinner": "Vegetable soup with lentil bread"},
        "Wednesday": {"Breakfast": "Avocado toast on whole grain bread",           "Lunch": "Lentil dal with brown rice & steamed greens",  "Snack": "Roasted chickpeas",                  "Dinner": "Quinoa vegetable khichdi"},
        "Thursday":  {"Breakfast": "Fruit & nut granola with coconut milk",        "Lunch": "Tofu scramble with multigrain roti & salad",   "Snack": "Watermelon slices",                  "Dinner": "Spicy black bean tacos with salsa"},
        "Friday":    {"Breakfast": "Green smoothie (spinach, banana, flaxseed)",   "Lunch": "Mushroom & pea curry with jeera rice",         "Snack": "Edamame & lemon",                    "Dinner": "Baked sweet potato with chickpea filling"},
        "Saturday":  {"Breakfast": "Idli with coconut chutney (no ghee)",          "Lunch": "Kadala curry with appam",                      "Snack": "Fresh fruit chaat",                  "Dinner": "Vegetable biryani with onion raita (vegan)"},
        "Sunday":    {"Breakfast": "Peanut butter on whole wheat toast & banana",  "Lunch": "Tempeh curry with brown rice & sautéed kale",  "Snack": "Mixed seeds & dried fruit",          "Dinner": "Lentil soup with crusty bread"},
    },
    "Eggetarian": {
        "Monday":    {"Breakfast": "Masala egg omelette with multigrain toast",    "Lunch": "Paneer curry with roti & cucumber salad",      "Snack": "Boiled egg & fruit bowl",            "Dinner": "Egg fried rice (minimal oil) & salad"},
        "Tuesday":   {"Breakfast": "Poha with boiled egg on the side",             "Lunch": "Dal, rice & stir-fried vegetables",            "Snack": "Mixed nuts & banana",                "Dinner": "Egg curry with multigrain roti"},
        "Wednesday": {"Breakfast": "Banana oat smoothie with a boiled egg",        "Lunch": "Rajma with jeera rice & raita",                "Snack": "Apple & peanut butter",              "Dinner": "Shakshuka (eggs in tomato sauce) with bread"},
        "Thursday":  {"Breakfast": "Egg paratha with yoghurt & mint chutney",      "Lunch": "Aloo matar with chapati & dal soup",           "Snack": "Roasted makhana",                    "Dinner": "Paneer bhurji with multigrain roti & salad"},
        "Friday":    {"Breakfast": "Scrambled eggs with sautéed mushrooms & toast","Lunch": "Chana masala with brown rice & papad",         "Snack": "Yoghurt with honey & granola",       "Dinner": "Egg dosa with sambar & coconut chutney"},
        "Saturday":  {"Breakfast": "French toast with seasonal fruits",             "Lunch": "Palak paneer with roti & boondi raita",        "Snack": "Corn chaat with lemon",              "Dinner": "Egg soup with multigrain bread"},
        "Sunday":    {"Breakfast": "Whole grain pancakes with eggs & maple syrup", "Lunch": "Matar paneer with jeera rice & salad",         "Snack": "Mixed fruit bowl",                   "Dinner": "Dal makhani with egg & steamed rice"},
    },
}

# Goal-based substitutions overlay (applied on top of base plan)
GOAL_NOTES = {
    "Muscle & Strength Support": "💪 High-protein focus: add an extra serving of legumes, eggs, or paneer at each meal.",
    "Balanced Nutrition"       : "🥗 Balanced macros: ensure your plate is ½ vegetables, ¼ protein, ¼ whole grains.",
    "Healthy Lifestyle"        : "🌿 Whole foods emphasis: minimize processed foods and added sugars.",
    "General Fitness"          : "🏃 Moderate calories: stay active and drink plenty of water between meals.",
}

# Foods to exclude per allergy keyword
ALLERGY_EXCLUSION = {
    "Nuts"   : ["nuts", "peanut", "almond", "cashew", "pistachio", "walnut", "makhana"],
    "Dairy"  : ["paneer", "yoghurt", "raita", "lassi", "butter", "ghee", "milk", "cheese", "buttermilk", "chaas"],
    "Gluten" : ["roti", "bread", "toast", "chapati", "naan", "paratha", "upma", "poha", "semolina", "wheat"],
    "Soy"    : ["tofu", "soy", "edamame", "tempeh"],
    "Eggs"   : ["egg", "omelette", "scrambled", "boiled egg", "egg white", "french toast"],
}

# Fallback substitutes when a meal is flagged
ALLERGY_FALLBACK = {
    "Nuts"   : "Sunflower seeds & fruit bowl",
    "Dairy"  : "Coconut yoghurt or soy-based alternative",
    "Gluten" : "Rice cakes or jowar roti",
    "Soy"    : "Lentil-based alternative",
    "Eggs"   : "Besan chilla (chickpea flour pancake)",
}

def meal_contains_allergen(meal_text: str, allergies: list[str]) -> bool:
    """Return True if meal text contains any allergen keyword."""
    text_lower = meal_text.lower()
    for allergy in allergies:
        for keyword in ALLERGY_EXCLUSION.get(allergy, []):
            if keyword in text_lower:
                return True
    return False

def safe_meal(meal_text: str, allergies: list[str]) -> str:
    """Return meal text or a safe substitute if an allergen is detected."""
    if not allergies:
        return meal_text
    if meal_contains_allergen(meal_text, allergies):
        subs = [ALLERGY_FALLBACK[a] for a in allergies if meal_contains_allergen(meal_text, [a])]
        return f"{meal_text} ⚠️ *Allergy detected — suggested substitute: {' / '.join(subs)}*"
    return meal_text

def generate_meal_plan(diet_type: str, allergies: list[str], goal: str) -> dict:
    """Return a 7-day meal plan dict filtered for allergies."""
    base = MEAL_PLANS.get(diet_type, MEAL_PLANS["Vegetarian"])
    result = {}
    for day in DAYS:
        result[day] = {
            meal_type: safe_meal(meal_text, allergies)
            for meal_type, meal_text in base[day].items()
        }
    return result

# ═══════════════════════════════════════════════════════════════════════════════
# AI MEAL PLAN (Gemini) — optional
# ═══════════════════════════════════════════════════════════════════════════════

def generate_ai_meal_plan(profile: dict) -> dict | None:
    """
    Try to generate a 7-day meal plan via Gemini API.
    Returns parsed dict or None on failure.
    """
    if not GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
You are a certified nutritionist. Create a 7-day personalized meal plan.

User profile:
- Age: {profile['age']} years
- Height: {profile['height']} cm, Weight: {profile['weight']} kg, BMI: {profile['bmi']} ({profile['bmi_category']})
- Activity Level: {profile['activity']}
- Dietary Preference: {profile['diet_type']}
- Wellness Goal: {profile['goal']}
- Food Allergies/Restrictions: {', '.join(profile['allergies']) if profile['allergies'] else 'None'}

Return ONLY a Python dictionary (valid JSON) in this exact format:
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
- Strictly respect dietary preference ({profile['diet_type']})
- Exclude allergens: {', '.join(profile['allergies']) if profile['allergies'] else 'none'}
- Vary meals — do not repeat the same dish in a week
- Align with goal: {profile['goal']}
- Keep meals practical and healthy
- Return ONLY the JSON, no explanation
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Extract JSON block
        import json, re
        match = re.search(r'\{[\s\S]+\}', text)
        if match:
            return json.loads(match.group())
    except Exception as e:
        return None
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# DOWNLOAD HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def meal_plan_to_txt(meal_plan: dict, profile: dict) -> str:
    """Convert meal plan dict to a nicely formatted text string."""
    lines = [
        "=" * 52,
        "          🥗  AI DIET PLANNER — 7-DAY MEAL PLAN",
        "=" * 52,
        f"  Diet Type   : {profile.get('diet_type', 'N/A')}",
        f"  Goal        : {profile.get('goal', 'N/A')}",
        f"  Restrictions: {', '.join(profile.get('allergies', [])) or 'None'}",
        f"  Generated   : {datetime.date.today().strftime('%d %B %Y')}",
        "=" * 52,
        "",
    ]
    for day, meals in meal_plan.items():
        lines.append(f"  📅 {day.upper()}")
        lines.append("  " + "-" * 48)
        for meal_type, meal_text in meals.items():
            # Strip any allergy warning markup for clean text
            clean = meal_text.split("⚠️")[0].strip()
            lines.append(f"  {meal_type:<12}: {clean}")
        lines.append("")
    lines += [
        "─" * 52,
        "  ⚠️  DISCLAIMER",
        "  This plan is for general wellness information only.",
        "  Consult a registered dietitian or healthcare",
        "  professional before making dietary changes.",
        "─" * 52,
    ]
    return "\n".join(lines)

def meal_plan_to_csv(meal_plan: dict) -> str:
    """Convert meal plan dict to CSV."""
    rows = []
    for day, meals in meal_plan.items():
        for meal_type, meal_text in meals.items():
            clean = meal_text.split("⚠️")[0].strip()
            rows.append({"Day": day, "Meal": meal_type, "Food": clean})
    return pd.DataFrame(rows).to_csv(index=False)

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def render_header():
    st.markdown("""
    <div class="app-header">
        <h1>🥗 AI Diet Planner</h1>
        <p>Personalized nutrition and healthy lifestyle planning</p>
    </div>
    """, unsafe_allow_html=True)

def render_profile_tab():
    """Tab 1: User Profile + BMI Calculator."""
    col_form, col_summary = st.columns([1, 1], gap="large")

    # ── Profile Form ──────────────────────────────────────────────────────────
    with col_form:
        st.markdown('<div class="section-title">👤 Your Profile</div>', unsafe_allow_html=True)

        with st.form("profile_form", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                height = st.number_input(
                    "Height (cm)", min_value=80.0, max_value=250.0,
                    value=float(st.session_state["height"]),
                    step=0.5, format="%.1f",
                    help="Your height in centimetres"
                )
                weight = st.number_input(
                    "Weight (kg)", min_value=20.0, max_value=300.0,
                    value=float(st.session_state["weight"]),
                    step=0.5, format="%.1f",
                    help="Your current weight in kilograms"
                )
            with c2:
                age = st.number_input(
                    "Age (years)", min_value=10, max_value=100,
                    value=int(st.session_state["age"]),
                    step=1,
                    help="Your age in years"
                )
                gender = st.selectbox(
                    "Gender",
                    ["Male", "Female", "Other"],
                    index=["Male", "Female", "Other"].index(st.session_state["gender"]),
                )

            activity = st.selectbox(
                "Activity Level",
                ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"],
                index=["Sedentary", "Lightly Active", "Moderately Active", "Very Active"].index(
                    st.session_state["activity"]
                ),
                help="How active are you on a typical day?"
            )

            diet_type = st.selectbox(
                "Dietary Preference",
                ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"],
                index=["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"].index(
                    st.session_state["diet_type"]
                ),
            )

            goal = st.selectbox(
                "Wellness Goal",
                ["Balanced Nutrition", "Muscle & Strength Support", "Healthy Lifestyle", "General Fitness"],
                index=["Balanced Nutrition", "Muscle & Strength Support", "Healthy Lifestyle", "General Fitness"].index(
                    st.session_state["goal"]
                ),
            )

            allergies = st.multiselect(
                "Food Restrictions / Allergies",
                ["Nuts", "Dairy", "Gluten", "Soy", "Eggs"],
                default=st.session_state["allergies"],
                help="Select any foods you need to avoid"
            )

            submitted = st.form_submit_button("💾 Save Profile & Calculate BMI", use_container_width=True, type="primary")

        if submitted:
            # Validate
            errors = []
            if height < 80 or height > 250:
                errors.append("Please enter a valid height (80–250 cm).")
            if weight < 20 or weight > 300:
                errors.append("Please enter a valid weight (20–300 kg).")
            if age < 10 or age > 100:
                errors.append("Please enter a valid age (10–100 years).")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                bmi      = calculate_bmi(weight, height)
                category = get_bmi_category(bmi)

                # ── Save to session state (the critical fix) ──
                st.session_state["height"]       = height
                st.session_state["weight"]       = weight
                st.session_state["age"]          = age
                st.session_state["gender"]       = gender
                st.session_state["activity"]     = activity
                st.session_state["diet_type"]    = diet_type
                st.session_state["goal"]         = goal
                st.session_state["allergies"]    = allergies
                st.session_state["bmi"]          = bmi
                st.session_state["bmi_category"] = category
                st.session_state["profile_saved"] = True

                # Pre-generate meal plan
                st.session_state["meal_plan"] = generate_meal_plan(diet_type, allergies, goal)
                st.session_state["ai_used"]   = False

                # Try AI upgrade if available
                if GEMINI_API_KEY:
                    with st.spinner("🤖 Generating AI-personalised meal plan…"):
                        ai_plan = generate_ai_meal_plan({
                            "age": age, "height": height, "weight": weight,
                            "bmi": bmi, "bmi_category": category,
                            "activity": activity, "diet_type": diet_type,
                            "goal": goal, "allergies": allergies
                        })
                        if ai_plan:
                            st.session_state["meal_plan"] = ai_plan
                            st.session_state["ai_used"]   = True

                st.success("✅ Profile saved! Navigate to Meal Plan or Nutrition tabs.")

    # ── BMI + Summary ─────────────────────────────────────────────────────────
    with col_summary:
        if st.session_state["profile_saved"] and st.session_state["bmi"] > 0:
            bmi      = st.session_state["bmi"]
            category = st.session_state["bmi_category"]
            color    = bmi_color(category)

            # BMI Card
            st.markdown(f"""
            <div class="bmi-card" style="border-top: 5px solid {color};">
                <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.1em;color:#9ca3af;font-weight:600;">YOUR BMI</div>
                <div class="bmi-value" style="color:{color};">{bmi}</div>
                <div class="bmi-category" style="color:{color};">{category}</div>
                <hr style="border:none;border-top:1px solid #e5e7eb;margin:1rem 0;">
                <div style="font-size:0.75rem;color:#9ca3af;">
                    BMI is a general screening measure and does not replace professional medical assessment.
                </div>
            </div>
            """, unsafe_allow_html=True)

            # BMI gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=bmi,
                number={"suffix": "", "font": {"size": 24}},
                gauge={
                    "axis": {"range": [10, 40], "tickwidth": 1, "tickcolor": "#374151"},
                    "bar": {"color": color, "thickness": 0.3},
                    "bgcolor": "white",
                    "steps": [
                        {"range": [10, 18.5], "color": "#dbeafe"},
                        {"range": [18.5, 25],  "color": "#d1fae5"},
                        {"range": [25, 30],    "color": "#fef3c7"},
                        {"range": [30, 40],    "color": "#fee2e2"},
                    ],
                    "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": bmi},
                },
                domain={"x": [0, 1], "y": [0, 1]},
            ))
            fig.update_layout(
                height=200, margin=dict(l=20, r=20, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)", font={"family": "Inter"},
            )
            st.plotly_chart(fig, use_container_width=True)

            # Profile summary grid
            st.markdown('<div class="section-title">📋 Profile Summary</div>', unsafe_allow_html=True)
            ss = st.session_state
            items = [
                ("📏 Height",   f"{ss['height']} cm"),
                ("⚖️ Weight",   f"{ss['weight']} kg"),
                ("🎂 Age",      f"{ss['age']} yrs"),
                ("⚡ Activity", ss['activity']),
                ("🥗 Diet",     ss['diet_type']),
                ("🎯 Goal",     ss['goal']),
            ]
            cols = st.columns(3)
            for i, (label, val) in enumerate(items):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="profile-item">
                        <div class="pi-label">{label}</div>
                        <div class="pi-value">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

            if ss["allergies"]:
                st.markdown(f"""
                <div class="disclaimer">
                    ⚠️ <strong>Restrictions noted:</strong> {', '.join(ss['allergies'])} — meal suggestions adjusted accordingly.
                    Please consult a healthcare professional for personalised medical advice.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:3rem 2rem;background:white;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,0.07);">
                <div style="font-size:3rem;">📝</div>
                <div style="font-size:1.1rem;font-weight:600;color:#374151;margin:1rem 0 0.5rem;">Profile Not Completed</div>
                <div style="color:#9ca3af;font-size:0.9rem;">Fill in the form on the left and click <strong>Save Profile</strong> to get started.</div>
            </div>
            """, unsafe_allow_html=True)


def render_meal_plan_tab():
    """Tab 2: 7-Day Personalised Meal Plan."""
    is_valid, missing = validate_profile()

    if not is_valid:
        st.warning(f"⚠️ Please complete your profile first. Missing: {', '.join(missing)}")
        st.info("👈 Go to the **Profile** tab, fill in your details, and click **Save Profile**.")
        return

    ss = st.session_state
    meal_plan = ss.get("meal_plan", {})

    # Header row
    col_title, col_badge = st.columns([3, 1])
    with col_title:
        st.markdown('<div class="section-title">📋 Your 7-Day Personalised Meal Plan</div>', unsafe_allow_html=True)
    with col_badge:
        badge = '<span class="badge-ai">🤖 AI-Generated</span>' if ss.get("ai_used") else '<span class="badge-rule">📊 Rule-Based Plan</span>'
        st.markdown(f"<div style='text-align:right;margin-top:1.6rem;'>{badge}</div>", unsafe_allow_html=True)

    # Goal note
    note = GOAL_NOTES.get(ss["goal"], "")
    if note:
        st.markdown(f'<div class="disclaimer">{note}</div>', unsafe_allow_html=True)

    if not meal_plan:
        st.error("Meal plan could not be generated. Please re-save your profile.")
        return

    # Display 7 days
    for day in DAYS:
        day_meals = meal_plan.get(day, {})
        st.markdown(f"""
        <div class="day-card">
            <div class="day-header">📅 {day}</div>
            <div class="meal-row"><span class="meal-type">🌅 Breakfast</span><span class="meal-name">{day_meals.get('Breakfast','—')}</span></div>
            <div class="meal-row"><span class="meal-type">☀️ Lunch</span><span class="meal-name">{day_meals.get('Lunch','—')}</span></div>
            <div class="meal-row"><span class="meal-type">🍎 Snack</span><span class="meal-name">{day_meals.get('Snack','—')}</span></div>
            <div class="meal-row"><span class="meal-type">🌙 Dinner</span><span class="meal-name">{day_meals.get('Dinner','—')}</span></div>
        </div>
        """, unsafe_allow_html=True)

    # Regenerate
    if GEMINI_API_KEY:
        if st.button("🔄 Regenerate AI Meal Plan", use_container_width=False):
            with st.spinner("🤖 Generating new AI meal plan…"):
                ai_plan = generate_ai_meal_plan({
                    "age": ss["age"], "height": ss["height"], "weight": ss["weight"],
                    "bmi": ss["bmi"], "bmi_category": ss["bmi_category"],
                    "activity": ss["activity"], "diet_type": ss["diet_type"],
                    "goal": ss["goal"], "allergies": ss["allergies"]
                })
                if ai_plan:
                    st.session_state["meal_plan"] = ai_plan
                    st.session_state["ai_used"] = True
                    st.success("✅ New AI meal plan generated!")
                    st.rerun()
                else:
                    st.error("AI generation failed. Showing rule-based plan.")

    # ── Downloads ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">⬇️ Download Your Meal Plan</div>', unsafe_allow_html=True)
    dl_col1, dl_col2 = st.columns(2)

    with dl_col1:
        txt_content = meal_plan_to_txt(meal_plan, {
            "diet_type": ss["diet_type"], "goal": ss["goal"], "allergies": ss["allergies"]
        })
        st.download_button(
            label="📄 Download as TXT",
            data=txt_content,
            file_name=f"meal_plan_{datetime.date.today()}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with dl_col2:
        csv_content = meal_plan_to_csv(meal_plan)
        st.download_button(
            label="📊 Download as CSV",
            data=csv_content,
            file_name=f"meal_plan_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown('<div class="disclaimer">⚠️ This meal plan is for general wellness guidance only. It is not a medical prescription. Please consult a registered dietitian before making significant dietary changes.</div>', unsafe_allow_html=True)


def render_nutrition_tab():
    """Tab 3: Nutrition Dashboard."""
    is_valid, missing = validate_profile()
    if not is_valid:
        st.warning(f"⚠️ Please complete your profile first. Missing: {', '.join(missing)}")
        return

    ss = st.session_state
    st.markdown('<div class="section-title">📊 Nutrition Dashboard</div>', unsafe_allow_html=True)

    # ── Quick stats row ──────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("BMI", f"{ss['bmi']}", ss['bmi_category'])
    with m2:
        st.metric("Diet Type", ss['diet_type'])
    with m3:
        st.metric("Activity", ss['activity'])
    with m4:
        st.metric("Goal", ss['goal'].split()[0] + "…" if len(ss['goal']) > 12 else ss['goal'])

    st.divider()

    # ── General Nutrition Guide ───────────────────────────────────────────────
    st.markdown('<div class="section-title">🥦 General Nutrition Guide</div>', unsafe_allow_html=True)
    st.caption("The following are general healthy eating guidelines — not a personalised medical assessment.")

    # Adjust rough guide by goal
    goal = ss.get("goal", "Balanced Nutrition")
    if goal == "Muscle & Strength Support":
        guides = [("🥩 Protein Sources",   85, "Legumes, paneer, eggs, fish, chicken"),
                  ("🥦 Vegetables",        75, "Leafy greens, cruciferous veg, salads"),
                  ("🍎 Fruits",            60, "Seasonal fruits, berries, citrus"),
                  ("🌾 Whole Grains",      70, "Brown rice, whole wheat, oats, quinoa"),
                  ("🫒 Healthy Fats",      50, "Nuts, seeds, olive oil, avocado")]
    elif goal == "Healthy Lifestyle":
        guides = [("🥩 Protein Sources",   65, "Legumes, paneer, tofu, eggs"),
                  ("🥦 Vegetables",        90, "Aim for 5+ servings per day"),
                  ("🍎 Fruits",            80, "2–3 whole fruits daily"),
                  ("🌾 Whole Grains",      80, "Choose whole over refined always"),
                  ("🫒 Healthy Fats",      60, "Olive oil, nuts, seeds in moderation")]
    else:  # Balanced / General Fitness
        guides = [("🥩 Protein Sources",   70, "Legumes, dairy, eggs, lean meats"),
                  ("🥦 Vegetables",        80, "Half your plate should be vegetables"),
                  ("🍎 Fruits",            70, "2–3 portions of whole fruit daily"),
                  ("🌾 Whole Grains",      75, "Brown rice, oats, whole wheat rotis"),
                  ("🫒 Healthy Fats",      55, "Nuts, seeds, ghee in moderation")]

    for label, pct, tip in guides:
        st.markdown(f'<div class="prog-label">{label} <span style="float:right;color:#9ca3af;">{pct}%</span></div>', unsafe_allow_html=True)
        st.progress(pct / 100)
        st.caption(tip)

    st.divider()

    # ── Macro pie ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🍽️ Estimated Macro Ratio</div>', unsafe_allow_html=True)
    st.caption("Approximate macronutrient distribution for your goal. Actual values depend on specific foods consumed.")

    macro_map = {
        "Balanced Nutrition"       : [40, 30, 30],
        "Muscle & Strength Support": [35, 40, 25],
        "Healthy Lifestyle"        : [45, 25, 30],
        "General Fitness"          : [40, 30, 30],
    }
    macro_vals = macro_map.get(goal, [40, 30, 30])

    fig_pie = go.Figure(go.Pie(
        labels=["Carbohydrates", "Protein", "Healthy Fats"],
        values=macro_vals,
        hole=0.45,
        marker_colors=["#34d399", "#60a5fa", "#fbbf24"],
        textinfo="label+percent",
        textfont_size=13,
    ))
    fig_pie.update_layout(
        height=320, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        font={"family": "Inter"},
    )
    col_pie, col_tips = st.columns([1, 1])
    with col_pie:
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_tips:
        st.markdown("**Nutrition Tips for Your Goal:**")
        tips_map = {
            "Balanced Nutrition":        ["Eat a rainbow of vegetables daily", "Choose whole grains over refined", "Include healthy fats from nuts & seeds", "Stay hydrated throughout the day"],
            "Muscle & Strength Support": ["Prioritise protein at every meal", "Eat within 30 min post-workout", "Don't skip carbs — they fuel your training", "Legumes + grains = complete plant protein"],
            "Healthy Lifestyle":         ["Minimise ultra-processed foods", "Cook at home when possible", "Eat slowly and mindfully", "Include fibre-rich foods every day"],
            "General Fitness":           ["Match food intake to activity level", "Hydrate well before & after exercise", "Include variety to cover all micronutrients", "Avoid skipping meals"],
        }
        for tip in tips_map.get(goal, []):
            st.markdown(f"✅ {tip}")

    st.markdown('<div class="disclaimer">⚠️ These ratios are general wellness guidelines, not a medically prescribed diet plan. Consult a registered dietitian for personalised advice.</div>', unsafe_allow_html=True)


def render_hydration_tab():
    """Tab 4: Water Intake Tracker."""
    st.markdown('<div class="section-title">💧 Hydration Tracker</div>', unsafe_allow_html=True)
    st.caption("Hydration needs vary by individual, activity level, climate, and health conditions.")

    water = st.session_state.get("water", 0.0)

    col_display, col_controls = st.columns([1, 1], gap="large")

    with col_display:
        # Visual water display
        pct = min(water / 3.0, 1.0)
        level_color = "#3b82f6" if pct >= 0.6 else "#f59e0b" if pct >= 0.3 else "#ef4444"
        status_text = "Great hydration! 💪" if pct >= 0.8 else "Keep drinking! 👍" if pct >= 0.5 else "Drink more water ⚠️"

        st.markdown(f"""
        <div style="background:white;border-radius:16px;padding:2rem;box-shadow:0 2px 12px rgba(0,0,0,0.07);text-align:center;">
            <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;color:#9ca3af;font-weight:600;">TODAY'S INTAKE</div>
            <div style="font-size:4rem;font-weight:800;color:{level_color};margin:0.5rem 0;">{water:.1f} L</div>
            <div style="font-size:0.95rem;color:#374151;">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)

        # Progress bar
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="prog-label">Progress toward ~3L daily reference <span style="float:right;">{pct*100:.0f}%</span></div>', unsafe_allow_html=True)
        st.progress(pct)
        st.caption("Note: The 3L reference is a general estimate. Your actual needs may differ.")

    with col_controls:
        st.markdown("**Log Water Intake**")
        preset_col1, preset_col2 = st.columns(2)
        with preset_col1:
            if st.button("+ 250 ml\n(1 glass)", use_container_width=True):
                st.session_state["water"] = round(water + 0.25, 2)
                st.rerun()
            if st.button("+ 500 ml\n(large glass)", use_container_width=True):
                st.session_state["water"] = round(water + 0.50, 2)
                st.rerun()
        with preset_col2:
            if st.button("+ 750 ml\n(bottle)", use_container_width=True):
                st.session_state["water"] = round(water + 0.75, 2)
                st.rerun()
            if st.button("+ 1.0 L\n(big bottle)", use_container_width=True):
                st.session_state["water"] = round(water + 1.00, 2)
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        custom_amount = st.number_input("Custom amount (litres)", min_value=0.0, max_value=5.0, value=0.25, step=0.25, format="%.2f")
        if st.button("➕ Add Custom Amount", use_container_width=True, type="primary"):
            st.session_state["water"] = round(water + custom_amount, 2)
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Reset Today's Count", use_container_width=True):
            st.session_state["water"] = 0.0
            st.rerun()

    # Tips
    st.divider()
    st.markdown("**💡 Hydration Tips**")
    tip_cols = st.columns(3)
    tips = [
        ("🌅 Morning", "Start your day with a glass of water before tea or coffee."),
        ("🍽️ Meals", "Drink a glass of water 30 min before each meal."),
        ("🏃 Exercise", "Drink 200–300 ml of water for every 30 min of activity."),
    ]
    for col, (title, body) in zip(tip_cols, tips):
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:1rem;box-shadow:0 1px 6px rgba(0,0,0,0.06);">
                <div style="font-weight:700;color:#1b4332;margin-bottom:0.3rem;">{title}</div>
                <div style="font-size:0.85rem;color:#6b7280;">{body}</div>
            </div>
            """, unsafe_allow_html=True)


def render_progress_tab():
    """Tab 5: Weight Progress Tracker."""
    st.markdown('<div class="section-title">📈 Weight Progress Tracker</div>', unsafe_allow_html=True)
    st.caption("Track your weight trend over time. This is a general wellness tool, not a medical monitoring system.")

    weight_history = st.session_state.get("weight_history", [])

    col_input, col_chart = st.columns([1, 2], gap="large")

    with col_input:
        st.markdown("**Log Today's Weight**")
        log_date   = st.date_input("Date", value=datetime.date.today())
        log_weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0,
                                     value=float(st.session_state.get("weight", 70.0)),
                                     step=0.1, format="%.1f")
        note = st.text_input("Note (optional)", placeholder="e.g. After workout, Morning")

        if st.button("➕ Log Entry", type="primary", use_container_width=True):
            new_entry = {
                "date"  : str(log_date),
                "weight": log_weight,
                "note"  : note,
            }
            # Check for duplicate date
            existing_dates = [e["date"] for e in weight_history]
            if str(log_date) in existing_dates:
                # Update existing
                for e in weight_history:
                    if e["date"] == str(log_date):
                        e["weight"] = log_weight
                        e["note"]   = note
                st.success("✅ Entry updated for this date.")
            else:
                weight_history.append(new_entry)
                st.success("✅ Weight logged successfully!")
            st.session_state["weight_history"] = weight_history
            st.rerun()

        if weight_history:
            st.divider()
            st.markdown("**Weight History**")
            df = pd.DataFrame(weight_history).sort_values("date")
            df_display = df[["date", "weight", "note"]].rename(columns={"date": "Date", "weight": "Weight (kg)", "note": "Note"})
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            if st.button("🗑️ Clear All Entries", use_container_width=True):
                st.session_state["weight_history"] = []
                st.rerun()

    with col_chart:
        if len(weight_history) < 1:
            st.markdown("""
            <div style="text-align:center;padding:4rem 2rem;background:white;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,0.07);">
                <div style="font-size:3rem;">📈</div>
                <div style="font-size:1rem;font-weight:600;color:#374151;margin:1rem 0 0.5rem;">No Data Yet</div>
                <div style="color:#9ca3af;font-size:0.9rem;">Log at least one weight entry to see your trend chart.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            df = pd.DataFrame(weight_history).sort_values("date")
            df["date"]   = pd.to_datetime(df["date"])
            df["weight"] = pd.to_numeric(df["weight"])

            first_w = df["weight"].iloc[0]
            last_w  = df["weight"].iloc[-1]
            delta   = round(last_w - first_w, 1)
            delta_str = f"+{delta}" if delta >= 0 else str(delta)

            # Stats
            s1, s2, s3 = st.columns(3)
            s1.metric("Current Weight", f"{last_w} kg", delta_str + " kg from start")
            s2.metric("Lowest Logged",  f"{df['weight'].min()} kg")
            s3.metric("Entries",        len(df))

            # Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["date"], y=df["weight"],
                mode="lines+markers",
                name="Weight",
                line=dict(color="#40916c", width=2.5, shape="spline"),
                marker=dict(size=8, color="#40916c", line=dict(width=2, color="white")),
                fill="tozeroy",
                fillcolor="rgba(64, 145, 108, 0.08)",
                text=df.get("note", ""),
                hovertemplate="<b>%{x|%d %b %Y}</b><br>Weight: %{y} kg<br>Note: %{text}<extra></extra>",
            ))
            fig.update_layout(
                title={"text": "Weight Trend", "font": {"size": 16, "family": "Inter"}, "x": 0},
                xaxis_title="Date", yaxis_title="Weight (kg)",
                height=380,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"family": "Inter"},
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=True, gridcolor="#f3f4f6", zeroline=False),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="disclaimer">⚠️ Healthy weight change is gradual. Avoid rapid weight loss. This tool tracks trends only — it is not a medical monitoring system.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    render_header()

    # Quick-access banner when profile is saved
    if st.session_state["profile_saved"]:
        ss = st.session_state
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:0.8rem 1.5rem;margin-bottom:1rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);display:flex;gap:2rem;flex-wrap:wrap;align-items:center;">
            <span style="font-weight:700;color:#1b4332;">👤 {ss['gender']}, {ss['age']} yrs</span>
            <span>⚖️ {ss['weight']} kg</span>
            <span>📏 {ss['height']} cm</span>
            <span>🔢 BMI <strong>{ss['bmi']}</strong> ({ss['bmi_category']})</span>
            <span>🥗 {ss['diet_type']}</span>
            <span>🎯 {ss['goal']}</span>
        </div>
        """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Profile",
        "📋 Meal Plan",
        "📊 Nutrition",
        "💧 Hydration",
        "📈 Progress",
    ])

    with tab1:
        render_profile_tab()

    with tab2:
        render_meal_plan_tab()

    with tab3:
        render_nutrition_tab()

    with tab4:
        render_hydration_tab()

    with tab5:
        render_progress_tab()


if __name__ == "__main__":
    main()
