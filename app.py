import streamlit as st
import easyocr
from PIL import Image
import numpy as np

st.set_page_config(page_title="MEDICAL-PLACEHOLDER")
st.title("MEDICAL BILL AUDITOR PLACEHOLDER")

uploaded_file=st.file_uploader("PLEASE UPLOAD YOUR FILE HERE :",type=["pdf","jpeg","jpg","png"])



if uploaded_file is not None:
    st.success("FILE UPLOADED SUCCESSFULLY...")

    #FILE INFO
    st.write("File Name : ", uploaded_file.name)




    #image
    if uploaded_file.type.startswith("image"):
        image= Image.open(uploaded_file)
        st.image(uploaded_file,caption="Uploaded Image",use_container_width= True ) 
        
        reader= easyocr.Reader(['en'])  
        result= reader.readtext(np.array(image))

        full_text="/n".join([item[1] for item in result])
        st.write(full_text)



    else:
        st.write("File uploaded,Preview will be added later")