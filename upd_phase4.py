import streamlit as st
import pandas as pd
import time

# Set page config
st.set_page_config(page_title="AI-Powered Zoning Advisor", page_icon="🌇️", layout="wide")

# Load zoning rules from CSV file
@st.cache_data
def load_zoning_rules():
    try:
        return pd.read_csv("zoning_data.csv")  # Change filename here
    except FileNotFoundError:
        st.error("Zoning rules data file not found.")
        return pd.DataFrame(columns=["land_type", "max_height", "pop_density_limit", "near_main_road", "setback_min", "floor_area_ratio"])


rules_df = load_zoning_rules()
start_time = time.time()

# Page header
st.title("AI-Powered Zoning Advisor")
st.write("Check zoning feasibility and compliance based on zoning regulations.")

# Sidebar
with st.sidebar:
    st.header("About Zoning Advisor")
    st.write("This tool helps developers and planners check zoning compliance.")
    st.subheader("Zoning Rules Reference")
    st.dataframe(rules_df)

# Main form
with st.form("zoning_form"):
    st.header("Enter Development Details")
    
    col1, col2 = st.columns(2)
    with col1:
        land_type = st.selectbox("Select Land Type", rules_df["land_type"].unique())
        height = st.number_input("Building Height (meters)", min_value=0.0, value=10.0, step=0.5)
        population_density = st.number_input("Population Density (per km²)", min_value=0, value=100)
    with col2:
        near_main_road = st.radio("Near Main Road?", ["yes", "no"])
        setback = st.number_input("Setback Distance (meters)", min_value=0.0, value=3.0, step=0.5)
        floor_area_ratio = st.number_input("Floor Area Ratio (FAR)", min_value=0.0, value=1.0, step=0.1)

    submit_button = st.form_submit_button("Check Compliance")

if submit_button:
    if land_type not in rules_df["land_type"].values:
        st.error(f"No zoning rules found for land type: {land_type}")
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
    elapsed_time = round(time.time() - start_time, 2)

    st.header("Zoning Analysis Results")
    st.metric("Compliance Score", f"{compliance_percentage:.1f}%")
    st.metric("Processing Time", f"{elapsed_time} sec")

    if not violations:
        st.success("✅ This plan complies with all zoning regulations.")
    else:
        st.error(f"⚠️ Found {len(violations)} compliance issues.")

    with st.expander("Zoning Violations", expanded=True):
        for v in violations:
            st.write(v)

    with st.expander("Compliance Checks", expanded=not violations):
        for c in compliances:
            st.write(c)

    if violations:
        st.subheader("Recommendations")
        for v in violations:
            if "Height" in v:
                st.write(f"- Reduce height to {selected_rule['max_height']}m or apply for variance.")
            elif "Density" in v:
                st.write("- Reduce population or adjust property size.")
            elif "Proximity" in v:
                st.write("- Consider alternative location.")
            elif "Setback" in v:
                st.write(f"- Increase setback to at least {selected_rule['setback_min']} meters.")
            elif "FAR" in v:
                st.write(f"- Lower FAR below {selected_rule['floor_area_ratio']}.")

st.markdown("---")
st.info("Note: This result is based on mock zoning rules. For real use, integrate official zoning databases.")
st.caption("\u00a9 2025 AI-Powered Zoning Advisor | Prototype Version")
