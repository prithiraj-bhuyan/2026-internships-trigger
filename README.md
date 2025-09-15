# 2026 Internships Trigger

## Overview
This project monitors and tracks new Summer 2026 internship opportunities by scraping a public GitHub repository's README file, parsing the internship listings, and sending email alerts for new postings. It also maintains a local JSON database of all internships found.

## Main Components

### 1. monitor_script.py
- **Purpose:** Main script for monitoring, parsing, and alerting about new internships.
- **Key Features:**
  - Fetches the latest internship table from a remote README file.
  - Parses internship listings (company, role, location, application link, date posted).
  - Compares with previously saved data to detect new internships.
  - Sends email notifications for new internships using SMTP (Gmail).
  - Saves the current internship data to `internships_data.json`.
- **Configuration:**
  - Requires environment variables for email credentials: `EMAIL_USER`, `EMAIL_PASSWORD`, `NOTIFY_EMAIL`.
  - Uses `pytz` for timezone-aware timestamps in notifications.

### 2. internships_data.json
- **Purpose:** Stores all internship listings found, with metadata.
- **Structure:**
  - `last_updated`: ISO timestamp of last update.
  - `total_count`: Number of internships.
  - `internships`: List of internship objects (id, company, role, location, apply_url, date_posted, found_at).

### 3. requirements.txt
- **Purpose:** Lists Python dependencies for the project.
- **Contents:**
  - Flask
  - requests
  - gunicorn
  - pytz

## How It Works
1. The script fetches the latest internship table from a remote GitHub README.
2. It parses the table, extracting all relevant internship details.
3. It loads previously saved data and compares to find new internships.
4. If new internships are found, it sends an email alert with details.
5. It saves the current internship data for future comparisons.

## Usage
- Set up the required environment variables for email notifications.
- Install dependencies: `pip install -r requirements.txt`
- Run the script: `python monitor_script.py`

## Example Internship Entry
```
{
  "id": "59b5ee1922dd6224463bb6238467affe",
  "company": "Microsoft",
  "role": "Undergraduate Research Intern, Computing",
  "location": "Redmond, WA; New York City, NY",
  "apply_url": "https://www.microsoft.com/en-us/research/academic-program/undergraduate-research-internship-computing/",
  "date_posted": "Sep 13",
  "found_at": "2025-09-15T11:32:15.829427"
}
```

## Notes
- The script is designed to be run periodically (e.g., via GitHub Actions or a cron job).
- Email notifications will only be sent if new internships are detected.
- The project is easily extensible to monitor other sources or add more notification methods.

## License
MIT License
