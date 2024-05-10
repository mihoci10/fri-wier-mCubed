import sys
import re
import json

def extract_with_regex():
    print("\n--------------------------------RTVSLO 1--------------------------------\n")
    print (rtvslo_extract("rtvslo.si\Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html"))
    print("\n--------------------------------RTVSLO 2--------------------------------\n")
    print(rtvslo_extract("rtvslo.si\Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html"))

    print("\n-------------------------------OVERSTOCK 1------------------------------\n")
    product_info = overstock_extract_all("overstock.com\jewelry01.html")
    print(json.dumps(product_info, indent=4, ensure_ascii=False))
    print("\n-------------------------------OVERSTOCK 2------------------------------\n")
    product_info = overstock_extract_all("overstock.com\jewelry02.html")
    print(json.dumps(product_info, indent=4, ensure_ascii=False))

    print("\n--------------------------------AVTONET 1-------------------------------\n")
    extracted_json = avtonet_extract("avto.net\Audi RS4 2.9 TFSI quattro+CARBON+PANO+20COL+MATRIX+KOT NOV, letnik_2019,73990 EUR - prodam __ Avtonet __ www.Avto.net.html")
    print(extracted_json)
    print("\n--------------------------------AVTONET 2-------------------------------\n")
    extracted_json = avtonet_extract("avto.net\BMW M3 , letnik_2017,61800 EUR - prodam __ Avtonet __ www.Avto.net.html")
    print(extracted_json)

def avtonet_extract(file):
    print(file)
    try:
        with open(file, "r", encoding="ISO-8859-1") as file:
            html_content = file.read()
    except FileNotFoundError:
        print("HTML file not found")
        sys.exit(1)

    extracted_data = {}

    title_pattern = r'<title>(.*?)<\/title>'

    title_match = re.search(title_pattern, html_content, re.DOTALL)

    if title_match:
        extracted_data["title"] = (re.sub(r'<[^>]*>', '', title_match.group(1)).strip()).split(',')[0]

    targeted_table_pattern = r'<table[^>]*>.*?<thead[^>]*>.*?Osnovni podatki.*?<\/thead>(.*?)<\/table>'
    
    table_match = re.search(targeted_table_pattern, html_content, re.DOTALL)
    
    if not table_match:
        extracted_data["error"] = "Targeted table not found"
        return json.dumps(extracted_data, indent=4, ensure_ascii=False)

    targeted_table_content = table_match.group(1)

    row_pattern = r'<tr>\s*<th[^>]*>(.*?)<\/th>\s*<td[^>]*>(.*?)<\/td>\s*</tr>'
    matches = re.findall(row_pattern, targeted_table_content, re.DOTALL)

    for match in matches:
        key = re.sub(r'<[^>]*>', '', match[0]).strip()
        value = re.sub(r'&nbsp;', ' ', re.sub(r'<[^>]*>', '', match[1])).strip()
        
        if key and value:
            extracted_data[key] = value

    icons_patterns = {
        "Prva registracija": r'<span[^>]*>\s*Prva registracija\s*</span>.*?<h5[^>]*>(.*?)<\/h5>',
        "Prevoženih": r'<span[^>]*>\s*Prevoženih\s*</span>.*?<h5[^>]*>(.*?)<\/h5>',
        "Lastnikov": r'<span[^>]*>\s*Lastnikov\s*</span>.*?<h5[^>]*>(.*?)<\/h5>',
        "Vrsta goriva": r'<span[^>]*>\s*Vrsta goriva\s*</span>.*?<h5[^>]*>(.*?)<\/h5>',
        "Moč motorja": r'<span[^>]*>\s*Moč motorja\s*</span>.*?<h5[^>]*>(.*?)<\/h5>',
        "Menjalnik": r'<span[^>]*>\s*Menjalnik\s*</span>.*?<h5[^>]*>(.*?)<\/h5>',
    }

    for key, pattern in icons_patterns.items():
        match = re.search(pattern, html_content, re.DOTALL)
        if match:
            value = re.sub(r'&nbsp;', ' ', re.sub(r'<[^>]*>', '', match.group(1)).strip())
            extracted_data[key] = value

    return json.dumps(extracted_data, indent=4, ensure_ascii=False)


