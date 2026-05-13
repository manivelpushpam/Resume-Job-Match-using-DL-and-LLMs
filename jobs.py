import cloudscraper
from bs4 import BeautifulSoup
import csv
import time
import urllib.parse
import sys
import random

def get_random_user_agent():
    """Returns a random user agent to avoid detection."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]
    return random.choice(user_agents)

def detect_indeed_domain(location):
    """Detects the appropriate Indeed domain based on location."""
    location_lower = location.lower()
    if 'india' in location_lower or 'mumbai' in location_lower or 'delhi' in location_lower or 'bangalore' in location_lower or 'bengaluru' in location_lower:
        return 'https://www.indeed.co.in'
    elif 'uk' in location_lower or 'london' in location_lower:
        return 'https://www.indeed.co.uk'
    elif 'canada' in location_lower or 'toronto' in location_lower:
        return 'https://www.indeed.ca'
    else:
        return 'https://www.indeed.com'

def get_job_details(card, base_url):
    """Extracts job details from a single job card."""
    job = {}
    
    # 1. Job Name / Title
    title_elem = card.select_one('h2.jobTitle span[title]')
    if not title_elem:
        title_elem = card.select_one('h2.jobTitle span')
    if not title_elem:
        title_elem = card.select_one('h2.jobTitle')
    if not title_elem:
        title_elem = card.select_one('a[data-jk]')
    job['job_name'] = title_elem.get_text(strip=True) if title_elem else "N/A"

    # 2. Company Name
    company_elem = card.select_one('[data-testid="company-name"]')
    if not company_elem:
        company_elem = card.select_one('span.companyName')
    if not company_elem:
        company_elem = card.select_one('.company')
    job['company_name'] = company_elem.get_text(strip=True) if company_elem else "N/A"

    # 3. Location
    location_elem = card.select_one('[data-testid="text-location"]')
    if not location_elem:
        location_elem = card.select_one('div.companyLocation')
    if not location_elem:
        location_elem = card.select_one('.location')
    job['location'] = location_elem.get_text(strip=True) if location_elem else "N/A"

    # 4. Description (Snippet)
    desc_elem = card.select_one('div.job-snippet')
    if not desc_elem:
        desc_elem = card.select_one('.job-snippet')
    if not desc_elem:
        desc_elem = card.select_one('div.summary')
    job['description'] = desc_elem.get_text(strip=True) if desc_elem else "N/A"

    # 5. Role (same as job name)
    job['role'] = job['job_name']

    # 6. URL
    url_elem = card.select_one('a.jcs-JobTitle')
    if not url_elem:
        url_elem = card.select_one('h2.jobTitle a')
    if not url_elem:
        url_elem = card.select_one('a[data-jk]')
    
    if url_elem and url_elem.get('href'):
        href = url_elem.get('href')
        if href.startswith('http'):
            job['url'] = href
        else:
            job['url'] = base_url + href
    else:
        job['url'] = "N/A"

    return job

def generate_demo_jobs(position, location, count=20):
    """Generates demo job data when scraping fails."""
    import random
    
    companies = [
        "Tech Innovations Inc", "AI Solutions Ltd", "DataCorp", "Future Systems",
        "Smart Analytics", "Cloud Dynamics", "Neural Networks Co", "Quantum Tech",
        "Digital Ventures", "Cyber Solutions", "Innovate Labs", "NextGen AI",
        "Machine Learning Pro", "Deep Learning Inc", "AI Research Group"
    ]
    
    cities_india = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai", "Gurgaon"]
    cities_us = ["New York", "San Francisco", "Seattle", "Austin", "Boston"]
    
    is_india = 'india' in location.lower() or any(city.lower() in location.lower() for city in cities_india)
    cities = cities_india if is_india else cities_us
    
    jobs = []
    for i in range(count):
        job = {
            'job_name': f"{position} - Level {random.choice(['Junior', 'Mid', 'Senior'])}",
            'company_name': random.choice(companies),
            'location': random.choice(cities),
            'description': f"We are looking for a talented {position} to join our team. Responsibilities include developing AI models, working with large datasets, and collaborating with cross-functional teams. {random.choice(['Remote work available.', '5+ years experience required.', 'Excellent benefits package.'])}",
            'role': position,
            'url': f"https://www.indeed.com/viewjob?jk=demo{i:04d}"
        }
        jobs.append(job)
    
    return jobs

def scrape_indeed_jobs(position, location, target_count=20, use_demo=False):
    # If demo mode is enabled, return demo data
    if use_demo:
        print("\n⚠️  Running in DEMO mode (generating sample data)")
        print("   Indeed's anti-scraping protection is blocking real requests.\n")
        time.sleep(1)
        return generate_demo_jobs(position, location, target_count)
    
    jobs = []
    start = 0
    
    # Detect appropriate domain
    base_url = detect_indeed_domain(location)
    print(f"Using Indeed domain: {base_url}")
    
    # Create a cloudscraper session to bypass Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    
    print(f"Scraping jobs for '{position}' in '{location}'...")

    max_attempts = 5  # Limit pagination attempts
    attempts = 0

    while len(jobs) < target_count and attempts < max_attempts:
        attempts += 1
        
        # Dynamic headers with random user agent
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': f'{base_url}/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
        }

        url = f"{base_url}/jobs?q={urllib.parse.quote(position)}&l={urllib.parse.quote(location)}&start={start}"
        
        try:
            # Random delay to mimic human behavior
            time.sleep(random.uniform(2, 4))
            
            response = scraper.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"Failed to retrieve page. Status code: {response.status_code}")
                # Save debug HTML
                with open("debug_indeed.html", "wb") as f:
                    f.write(response.content)
                print("Saved debug_indeed.html for inspection.")
                break
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors to find job cards
            job_cards = soup.select('.job_seen_beacon')
            if not job_cards:
                job_cards = soup.select('.jobsearch-SerpJobCard')
            if not job_cards:
                job_cards = soup.select('.result')
            if not job_cards:
                job_cards = soup.select('[data-jk]')

            if not job_cards:
                print("No jobs found. Possible reasons:")
                print("  - Indeed blocked the request (anti-scraping)")
                print("  - No jobs match the search criteria")
                print("  - HTML structure changed")
                break

            print(f"Found {len(job_cards)} job cards on page {attempts}")

            for card in job_cards:
                if len(jobs) >= target_count:
                    break
                
                try:
                    job = get_job_details(card, base_url)
                    # Only add if we got meaningful data
                    if job['job_name'] != "N/A" and job['company_name'] != "N/A":
                        jobs.append(job)
                        print(f"  [{len(jobs)}] {job['job_name']} at {job['company_name']}")
                except Exception as e:
                    print(f"Error parsing a card: {e}")
                    continue

            # If no new jobs found, stop
            if not job_cards or len(job_cards) == 0:
                break

            start += 10

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return jobs

def save_to_csv(jobs, filename="indeed_jobs_3.csv"):
    if not jobs:
        print("No jobs to save.")
        return

    keys = ['job_name', 'company_name', 'location', 'description', 'role', 'url']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(jobs)
    
    print(f"\n✓ Successfully saved {len(jobs)} jobs to {filename}")

def jobs_main(position, location):
    print("=" * 50)
    print("       Indeed Job Scraper")
    print("=" * 50)
    
    # Check for demo mode flag
    use_demo = '--demo' in sys.argv

    if len(sys.argv) > 2 and sys.argv[1] != '--demo':
        position = sys.argv[1]
        location = sys.argv[2]
    elif len(sys.argv) > 3 and sys.argv[1] == '--demo':
        position = sys.argv[2]
        location = sys.argv[3]
    else:
        position = position
        location = location
    # Try real scraping first
    jobs = scrape_indeed_jobs(position, location, target_count=20, use_demo=use_demo)
    
    # If scraping failed and not in demo mode, offer to use demo
    if not jobs and not use_demo:
        print("\n" + "=" * 50)
        print("⚠️  SCRAPING FAILED - Indeed blocked the request")
        print("=" * 50)
        print("\nIndeed uses advanced anti-scraping protection (Cloudflare).")
        print("\nOptions to proceed:")
        print("  1. Use DEMO mode (generates sample data)")
        print("  2. Use Selenium/Playwright (headless browser)")
        print("  3. Use a commercial scraping API")
        print("  4. Use Indeed's official API (if available)")
        
        choice = input("\nWould you like to run in DEMO mode? (y/n): ").lower()
        if choice == 'y':
            print("\nGenerating demo data...")
            jobs = generate_demo_jobs(position, location, 15)
    
    save_to_csv(jobs)

if __name__ == "__main__":

    position = input("enter position: ")
    location = input("enter location: ")
    

    jobs_main(position, location)
