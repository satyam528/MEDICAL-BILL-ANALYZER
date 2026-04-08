# import streamlit as st
# from PIL import Image
# import easyocr
# import numpy as np
# import re

# # Cache the OCR reader (fast re-use)
# @st.cache_resource
# def load_reader():
#     return easyocr.Reader(['en'])

# # ====================== UI ======================
# st.set_page_config(page_title="Medical Bill Auditor", layout="centered")
# st.title("🧾 Medical Bill Auditor")
# st.markdown("Upload your hospital bill to detect overcharges, duplicates & mistakes")

# uploaded_file = st.file_uploader(
#     "Upload Bill (PDF or Image)", 
#     type=["pdf", "jpg", "jpeg", "png"]
# )

# if uploaded_file is not None:
#     st.success("✅ File uploaded successfully!")
#     st.write(f"**File Name:** {uploaded_file.name}")

#     if uploaded_file.type.startswith("image"):
#         image = Image.open(uploaded_file)
#         st.image(image, caption="Uploaded Bill", use_container_width=True)

#         # OCR
#         reader = load_reader()
#         result = reader.readtext(np.array(image))

#         # Raw extracted text
#         full_text = "\n".join([item[1] for item in result])
#         clean_text = re.sub(r'[^a-zA-Z0-9.\s]', ' ', full_text)
#         # ==================== ITEM + PRICE MAPPING ====================
#         item_price_list = []

#         for item in result:
#             text = item[1]
    
#     # Extract price
#         price_match = re.search(r'(\d+\.\d{2})', text)
    
#         if price_match:
#             price = float(price_match.group(1))
        
#         # Remove price from text → remaining is item name
#         item_name = re.sub(r'\d+\.\d{2}', '', text).strip()
        
#         if len(item_name) > 2:  # avoid junk
#             item_price_list.append((item_name.lower(), price))

# st.subheader("Item-wise Data")
# st.write(item_price_list)

#         st.subheader("Extracted Text")
#         st.text_area("OCR Output", clean_text, height=300)

#         # ==================== TOTAL DETECTION ====================
#         total_patterns = [
#             r'total.*?(\d+\.\d{2})',
#             r'grand total.*?(\d+\.\d{2})',
#             r'amount payable.*?(\d+\.\d{2})',
#             r'to pay.*?(\d+\.\d{2})',
#             r'final amount.*?(\d+\.\d{2})',
#             r'payable amount.*?(\d+\.\d{2})'
#         ]

#         detected_total = None
#         for pattern in total_patterns:
#             match = re.search(pattern, clean_text.lower())
#             if match:
#                 detected_total = float(match.group(1))
#                 break

#         if detected_total:
#             st.success(f"**Detected Total Amount:** ₹{detected_total}")
#         else:
#             st.warning("Could not detect total amount")

#         # ==================== PRICE EXTRACTION ====================
#         filtered_prices = []
#         for item in result:
#             text = item[1]
#             numbers = re.findall(r'\d+\.\d{2}', text)
#             for num in numbers:
#                 price = float(num)
#                 if 5 <= price <= 2000:          # realistic hospital price range
#                     filtered_prices.append(price)

#         st.subheader("All Detected Prices")
#         st.write(filtered_prices)

#         # ==================== CLEANED PRICES ====================
#         if detected_total:
#             cleaned_prices = [p for p in filtered_prices if abs(p - detected_total) > 1]
#         else:
#             cleaned_prices = filtered_prices

#         st.subheader("Cleaned Prices (without Total)")
#         st.write(cleaned_prices)

#         calculated_total = sum(cleaned_prices)

#         st.write(f"**Calculated Total from Items:** ₹{calculated_total}")

#         # ==================== FINAL CHECK ====================
#         if detected_total:
#             difference = abs(calculated_total - detected_total)
#             if difference > 50:                     # 50 rupees threshold (adjustable)
#                 st.error(f"⚠️ Possible Issue Found! Difference = ₹{difference}")
#             else:
#                 st.success("✅ Bill looks correct")
#         else:
#             st.warning("Cannot verify total")

