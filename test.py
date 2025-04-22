import requests

url = "http://127.0.0.1:5000/api/jobs/search"
payload = {
    "keywords": "Data Scientist",
    "location": "DO",
    "platforms": ["LinkedIn", "Indeed"],
    "count": 10,
    "remote_only": True,
    "job_type": "Full-time"
}

response = requests.post(url, json=payload)
response = response.json()
data = response