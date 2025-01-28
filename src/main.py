import ssl
import urllib3
import requests
import re
from bs4 import BeautifulSoup


# Mapping months
months_mapping = {
        "OCAK": "01", "ŞUBAT": "02", "MART": "03", "NİSAN": "04",
        "MAYIS": "05", "HAZİRAN": "06", "TEMMUZ": "07", "AĞUSTOS": "08",
        "EYLÜL": "09", "EKİM": "10", "KASIM": "11", "ARALIK": "12"
    }

def disable_ssl_warnings():
    ssl._create_default_https_context = ssl._create_unverified_context
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_page_content(url):
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to retrieve the page. Status code is {response.status_code}")
    return None

def tr_upper_char(text):
    char_map = {
        "ç":"Ç", "ğ":"Ğ", "ı":"I", "i":"İ", "ö":"Ö", "ş":"Ş", "ü":"Ü" 
    }

    return ''.join(char_map.get(m, m.upper()) for m in text)

def extract_year_month(date_info):
    normalized_info = tr_upper_char(date_info.strip())

    match = re.search(r"([A-ZÇŞİĞÜ]+)\s?(\d{4})", normalized_info)
    if match:
        month_text = match.group(1) # Month name
        year = match.group(2) # Year
        month = months_mapping.get(month_text.upper(), "00")
        return f"{year}-{month}-01"
    
    print(f"Invalid date_info format: {date_info}")
    return None

def find_month_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    year_months = []

    for element in soup.find_all('a'):
        href = element.get('href')
        if href:  # Eğer href varsa yazdır
            print(f"Found href: {href}")

        if href and '.pdf' in href and extract_year_month(element.get_text()):
            year_months.append(extract_year_month(element.get_text()))

    return year_months



url = "https://istanbul.ktb.gov.tr/TR-368430/istanbul-turizm-istatistikleri---2024.html"

content = fetch_page_content(url)
if content:
    print("ok")

else:
    print("whops")


result = find_month_html(content)
print(f"Extracted Year-Months: {result}")

