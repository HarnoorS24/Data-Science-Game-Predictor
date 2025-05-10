import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidSessionIdException
from bs4 import BeautifulSoup
import os
import time
import csv
import traceback
import functools

# from xvfbwrapper import Xvfb
# vdisplay = Xvfb()
# vdisplay.start()

print = functools.partial(print, flush=True)

# === CONFIGURATION ===
csv_path = "temp CSV files/bad_user_reviews.csv"
checkpoint_path = "checkpoint.txt"
output_csv = "scraped_user_negative_reviews.csv"
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
    print(f" Resuming from index {start_index}")

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
    base_url = df.loc[idx, 'Game URL'].rstrip('/') + "/user-reviews"
    print(f"\n Scraping: {idx}. {title}")
    print(f" Base URL: {base_url}")

    game_start = time.time()

    try:
        try:
            driver.get(base_url)
        except InvalidSessionIdException:
            driver.quit()
            driver = start_driver()
            driver.get(base_url)

        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        try:
            cookie_btn = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept')]"))
            )
            cookie_btn.click()
            print(" Dismissed cookie banner.")
        except:
            print(" No cookie banner to dismiss.")

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
            print(f" Platforms extracted (fallback only): {platforms}")
        except Exception:
            platforms = [("unknown", "")]
            print(" Could not extract platform from dropdown. Defaulting to unknown.")

        for platform_name, platform_slug in platforms:
            try:
                review_url = f"{base_url}/?platform={platform_slug}&filter=Negative%20Reviews"
                print(f" Platform: {platform_name}")
                print(f" Scraping URL: {review_url}")

                try:
                    driver.get(review_url)
                except InvalidSessionIdException:
                    driver.quit()
                    driver = start_driver()
                    driver.get(review_url)

                WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                reviews = []
                scores = []

                try:
                    no_reviews = driver.find_elements(By.CSS_SELECTOR, ".c-pageProductReviews_message.u-text-center")
                    if no_reviews:
                        print(" No user reviews found (empty review message on page). Skipping.")
                        continue
                except:
                    pass

                scroll_attempts = 0
                while scroll_attempts < 5:
                    review_blocks = driver.find_elements(By.CSS_SELECTOR, "div.c-siteReview")
                    if len(review_blocks) >= MAX_REVIEWS_PER_PLATFORM:
                        break
                    driver.execute_script("window.scrollBy(0, window.innerHeight);")
                    scroll_attempts += 1

                review_elements = driver.find_elements(By.CSS_SELECTOR, "div.c-siteReview")
                print(f" Found {len(review_elements)} review blocks to parse.")

                for review_el in review_elements:
                    try:
                        try:
                            score_el = review_el.find_element(By.CSS_SELECTOR, 'div[class*="c-siteReviewScore_user"] span')
                            score_text = score_el.text.strip()
                            score_val = int(score_text) * 10 if score_text.isdigit() else -1
                        except:
                            score_val = -1

                        try:
                            quote_el = review_el.find_element(By.CSS_SELECTOR, "div.c-siteReview_quote")
                            span_el = quote_el.find_element(By.TAG_NAME, "span") if quote_el.find_elements(By.TAG_NAME, "span") else quote_el
                            text = span_el.text.strip()
                        except:
                            text = ""

                        if "spoiler alert" in text.lower() or not text.strip():
                            try:
                                read_more_btn = review_el.find_element(By.CSS_SELECTOR, 'button.c-globalButton_container')
                                if "read more" in read_more_btn.text.lower():
                                    driver.execute_script("arguments[0].click();", read_more_btn)

                                    full_text_div = WebDriverWait(driver, 3).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, "c-siteReviewReadMore_wrapper"))
                                    )

                                    placeholder_text = full_text_div.text.strip()
                                    wait_time = 0
                                    while wait_time < 3:
                                        time.sleep(0.5)
                                        wait_time += 0.5
                                        current_text = full_text_div.text.strip()
                                        if current_text != placeholder_text and len(current_text) > len(placeholder_text):
                                            text = current_text
                                            break
                                    else:
                                        text = placeholder_text
                                        print(" Modal opened, but content is still a placeholder.")

                                    if text and "[spoiler alert" not in text.lower():
                                        print(f" Replaced with full modal review: {text[:80]}...")

                                    try:
                                        close_svg = WebDriverWait(driver, 3).until(
                                            EC.element_to_be_clickable((By.CSS_SELECTOR, "svg.c-globalModal_closeButton"))
                                        )
                                        driver.execute_script("arguments[0].click();", close_svg)
                                        print(" Closed modal (SVG button).")
                                    except:
                                        try:
                                            close_svg = WebDriverWait(driver, 3).until(
                                                EC.presence_of_element_located((By.CSS_SELECTOR, "svg.c-globalModal_closeButton"))
                                            )
                                            driver.execute_script(
                                                "arguments[0].dispatchEvent(new MouseEvent('click', { bubbles: true }));",
                                                close_svg
                                            )
                                            print(" Closed modal (SVG click event fallback).")
                                        except:
                                            print(" Failed to close modal (SVG fallback also failed).")
                            except:
                                print(" Could not expand spoiler modal.")

                        if text:
                            reviews.append(text)
                            scores.append(score_val)
                        else:
                            print(" Skipped review with no text.")

                        if len(reviews) >= MAX_REVIEWS_PER_PLATFORM:
                            break

                    except Exception:
                        print(" Error while parsing review.")
                        traceback.print_exc()

                if not reviews:
                    print(f" No reviews found for {platform_name}")
                    continue

                print(f" Scraped {len(reviews)} reviews from {platform_name}")

                with open(output_csv, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for text, score in zip(reviews, scores):
                        writer.writerow([title, text, score, "User", "0", platform_name, review_url])

            except Exception:
                print(f" Failed scraping platform: {platform_name}")
                traceback.print_exc()

    except Exception:
        print(" Failed to scrape this game.")
        traceback.print_exc()

    with open(checkpoint_path, "w") as f:
        f.write(str(idx + 1))

    game_time = time.time() - game_start
    print(f" Time taken: {game_time:.2f}s")

driver.quit()
print(" Done.")
# vdisplay.stop()
