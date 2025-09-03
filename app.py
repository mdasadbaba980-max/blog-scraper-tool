import streamlit as st
import pandas as pd
import requests
import time

# 🔑 Apni API Key yahan daalein
API_KEY = "af3e3d615cb623341c2b05db409e0a3880d4379fa6891adf99191946fb2ba05b"
SEARCH_URL = "https://serpapi.com/search.json"

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Blogging Site Scraper", page_icon="🔎", layout="centered")

st.title("🔎 Guest Post Site Scraper")
st.write("Keyword dijiye aur selected number of sites ko scrape karke Excel/CSV download kijiye.")

# Input fields
keyword = st.text_input("📝 Enter your keyword (e.g., guest post, write for us, contribute):")

options = [100, 500, 1000, 10000]
num_results = st.selectbox("📌 Select number of sites:", options, index=1)

if st.button("🚀 Generate Sites"):
    if not keyword.strip():
        st.error("❌ Please enter a keyword.")
    elif not API_KEY or API_KEY == "PASTE_YOUR_API_KEY_HERE":
        st.error("❌ Please add your SerpAPI key in the script!")
    else:
        st.info(f"🔍 Searching for **{keyword}** ... Please wait ⏳")

        progress_bar = st.progress(0)
        status_text = st.empty()

        all_links = []
        pages = num_results // 10  # Google API returns ~10 results per page

        for i, start in enumerate(range(0, num_results, 10)):
            params = {
                "engine": "google",
                "q": f"{keyword} site:.us",
                "api_key": API_KEY,
                "start": start
            }
            try:
                response = requests.get(SEARCH_URL, params=params)
                data = response.json()

                if "organic_results" in data:
                    for result in data["organic_results"]:
                        if "link" in result:
                            all_links.append(result["link"])

                # Update progress
                progress = int(((i + 1) / pages) * 100)
                progress_bar.progress(progress)
                status_text.text(f"Scraping progress: {progress}% ({len(all_links)} sites found)")

                time.sleep(1)  # avoid rate limit
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                break

        progress_bar.empty()
        status_text.empty()

        if all_links:
            df = pd.DataFrame(all_links, columns=["Website URLs"])
            
            st.success(f"✅ Done! {len(all_links)} sites found.")
            st.dataframe(df.head(50))  # show first 50 in webpage

            # Excel file download
            excel_file = "scraped_sites.xlsx"
            df.to_excel(excel_file, index=False)

            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", data=csv_data, file_name="scraped_sites.csv", mime="text/csv")

            with open(excel_file, "rb") as f:
                st.download_button("📥 Download Excel", data=f, file_name=excel_file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning("⚠️ No sites found. Try another keyword.")

                    else:
            st.warning("⚠️ No sites found. Try another keyword.")

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("👨‍💻 **Author:** Ahmed Raza  |  👩‍💼 **Director:** Sania")

