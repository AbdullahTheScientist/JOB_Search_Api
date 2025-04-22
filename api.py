from flask import Flask, request, jsonify
import pandas as pd
from utils.scrapingdog_api import ScrapingDog
from functools import wraps
import json

app = Flask(__name__)

# ISO 3166 Alpha-2 Country Codes
COUNTRIES = {
    "AD": "Andorra",
    "AE": "United Arab Emirates",
    "AF": "Afghanistan",
    "AG": "Antigua and Barbuda",
    "AI": "Anguilla",
    "AL": "Albania",
    "AM": "Armenia",
    "AO": "Angola",
    "AQ": "Antarctica",
    "AR": "Argentina",
    "AS": "American Samoa",
    "AT": "Austria",
    "AU": "Australia",
    "AW": "Aruba",
    "AX": "Åland Islands",
    "AZ": "Azerbaijan",
    "BA": "Bosnia and Herzegovina",
    "BB": "Barbados",
    "BD": "Bangladesh",
    "BE": "Belgium",
    "BF": "Burkina Faso",
    "BG": "Bulgaria",
    "BH": "Bahrain",
    "BI": "Burundi",
    "BJ": "Benin",
    "BL": "Saint Barthélemy",
    "BM": "Bermuda",
    "BN": "Brunei Darussalam",
    "BO": "Bolivia (Plurinational State of)",
    "BQ": "Bonaire, Sint Eustatius and Saba",
    "BR": "Brazil",
    "BS": "Bahamas",
    "BT": "Bhutan",
    "BV": "Bouvet Island",
    "BW": "Botswana",
    "BY": "Belarus",
    "BZ": "Belize",
    "CA": "Canada",
    "CC": "Cocos (Keeling) Islands",
    "CD": "Congo, Democratic Republic of the",
    "CF": "Central African Republic",
    "CG": "Congo",
    "CH": "Switzerland",
    "CI": "Côte d'Ivoire",
    "CK": "Cook Islands",
    "CL": "Chile",
    "CM": "Cameroon",
    "CN": "China",
    "CO": "Colombia",
    "CR": "Costa Rica",
    "CU": "Cuba",
    "CV": "Cabo Verde",
    "CW": "Curaçao",
    "CX": "Christmas Island",
    "CY": "Cyprus",
    "CZ": "Czechia",
    "DE": "Germany",
    "DJ": "Djibouti",
    "DK": "Denmark",
    "DM": "Dominica",
    "DO": "Dominican Republic",
    "DZ": "Algeria",
    "EC": "Ecuador",
    "EE": "Estonia",
    "EG": "Egypt",
    "EH": "Western Sahara",
    "ER": "Eritrea",
    "ES": "Spain",
    "ET": "Ethiopia",
    "FI": "Finland",
    "FJ": "Fiji",
    "FK": "Falkland Islands (Malvinas)",
    "FM": "Micronesia (Federated States of)",
    "FO": "Faroe Islands",
    "FR": "France",
    "GA": "Gabon",
    "GB": "United Kingdom of Great Britain and Northern Ireland",
    "GD": "Grenada",
    "GE": "Georgia",
    "GF": "French Guiana",
    "GG": "Guernsey",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GL": "Greenland",
    "GM": "Gambia",
    "GN": "Guinea",
    "GP": "Guadeloupe",
    "GQ": "Equatorial Guinea",
    "GR": "Greece",
    "GS": "South Georgia and the South Sandwich Islands",
    "GT": "Guatemala",
    "GU": "Guam",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HK": "Hong Kong",
    "HM": "Heard Island and McDonald Islands",
    "HN": "Honduras",
    "HR": "Croatia",
    "HT": "Haiti",
    "HU": "Hungary",
    "ID": "Indonesia",
    "IE": "Ireland",
    "IM": "Isle of Man",
    "IN": "India",
    "IO": "British Indian Ocean Territory",
    "IQ": "Iraq",
    "IR": "Iran (Islamic Republic of)",
    "IS": "Iceland",
    "IT": "Italy",
    "JE": "Jersey",
    "JM": "Jamaica",
    "JO": "Jordan",
    "JP": "Japan",
    "KE": "Kenya",
    "KG": "Kyrgyzstan",
    "KH": "Cambodia",
    "KI": "Kiribati",
    "KM": "Comoros",
    "KN": "Saint Kitts and Nevis",
    "KP": "Korea (Democratic People's Republic of)",
    "KR": "Korea, Republic of",
    "KW": "Kuwait",
    "KY": "Cayman Islands",
    "KZ": "Kazakhstan",
    "LA": "Lao People's Democratic Republic",
    "LB": "Lebanon",
    "LC": "Saint Lucia",
    "LI": "Liechtenstein",
    "LK": "Sri Lanka",
    "LR": "Liberia",
    "LS": "Lesotho",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "LY": "Libya",
    "MA": "Morocco",
    "MC": "Monaco",
    "MD": "Moldova, Republic of",
    "ME": "Montenegro",
    "MF": "Saint Martin (French part)",
    "MG": "Madagascar",
    "MH": "Marshall Islands",
    "MK": "North Macedonia",
    "ML": "Mali",
    "MM": "Myanmar",
    "MN": "Mongolia",
    "MO": "Macao",
    "MP": "Northern Mariana Islands",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MS": "Montserrat",
    "MT": "Malta",
    "MU": "Mauritius",
    "MV": "Maldives",
    "MW": "Malawi",
    "MX": "Mexico",
    "MY": "Malaysia",
    "MZ": "Mozambique",
    "NA": "Namibia",
    "NC": "New Caledonia",
    "NE": "Niger",
    "NF": "Norfolk Island",
    "NG": "Nigeria",
    "NI": "Nicaragua",
    "NL": "Netherlands",
    "NO": "Norway",
    "NP": "Nepal",
    "NR": "Nauru",
    "NU": "Niue",}


