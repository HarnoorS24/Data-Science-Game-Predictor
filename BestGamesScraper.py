import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

#i'll rewrite this code later


print("\n🔍 Will save to:", os.path.abspath("all_metacritic_games.csv"))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

BASE_URL = "https://www.metacritic.com"
BROWSE_URL = "https://www.metacritic.com/browse/game/?releaseYearMin=1958&releaseYearMax=2025&sort=desc&page={}"
game_data = []
game_index = 0

# 🔁 Safe request function with retry logic
def safe_get(url, headers, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Request failed ({e}), retrying in {delay} seconds... (Attempt {attempt+1}/{retries})")
            time.sleep(delay)
    print(f"❌ Failed to fetch {url} after {retries} retries.")
    return None

# 🔍 Scrape a game's page for critic and user scores
def scrape_game_page(url):
    try:
        res = safe_get(url, HEADERS)
        if res is None or res.status_code != 200:
            return None, None

        soup = BeautifulSoup(res.text, "html.parser")

        # Critic Score
        critic_div = soup.find("div", class_="c-siteReviewScore_background-critic_medium")
        critic_span = critic_div.find("span") if critic_div else None
        try:
            metascore = float(critic_span.text.strip()) if critic_span else None
        except:
            metascore = None

        # User Score
        user_div = soup.find("div", class_="c-siteReviewScore_background-user")
        user_span = user_div.find("span") if user_div else None
        try:
            user_score = float(user_span.text.strip()) * 10 if user_span else None
        except:
            user_score = None

        return metascore, user_score

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None, None

# 🔁 Main scraping loop
for page in range(276, 568):  # Skip page 0 (it's a duplicate of page 1)
    url = BROWSE_URL.format(page)
    print(f"\nScraping page {page}/567: {url}")

    res = safe_get(url, HEADERS)
    if res is None or res.status_code != 200:
        continue

    soup = BeautifulSoup(res.text, "html.parser")
    game_cards = soup.find_all("div", class_="c-finderProductCard")

    if not game_cards:
        print(f"⚠️ No games found on page {page} — possibly blocked or end of list.")
        continue

    for card in game_cards:
        try:
            game_index += 1

            title_tag = card.find("h3")
            title = title_tag.text.strip() if title_tag else None

            link_tag = card.find("a", href=True)
            relative_link = link_tag["href"] if link_tag else None
            full_link = BASE_URL + relative_link if relative_link else None

            metascore, user_score = scrape_game_page(full_link)

            game_data.append({
                "Title": title,
                "Metascore": metascore,
                "User Score (out of 100)": user_score,
                "Game URL": full_link
            })

            print(f"✓ {game_index}. {title} | Critic: {metascore} | User: {user_score}")
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ Error parsing game card: {e}")
            continue

    # 💾 Auto-save checkpoint
    if page % 25 == 0:
        checkpoint_name = f"checkpoint_page_{page}.csv"
        pd.DataFrame(game_data).to_csv(checkpoint_name, index=False)
        print(f"\n💾 Saved checkpoint to {checkpoint_name}")

    #time.sleep(1)

# ✅ Final save
df = pd.DataFrame(game_data)
df.to_csv("all_metacritic_games.csv", index=False)
print("\n✅ Done. Saved to all_metacritic_games.csv")
