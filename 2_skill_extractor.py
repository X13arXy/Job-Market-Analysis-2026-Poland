import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
import os

# --- CONFIGURATION ---
input_file = 'big_data_links.csv'   # Input file containing links (from Stage 1)
output_file = 'final_1000_jobs.csv' # Output file for final results

# Validate input file existence
if not os.path.exists(input_file):
    print(f"❌ Error: File '{input_file}' not found. Ensure it is in the same directory.")
    exit()

# Load job links
full_df = pd.read_csv(input_file)
print(f"📂 Database loaded: {len(full_df)} offers ready for analysis.")

# Define Keywords / Tech Stack
KEYWORDS = {
    'SQL': ['SQL', 'T-SQL', 'PL/SQL', 'DATABASE', 'BAZY DANYCH'],
    'Python': ['PYTHON', 'PANDAS', 'NUMPY', 'SCIPY', 'SELENIUM'],
    'Power BI': ['POWER BI', 'POWERBI', 'DAX', 'POWER QUERY'],
    'Excel': ['EXCEL', 'VBA', 'ARKUSZ', 'PIVOT'],
    'Tableau': ['TABLEAU'],
    'English': ['ENGLISH', 'ANGIELSKI', 'B2', 'C1'], 
    'Cloud': ['AWS', 'AZURE', 'GCP', 'CHMURA'],
    'R': [' R ', 'LANGUAGE R'] # Spaces are crucial to avoid false positives
}

# Initialize columns for each skill with 0
for key in KEYWORDS.keys():
    full_df[key] = 0

# --- CONNECT TO EXISTING CHROME INSTANCE ---
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=chrome_options)
    print("✅ Successfully connected to Chrome instance. Starting...")
except Exception as e:
    print("❌ Error: Could not connect to Chrome on port 9222.")
    exit()

print("🚀 Starting Skill Extraction... (Grab a coffee ☕)")

# --- MAIN LOOP ---
start_time = time.time()

for index, row in full_df.iterrows():
    url = row['Link']
    
    # Display progress
    progress = round((index + 1) / len(full_df) * 100, 1)
    print(f"[{index+1}/{len(full_df)}] ({progress}%) ", end="")
    
    if pd.isna(url):
        print("Skipping empty link.")
        continue

    try:
        driver.get(url)
        # Random sleep to mimic human behavior and avoid blocking
        time.sleep(random.uniform(1.5, 3.0))
        
        # Extract page content (with simple retry logic)
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text.upper()
        except:
            driver.refresh()
            time.sleep(2)
            body_text = driver.find_element(By.TAG_NAME, "body").text.upper()

        # Scan for keywords
        found_skills = []
        for tech, variations in KEYWORDS.items():
            if any(var in body_text for var in variations):
                full_df.at[index, tech] = 1
                found_skills.append(tech)
        
        print(f"-> {str(row['Title'])[:20]}... : {found_skills}")

    except Exception as e:
        print(f"⚠️ Error: {e}")

    # --- AUTO-SAVE EVERY 50 OFFERS ---
    # Prevents data loss in case of crash/network failure
    if (index + 1) % 50 == 0:
        full_df.to_csv(output_file, index=False)
        print(f"💾 [AUTO-SAVE] Progress saved to {output_file}")

# Final save
full_df.to_csv(output_file, index=False)
end_time = time.time()
duration = round((end_time - start_time) / 60, 1)

print(f"\n🎉 SUCCESS! Analyzed {len(full_df)} offers in {duration} minutes.")
print(f"Results saved to: {output_file}")