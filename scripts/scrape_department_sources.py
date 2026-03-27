#!/usr/bin/env python3
"""
Targeted scraper for the Electrical Engineering Department knowledge base.

This script is designed for offline ingestion, not runtime chatbot lookup.
It fetches a curated set of official department/faculty pages, stores raw HTML,
extracts cleaned content, and writes structured outputs under data/web/.
"""

from __future__ import annotations

import json
import hashlib
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "data" / "web"
RAW_ROOT = DATA_ROOT / "raw"
CLEAN_ROOT = DATA_ROOT / "clean"
DOWNLOAD_ROOT = DATA_ROOT / "downloads"
INDEX_PATH = DATA_ROOT / "index.json"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 30

FOOTER_MARKERS = (
    "Copyright",
    "All rights reserved",
)


@dataclass
class SourceSpec:
    key: str
    url: str
    category: str
    parser: str
    title: str
    description: str


SOURCES: List[SourceSpec] = [
    SourceSpec(
        key="department_contact",
        url="https://ee-eng.su.ac.th/ContactUs.aspx",
        category="contact",
        parser="contact",
        title="Department Contact Information",
        description="Official department contact page with address, phone numbers, and Facebook page.",
    ),
    SourceSpec(
        key="department_lecturers",
        url="https://ee-eng.su.ac.th/Staff.aspx?Type=Lecturer",
        category="faculty",
        parser="staff",
        title="Department Academic Staff",
        description="Official lecturer directory for the department.",
    ),
    SourceSpec(
        key="department_support_staff",
        url="https://ee-eng.su.ac.th/Staff.aspx?Type=Officials",
        category="staff",
        parser="staff",
        title="Department Support Staff",
        description="Official support staff directory for the department.",
    ),
    SourceSpec(
        key="program_ecs",
        url="https://ee-eng.su.ac.th/Program.aspx?Course=ElectronicsAndComputerSystemsEngineering",
        category="academic",
        parser="program",
        title="Electronics and Computer Systems Engineering Program",
        description="Bachelor program page for Electronics and Computer Systems Engineering.",
    ),
    SourceSpec(
        key="program_electrical_communications",
        url="https://ee-eng.su.ac.th/Program.aspx?Course=ElectricalCommunicationsEngineering",
        category="academic",
        parser="program",
        title="Electrical Communications Engineering Program",
        description="Bachelor program page for Electrical Communications Engineering.",
    ),
    SourceSpec(
        key="program_master_ece",
        url="https://ee-eng.su.ac.th/Program.aspx?Course=ElectricalAndComputerEngineering",
        category="academic",
        parser="program",
        title="Electrical and Computer Engineering Master's Program",
        description="Master's program page for Electrical and Computer Engineering.",
    ),
    SourceSpec(
        key="faculty_department_overview",
        url="https://eng2.su.ac.th/department_electrical_engineering.php",
        category="overview",
        parser="faculty_overview",
        title="Faculty Department Overview",
        description="Faculty website overview page for the department, including history and curriculum summary.",
    ),
]


def ensure_directories() -> None:
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    CLEAN_ROOT.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_ROOT.mkdir(parents=True, exist_ok=True)


