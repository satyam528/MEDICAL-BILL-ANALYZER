import streamlit as st

st.set_page_config(page_title="MEDICAL-PLACEHOLDER")
st.title("MEDICAL BILL AUDITOR PLACEHOLDER")

uploaded_file=st.file_uploader("PLEASE UPLOAD YOUR FILE HERE :",type=["pdf","jpeg","jpg","png"])

if uploaded_file is not None:
    st.write("FILE UPLOADED SUCCESSFULLY...")

    #FILE INFO
    st.write("File Name : ", uploaded_file.name)

    #image
    if uploaded_file.type.startswith("image"):
        st.image(uploaded_file,caption="Uploaded Image",use_colomn_width= true ) 
    else:
        st.write("File uploaded,Preview will be added later")