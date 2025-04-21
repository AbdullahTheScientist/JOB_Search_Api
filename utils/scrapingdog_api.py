import json
import requests


class ScrapingDog:
    def search_jobs(
        self,
        keywords,
        location,
        platform=None,
        count=5,
        days_ago=5,
        country="us",
        language="en_us",
        next_page_token=None,
        chips=None,
        lrad=None,
        ltype=None,
        uds=None
    ):
        try:
            url = "https://api.scrapingdog.com/google_jobs"
            api_key = "6805ab3cd8dc6061cf559e64"

            params = {
                "api_key": api_key,
                "query": f"{keywords} jobs in {location}".replace(" ", "+"),
                "country": country,
                "language": language,
                "chips": f"date_posted:{days_ago}d" if not chips else chips,
                "next_page_token": next_page_token,
                "lrad": lrad,
                "ltype": ltype,
                "uds": uds
            }

            # Remove None values to avoid invalid params
            params = {k: v for k, v in params.items() if v is not None}

            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
            
            if "error" in data:
                print(f"ScrapingDog API error: {data['error']}")
                return []

            jobs = []
            if "jobs_results" in data:
                job_results = data["jobs_results"]

                for i, job in enumerate(job_results):
                    if i >= count:
                        break

                    title = job.get("title", "Unknown Title")
                    company = job.get("company_name", "Unknown Company")
                    location_name = job.get("location", "Unknown Location")
                    
                    description = job.get("description") or job.get("snippet", "No available description")

                    # Extract job type
                    job_type = "Not Specified"
                    if "detected_extensions" in job:
                        ext = job["detected_extensions"]
                        job_type = ext.get("schedule_type") or ext.get("employment_type", job_type)
            

                    # Apply URL
                    apply_url = None
                    if "apply_link" in job and "link" in job["apply_link"]:
                        apply_url = job["apply_link"]["link"]
                    elif "apply_options" in job and job["apply_options"]:
                        apply_url = job["apply_options"][0].get("link")
                    elif "job_id" in job and "related_links" in data:
                        for link in data.get("related_links", []):
                            if "apply" in link.get("text", "").lower():
                                apply_url = link.get("link")
                                break
                    if not apply_url and "job_id" in job:
                        apply_url = f"https://www.google.com/search?q={job['job_id']}"

                    date_posted = "Recent"
                    if "detected_extensions" in job and "posted_at" in job["detected_extensions"]:
                        date_posted = job["detected_extensions"]["posted_at"]

                    job_platform = job.get("via", "unknown")

                    if platform and platform.lower() != "all" and platform.lower() not in job_platform.lower():
                        continue

                    job_entry = {
                        "title": title,
                        "company": company,
                        "location": location_name,
                        "description": description,
                        "url": apply_url,
                        "apply_url": apply_url,
                        "date_posted": date_posted,
                        "platform": job_platform,
                        "job_type": job_type,
                        "is_real_job": True
                    }

                    jobs.append(job_entry)

                return jobs
            else:
                print("No job results found in response.")
                return []

        except Exception as e:
            print(f"ScrapingDog API error: {e}")
            return []