def build_chips(date_posted, job_type, experience_level):
    chips_parts = []
    
    # Date posted
    if date_posted != "Any time":
        if date_posted == "Past 24 hours":
            chips_parts.append("date_posted:today")
        elif date_posted == "Past week":
            chips_parts.append("date_posted:week")
        elif date_posted == "Past month":
            chips_parts.append("date_posted:month")
    
    # Job type
    if job_type != "Any":
        job_type_map = {
            "Full-time": "FULLTIME",
            "Part-time": "PARTTIME",
            "Contract": "CONTRACTOR",
            "Internship": "INTERN",
            "Temporary": "TEMPORARY"
        }
        chips_parts.append(f"employment_type:{job_type_map[job_type]}")
    
    # Experience level
    if experience_level != "Any":
        exp_map = {
            "Internship": "INTERNSHIP",
            "Entry level": "ENTRY_LEVEL",
            "Associate": "ASSOCIATE",
            "Mid-Senior level": "MID_LEVEL",
            "Director": "DIRECTOR",
            "Executive": "EXECUTIVE"
        }
        chips_parts.append(f"experience_level:{exp_map[experience_level]}")
    
    return ",".join(chips_parts) if chips_parts else None

def filter_jobs_by_platform(jobs, platforms, select_all):
    """Filter jobs to only include selected platforms"""
    if select_all or not platforms:
        return jobs
    return [job for job in jobs if any(platform.lower() in job['platform'].lower() for platform in platforms)]

@app.route('/api/jobs/search', methods=['POST'])
def search_jobs():
    try:
        data = request.get_json()
        
        # Required parameters
        keywords = data.get('keywords', '')
        location = data.get('location', '')
        
        if not keywords:
            return jsonify({"error": "Please enter at least one keyword to search for"}), 400
        
        # Optional parameters with defaults
        platforms = data.get('platforms', ["LinkedIn", "Indeed", "Glassdoor", "Monster", "ZipRecruiter"])
        select_all = data.get('select_all', True)
        count = data.get('count', 10)
        days_ago = data.get('days_ago', 7)
        country = data.get('country', 'US')
        remote_only = data.get('remote_only', False)
        search_radius = data.get('search_radius', 10)
        job_type = data.get('job_type', 'Any')
        date_posted = data.get('date_posted', 'Any time')
        experience_level = data.get('experience_level', 'Any')
        
        # Build chips parameter
        chips_value = build_chips(date_posted, job_type, experience_level)
        
        # Call the ScrapingDog API
        api = ScrapingDog()
        jobs = api.search_jobs(
            keywords=keywords,
            location=location,
            platform=None,
            count=count,
            days_ago=days_ago,
            country=country,
            lrad=str(search_radius) if (search_radius > 0 and not remote_only) else None,
            ltype="1" if remote_only else None,
            chips=chips_value,
        )
        
        # Filter jobs based on selected platforms
        filtered_jobs = filter_jobs_by_platform(jobs, platforms, select_all)
        
        if not filtered_jobs:
            return jsonify({"message": "No jobs found matching your criteria", "results": []}), 200
        
        # Prepare response
        response = {
            "count": len(filtered_jobs),
            "results": filtered_jobs
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/jobs/countries', methods=['GET'])
def get_countries():
    return jsonify(COUNTRIES), 200

@app.route('/api/jobs/platforms', methods=['GET'])
def get_platforms():
    platforms = ["LinkedIn", "Indeed", "Glassdoor", "Monster", "ZipRecruiter"]
    return jsonify(platforms), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)