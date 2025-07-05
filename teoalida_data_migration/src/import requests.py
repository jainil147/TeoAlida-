import requests
import re
import json

url = "https://www.bmwpartsnow.com/search?search_str=ECU&make=bmw&model=330i&year=2024"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
html = response.text

# Step 1: Extract the <script> block that contains 'tracking = {...};'
script_pattern = r"var tracking\s*=\s*({.*?});\s*var digitalData"
script_match = re.search(script_pattern, html, re.DOTALL)

if script_match:
    tracking_js = script_match.group(1)

    # Step 2: Extract the "products": [...] array from within
    products_pattern = r'"products"\s*:\s*(\[\s*{.*?}\s*])'
    products_match = re.search(products_pattern, tracking_js, re.DOTALL)

    if products_match:
        products_json_str = products_match.group(1)
        try:
            products = json.loads(products_json_str)
            print(json.dumps(products, indent=2))
        except json.JSONDecodeError as e:
            print("❌ JSON decoding failed:", e)
    else:
        print("❌ 'products' array not found in tracking object.")
else:
    print("❌ 'tracking' object not found in script tag.")
