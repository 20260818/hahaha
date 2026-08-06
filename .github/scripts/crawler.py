#!/usr/bin/env python3
"""
Crawler for Guangdong Provincial Games basketball men's B group scores.
Searches multiple media sources for score reports.
Crawler scores always take priority over manual entry.

Key design: sentence-level matching ensures scores are only extracted
when both team names AND the score appear in the same sentence, preventing
false positives from summary articles that mention all teams.
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
# scoreIndex: 0=深圳vs江门(R1), 1=佛山vs深圳(R2), 2=中山vs深圳(R3),
#             3=中山vs佛山(R1), 4=江门vs中山(R2), 5=江门vs佛山(R3)
B_MATCHES = {
    0: {"teamA": "深圳", "teamB": "江门", "round": "第一轮"},
    1: {"teamA": "佛山", "teamB": "深圳", "round": "第二轮"},
    2: {"teamA": "中山", "teamB": "深圳", "round": "第三轮"},
    3: {"teamA": "中山", "teamB": "佛山", "round": "第一轮"},
    4: {"teamA": "江门", "teamB": "中山", "round": "第二轮"},
    5: {"teamA": "江门", "teamB": "佛山", "round": "第三轮"},
}

ALL_TEAMS = ["深圳", "江门", "佛山", "中山"]

TEAM_ALIASES = {
    "深圳": ["深圳", "深圳市", "深圳队"],
    "江门": ["江门", "江门市", "江门队"],
    "佛山": ["佛山", "佛山市", "佛山队"],
    "中山": ["中山", "中山市", "中山队"],
}

SCORES_FILE = Path(__file__).parent.parent.parent / "scores.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Known article URLs that are likely to contain B group results.
# These are checked first as they are the most reliable sources.
KNOWN_ARTICLE_URLS = [
    # Sohu - first round coverage
    "https://m.sohu.com/a/1059097621_122001004/",
    # Dongguan Daily - covers tournament daily
    "https://webzdg.sun0769.com/web/news/content/871402",
    "https://webzdg.sun0769.com/web/news/content/872217",
]


def load_current_scores():
    if not SCORES_FILE.exists():
        return {}
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_scores(scores):
    scores["updated_at"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
    scores["source"] = "crawler"
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


def get_plain_text(html_text):
    """Extract readable text from HTML, removing scripts and tags."""
    soup = BeautifulSoup(html_text, "html.parser")
    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    # Clean up whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def split_sentences(text):
    """
    Split text into sentences using Chinese and English delimiters.
    This is the key to preventing cross-sentence false matches.
    """
    # Split by Chinese period, exclamation, question mark, semicolon, and newline
    raw_parts = re.split(r'[。！？；;！\n]+', text)
    sentences = []
    for part in raw_parts:
        part = part.strip()
        if len(part) >= 3:
            sentences.append(part)
    return sentences


def find_team_positions(sentence):
    """Find all team name positions in a sentence. Returns sorted list of (position, team_name)."""
    positions = []
    for team in ALL_TEAMS:
        for alias in TEAM_ALIASES.get(team, [team]):
            start = 0
            while True:
                pos = sentence.find(alias, start)
                if pos < 0:
                    break
                positions.append((pos, team))
                start = pos + len(alias)
    positions.sort()
    return positions


def find_match_for_teams(team1, team2):
    """Find the match index for a pair of teams. Returns (idx, match_def) or (None, None)."""
    for idx, md in B_MATCHES.items():
        if {md["teamA"], md["teamB"]} == {team1, team2}:
            return idx, md
    return None, None


def extract_scores_from_text(text):
    """
    Extract basketball scores from article text using sentence-level matching.

    Core principle: for each score pattern found in a sentence, identify the
    SUBJECT team (mentioned before the score) and the OPPONENT team (mentioned
    after the score, or the only other team in the sentence). This ensures
    each score maps to exactly one match, preventing false positives.

    Score patterns handled:
    - "深圳队以112比56大胜江门队" → 深圳=112, 江门=56
    - "佛山队以77比68险胜" (opponent mentioned earlier) → 佛山=77, opponent=68
    - "深圳 112:56 江门" → 深圳=112, 江门=56
    """
    found = {}
    sentences = split_sentences(text)

    for sentence in sentences:
        team_pos_list = find_team_positions(sentence)
        if len(team_pos_list) < 2:
            continue

        # Collect unique teams in this sentence
        unique_teams = set(team for _, team in team_pos_list)
        if len(unique_teams) < 2:
            continue

        # Process "以X比Y" patterns
        for m in re.finditer(r'以\s*(\d+)\s*比\s*(\d+)', sentence):
            s1, s2 = int(m.group(1)), int(m.group(2))
            if not (1 <= s1 <= 200 and 0 <= s2 <= 200 and s1 != s2):
                continue

            yi_pos = m.start()
            score_end = m.end()

            # Subject = last team mentioned before "以"
            subject = None
            for pos, team in reversed(team_pos_list):
                if pos < yi_pos:
                    subject = team
                    break

            # Opponent = first team mentioned after the score (different from subject)
            opponent = None
            for pos, team in team_pos_list:
                if pos >= score_end and team != subject:
                    opponent = team
                    break

            # If no opponent after score, look for other team before "以"
            if not opponent and subject:
                others_before = [(pos, team) for pos, team in team_pos_list
                                 if pos < yi_pos and team != subject]
                # Only accept if exactly one other team (unambiguous)
                other_teams = set(team for _, team in others_before)
                if len(other_teams) == 1:
                    opponent = list(other_teams)[0]

            if not subject or not opponent or subject == opponent:
                continue

            idx, md = find_match_for_teams(subject, opponent)
            if idx is None:
                continue

            # Subject gets s1, opponent gets s2
            if md["teamA"] == subject:
                found[idx] = {"a": s1, "b": s2}
            else:
                found[idx] = {"a": s2, "b": s1}

        # Process "X:Y" or "X：Y" patterns (only for matches not already found)
        for m in re.finditer(r'(\d+)\s*[:：]\s*(\d+)', sentence):
            s1, s2 = int(m.group(1)), int(m.group(2))
            if not (1 <= s1 <= 200 and 0 <= s2 <= 200 and s1 != s2):
                continue
            # Skip times like 8:30
            if s1 <= 24 and s2 <= 59:
                continue

            score_start = m.start()
            score_end = m.end()

            # Team before score = last team before score start
            team_before = None
            for pos, team in reversed(team_pos_list):
                if pos < score_start:
                    team_before = team
                    break

            # Team after score = first team after score end
            team_after = None
            for pos, team in team_pos_list:
                if pos >= score_end and team != team_before:
                    team_after = team
                    break

            if not team_before or not team_after or team_before == team_after:
                continue

            idx, md = find_match_for_teams(team_before, team_after)
            if idx is None:
                continue
            if idx in found:
                continue  # Already found via "以X比Y" pattern

            if md["teamA"] == team_before:
                found[idx] = {"a": s1, "b": s2}
            else:
                found[idx] = {"a": s2, "b": s1}

    return found


def fetch_url_text(url, timeout=20):
    """Fetch URL and return plain text, or None on error."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.text
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def fetch_known_articles():
    """Fetch known article URLs that are likely to contain B group results."""
    scores_found = {}
    for url in KNOWN_ARTICLE_URLS:
        print(f"  Checking known article: {url}")
        html = fetch_url_text(url)
        if not html:
            continue
        text = get_plain_text(html)
        # Quick filter: must mention basketball and at least one B group team
        if not any(kw in text for kw in ["男子乙组", "男篮乙组", "篮球"]):
            continue
        if not any(team in text for team in ALL_TEAMS):
            continue
        scores = extract_scores_from_text(text)
        if scores:
            scores_found.update(scores)
            print(f"    Found scores: {scores}")
    return scores_found


