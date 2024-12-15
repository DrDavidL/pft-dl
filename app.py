import streamlit as st
import numpy as np

# Helper function to calculate Lower Limit of Normal (LLN)
def calculate_lln(parameter, age, gender, height, ethnicity):
    # Implement GLI or NHANES equations here
    if ethnicity == "Caucasian":
        adjustment_factor = 1.0
    elif ethnicity == "African American":
        adjustment_factor = 0.88
    elif ethnicity == "Asian":
        adjustment_factor = 0.94
    else:  # Other or unknown ethnicity
        adjustment_factor = 1.0

    # Example LLN calculation using an adjustment factor and height
    lln_value = adjustment_factor * (parameter - (age * 0.02) + (height * 0.05))  # Placeholder formula
    return max(0, lln_value)  # Ensure LLN is non-negative

# NHANES peak flow equation
# Example formula for peak expiratory flow (PEF)
def calculate_pef(age, gender, height):
    if gender == "Male":
        return 187 + (5.48 * height) - (0.034 * age)  # Example equation
    elif gender == "Female":
        return 153 + (4.50 * height) - (0.026 * age)  # Example equation
    else:
        return None  # Unsupported gender for equation

# Helper function to interpret PFT results
def interpret_pft(fev1, fvc, fev1_fvc, age, gender, height, ethnicity, dlco_sb=None, dl_va=None, va_sb=None, ivc_sb=None, bht=None):
    interpretation = []

    # Calculate LLN for FEV1/FVC ratio
    fev1_fvc_lln = calculate_lln(1.0, age, gender, height, ethnicity)

    # Obstructive pattern
    if fev1_fvc < fev1_fvc_lln:
        interpretation.append(f"Obstructive pattern detected (LLN-adjusted cutoff: {fev1_fvc_lln:.2f}).")
        if fev1 >= 70:
            interpretation.append("Severity: Mild obstruction.")
            interpretation.append("Next steps: Consider a short-acting beta-agonist (e.g., albuterol). Reassess if symptoms persist.")
        elif 50 <= fev1 < 70:
            interpretation.append("Severity: Moderate obstruction.")
            interpretation.append("Next steps: Consider adding long-acting bronchodilators (e.g., LABA or LAMA). Evaluate for inhaled corticosteroids if needed.")
        elif fev1 < 50:
            interpretation.append("Severity: Severe obstruction.")
            interpretation.append("Next steps: Refer to a pulmonologist. Consider advanced therapies like combination inhalers or oxygen therapy if indicated.")

    # Restrictive pattern
    if fvc < 80 and fev1_fvc >= fev1_fvc_lln:
        interpretation.append("Restrictive pattern detected.")
        interpretation.append("Next steps: Evaluate for interstitial lung disease, obesity, or neuromuscular disorders. Consider high-resolution CT or referral to a specialist.")
        
    # Mixed pattern
    if fev1_fvc < fev1_fvc_lln and fvc < 80:
        interpretation.append("Mixed obstructive and restrictive pattern detected.")
        interpretation.append("Next steps: Comprehensive workup needed. Evaluate for concurrent obstructive and restrictive conditions. Referral to pulmonology recommended.")

    # DLCO evaluation
    if dlco_sb is not None:
        if dlco_sb < 80:
            interpretation.append("Reduced DLCO_SB: Suggests impaired gas exchange.")
            interpretation.append("Next steps: Investigate causes such as interstitial lung disease, pulmonary hypertension, or emphysema. Consider echocardiography or CT imaging.")
        else:
            interpretation.append("DLCO_SB is within normal limits.")

    if dl_va is not None:
        interpretation.append(f"DL/VA ratio: {dl_va:.2f}. Interpretation depends on clinical context (e.g., lung volume and gas exchange).")

    if va_sb is not None:
        interpretation.append(f"VA_SB: {va_sb:.2f} L. This represents the alveolar volume.")

    if ivc_sb is not None:
        interpretation.append(f"IVC_SB: {ivc_sb:.2f} L. Represents inspiratory capacity during single breath testing.")

    if bht is not None:
        interpretation.append(f"Breath-holding time (BHT): {bht:.2f} seconds. Ensure proper technique during test.")

    if not interpretation:
        interpretation.append("Normal PFT values.")
        interpretation.append("Next steps: No action needed. Encourage routine follow-up if indicated.")

    return interpretation

# Streamlit app
st.title("Pulmonary Function Test (PFT) Interpreter")

