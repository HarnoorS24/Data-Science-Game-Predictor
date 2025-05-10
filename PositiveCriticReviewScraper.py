import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException
import os
import time
import csv
import traceback
import functools

# from xvfbwrapper import Xvfb
# vdisplay = Xvfb()
# vdisplay.start()

print = functools.partial(print, flush=True)

#i need to rerun this lmao im retarded

# === CONFIGURATION ===
csv_path = "temp CSV files/good_critic_reviews.csv"
checkpoint_path = "checkpoint_critic_positive.txt"
output_csv = "scraped_critic_positive_reviews.csv"
driver_path = "chromedriver"

MAX_REVIEWS_PER_PLATFORM = 50

# === LOAD CSV ===
df = pd.read_csv(csv_path)
print("CSV Columns:", df.columns.tolist())

# === CHECKPOINT ===
start_index = 0
if os.path.exists(checkpoint_path):
    with open(checkpoint_path, "r") as f:
        start_index = int(f.read().strip())
    print(f"🔁 Resuming from index {start_index}")

# === CSV HEADER SETUP ===
if not os.path.exists(output_csv):
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Review Text", "Score", "User/Critic", "+/-", "Platform", "Link"])

# === SELENIUM SETUP ===
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

def start_driver():
    return webdriver.Chrome(executable_path=driver_path, options=options)

driver = start_driver()

# === SCRAPE LOOP ===
for idx in range(start_index, len(df)):
    title = df.loc[idx, 'Title']
    base_url = df.loc[idx, 'Game URL'].rstrip('/') + "/critic-reviews"
    print(f"\n🔍 Scraping: {idx}. {title}")
    print(f"🌐 Base URL: {base_url}")

    game_start = time.time()

    try:
        try:
            driver.get(base_url)
        except InvalidSessionIdException:
            try:
                driver.quit()
            except:
                pass
            driver = start_driver()
            driver.get(base_url)

        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Dismiss cookie banner
        try:
            cookie_btn = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept')]"))
            )
            cookie_btn.click()
            print("✅ Dismissed cookie banner.")
        except:
            print("⚠️ No cookie banner to dismiss.")

        # === PLATFORM DETECTION ===
        platforms = []
        try:
            selected = driver.find_element(By.CLASS_NAME, "c-siteDropdown_choice").text.strip()
            lines = selected.splitlines()
            for line in lines:
                clean_name = line.strip()
                if clean_name:
                    slug = clean_name.lower().replace(" ", "-").replace("/", "").replace("--", "-")
                    if "ios" in slug:
                        slug = "ios-iphoneipad"
                    platforms.append((clean_name, slug))
            print(f"🔎 Platforms extracted (fallback only): {platforms}")
        except:
            print("⚠️ Could not extract platform from dropdown. Defaulting to unknown.")
            platforms = [("unknown", "")]

        for platform_name, platform_slug in platforms:
            try:
                review_url = f"{base_url}/?platform={platform_slug}&filter=Positive%20Reviews"
                print(f"🕹️ Platform: {platform_name}")
                print(f"🔗 Scraping URL: {review_url}")

                try:
                    driver.get(review_url)
                except InvalidSessionIdException:
                    try:
                        driver.quit()
                    except:
                        pass
                    driver = start_driver()
                    driver.get(review_url)

                WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                reviews = []
                scores = []

                try:
                    no_reviews = driver.find_elements(By.CSS_SELECTOR, ".c-pageProductReviews_message.u-text-center")
                    if no_reviews:
                        print("❌ No critic reviews found (empty review message on page). Skipping.")
                        continue
                except:
                    pass

                try:
                    scroll_attempts = 0
                    while scroll_attempts < 5:
                        review_blocks = driver.find_elements(By.CSS_SELECTOR, "div.c-siteReview")
                        if len(review_blocks) >= MAX_REVIEWS_PER_PLATFORM:
                            break
                        driver.execute_script("window.scrollBy(0, window.innerHeight);")
                        scroll_attempts += 1

                    review_elements = driver.find_elements(By.CSS_SELECTOR, "div.c-siteReview")
                    print(f"🔍 Found {len(review_elements)} review blocks to parse.")

                    for review_el in review_elements:
                        try:
                            try:
                                score_el = review_el.find_element(By.CSS_SELECTOR, 'div.c-siteReviewScore span')
                                score_text = score_el.text.strip()
                                score_val = int(score_text) if score_text.isdigit() else -1
                            except:
                                score_val = -1

                            try:
                                quote_el = review_el.find_element(By.CSS_SELECTOR, "div.c-siteReview_quote")
                                span_el = quote_el.find_element(By.TAG_NAME, "span") if quote_el.find_elements(By.TAG_NAME, "span") else quote_el
                                text = span_el.text.strip()
                            except:
                                text = ""

                            if text:
                                reviews.append(text)
                                scores.append(score_val)

                            if len(reviews) >= MAX_REVIEWS_PER_PLATFORM:
                                break

                        except Exception:
                            print("⚠️ Error while parsing review.")
                            traceback.print_exc()

                except Exception as e:
                    print("⚠️ Error during scroll or parsing.")
                    traceback.print_exc()

                if not reviews:
                    print(f"❌ No reviews found for {platform_name}")
                    continue

                print(f"✅ Scraped {len(reviews)} reviews from {platform_name}")

                with open(output_csv, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for text, score in zip(reviews, scores):
                        writer.writerow([title, text, score, "Critic", "1", platform_name, review_url])

            except Exception:
                print(f"⚠️ Failed scraping platform: {platform_name}")
                traceback.print_exc()

    except Exception:
        print("❌ Failed to scrape this game.")
        traceback.print_exc()

    with open(checkpoint_path, "w") as f:
        f.write(str(idx + 1))

    game_time = time.time() - game_start
    print(f"⏱️ Time taken: {game_time:.2f}s")

# === CLEANUP ===
driver.quit()
print("✅ Done.")
# vdisplay.stop()
