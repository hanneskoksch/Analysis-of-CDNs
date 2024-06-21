import csv
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import tldextract


# Function to check if request is an actual URL or embedded data
def is_embedded_data(request_url):
    # Check if the URL starts with "data:"
    if request_url.startswith("data:"):
        return True
    return False


# Path to chromedriver
# (download from https://googlechromelabs.github.io/chrome-for-testing/)
chromedriver_path = "chromedriver-mac-arm64/chromedriver"

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Enable performance logging for insights into network requests
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# Start WebDriver
service = ChromeService(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# List to store all requests
all_requests = []

# Define the URL to visit
most_popular_website_urls = [
    "https://www.google.com",
    "https://www.youtube.com",
    "https://www.facebook.com",
    "https://www.baidu.com",
    "https://www.wikipedia.org",
    "https://www.qq.com",
    "https://www.taobao.com",
    "https://www.tmall.com",
    "https://www.yahoo.com",
    "https://www.amazon.com",
]

for index, url in enumerate(most_popular_website_urls):
    print(f"Fetching url {
          index+1} of {len(most_popular_website_urls)} - ({url})")

    # Visit the URL
    driver.get(url)
    # Wait for the page to load and requests to complete
    time.sleep(10)

    # Get performance logs
    logs = driver.get_log("performance")

    # Process logs and extract request details
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if log["method"] == "Network.requestWillBeSent":
            request = log["params"]["request"]
            method = request["method"]
            request_url = request["url"]
            # headers = request['headers']
            all_requests.append(
                {
                    "page": url,
                    "method": method,
                    "full_url": request_url,
                    "subdomain": tldextract.extract(request_url).subdomain,
                    "domain": tldextract.extract(request_url).domain,
                    "suffix": tldextract.extract(request_url).suffix,
                    # "headers": headers
                }
            )

# Save requests to a CSV file
with open("requests.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Page", "Method", "Full URL", "Subdomain", "Domain", "Suffix"])
    # writer.writerow(["Method", "URL", "Headers"])
    for request in all_requests:
        if not is_embedded_data(request["full_url"]):
            writer.writerow(
                [
                    request["page"],
                    request["method"],
                    request["full_url"],
                    request["subdomain"],
                    request["domain"],
                    request["suffix"],
                ]
            )
            # writer.writerow([request["method"], request["url"], json.dumps(request["headers"])])

# Quit the driver
driver.quit()
