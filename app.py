import streamlit as st

st.set_page_config(page_title="MEDICAL-PLACEHOLDER")
st.title("MEDICAL BILL AUDITOR PLACEHOLDER")

uploaded_file=st.file_uploader("PLEASE UPLOAD YOUR FILE HERE :",type=["pdf","jpeg","jpg","png"])

if upload_file is not None:
    st.write("FILE UPLOADED SUCCESSFULLY...")

    st.write("File Name : ", uploaded_file.name)
    