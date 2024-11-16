import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import os

def parse_date(date_string):
    try:
        return datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z").isoformat()
    except ValueError:
        return date_string

# Last ned XML-innholdet
url = "https://sindrel.github.io/nrk-pod-feeds/rss/debatten.xml"
response = requests.get(url)
xml_content = response.content

# Parse XML
root = ET.fromstring(xml_content)

# Finn kanalinformasjon
channel = root.find("channel")
channel_info = {
    "title": channel.find("title").text,
    "description": channel.find("description").text,
    "lastBuildDate": parse_date(channel.find("lastBuildDate").text),
    "items": []
}

# Finn alle episoder
items = channel.findall("item")

# Hent informasjon om hver episode
for item in items:
    episode = {
        "title": item.find("title").text,
        "description": item.find("description").text.strip(),
        "guid": item.find("guid").text,
        "pubDate": parse_date(item.find("pubDate").text),
        "duration": item.find("itunes:duration", namespaces={"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}).text
    }
    channel_info["items"].append(episode)

# Opprett en mappe for nedlastinger hvis den ikke eksisterer
download_folder = "podcast_downloads"
os.makedirs(download_folder, exist_ok=True)

# Gå gjennom hver episode og last ned
for item in channel_info["items"]:
    title = item["title"]
    url = item["guid"]
    
    # Fjern ugyldige tegn fra filnavnet
    filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"{filename}.mp3"
    
    # Fullt filsti
    filepath = os.path.join(download_folder, filename)
    
    print(f"Laster ned: {title}")
    
    # Last ned filen
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f"Nedlasting fullført: {filename}")
    else:
        print(f"Feil ved nedlasting av {title}: HTTP status {response.status_code}")

print("Alle nedlastinger er fullført.")

# Skriv ut JSON-data (valgfritt)
json_output = json.dumps(channel_info, ensure_ascii=False, indent=2)
print(json_output)
