import streamlit as st
import pandas as pd

# Load mock zoning rules from CSV file
try:
    rules_df = pd.read_csv("zoning_data.csv")
    rules_df.columns = rules_df.columns.str.strip()  # Remove any extra spaces
except FileNotFoundError:
    st.error("Error: CSV file 's.csv' not found. Ensure it's in the correct directory.")
    st.stop()
except pd.errors.EmptyDataError:
    st.error("Error: CSV file 's.csv' is empty or malformed.")
    st.stop()

# Ensure 'land_type' column exists
if "land_type" not in rules_df.columns:
    st.error("Error: 'land_type' column missing from CSV file.")
    st.stop()

# Page title
st.title("AI-Powered Zoning Advisor")
st.write("Check zoning feasibility and compliance based on basic land parameters.")

# User inputs
land_type = st.selectbox("Select Land Type", rules_df["land_type"].unique())
height = st.number_input("Enter Proposed Building Height (meters)", min_value=1)
population_density = st.number_input("Enter Estimated Population Density (per km²)", min_value=1)
near_main_road = st.radio("Is the site near a main road?", ["yes", "no"])

# Fetch rules for selected land type
selected_rule = rules_df[rules_df["land_type"] == land_type]

if selected_rule.empty:
    st.error(f"No zoning rules found for selected land type: {land_type}")
    st.stop()
else:
    selected_rule = selected_rule.iloc[0]

# Rule checks
violations = []
if height > selected_rule["max_height"]:
    violations.append(f"Height exceeds max limit of {selected_rule['max_height']} meters.")
if population_density > selected_rule["pop_density_limit"]:
    violations.append(f"Population density exceeds the allowed limit of {selected_rule['pop_density_limit']}.")
if near_main_road.lower() != str(selected_rule["near_main_road"]).lower():
    violations.append(f"Proximity to main road does not match zoning requirement ({selected_rule['near_main_road']}).")

# Results
st.subheader("Zoning Analysis Result:")
if not violations:
    st.success("This plan complies with the zoning rules.")
else:
    st.error("Zoning Violations Detected:")
    for v in violations:
        st.write(f"- {v}")

# Legal reference placeholder
st.markdown("---")
st.info("Note: This result is based on mock zoning rules. For real use, connect to official planning data.")
