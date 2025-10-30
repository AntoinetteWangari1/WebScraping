import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

base_url = "https://www.myjobmag.co.ke"

# ----------- STEP 1: scrape main job list -----------
url = f"{base_url}/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

ul = soup.find('ul', class_='job-list')
jobs_data = []

# Loop through *only top-level* job-list-li items
for job in ul.find_all('li', class_='job-list-li', recursive=False):
    info = job.find('li', class_='job-info')
    a_tag = info.find('a') if info else None

    title = info.find('h2').get_text(strip=True) if info and info.find('h2') else None
    link = a_tag['href'] if a_tag and a_tag.has_attr('href') else None
    if link and not link.startswith('http'):
        link = f"{base_url}{link}"

    desc = job.find('li', class_='job-desc')
    description = desc.get_text(strip=True) if desc else None

    date = job.find('li', id='job-date')
    posted_date = date.get_text(strip=True) if date else None

    if title and description:
        jobs_data.append({
            'Job Title & Company': title,
            'Company Info': description,
            'Posted Date': posted_date,
            'Link': link
        })

df = pd.DataFrame(jobs_data)
df.drop_duplicates(inplace=True)
df.dropna(subset=['Job Title & Company'], inplace=True)

# ----------- STEP 2: visit each job detail page -----------
details_list = []

print("\n--- Visiting job detail pages ---\n")

for idx, row in df.iterrows():
    link = row['Link']
    print(f"\nScraping details for: {row['Job Title & Company']}")
    if not link:
        continue

    try:
        resp = requests.get(link)
        job_soup = BeautifulSoup(resp.text, 'html.parser')

        # Initialize detail fields
        job_type = qualification = experience = location = field = salary = None
        details_text = None

        # --- Extract from <ul class="job-key-info"> ---
        key_info = job_soup.find('ul', class_='job-key-info')
        if key_info:
            for li in key_info.find_all('li'):
                key = li.find('span', class_='jkey-title')
                val = li.find('span', class_='jkey-info')
                if not key or not val:
                    continue
                key_text = key.get_text(strip=True).lower()
                val_text = val.get_text(" ", strip=True)

                if "type" in key_text:
                    job_type = val_text
                elif "qualification" in key_text:
                    qualification = val_text
                elif "experience" in key_text:
                    experience = val_text
                elif "location" in key_text:
                    location = val_text
                elif "field" in key_text:
                    field = val_text
                elif "salary" in key_text:
                    salary = val_text

        # --- Extract job details description ---
        details_div = job_soup.find('div', class_='job-details')
        if details_div:
            details_text = details_div.get_text("\n", strip=True)

        # Combine into dictionary
        details_list.append({
            'Job Title & Company': row['Job Title & Company'],
            'Company Info': row['Company Info'],
            'Posted Date': row['Posted Date'],
            'Link': link,
            'Job Type': job_type,
            'Qualification': qualification,
            'Experience': experience,
            'Location': location,
            'Field': field,
            'Salary Range': salary,
            'Full Description': details_text
        })

        time.sleep(1)  

    except Exception as e:
        print(f"Error scraping {link}: {e}")
        continue

# ----------- STEP 3: Save final structured CSV -----------
final_df = pd.DataFrame(details_list)
final_df.to_csv('myjobs_detailed.csv', index=False, encoding='utf-8-sig')

print("\n Saved as myjobs_detailed.csv")
print(final_df.head())
