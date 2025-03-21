import ssl
import urllib3
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pdfplumber
from io import BytesIO
import pandas as pd
from sqlalchemy.orm import sessionmaker
from models import ist_sinir_gelen_yabanci
from sqlalchemy import extract
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from models import engine

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

def find_pdf_links_with_base_url(html_content, base_url):
    soup = BeautifulSoup(html_content, "html.parser")
    pdf_links = []

    for element in soup.find_all('a'):
        href = element.get('href')
        if href and '.pdf' in href:  
            clean_href = href.split('?')[0]
            full_url = urljoin(base_url, clean_href)
            pdf_links.append(full_url)
            #print(f"Full PDF URL: {full_url}")

    return pdf_links

def find_month_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    year_months = []

    for element in soup.find_all('a'):
        href = element.get('href')
        if href and '.pdf' in href:
            pass
            #print(f"Found href: {href}")

        if href and '.pdf' in href and extract_year_month(element.get_text()):
            year_months.append(extract_year_month(element.get_text()))

    return year_months

def find_page_with_title(pdf_content, search_title):
    matching_pages = []
    with pdfplumber.open(BytesIO(pdf_content)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text_simple()
            text_dry = " ".join(text.split())
            if text and re.search(search_title, text_dry, re.IGNORECASE):
                matching_pages.append(i) # Append page numbers to a list.
    
    if len(matching_pages) >= 2:
        return matching_pages[1] # Pick second match.
    return None

def read_pdf_simple(pdf_url, search_title):
    try:
        response = requests.get(pdf_url, verify=False)
        response.raise_for_status()
        pdf_content = response.content

        page_number = find_page_with_title(pdf_content, search_title)

        if page_number is not None:
            #print(f"{search_title} header at {page_number+1}. page")
            with pdfplumber.open(BytesIO(response.content)) as pdf:
                page = pdf.pages[page_number]
                table_txt = page.extract_text_simple()
                if table_txt:
                    #print(table_txt)
                    return table_txt
                else:
                    print(f"Text could not retrieved")
        else:
            print(f"{search_title} cannot found")
    except Exception as e:
        print(f"Error raised: {e}")
    return None

def year_from_page(page_text):
    lines = [line.strip() for line in page_text.split("\n") if line.strip()]

    for line in lines:
        if "Toplam" in line:
            year = line.split()[0]
            return year
    print("No 'Toplam' keyword found.")
    return None


def extract_from_pdf(page_text, latest_month):
    latest_month = int(latest_month)
    if not page_text:
        print("Page text couldn't retrieved.")
        return
    
    lines = [line.strip() for line in page_text.split("\n") if line.strip()]
    
    months_map = {
            "Ocak": "01", "Şubat": "02", "Mart": "03", "Nisan": "04",
            "Mayıs": "05", "Haziran": "06", "Temmuz": "07", "Ağustos": "08",
            "Eylül": "09", "Ekim": "10", "Kasım": "11", "Aralık": "12"
    }

    toplam_indices = [i for i, line in enumerate(lines) if "TOPLAM" in line]
    
    if not toplam_indices:
        print("No 'TOPLAM' keyword found.")
        return

    toplam_index = toplam_indices[0]
    year = year_from_page(page_text)
    
    extracted_data = []
    found_months = []

    for i in range(toplam_index - 1, -1, -1):
        for month_name, month_str in months_map.items():
            if month_name in lines[i]:
                month_num = int(month_str)
                if month_num <= latest_month and month_name not in found_months:
                    line_parts = lines[i].split()
                    
                    if len(line_parts) < 2:
                        print(f"No data found for {month_name}!")
                        continue
                    
                    tarih = f"{year}-{month_str}-01"
                    extracted_data.append([tarih] + line_parts[1:])
                    found_months.append(month_name)  

                if len(found_months) > 0 and found_months[-1] == month_name:
                    break

    havalimanlari = [
        "tarih", "Atatürk Havalimanı (H)", "S. Gökçen (H)", "İstanbul Havalimanı (H)", 
        "Haydarpaşa (D)", "Karaköy (D)", "Sarayburnu (D)", "Marmara (D)", 
        "Tuzla (D)", "Pendik (D)", "Ambarlı (D)", "Zeytinburnu (D)", "Toplam"
    ]

    if extracted_data:
        df = pd.DataFrame(extracted_data, columns=havalimanlari)

        # *** MELT ***
        df_melted = df.melt(id_vars=["tarih"], var_name="sinir_kapilari", value_name="yabanci_ziyaretci")

        #print("\nMelted DataFrame:")
        #print(df_melted)
        return df_melted
    else:
        print("No valid month data found.")
        return None

def check_month_year_exitst(session, month, year):
    exists = (
        session.query(ist_sinir_gelen_yabanci)
        .filter(
            extract('month', ist_sinir_gelen_yabanci.tarih) == month,
            extract('year', ist_sinir_gelen_yabanci.tarih) == year
        )
        .first()
    )
    return exists is not None

def save_to_database(df, session):
    for _, row in df.iterrows():
        try:
            yabanci_ziyaretci = float(str(row["yabanci_ziyaretci"]).replace(".","")) # Remove dot

            new_record = ist_sinir_gelen_yabanci(
                tarih = row["tarih"],
                sinir_kapilari = str(row["sinir_kapilari"]),
                yabanci_ziyaretci = yabanci_ziyaretci,
                erisim_tarihi=datetime.today().strftime("%Y-%m-%d")
            )
            session.add(new_record)
            session.commit()
        except ValueError:
            print(f"Error converting yabanci_ziyaretci: {row['yabanci_ziyaretci']}. Skipping this row.")
            session.rollback()
        except IntegrityError:
            print(f"Duplicate entry for date {row['tarih']}. Skipping...")
            session.rollback()
    print("Data added to the database.")     

# Main script execution
def main_02_02_ktb():
    Session = sessionmaker(bind=engine)
    session = Session()

    # URL
    base_url = "https://istanbul.ktb.gov.tr/"
    url = "https://istanbul.ktb.gov.tr/TR-368430/istanbul-turizm-istatistikleri---2024.html"  #
    html_content = fetch_page_content(url)

    if html_content:
        
        pdf_links = find_pdf_links_with_base_url(html_content, base_url)

        if not pdf_links:
            print("No PDF found.")
        else:
            all_dataframes = []

            for pdf_path in pdf_links:  # 
                print(f"Processing: {pdf_path}")
                page_text = read_pdf_simple(pdf_path, r"İSTANBUL’A GİRİŞ YAPAN YABANCI ZİYARETÇİLERİN SINIR KAPILARINA GÖRE DAĞILIMI")  #
                
                if page_text:
                    latest_month = "12"
                    df = extract_from_pdf(page_text, latest_month)
                    
                    if df is not None:
                        #df['source'] = pdf_path  # Delete this
                        all_dataframes.append(df)

            if all_dataframes is not None:
                final_df = pd.concat(all_dataframes, ignore_index=True)
                print("All ok.")
                #print(final_df.head())
            
                for _, row in final_df.iterrows():
                    parsed_date = datetime.strptime(row['tarih'], "%Y-%m-%d")
                    year = parsed_date.year
                    month = parsed_date.month

                    if check_month_year_exitst(session, month, year):
                            print(f"Record already exists for {month}/{year}. Skipping...")
                    else:
                        print(f"New data for {month}/{year}. Adding to database...")
                        save_to_database(final_df, session)
            else:
                print(f"Final dataframe could not prepared")
    else:
        print("Failed to fetch HTML content..")
    session.close()
    print("Database update complete.")

#def run_main_02_02_ktb():
    #main_02_02_ktb()

if __name__ == "__main__":
 main_02_02_ktb()