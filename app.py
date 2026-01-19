import streamlit as st
import json
import pandas as pd
from backend import map_users_to_houses

WA_TXT_PATH = "_chat.txt"

st.set_page_config(page_title="The Sorting Hack", layout="centered")
st.title("Harry Potter House Mapper")

uploaded_file = st.file_uploader(
    "Upload WhatsApp chat (.txt)",
    type=["txt"]
)

if uploaded_file:
    with open(WA_TXT_PATH, "wb") as f:
        f.write(uploaded_file.read())

    st.success("Chat uploaded")

    with st.spinner("Sorting users into houses..."):
        mapping = map_users_to_houses(WA_TXT_PATH)

    # Convert to table
    rows = []
    for user, data in mapping.items():
        rows.append([user, data["assigned_house"]])

    result_df = pd.DataFrame(
        rows, columns=["User", "Assigned House"]
    )

    st.subheader("🏰 House Assignment")
    st.dataframe(result_df)

    st.subheader("⬇️ Download Results")

    st.download_button(
        "Download JSON",
        json.dumps(mapping, indent=2),
        file_name="house_mapping.json",
        mime="application/json"
    )

    st.download_button(
        "Download CSV",
        result_df.to_csv(index=False),
        file_name="house_mapping.csv",
        mime="text/csv"
    )