def create_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def get_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize_filename(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")
    if not safe:
        safe = "file"
    if len(safe) > 80:
        safe = safe[:80].rstrip("_")
    return safe


def clean_lines(lines: List[str]) -> List[str]:
    cleaned: List[str] = []
    previous = None
    for line in lines:
        normalized = " ".join(line.split()).strip()
        if not normalized:
            continue
        if normalized == previous:
            continue
        previous = normalized
        cleaned.append(normalized)
    return cleaned


def extract_main_text_lines(soup: BeautifulSoup) -> List[str]:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text("\n", strip=True)
    raw_lines = text.splitlines()
    lines = clean_lines(raw_lines)

    filtered: List[str] = []
    for line in lines:
        if line.startswith("Image"):
            continue
        if line in {"TH", "EN", "หน้าแรก", "เกี่ยวกับเรา", "บุคลากร"}:
            continue
        filtered.append(line)
    return filtered


def trim_footer(lines: List[str]) -> List[str]:
    for index, line in enumerate(lines):
        if any(marker in line for marker in FOOTER_MARKERS):
            return lines[:index]
    return lines


def find_emails(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)


def parse_contact_page(soup: BeautifulSoup, source: SourceSpec) -> Dict:
    page_text = soup.get_text("\n", strip=True)

    address = ""
    address_header = soup.find(id="cphData_lbHead") or soup.find(id="cphData_Label2")
    if address_header:
        header_row = address_header.find_parent("tr")
        if header_row:
            next_row = header_row.find_next_sibling("tr")
            if next_row:
                address = " ".join(next_row.get_text(" ", strip=True).split())

    contact_lines: List[str] = []
    contact_header = soup.find(id="cphData_Label1") or soup.find(id="cphData_Label3")
    if contact_header:
        header_row = contact_header.find_parent("tr")
        if header_row:
            next_row = header_row.find_next_sibling("tr")
            if next_row:
                raw_contact_text = next_row.get_text("\n", strip=True)
                contact_lines = clean_lines(raw_contact_text.splitlines())

    phones = re.findall(r"โทรศัพท์(?:\s*/\s*โทรสาร)?\s*:\s*[0-9\- ]+(?:ต่อ\s*\d+)?", page_text)
    facebook_name_match = re.search(
        r"Department of Electrical Engineering - Silpakorn University",
        page_text,
    )

    relevant: List[str] = []
    if address:
        relevant.append("สถานที่ตั้ง")
        relevant.append(address)
    if contact_lines or phones:
        relevant.append("ข้อมูลการติดต่อ")
        if contact_lines:
            relevant.extend(contact_lines)
        else:
            relevant.extend(dict.fromkeys(" ".join(phone.split()) for phone in phones))
    if facebook_name_match:
        relevant.append("เฟสบุค : Department of Electrical Engineering - Silpakorn University")

    facebook_url = None
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if "facebook.com" in href:
            facebook_url = href
            break

    markdown_lines = [
        f"# {source.title}",
        "",
        f"Source URL: {source.url}",
        "",
        "## Extracted Content",
        "",
    ]
    markdown_lines.extend(f"- {line}" for line in relevant)

    return {
        "kind": "contact_page",
        "title": source.title,
        "source_url": source.url,
        "category": source.category,
        "scraped_at": get_timestamp(),
        "facebook_url": facebook_url,
        "lines": relevant,
        "markdown": "\n".join(markdown_lines) + "\n",
    }


def looks_like_person_name(line: str) -> bool:
    if "@" in line or "โทรศัพท์" in line or "เฟสบุค" in line:
        return False
    if len(line) < 6:
        return False
    title_markers = ("ศาสตราจารย์", "อาจารย์", "นาย", "นาง", "นางสาว")
    return any(marker in line for marker in title_markers)


def parse_staff_page(soup: BeautifulSoup, source: SourceSpec) -> Dict:
    entries: List[Dict[str, str]] = []
    for card in soup.select("a.ContainPerson"):
        prefix = card.select_one("span[id$='_lbPrefix']")
        name = card.select_one("span[id$='_lbName']")
        role = card.select_one("span[id$='_lbPosition']")
        email = card.select_one("span[id$='_lbEmail']")

        if not name:
            continue

        href = card.get("href", "").strip()
        detail_url = None
        match = re.search(r"StaffDetail\.aspx\?PersonID=\d+&amp;Type=[A-Za-z]+", href)
        if match:
            detail_url = urljoin(source.url, match.group(0).replace("&amp;", "&"))

        full_name = " ".join(
            part.strip()
            for part in [
                prefix.get_text(" ", strip=True) if prefix else "",
                name.get_text(" ", strip=True),
            ]
            if part.strip()
        )

        email_text = email.get_text(" ", strip=True) if email else ""
        email_matches = find_emails(email_text)

        entries.append(
            {
                "name": full_name,
                "role": role.get_text(" ", strip=True) if role else "",
                "email": email_matches[0] if email_matches else "",
                "detail_url": detail_url or "",
                "source_url": source.url,
                "category": source.category,
            }
        )

    markdown_lines = [
        f"# {source.title}",
        "",
        f"Source URL: {source.url}",
        "",
        "## Directory",
        "",
    ]
    for entry in entries:
        markdown_lines.append(f"### {entry['name']}")
        if entry["role"]:
            markdown_lines.append(f"- Role: {entry['role']}")
        if entry["email"]:
            markdown_lines.append(f"- Email: {entry['email']}")
        markdown_lines.append("")

    return {
        "kind": "staff_directory",
        "title": source.title,
        "source_url": source.url,
        "category": source.category,
        "scraped_at": get_timestamp(),
        "entries": entries,
        "markdown": "\n".join(markdown_lines).strip() + "\n",
    }


def collect_links(soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
    links: List[Dict[str, str]] = []
    seen = set()
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        text = " ".join(anchor.get_text(" ", strip=True).split())
        absolute_url = urljoin(base_url, href)
        key = (text, absolute_url)
        if key in seen:
            continue
        seen.add(key)
        links.append({"text": text, "url": absolute_url})
    return links


def parse_program_page(soup: BeautifulSoup, source: SourceSpec) -> Dict:
    lines = trim_footer(extract_main_text_lines(soup))
    links = collect_links(soup, source.url)
    download_links = [
        link for link in links
        if "download" in link["text"].lower() or link["url"].lower().endswith(".pdf")
    ]

    markdown_lines = [
        f"# {source.title}",
        "",
        f"Source URL: {source.url}",
        "",
        "## Extracted Content",
        "",
    ]
    markdown_lines.extend(f"- {line}" for line in lines)

    if download_links:
        markdown_lines.extend(["", "## Download Links", ""])
        markdown_lines.extend(f"- {link['text'] or 'Download'}: {link['url']}" for link in download_links)

    return {
        "kind": "program_page",
        "title": source.title,
        "source_url": source.url,
        "category": source.category,
        "scraped_at": get_timestamp(),
        "lines": lines,
        "download_links": download_links,
        "markdown": "\n".join(markdown_lines) + "\n",
    }


def parse_faculty_overview(soup: BeautifulSoup, source: SourceSpec) -> Dict:
    lines = extract_main_text_lines(soup)
    start = next((i for i, line in enumerate(lines) if "แนะนำภาควิศวกรรมไฟฟ้า" in line), 0)
    relevant = trim_footer(lines[start:])
    links = collect_links(soup, source.url)
    download_links = [
        link for link in links
        if "download" in link["text"].lower() or link["url"].lower().endswith(".pdf")
    ]

    markdown_lines = [
        f"# {source.title}",
        "",
        f"Source URL: {source.url}",
        "",
        "## Extracted Content",
        "",
    ]
    markdown_lines.extend(f"- {line}" for line in relevant)

    if download_links:
        markdown_lines.extend(["", "## Download Links", ""])
        markdown_lines.extend(f"- {link['text'] or 'Download'}: {link['url']}" for link in download_links)

    return {
        "kind": "faculty_overview",
        "title": source.title,
        "source_url": source.url,
        "category": source.category,
        "scraped_at": get_timestamp(),
        "lines": relevant,
        "download_links": download_links,
        "markdown": "\n".join(markdown_lines) + "\n",
    }


PARSERS: Dict[str, Callable[[BeautifulSoup, SourceSpec], Dict]] = {
    "contact": parse_contact_page,
    "staff": parse_staff_page,
    "program": parse_program_page,
    "faculty_overview": parse_faculty_overview,
}


def download_pdf(session: requests.Session, url: str) -> Optional[str]:
    parsed = urlparse(url)
    if not parsed.scheme.startswith("http"):
        return None

    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        return None

    content_type = response.headers.get("Content-Type", "").lower()
    if "pdf" not in content_type and not url.lower().endswith(".pdf"):
        return None

    normalized_key = parsed.path.lower()
    original_name = Path(parsed.path).name or "download.pdf"
    base_name = sanitize_filename(Path(original_name).stem or "download")
    digest = hashlib.sha1(normalized_key.encode("utf-8")).hexdigest()[:10]
    filename = f"{base_name[:50]}_{digest}.pdf"

    output_path = DOWNLOAD_ROOT / filename
    if output_path.exists():
        return str(output_path.relative_to(PROJECT_ROOT))
    output_path.write_bytes(response.content)
    return str(output_path.relative_to(PROJECT_ROOT))


def save_outputs(source: SourceSpec, html: str, parsed: Dict, session: requests.Session) -> Dict:
    raw_path = RAW_ROOT / f"{source.key}.html"
    raw_path.write_text(html, encoding="utf-8")

    markdown_path = CLEAN_ROOT / f"{source.key}.md"
    markdown_path.write_text(parsed["markdown"], encoding="utf-8")

    json_path = CLEAN_ROOT / f"{source.key}.json"
    json_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")

    downloaded_files: List[str] = []
    for link in parsed.get("download_links", []):
        local_path = download_pdf(session, link["url"])
        if local_path:
            downloaded_files.append(local_path)

    return {
        "key": source.key,
        "title": source.title,
        "category": source.category,
        "source_url": source.url,
        "scraped_at": parsed["scraped_at"],
        "raw_html_path": str(raw_path.relative_to(PROJECT_ROOT)),
        "markdown_path": str(markdown_path.relative_to(PROJECT_ROOT)),
        "json_path": str(json_path.relative_to(PROJECT_ROOT)),
        "downloaded_files": downloaded_files,
    }


def scrape_source(session: requests.Session, source: SourceSpec) -> Dict:
    parser = PARSERS[source.parser]
    response = session.get(source.url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or response.encoding

    soup = BeautifulSoup(response.text, "html.parser")
    parsed = parser(soup, source)
    return save_outputs(source, response.text, parsed, session)


def main() -> None:
    ensure_directories()
    session = create_session()
    results: List[Dict] = []
    failures: List[Dict[str, str]] = []

    print("Starting targeted department source scraping...")
    for source in SOURCES:
        print(f"- Scraping {source.key}: {source.url}")
        try:
            result = scrape_source(session, source)
            results.append(result)
            print(f"  Saved: {result['markdown_path']}")
        except requests.RequestException as exc:
            failures.append({"key": source.key, "url": source.url, "error": str(exc)})
            print(f"  Failed: {exc}")

    index = {
        "generated_at": get_timestamp(),
        "sources": [asdict(source) for source in SOURCES],
        "results": results,
        "failures": failures,
    }
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    print("")
    print(f"Completed. Index written to {INDEX_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Successful sources: {len(results)}")
    print(f"Failed sources: {len(failures)}")


if __name__ == "__main__":
    main()
