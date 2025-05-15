import streamlit as st
import pandas as pd
import time

# Set page config
st.set_page_config(page_title="AI-Urban Planning and Design", page_icon="🏠", layout="wide")
st.markdown("""
    <style>
    /* Apply black border to chatbox */
    .stTextInput > div > div > input {
        border: 3px solid black !important; /* Black border by default */
        padding: 8px; /* Spacing inside box */
        border-radius: 5px; /* Smooth edges */
        color: black !important; /* Black text */
        background-color: white !important; /* White background */
    }

    /* When focused, change border to red */
    .stTextInput > div > div > input:focus {
        border: 3px solid red !important; /* Changes to red when typing */
        outline: none !important; /* Removes unwanted outline */
    }
    </style>
""", unsafe_allow_html=True)

# Load zoning rules from CSV file
@st.cache_data
def load_zoning_rules():
    try:
        return pd.read_csv("zoning_data.csv")  # Ensure the file exists
    except FileNotFoundError:
        st.error("⚠️ Zoning rules data file not found.")
        return pd.DataFrame(columns=["land_type", "max_height", "pop_density_limit", "near_main_road", "setback_min", "floor_area_ratio"])

rules_df = load_zoning_rules()

# Page header
st.title("🌆 AI-Urban Planning and Design")
st.write("Check zoning feasibility and compliance based on zoning regulations.")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About Zoning Advisor")
    st.write("This tool helps developers and planners check zoning compliance.")
    st.subheader("📜 Zoning Rules Reference")
    st.dataframe(rules_df)

# Main form
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

if submit_button:
    if land_type not in rules_df["land_type"].values:
        st.error(f"❌ No zoning rules found for land type: {land_type}")
        st.stop()

    selected_rule = rules_df[rules_df["land_type"] == land_type].iloc[0]

    violations, compliances = [], []
    
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
    elapsed_time = round(time.time() - time.time(), 2)

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

st.header("🤖 AI Zoning Chatbot")

# Initialize chat history if not present
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display previous messages
for message in st.session_state.chat_history:
    st.write(message)

# Chat input with dynamic key to prevent duplicate keys when reloading
user_query = st.text_input("Ask about zoning rules, compliance, restrictions...", key=str(len(st.session_state.chat_history)))

# Predefined responses
responses = {
    "height limit": "🚧 The maximum building height allowed varies by zone.",
    "population density": "🏙️ Population density limits help prevent overcrowding.",
    "FAR": "📐 Floor Area Ratio defines the relationship between building size and land area.",
    "setback": "🏠 Setbacks ensure buildings maintain proper distance from roads and neighboring properties.",
}

# Handle user input
if st.button("Submit"):
    if user_query.lower() in responses:
        response = responses[user_query.lower()]
    else:
        response = "🤔 I can help with zoning regulations, setbacks, FAR, and population density!"

    # Append AI response to chat history
    st.session_state.chat_history.append(f"**You:** {user_query}")
    st.session_state.chat_history.append(f"**Bot:** {response}")

    # Refresh UI to display updated chat history
    st.rerun()
# Predefined responses
responses = {
    "Height Limit": "🚧 The maximum building height allowed varies by zone.",
    "Population Density": "🏙️ Population density limits help prevent overcrowding.",
    "FAR": "📐 Floor Area Ratio defines the relationship between building size and land area.",
    "Setback": "🏠 Setbacks ensure buildings maintain proper distance from roads and neighboring properties.",
    "Exit": "👋 Goodbye! Chat session has ended."
}

# UI for selecting predefined queries
st.title("Zoning Regulations Assistant")
st.write("Select a topic to get more details:")

question = st.selectbox("Choose a question:", list(responses.keys()))

# Display response without linking to chat history
if question:
    st.write(f"**Bot:** {responses.get(question, '🤔 I can help with zoning regulations, setbacks, FAR, and population density!')}")

    # Stop execution if exit is chosen
    if question == "Exit":
        st.stop()
    
st.markdown("---")
st.info("Note: This AI chatbot is a prototype. Customize further to fit your needs.")