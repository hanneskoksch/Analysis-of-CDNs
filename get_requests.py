import csv
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

# Path to chromedriver 
# (download from https://googlechromelabs.github.io/chrome-for-testing/)
chromedriver_path = 'chromedriver-mac-arm64/chromedriver'

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Enable performance logging for insights into network requests
chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

# Start WebDriver
service = ChromeService(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the URL to visit
url = "https://www.google.com"

# Visit the URL
driver.get(url)
# Wait for the page to load and requests to complete
time.sleep(10)  

# Get performance logs
logs = driver.get_log('performance')

# Process logs and extract request details
requests = []
for entry in logs:
    log = json.loads(entry['message'])['message']
    if log['method'] == 'Network.requestWillBeSent':
        request = log['params']['request']
        method = request['method']
        request_url = request['url']
        headers = request['headers']
        requests.append({
            "method": method,
            "url": request_url,
            "headers": headers
        })

# Save requests to a CSV file
with open("requests.csv", mode="w", newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Page", "Method", "URL"])
    # writer.writerow(["Method", "URL", "Headers"])
    for request in requests:
        writer.writerow([url, request["method"], request["url"]])
        # writer.writerow([request["method"], request["url"], json.dumps(request["headers"])])

# Quit the driver
driver.quit()
