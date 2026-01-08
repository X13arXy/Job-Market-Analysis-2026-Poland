import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random

# --- CONFIGURATION ---
KEYWORD = "data analyst"
PAGES_TO_SCRAPE = 20     # 20 pages * 50 offers = target approx. 1000 offers

# Connect to an existing Chrome instance (via remote debugging port)
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=chrome_options)
    print("✅ Successfully connected to Chrome instance!")
except Exception as e:
    print("❌ Chrome not detected. Please run Chrome via CMD using: --remote-debugging-port=9222")
    exit()

all_offers = []
seen_links = set() # Set to prevent duplicates in real-time

print(f"🚀 Starting Link Harvester (Smart Filtering: ON)...")

for page in range(1, PAGES_TO_SCRAPE + 1):
    # Construct URL with pagination parameter
    url = f"https://www.pracuj.pl/praca/{KEYWORD.replace(' ', '%20')};kw?pn={page}"
    print(f"📄 Processing page {page}/{PAGES_TO_SCRAPE}...", end="")
    
    try:
        driver.get(url)
        # Random sleep to mimic human behavior
        time.sleep(random.uniform(2, 3.5)) 
        
        # Find main offer containers
        offers_on_page = driver.find_elements(By.CSS_SELECTOR, "div[class*='tiles_']")
        
        count_this_page = 0
        
        for offer in offers_on_page:
            try:
                # --- CORE LOGIC: EXTRACT LINK FROM HEADER (H2) ONLY ---
                # We target H2 to avoid grabbing links from logos or company names.
                try:
                    title_element = offer.find_element(By.TAG_NAME, "h2")
                    link_element = title_element.find_element(By.TAG_NAME, "a")
                except:
                    continue # Skip if H2 is missing (likely an ad or banner)

                link = link_element.get_attribute("href")
                title = title_element.text
                
                # --- URL FILTER ---
                # 1. Must contain "/praca/" (valid job offer)
                # 2. Must not be a duplicate
                if link and "/praca/" in link and link not in seen_links:
                    all_offers.append({
                        'Title': title,
                        'Link': link
                    })
                    seen_links.add(link)
                    count_this_page += 1
                    
            except Exception as e:
                continue
        
        print(f" -> Extracted {count_this_page} unique offers.")

    except Exception as e:
        print(f"\n⚠️ Error on page {page}: {e}")

# Save data to CSV
df = pd.DataFrame(all_offers)
filename = 'big_data_links.csv'
df.to_csv(filename, index=False)

print(f"\n🎉 SUCCESS! Collected a total of {len(df)} VALID offers.")
print(f"Data saved to: {filename}")