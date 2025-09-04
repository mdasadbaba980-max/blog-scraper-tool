import streamlit as st
import pandas as pd
import requests
import time

# 🔑 Apni API Key
API_KEY = "af3e3d615cb623341c2b05db409e0a3880d4379fa6891adf99191946fb2ba05b"
SEARCH_URL = "https://serpapi.com/search"

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Blogging Site Scraper", page_icon="🔎", layout="centered")

st.title("🔎 Guest Post Site Scraper")
st.write("Keyword dijiye aur selected number of sites ko scrape karke Excel/CSV download kijiye.")

# Input fields
keyword = st.text_input("📝 Enter your keyword (e.g., guest post, write for us, contribute):")

options = [100, 500, 1000]
num_results = st.selectbox("📌 Select number of sites:", options, index=1)

if st.button("🚀 Generate Sites"):
    if not keyword.strip():
        st.error("❌ Please enter a keyword.")
    else:
        st.info(f"🔍 Searching for **{keyword}** ... Please wait ⏳")

        progress_bar = st.progress(0)
        status_text = st.empty()

        all_links = []
        results_data = []
        pages = num_results // 20  # Har page ~20 results deta hai

        for i, start in enumerate(range(0, num_results, 20)):
            params = {
                "engine": "google",
                "q": f"{keyword} site:.us",
                "api_key": API_KEY,
                "start": start,
                "num": 20,
                "hl": "en",
                "gl": "us"
            }
            try:
                response = requests.get(SEARCH_URL, params=params)
                data = response.json()

                if "organic_results" in data:
                    for item in data["organic_results"]:
                        title = item.get("title")
                        link = item.get("link")
                        if link and link not in all_links:
                            all_links.append(link)
                            results_data.append({"Title": title, "URL": link})

                # Update progress
                progress = int(((i + 1) / pages) * 100)
                progress_bar.progress(progress)
                status_text.text(f"Scraping progress: {progress}% ({len(all_links)} sites found)")

                time.sleep(1)  # API rate limit se bachne ke liye
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                break

        progress_bar.empty()
        status_text.empty()

        if results_data:
            df = pd.DataFrame(results_data)
            
            st.success(f"✅ Done! {len(df)} sites found.")
            st.dataframe(df.head(50))  # sirf pehle 50 show karna

            # Excel file download
            excel_file = "scraped_sites.xlsx"
            df.to_excel(excel_file, index=False)

            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", data=csv_data, file_name="scraped_sites.csv", mime="text/csv")

            with open(excel_file, "rb") as f:
                st.download_button("📥 Download Excel", data=f, file_name=excel_file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning("⚠️ No sites found. Try another keyword.")

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("👨‍💻 **Author:** Ahmed Raza **)
