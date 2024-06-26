import dns.resolver
import tldextract


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
