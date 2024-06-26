import dns.resolver
import tldextract
import requests


def extract_domain_from_url(url):
    # Parse the URL and extract the subdomain, domain, and suffix
    extracted = tldextract.extract(url)
    # Combine the subdomain, domain, and suffix to get the full domain
    full_domain = f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}"
    return full_domain


def get_cname(domain):
    domain = extract_domain_from_url(domain)
    cnames = []
    try:
        while True:
            answers = dns.resolver.resolve(domain, "CNAME")
            domain = answers[0].target.to_text().rstrip(".")  # Remove trailing dot
            cnames.append(domain)
    except Exception as _:
        pass
    if len(cnames) == 0:
        return None
    return cnames[-1]


def get_asn_description(ip):
    if ip == "" or ip is None:
        return None, None

    # Request to locally running API
    response = requests.get(f"http://127.0.0.1:80/v1/as/ip/{ip}")
    data = response.json()
    if "as_number" in data and "as_description" in data:
        # Return tuple with ASN and description
        return (data["as_description"], data["as_number"])
    return None, None
