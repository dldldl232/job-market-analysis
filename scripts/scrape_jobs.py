import requests
import pandas as pd
import time

RAPIDAPI_KEY = 'a89cfdf635mshb4b5fe89f7ad8f0p170920jsn600676274b9a'  # Replace with your RapidAPI key
HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": "jsearch.p.rapidapi.com"
}

# ✅ API Endpoints
SEARCH_URL = "https://jsearch.p.rapidapi.com/search"
DETAILS_URL = "https://jsearch.p.rapidapi.com/job-details"

# ✅ Job Search Parameters
QUERY_PARAMS = {
    "query": "data analyst",  # Job title
    "location": "New York",  # Location
    "page": "1",  # Start at page 1
    "num_pages": "1",  # Number of pages to fetch
    "date_posted": "week",  # Jobs posted in the last week
    "radius": "50",  # Search within 50 miles
    "employment_types": "FULLTIME"  # Filter by full-time jobs
}

# ✅ Store All Jobs
all_jobs = []

print("🔍 Searching for jobs...")

# ✅ PAGINATION: Fetch jobs from multiple pages
while True:
    try:
        response = requests.get(SEARCH_URL, headers=HEADERS, params=QUERY_PARAMS)

        if response.status_code == 200:
            job_data = response.json()  # Convert to JSON
            jobs = job_data.get("data", [])  # Extract job results

            if not jobs:  # If no jobs found, stop loop
                print("✅ No more job results. Stopping search.")
                break

            all_jobs.extend(jobs)  # Add jobs to our list
            print(f"📄 Retrieved {len(jobs)} jobs from page {QUERY_PARAMS['page']}")

            # Move to the next page
            QUERY_PARAMS["page"] = str(int(QUERY_PARAMS["page"]) + 1)

            # Prevent hitting rate limits
            time.sleep(1)
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")  # Print the response for debugging
            break  # Stop if there's an error
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        break

# ✅ Convert to DataFrame & Save to CSV
if all_jobs:
    df_jobs = pd.DataFrame(all_jobs)
    df_jobs.to_csv("jsearch_job_listings.csv", index=False)
    print("📁 Job listings saved to 'jsearch_job_listings.csv' ✅")
else:
    print("❌ No jobs found to save.")

# ----------------------------
# ✅ FETCH DETAILED JOB INFO
# ----------------------------
print("\n🔍 Fetching job details...")

detailed_jobs = []

for job in all_jobs:
    try:
        job_id = job["job_id"]  # JSearch uses "job_id" for job details
        detail_params = {
            "job_id": job_id,
            "extended_publisher_details": "false"
        }

        detail_response = requests.get(DETAILS_URL, headers=HEADERS, params=detail_params)

        if detail_response.status_code == 200:
            job_details = detail_response.json()
            job.update(job_details["data"][0])  # Merge details into main job dictionary
            detailed_jobs.append(job)
            print(f"✅ Retrieved details for job ID: {job_id}")

        elif detail_response.status_code == 429:
            # Quota exceeded, stop fetching details
            print(f"❌ Quota exceeded. Stopping further requests.")
            print(f"Response: {detail_response.text}")
            break  # Exit the loop

        else:
            print(f"❌ Failed to fetch details for job ID: {job_id}. Status Code: {detail_response.status_code}")
            print(f"Response: {detail_response.text}")  # Print the response for debugging

        # Prevent hitting rate limits
        time.sleep(1)
    except Exception as e:
        print(f"❌ An error occurred for job ID {job_id}: {e}")

# ✅ Save the detailed job listings
if detailed_jobs:
    df_detailed = pd.DataFrame(detailed_jobs)
    df_detailed.to_csv("detailed_jsearch_job_listings.csv", index=False)
    print("📁 Detailed job data saved to 'detailed_jsearch_job_listings.csv' ✅")
else:
    print("❌ No detailed job data found to save.")
