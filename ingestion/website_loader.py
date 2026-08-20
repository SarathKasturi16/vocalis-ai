from bs4 import BeautifulSoup
import requests

def load_website(url: str) -> str:
    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "AI-Assessment-KB/1.0"}
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    return soup.get_text("\n", strip=True)
