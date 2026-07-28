#!/usr/bin/env python3
"""
Crawler for Guangdong Provincial Games basketball men's B group scores.
Tries multiple data sources and updates scores.json if new scores are found.
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies: requests, beautifulsoup4")
    sys.exit(1)

# B group match definitions (must match HTML)
B_MATCHES = {
    0: {"teamA": "深圳", "teamB": "江门", "round": "第一轮"},
    1: {"teamA": "佛山", "teamB": "深圳", "round": "第二轮"},
    2: {"teamA": "中山", "teamB": "深圳", "round": "第三轮"},
    3: {"teamA": "中山", "teamB": "佛山", "round": "第一轮"},
    4: {"teamA": "江门", "teamB": "中山", "round": "第二轮"},
    5: {"teamA": "江门", "teamB": "佛山", "round": "第三轮"},
}

TEAM_ALIASES = {
    "深圳": ["深圳", "深圳市", "深圳队"],
    "江门": ["江门", "江门市", "江门队"],
    "佛山": ["佛山", "佛山市", "佛山队"],
    "中山": ["中山", "中山市", "中山队"],
}

SCORES_FILE = Path(__file__).parent.parent.parent / "scores.json"


def load_current_scores():
    """Load existing scores from JSON file."""
    if not SCORES_FILE.exists():
        return {}
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_scores(scores):
    """Save scores to JSON file."""
    scores["updated_at"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
    scores["source"] = "crawler"
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


def extract_scores_from_text(text):
    """
    Extract basketball scores from text using multiple patterns.
    Returns dict: {match_idx: {"a": scoreA, "b": scoreB}}
    """
    found = {}

    # Pattern 1: "以 X:Y 战胜" or "以 X比Y "
    # Pattern 2: "X:Y" near team names
    # Pattern 3: "X 比 Y" near team names

    for idx, match in B_MATCHES.items():
        team_a = match["teamA"]
        team_b = match["teamB"]
        aliases_a = TEAM_ALIASES.get(team_a, [team_a])
        aliases_b = TEAM_ALIASES.get(team_b, [team_b])

        # Try to find score near both team names
        for alias_a in aliases_a:
            for alias_b in aliases_b:
                # Pattern: teamA ... X:Y ... teamB
                pattern = re.compile(
                    rf"{re.escape(alias_a)}.*?[:：]\s*(\d+)\s*[:\-：]\s*(\d+)\s*.*?{re.escape(alias_b)}",
                    re.IGNORECASE | re.DOTALL,
                )
                m = pattern.search(text)
                if m:
                    found[idx] = {"a": int(m.group(1)), "b": int(m.group(2))}
                    break

                # Pattern: teamB ... X:Y ... teamA
                pattern2 = re.compile(
                    rf"{re.escape(alias_b)}.*?[:：]\s*(\d+)\s*[:\-：]\s*(\d+)\s*.*?{re.escape(alias_a)}",
                    re.IGNORECASE | re.DOTALL,
                )
                m2 = pattern2.search(text)
                if m2:
                    found[idx] = {"a": int(m2.group(1)), "b": int(m2.group(2))}
                    break

                # Pattern: "以 X比Y 战胜/击败" with team names
                pattern3 = re.compile(
                    rf"{re.escape(alias_a)}.*?以\s*(\d+)\s*比\s*(\d+)\s*.*?{re.escape(alias_b)}",
                    re.IGNORECASE | re.DOTALL,
                )
                m3 = pattern3.search(text)
                if m3:
                    found[idx] = {"a": int(m3.group(1)), "b": int(m3.group(2))}
                    break

                # Pattern: simple "X:Y" in context
                pattern4 = re.compile(
                    rf"{re.escape(alias_a)}.*?\b(\d+)\s*[:\-：]\s*(\d+)\b.*?{re.escape(alias_b)}",
                    re.IGNORECASE | re.DOTALL,
                )
                m4 = pattern4.search(text)
                if m4:
                    s1, s2 = int(m4.group(1)), int(m4.group(2))
                    # Only accept if both scores are reasonable (0-200)
                    if 0 <= s1 <= 200 and 0 <= s2 <= 200:
                        found[idx] = {"a": s1, "b": s2}
                        break

    return found


def fetch_tyj_news():
    """
    Fetch news from tyj.gd.gov.cn and look for basketball men's B group scores.
    Returns extracted scores dict.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # News list pages to check
    list_urls = [
        "https://tyj.gd.gov.cn/tyxw_zyxw/",
        "https://tyj.gd.gov.cn/tyxw_zyxw/index_2.html",
    ]

    article_urls = []
    scores_found = {}

    for list_url in list_urls:
        try:
            resp = requests.get(list_url, headers=headers, timeout=20)
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")

            # Find article links
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                text = link.get_text(strip=True)
                # Look for basketball-related articles
                if any(kw in text for kw in ["篮球", "男子乙组", "省运", "战报"]):
                    if href.startswith("http"):
                        article_urls.append(href)
                    elif href.startswith("/"):
                        article_urls.append(f"https://tyj.gd.gov.cn{href}")
                    else:
                        article_urls.append(f"https://tyj.gd.gov.cn/tyxw_zyxw/{href}")
        except Exception as e:
            print(f"Error fetching {list_url}: {e}")
            continue

    # Deduplicate
    article_urls = list(dict.fromkeys(article_urls))

    for article_url in article_urls[:10]:  # Limit to first 10 articles
        try:
            resp = requests.get(article_url, headers=headers, timeout=20)
            resp.encoding = "utf-8"
            text = resp.text

            # Check if article is about men's B group
            if not any(kw in text for kw in ["男子乙组", "男篮乙组"]):
                continue

            # Also check for B group teams
            if not any(team in text for team in ["深圳", "江门", "佛山", "中山"]):
                continue

            scores = extract_scores_from_text(text)
            if scores:
                scores_found.update(scores)
                print(f"Found scores in {article_url}: {scores}")
        except Exception as e:
            print(f"Error fetching article {article_url}: {e}")
            continue

    return scores_found


def main():
    print(f"[{datetime.now()}] Starting crawler...")

    current = load_current_scores()
    new_scores = fetch_tyj_news()

    if not new_scores:
        print("No new scores found.")
        return

    updated = False
    for idx, score in new_scores.items():
        key = str(idx)
        # Only update if not already set by crawler or manual
        if key not in current or current[key].get("a") is None:
            current[key] = {"a": score["a"], "b": score["b"], "source": "crawler"}
            updated = True
            print(f"Updated match {idx}: {score}")

    if updated:
        save_scores(current)
        print("Scores updated and saved.")
    else:
        print("No updates needed.")


if __name__ == "__main__":
    main()