#     else:
#         st.info("📄 PDF support coming in next step")

# else:
#     st.info("Please upload a bill to start analysis")


#     # 06/04/2026 break




import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import re
from collections import defaultdict

# ====================== CONFIG ======================
st.set_page_config(page_title="Medical Bill Auditor", layout="centered")

# ====================== OCR CACHE ======================
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

# ====================== FUNCTIONS ======================

def extract_text(image):
    reader = load_ocr()
    result = reader.readtext(np.array(image))
    texts = [item[1] for item in result]
    return result, "\n".join(texts)


def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9.\s]', ' ', text)


def detect_total(text):
    patterns = [
        r'total.*?(\d+\.\d{2})',
        r'grand total.*?(\d+\.\d{2})',
        r'amount payable.*?(\d+\.\d{2})',
        r'final amount.*?(\d+\.\d{2})',
        r'to pay.*?(\d+\.\d{2})'
    ]

    for p in patterns:
        match = re.search(p, text.lower())
        if match:
            return float(match.group(1))
    return None


def extract_prices(ocr_result):
    prices = []
    for item in ocr_result:
        numbers = re.findall(r'\d+\.\d{2}', item[1])
        for n in numbers:
            value = float(n)
            if 5 <= value <= 2000:
                prices.append(value)
    return prices


def map_items_prices(ocr_result):
    items = []

    for item in ocr_result:
        text = item[1]

        match = re.search(r'(\d+\.\d{2})', text)
        if match:
            price = float(match.group(1))
            name = re.sub(r'\d+\.\d{2}', '', text).strip()

            if len(name) > 2:
                items.append((name.lower(), price))

    return items


def detect_duplicates(items):
    bucket = defaultdict(list)

    for name, price in items:
        bucket[name].append(price)

    return {k: v for k, v in bucket.items() if len(v) > 1}


def detect_high_prices(items, threshold=1000):
    return [(n, p) for n, p in items if p > threshold]


# ====================== UI ======================

st.title("🧾 Medical Bill Auditor")
st.markdown("Detect duplicate charges, pricing errors & suspicious billing")

file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png"])

if file:

    st.success("File uploaded successfully")

    # Show Image
    image = Image.open(file)
    st.image(image, caption="Uploaded Bill", use_container_width=True)

    # OCR
    with st.spinner("Extracting text..."):
        ocr_result, raw_text = extract_text(image)
        text = clean_text(raw_text)

    st.subheader("Extracted Text")
    st.text_area("OCR Output", text, height=250)

    # ================= TOTAL =================
    total = detect_total(text)

    if total:
        st.success(f"Detected Total: ₹{total}")
    else:
        st.warning("Total not detected")

    # ================= PRICES =================
    prices = extract_prices(ocr_result)

    st.subheader("All Prices")
    st.write(prices)

    # Remove total from list
    if total:
        prices = [p for p in prices if abs(p - total) > 1]

    calc_total = sum(prices)

    st.write(f"Calculated Total: ₹{calc_total}")

    # ================= VALIDATION =================
    if total:
        diff = abs(calc_total - total)

        if diff > 50:
            st.error(f"Mismatch detected! Difference = ₹{diff}")
        else:
            st.success("Bill total looks correct")

    # ================= ITEM ANALYSIS =================
    st.header("Item Analysis")

    items = map_items_prices(ocr_result)
    st.write(items)

    # Duplicates
    duplicates = detect_duplicates(items)

    st.subheader("Duplicate Charges")
    if duplicates:
        for item, vals in duplicates.items():
            st.error(f"{item} → {len(vals)} times (₹{vals})")
    else:
        st.success("No duplicates found")

    # High prices
    high = detect_high_prices(items)

    st.subheader("Suspicious High Charges")
    if high:
        for item, price in high:
            st.warning(f"{item} → ₹{price}")
    else:
        st.success("No high charges")

else:
    st.info("Upload a bill image to begin")