def overstock_extract_all(file):
    try:
        with open(file, "r", encoding="ISO-8859-1") as file:
            html_content = file.read()
    except FileNotFoundError:
        print("HTML file not found")
        sys.exit(1)

    product_list = []

    product_section_pattern = r'<a[^>]*href="[^"]*PROD_ID=[^"]+"[^>]*><b>([^<]+)</b></a>.*?(<table>.*?</table>)'
    product_sections = re.findall(product_section_pattern, html_content, re.DOTALL)

    for product_name, product_section in product_sections:
        product_info = {}

        product_info["product_name"] = product_name.strip()

        list_price_pattern = r'<s>(.*?)<\/s>'
        list_price_match = re.search(list_price_pattern, product_section, re.DOTALL)
        if list_price_match:
            product_info["list_price"] = list_price_match.group(1).strip()

        price_pattern = r'<span[^>]*class="bigred"[^>]*><b>(.*?)<\/b></span>'
        price_match = re.search(price_pattern, product_section, re.DOTALL)
        if price_match:
            product_info["price"] = price_match.group(1).strip()

        savings_pattern = r'<span[^>]*class="littleorange"[^>]*>\s*(\$[\d,.]+)\s*\((\d+%?)\)\s*</span>'
        savings_match = re.search(savings_pattern, product_section, re.DOTALL)
        if savings_match:
            product_info["savings"] = savings_match.group(1).strip()
            product_info["savings_percent"] = savings_match.group(2).strip()

        product_list.append(product_info)

    return product_list

def rtvslo_extract(file):
    try:
        with open(file, "r", encoding="utf-8") as file:
            html_content = file.read()
    except FileNotFoundError:
        print("HTML file not found")
        sys.exit(1)

    authorPublishedTime = r'<strong>(.*?)<\/strong>\s*\|\s*(.+)'
    title = r'<title>(.*?)<\/title>'
    subTitle = r'<div\s+class="subtitle">(.*?)<\/div>'
    lead = r'<p\s+class="lead">(.*?)<\/p>'
    kljucniPodatki = r'<p><strong>Ključni tehnični podatki:</strong>(.*?)<\/p>'
    
    match = re.search(authorPublishedTime, html_content)
    matchTitle = re.search(title, html_content)
    matchSubTitle = re.search(subTitle, html_content)
    matchLead = re.search(lead, html_content)
    matchKljucniPodatki = re.search(kljucniPodatki, html_content, re.DOTALL)

    if not match or not matchTitle or not matchSubTitle or not matchLead or not matchKljucniPodatki:
        return json.dumps({"error": "Pattern not found"}, indent=4, ensure_ascii=False)

    author = match.group(1)  # Author
    publishedTime = match.group(2)  # Date-time
    pageTitle = matchTitle.group(1)
    pageSubTitle = matchSubTitle.group(1)
    pageLead = matchLead.group(1)
    pageKljucniPodatki = matchKljucniPodatki.group(1).strip()

    data = {
        "author": author,
        "published_time": publishedTime,
        "page_title": pageTitle,
        "page_sub_title": pageSubTitle,
        "page_lead": pageLead,
        "page_kljucni_podatki": pageKljucniPodatki,
    }

    pattern = r'(?i)(Mere:|Pogon:|Stroški pri 15\.000 km in 5-letni uporabi:)(.*?)(?=<p>|<\/p>)'
    matches = re.findall(pattern, html_content, re.DOTALL)

    additional_sections = {}
    for m in matches:
        section_title = m[0].strip()
        section_content = m[1].strip()
        if section_content:
            list_items = [item.strip() for item in section_content.split("<br>")]
            additional_sections[section_title] = list_items

    data["additional_sections"] = additional_sections

    return json.dumps(data, indent=4, ensure_ascii=False)