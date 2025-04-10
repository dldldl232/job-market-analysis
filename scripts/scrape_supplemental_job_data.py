import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Load your CSV from the API job data
INPUT_FILE = "../detailed_jsearch_job_listings.csv"
OUTPUT_FILE = "../enriched_job_listings.csv"

# Load job data
df = pd.read_csv(INPUT_FILE)

# Create a copy to work with
df_scraped = df.copy()
scraped_descriptions = []

print("Starting web scraping of job application links...\n")

# Loop through each job posting
for idx, row in df_scraped.iterrows():
    job_url = row.get('job_apply_link')
    summary_text = "N/A"

    if pd.notna(job_url):
        try:
            print(f"Scraping: {job_url}")
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(job_url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                meta_desc = soup.find("meta", attrs={"name": "description"})

                if meta_desc and meta_desc.get("content"):
                    summary_text = meta_desc["content"]
                else:
                    # Try to fall back to the first paragraph text
                    paragraph = soup.find("p")
                    summary_text = paragraph.get_text(strip=True) if paragraph else "No description found"
            else:
                summary_text = f"Failed to fetch page: {response.status_code}"

        except Exception as e:
            summary_text = f"Error: {e}"

        time.sleep(1)

    scraped_descriptions.append(summary_text)

# Add scraped text to the DataFrame
df_scraped['scraped_summary'] = scraped_descriptions

# Save to a new CSV
df_scraped.to_csv(OUTPUT_FILE, index=False)
print(f"\n Scraping complete. Enriched data saved to: {OUTPUT_FILE}")
