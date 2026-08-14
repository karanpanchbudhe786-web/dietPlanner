# 🥗 AI Diet Planner

A complete personal nutrition planning dashboard built with **Python + Streamlit**.

## Features

- 🏠 **Profile** — BMI calculator, activity level, dietary preference, goals, allergy restrictions
- 📋 **7-Day Meal Plan** — Personalized plans for Vegetarian, Non-Vegetarian, Vegan, Eggetarian
- 📊 **Nutrition Dashboard** — Macro breakdown, nutrition guide, goal-tailored tips
- 💧 **Hydration Tracker** — Daily water intake tracker
- 📈 **Progress Tracker** — Weight trend chart over time
- ⬇️ **Download** — Export meal plan as TXT or CSV

## Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/karanpanchbudhe786-web/dietPlanner.git
cd dietPlanner

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select this repo → set main file to `app.py`
4. Click **Deploy**

## Optional: AI Meal Generation (Gemini)

To enable AI-powered meal plans, add your Gemini API key:

**Locally:**
```bash
set GEMINI_API_KEY=your_key_here   # Windows
export GEMINI_API_KEY=your_key_here  # Mac/Linux
```

**Streamlit Cloud:**
- Go to App Settings → Secrets
- Add: `GEMINI_API_KEY = "your_key_here"`

## Tech Stack

- Python 3.9+
- Streamlit 1.32+
- Plotly
- Pandas
