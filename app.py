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
    result = reader.readtext(np.array(image),paragraph=False,detail=1)
    texts = [item[1] for item in result]
    return result, "\n".join(texts)


def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9.\s]', ' ', text)

def normalize_ocr_text(text):

    # text = text.replace("o", "0")
    # text = text.replace("O", "0")

    return text


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


def group_rows(ocr_result):
    rows = {}

    for item in ocr_result:
        y = item[0][0][1]
        text = item[1]

        row_key = round(y / 20) * 20

        if row_key not in rows:
            rows[row_key] = []

        rows[row_key].append(text)

    return rows


def map_items_prices(ocr_result):

    rows = group_rows(ocr_result)

    items = []

    for y, texts in rows.items():

        if len(texts) < 2:
            continue

        name = texts[0]
        if any(word in name.lower() for word in [
           "total",
           "amount due",
            "grand total",
            "payable"
        ]):
            continue

        # skip headers
        if name.lower() in [
            "bill summary",
            "quantity",
            "unit price",
            "total"
        ]:
            continue

        prices = []

        for t in texts[1:]:

            t = normalize_ocr_text(str(t))
            match = re.search(r'(\d+\.?\d*)', t)

            if match:
                prices.append(float(match.group(1)))

        if prices:

            final_price = max(prices)

            items.append(
                (
                    name.lower(),
                    final_price
                )
            )

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

file = st.file_uploader("Upload Bill Image", type=["jpg", "jpeg", "png","pdf"])

if file:

    st.success("File uploaded successfully")
    
    # Show Image
    image = Image.open(file)

    width,height=image.size
    image = image.resize((width*2,height*2))
    st.image(image, caption="Uploaded Bill", use_container_width=True)

    # OCR
    with st.spinner("Extracting text..."):
        ocr_result, raw_text = extract_text(image)
        text = clean_text(raw_text)

        # st.subheader("Raw OCR Result")
    # rows = group_rows(ocr_result)

    # st.subheader("Grouped Rows")

    # for y, texts in rows.items():
    #     st.write(y, "->", texts)

        # for item in ocr_result:
        #     st.write(item)

    # st.subheader("OCR Positions")

    # for item in ocr_result:
    #     box = item[0]
    #     text = item[1]

    #     y = box[0][1]

    #     st.write(
    #         f"Y={y} -> {text}"
    #         )
    

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

    st.subheader("Parsed Items")
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
    