def fetch_sohu_search():
    """Search Sohu for articles about 省运会 篮球 男子乙组."""
    scores_found = {}
    search_urls = [
        "https://search.sohu.com/?keyword=省运会+男子乙组+篮球+比分",
        "https://search.sohu.com/?keyword=省运会+男篮乙组+深圳",
        "https://search.sohu.com/?keyword=省运会+篮球+乙组+B组",
    ]

    article_urls = set()
    for search_url in search_urls:
        html = fetch_url_text(search_url)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if any(kw in text for kw in ["男子乙组", "男篮乙组", "省运", "篮球"]):
                if "sohu.com" in href and "/a/" in href:
                    article_urls.add(href)

    for url in list(article_urls)[:10]:
        html = fetch_url_text(url)
        if not html:
            continue
        text = get_plain_text(html)
        if not any(kw in text for kw in ["男子乙组", "男篮乙组"]):
            continue
        scores = extract_scores_from_text(text)
        if scores:
            scores_found.update(scores)
            print(f"  Found scores in Sohu {url}: {scores}")

    return scores_found


def fetch_baidu_news():
    """Search Baidu News for score articles."""
    scores_found = {}
    keywords = [
        "省运会 男子乙组 篮球 比分",
        "省运会 男篮乙组 深圳 江门",
        "省运会 篮球 乙组 B组 佛山 中山",
    ]

    article_urls = set()
    for kw in keywords:
        url = f"https://www.baidu.com/s?wd={kw}"
        html = fetch_url_text(url)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if any(kw in text for kw in ["男子乙组", "男篮乙组", "省运", "篮球乙组"]):
                if href.startswith("http") and "baidu.com/link" not in href:
                    article_urls.add(href)

    for url in list(article_urls)[:10]:
        html = fetch_url_text(url)
        if not html:
            continue
        text = get_plain_text(html)
        if not any(kw in text for kw in ["男子乙组", "男篮乙组"]):
            continue
        if not any(team in text for team in ALL_TEAMS):
            continue
        scores = extract_scores_from_text(text)
        if scores:
            scores_found.update(scores)
            print(f"  Found scores in Baidu {url}: {scores}")

    return scores_found


