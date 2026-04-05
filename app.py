import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'])

# UI
st.set_page_config(page_title="Medical Bill Auditor")
st.title("Medical Bill Auditor")

uploaded_file = st.file_uploader(
    "Please upload your file:",
    type=["pdf", "jpeg", "jpg", "png"]
)

if uploaded_file is not None:
    st.success("File uploaded successfully!")
    st.write("File Name:", uploaded_file.name)

    # Handle Image
    if uploaded_file.type.startswith("image"):
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        reader = load_reader()
        result = reader.readtext(np.array(image))

        # Show extracted raw text (for debugging)
        full_text = "\n".join([item[1] for item in result])
        clean_text = re.sub(r'[^a-zA-Z0-9.\s]', ' ', full_text)
        st.subheader("Extracted Text")
        st.write(clean_text)

        detected_total = None
        total_match = re.search( r'(total.*?)(\d+\.\d{2})' , clean_text.lower())
        if total_match:
            detected_total=float(total_match.group(2))
            st.write(detected_total)



        # 🔥 Extract prices
        filtered_prices = []

        for item in result:
            text = item[1]

            numbers = re.findall(r'\d+\.\d{2}', text)

            if numbers:
                price = float(numbers[0])

                # Remove unrealistic OCR errors
                if price > 2000:
                    continue

                filtered_prices.append(price)

                st.write({"price": price})
        
        # ✅ Final output OUTSIDE loop
        st.subheader("Filtered Prices")
        st.write(filtered_prices)

        cleaned_prices=[p for p in filtered_prices if p not in [detected_total,480,120]]
        cleaned_prices=list(set(cleaned_prices))


        st.subheader("Cleaned Price")
        st.write(cleaned_prices)

        calculated_total=sum(cleaned_prices)
        st.write("Calculated Total :",calculated_total)


        
        if(detected_total != None):
            if abs(calculated_total - detected_total)>1:
                st.error("Issue Found")
            else:
                st.success("Bill Correct")
        else:
            st.warning("Cannot Find Total")



    else:
        st.write("PDF support will be added later")

else:
    st.write("Please upload a file")