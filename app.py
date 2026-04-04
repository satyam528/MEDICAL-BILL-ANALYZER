import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])




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
        st.image(image,caption="Uploaded Image",width= "stretch" ) 
        
        reader= load_reader()  
        result= reader.readtext(np.array(image))

        full_text="\n".join([item[1] for item in result])
        clean_text=re.sub(r'[^a-zA-Z0-9.\s]', ' ', full_text)
        clean_text = clean_text.replace('S', '')
        st.write(clean_text)

        filtered_prices = []

        for item in result:
            text = item[1]

            numbers = re.findall(r'\d+\.\d{2}', text)

            if numbers:
               item_name = re.sub(r'\d+\.\d{2}', '', text)
               item_name = re.sub(r'\s+', ' ', item_name).strip()

               if item_name == "": 
                continue

               price = float(numbers[0])

               if any(word in item_name.lower() for word in ["amount", "covered", "patient", "insurance", "total"]):
                continue

               if price > 2000:
                continue
 
               filtered_prices.append(price)

               st.write({"item": item_name, "price": price})

        st.write("Filtered Prices:", filtered_prices)

    else:
        st.write("File uploaded,Preview will be added later")

else:
   ("Please Upload a file")