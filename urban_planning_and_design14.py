import streamlit as st
import pandas as pd
import time

# Set page config
st.set_page_config(page_title="AI-Urban Planning and Design", page_icon="🏠", layout="wide")

# Custom CSS styling for chat input
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        border: 3px solid black !important;
        padding: 8px;
        border-radius: 5px;
        color: black !important;
        background-color: white !important;
    }
    .stTextInput > div > div > input:focus {
        border: 3px solid red !important;
        outline: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Load zoning rules
@st.cache_data
def load_zoning_rules():
    try:
        return pd.read_csv("zoning_data.csv")
    except FileNotFoundError:
        st.error("⚠️ Zoning rules data file not found.")
        return pd.DataFrame(columns=["land_type", "max_height", "pop_density_limit", "near_main_road", "setback_min", "floor_area_ratio"])

rules_df = load_zoning_rules()

# Sidebar
with st.sidebar:
    st.header("ℹ️ About Zoning Advisor")
    st.write("This tool helps developers and planners check zoning compliance.")
    st.subheader("📜 Zoning Rules Reference")
    st.dataframe(rules_df)

# Page header
st.title("🌆 AI-Urban Planning and Design")
st.write("Check zoning feasibility and compliance based on zoning regulations.")

# Form to input development details
with st.form("zoning_form"):
    st.header("🏗️ Enter Development Details")

    col1, col2 = st.columns(2)
    with col1:
        land_type = st.selectbox("Select Land Type", rules_df["land_type"].unique())
        height = st.number_input("Building Height (meters)", min_value=0.0, value=10.0, step=0.5)
        population_density = st.number_input("Population Density (per km²)", min_value=0, value=100)
    with col2:
        near_main_road = st.radio("Near Main Road?", ["yes", "no"])
        setback = st.number_input("Setback Distance (meters)", min_value=0.0, value=3.0, step=0.5)
        floor_area_ratio = st.number_input("Floor Area Ratio (FAR)", min_value=0.0, value=1.0, step=0.1)

    submit_button = st.form_submit_button("✅ Check Compliance")

# Zoning Compliance Logic
if submit_button:
    start_time = time.time()

    if land_type not in rules_df["land_type"].values:
        st.error(f"❌ No zoning rules found for land type: {land_type}")
        st.stop()

    selected_rule = rules_df[rules_df["land_type"] == land_type].iloc[0]
    violations, compliances = [], []

    # Compliance checks
    if height > selected_rule["max_height"]:
        violations.append(f"🚫 Height exceeds {selected_rule['max_height']} meters.")
    else:
        compliances.append(f"✅ Height of {height}m is within the allowed limit.")

    if population_density > selected_rule["pop_density_limit"]:
        violations.append(f"🚫 Density exceeds {selected_rule['pop_density_limit']} per km².")
    else:
        compliances.append(f"✅ Population density of {population_density} per km² is allowed.")

    if near_main_road != selected_rule["near_main_road"]:
        violations.append(f"🚫 Site should be {selected_rule['near_main_road']} to a main road.")
    else:
        compliances.append(f"✅ Proximity to main road is acceptable.")

    if setback < selected_rule["setback_min"]:
        violations.append(f"🚫 Setback is less than {selected_rule['setback_min']} meters.")
    else:
        compliances.append(f"✅ Setback of {setback}m is compliant.")

    if floor_area_ratio > selected_rule["floor_area_ratio"]:
        violations.append(f"🚫 FAR exceeds {selected_rule['floor_area_ratio']}.")
    else:
        compliances.append(f"✅ FAR of {floor_area_ratio} is compliant.")

    compliance_percentage = (len(compliances) / (len(violations) + len(compliances)) * 100) if (violations or compliances) else 0
    elapsed_time = round(time.time() - start_time, 2)

    # Display Results
    st.header("📊 Zoning Analysis Results")
    st.metric("Compliance Score", f"{compliance_percentage:.1f}%")
    st.metric("Processing Time", f"{elapsed_time} sec")

    if not violations:
        st.success("✅ This plan complies with all zoning regulations.")
    else:
        st.error(f"⚠️ Found {len(violations)} compliance issues.")

    with st.expander("🚨 Zoning Violations", expanded=True):
        for v in violations:
            st.write(v)

    with st.expander("✅ Compliance Checks", expanded=not violations):
        for c in compliances:
            st.write(c)

    with st.expander("📋 Rule Used for Evaluation"):
        st.dataframe(selected_rule.to_frame().T)

# --- Chatbot and FAQ Section in Tabs ---
responses = {
    "height limit": "🚧 The maximum building height allowed varies by zone.",
    "population density": "🏙️ Population density limits help prevent overcrowding.",
    "far": "📐 Floor Area Ratio defines the relationship between building size and land area.",
    "setback": "🏠 Setbacks ensure buildings maintain proper distance from roads and neighboring properties.",
    "exit": "👋 Goodbye! Chat session has ended."
}

st.header("🧠 AI Zoning Assistant")

tab1, tab2 = st.tabs(["💬 Chatbot", "📋 FAQ Help"])

with tab1:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        st.write(msg)

    user_query = st.text_input("Ask about zoning rules...", key=str(len(st.session_state.chat_history)))
    
    if st.button("Submit", key="submit_query"):
        query_key = user_query.lower().strip()
        bot_response = responses.get(query_key, "🤖 I can help with zoning regulations like height limits, FAR, setbacks, and density.")
        
        st.session_state.chat_history.append(f"**You:** {user_query}")
        st.session_state.chat_history.append(f"**Bot:** {bot_response}")
        st.rerun()

with tab2:
    st.subheader("📌 Common Questions")
    question = st.selectbox("Choose a topic:", list(responses.keys()))

    if question:
        st.write(f"**Bot:** {responses[question.lower()]}")
        if question.lower() == "exit":
            st.stop()

st.markdown("---")
st.info("Note: This AI assistant is a prototype. Extend it further using NLP or rule explanation systems.")