def fetch_dongguan_news():
    """Fetch from Dongguan Daily (webzdg.sun0769.com) which covers the tournament daily."""
    scores_found = {}
    # Try the news list pages
    list_urls = [
        "https://webzdg.sun0769.com/web/news/search?keyword=省运会+篮球+乙组",
        "https://webzdg.sun0769.com/web/news/search?keyword=省运会+男篮",
    ]

    article_urls = set()
    for list_url in list_urls:
        html = fetch_url_text(list_url)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if any(kw in text for kw in ["男子乙组", "男篮乙组", "省运", "篮球"]):
                if href.startswith("http"):
                    article_urls.add(href)
                elif href.startswith("/"):
                    article_urls.add(f"https://webzdg.sun0769.com{href}")

    for url in list(article_urls)[:10]:
        html = fetch_url_text(url)
        if not html:
            continue
        text = get_plain_text(html)
        if not any(kw in text for kw in ["男子乙组", "男篮乙组", "篮球"]):
            continue
        scores = extract_scores_from_text(text)
        if scores:
            scores_found.update(scores)
            print(f"  Found scores in Dongguan news {url}: {scores}")

    return scores_found


def fetch_gdyxzx():
    """Fetch from gdyxzx.com (粤西资讯网) which republishes local news."""
    scores_found = {}
    html = fetch_url_text("http://www.gdyxzx.com/forum.php?mod=forumdisplay&fid=2&mobile=2")
    if not html:
        return scores_found

    soup = BeautifulSoup(html, "html.parser")
    article_urls = set()
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        text = link.get_text(strip=True)
        if any(kw in text for kw in ["男子乙组", "男篮", "省运", "篮球"]):
            if "tid=" in href:
                if href.startswith("http"):
                    article_urls.add(href)
                else:
                    article_urls.add(f"http://www.gdyxzx.com/{href}")

    for url in list(article_urls)[:10]:
        html = fetch_url_text(url)
        if not html:
            continue
        text = get_plain_text(html)
        if not any(kw in text for kw in ["男子乙组", "男篮乙组"]):
            continue
        scores = extract_scores_from_text(text)
        if scores:
            scores_found.update(scores)
            print(f"  Found scores in gdyxzx {url}: {scores}")

    return scores_found


def fetch_toutiao():
    """Search Toutiao for score articles."""
    scores_found = {}
    search_url = "https://www.toutiao.com/search/?keyword=省运会+男子乙组+篮球+比分"
    html = fetch_url_text(search_url)
    if not html:
        return scores_found

    soup = BeautifulSoup(html, "html.parser")
    article_urls = set()
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        text = link.get_text(strip=True)
        if any(kw in text for kw in ["男子乙组", "男篮乙组", "省运"]):
            if href.startswith("http"):
                article_urls.add(href)

    for url in list(article_urls)[:8]:
        html = fetch_url_text(url)
        if not html:
            continue
        text = get_plain_text(html)
        if not any(kw in text for kw in ["男子乙组", "男篮乙组"]):
            continue
        scores = extract_scores_from_text(text)
        if scores:
            scores_found.update(scores)
            print(f"  Found scores in Toutiao {url}: {scores}")

    return scores_found


def main():
    print(f"[{datetime.now()}] Starting crawler...")

    current = load_current_scores()

    # Fetch from all sources
    all_scores = {}

    print("Checking known articles...")
    all_scores.update(fetch_known_articles())

    print("Searching Sohu...")
    all_scores.update(fetch_sohu_search())

    print("Searching Baidu News...")
    all_scores.update(fetch_baidu_news())

    print("Searching Dongguan Daily...")
    all_scores.update(fetch_dongguan_news())

    print("Searching gdyxzx.com...")
    all_scores.update(fetch_gdyxzx())

    print("Searching Toutiao...")
    all_scores.update(fetch_toutiao())

    if not all_scores:
        print("No scores found from any source.")
        return

    print(f"Total scores found: {all_scores}")

    # Always update with crawler scores (crawler priority > manual)
    updated = False
    for idx, score in all_scores.items():
        key = str(idx)
        existing = current.get(key, {})
        existing_a = existing.get("a") if isinstance(existing, dict) else None
        existing_b = existing.get("b") if isinstance(existing, dict) else None
        if existing_a != score["a"] or existing_b != score["b"]:
            current[key] = {"a": score["a"], "b": score["b"], "source": "crawler"}
            updated = True
            print(f"  Updated match {idx}: {score['a']}:{score['b']}")

    if updated:
        save_scores(current)
        print("Scores updated and saved.")
    else:
        print("No updates needed (scores unchanged).")


if __name__ == "__main__":
    main()
