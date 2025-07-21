import requests
import time
import json

# Your credentials and phantom IDs
API_KEY = 'E3vAWDOAGi9xj8Nl7dN1Na3GARcMSm9pad3niJgxLSU'
URL_FINDER_PHANTOM_ID = 'your_url_finder_phantom_id'
PROFILE_SCRAPER_PHANTOM_ID = 'your_profile_scraper_phantom_id'

headers = {
    'X-Phantombuster-Key-1': API_KEY,
    'Content-Type': 'application/json'
}

def launch_phantom(phantom_id):
    url = f"https://api.phantombuster.com/api/v2/agents/launch?id={phantom_id}"
    response = requests.post(url, headers=headers)
    print(f"Launched Phantom {phantom_id}")
    return response.json()

def get_output(phantom_id):
    time.sleep(60)  # You can use a loop to check status instead of static sleep
    url = f"https://api.phantombuster.com/api/v2/agents/fetch-output?id={phantom_id}"
    response = requests.get(url, headers=headers)
    return response.json()

# Step 1: Run URL Finder
print("🔍 Running LinkedIn URL Finder...")
launch_phantom(URL_FINDER_PHANTOM_ID)
url_finder_output = get_output(URL_FINDER_PHANTOM_ID)

# Extract LinkedIn URLs
linkedin_urls = []
for entry in url_finder_output.get('container', []):
    if entry.get('linkedinUrl'):
        linkedin_urls.append(entry['linkedinUrl'])

print(f"✅ Found {len(linkedin_urls)} LinkedIn URLs")

# Step 2: Prepare CSV of LinkedIn URLs
with open("linkedin_urls.csv", "w") as f:
    f.write("linkedinUrl\n")
    for url in linkedin_urls:
        f.write(url + "\n")

# NOTE: Upload this CSV to GitHub, Dropbox, or Google Drive and get the raw URL
print("📤 Upload 'linkedin_urls.csv' to a public link (e.g. GitHub raw link)")

# Step 3: Update Phantom input to point to your new CSV
# You can do this step manually in Phantom or automate input settings via API
# Let me know if you want to automate the config upload too

# Step 4: Run LinkedIn Profile Scraper
input("📌 After uploading CSV and setting it in Phantom, press ENTER to continue scraping...")

print("🕵️ Scraping LinkedIn Profiles...")
launch_phantom(PROFILE_SCRAPER_PHANTOM_ID)
scraper_output = get_output(PROFILE_SCRAPER_PHANTOM_ID)

# Print results
print("📄 Scraped Data:")
for person in scraper_output.get('container', []):
    print(f"{person['fullName']} | {person.get('job', 'No Job Info')} | {person.get('location', 'No Location')}")