# Sidebar for input fields
st.sidebar.header("Patient Demographics")
age = st.sidebar.number_input("Age (years)", min_value=0, max_value=120, step=1, help="Age of the patient in years.")
weight_lbs = st.sidebar.number_input("Weight (lbs)", min_value=0.0, max_value=660.0, step=0.1, help="Weight of the patient in pounds.")
weight_kg = round(weight_lbs * 0.453592, 2)
st.sidebar.write(f"Converted Weight: {weight_kg} kg")

height_inches = st.sidebar.number_input("Height (inches)", min_value=0.0, max_value=100.0, step=0.1, help="Height of the patient in inches.")
height_cm = round(height_inches * 2.54, 2)
st.sidebar.write(f"Converted Height: {height_cm} cm")

gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"], help="Gender of the patient.")
ethnicity = st.sidebar.selectbox("Ethnicity", ["Caucasian", "African American", "Asian", "Other"], help="Ethnicity of the patient, used for adjustments in interpretation.")

# Required inputs
st.sidebar.header("Essential PFT Measurements")
fev1 = st.sidebar.number_input("FEV1 (% predicted)", min_value=0.0, max_value=150.0, step=0.1, help="Forced expiratory volume in 1 second, as a percentage of predicted.")
fvc = st.sidebar.number_input("FVC (% predicted)", min_value=0.0, max_value=150.0, step=0.1, help="Forced vital capacity, as a percentage of predicted.")
fev1_fvc = st.sidebar.number_input("FEV1/FVC ratio (%)", min_value=0.0, max_value=100.0, step=0.1, help="FEV1/FVC ratio, as a percentage.")

# Optional inputs
if st.sidebar.checkbox("Show additional optional inputs"):
    st.sidebar.header("Additional PFT Measurements")
    dlco_sb = st.sidebar.number_input("DLCO_SB (mL/min/mmHg)", min_value=0.0, max_value=150.0, step=0.1, help="Single breath diffusing capacity for carbon monoxide.")
    dl_va = st.sidebar.number_input("DL/VA ratio (mL/min/mmHg/L)", min_value=0.0, max_value=10.0, step=0.1, help="Diffusing capacity normalized to alveolar volume.")
    va_sb = st.sidebar.number_input("VA_SB (L)", min_value=0.0, max_value=10.0, step=0.1, help="Alveolar volume from single breath testing.")
    ivc_sb = st.sidebar.number_input("IVC_SB (L)", min_value=0.0, max_value=10.0, step=0.1, help="Inspiratory capacity during single breath testing.")
    bht = st.sidebar.number_input("BHT (seconds)", min_value=0.0, max_value=60.0, step=0.1, help="Breath-holding time during single breath testing.")
else:
    dlco_sb = None
    dl_va = None
    va_sb = None
    ivc_sb = None
    bht = None

# Main window output
if st.sidebar.button("Interpret Results"):
    results = interpret_pft(fev1, fvc, fev1_fvc / 100, age, gender, height_cm, ethnicity, dlco_sb, dl_va, va_sb, ivc_sb, bht)
    st.header("Results")
    st.write(f"**Patient Details:** Age: {age}, Weight: {weight_kg} kg, Height: {height_cm} cm, Gender: {gender}, Ethnicity: {ethnicity}")
    for line in results:
        st.write(f"- {line}")

# Optional visualization
if st.sidebar.checkbox("Show visual comparison"):
    import matplotlib.pyplot as plt

    predicted = [100, 100, 100]
    observed = [fev1, fvc, fev1_fvc]

    labels = ["FEV1", "FVC", "FEV1/FVC"]

    if dlco_sb is not None:
        predicted.append(100)
        observed.append(dlco_sb)
        labels.append("DLCO_SB")

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar(x - width/2, predicted, width, label="Predicted")
    ax.bar(x + width/2, observed, width, label="Observed")

    ax.set_ylabel("%")
    ax.set_title("PFT Results Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    st.pyplot(fig)

# Optional: Calculate and display PEF
if st.sidebar.checkbox("Show Peak Expiratory Flow (PEF)"):
    pef = calculate_pef(age, gender, height_cm)
    if pef:
        st.write(f"**Estimated Peak Expiratory Flow (PEF):** {pef:.2f} L/min (based on NHANES equations).")
        st.write("**Caveat:** NHANES equations may not fully account for variations across all ethnic groups.")
    else:
        st.write("PEF calculation not available for the selected gender.")
