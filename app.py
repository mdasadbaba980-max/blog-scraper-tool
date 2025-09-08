import streamlit as st
import pandas as pd
import string
import itertools
import random
from duckduckgo_search import DDGS

# ------------- UI styling (background image, transparent card) --------------
BG_IMAGE = "https://pin.it/i/3zQJ2tf71/"  # user-provided link (Pinterest)
# CSS: background + transparent card with shadow
st.markdown(
    f"""
    <style>
    body {{
        background-image: url('{BG_IMAGE}');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .card {{
        background: rgba(255,255,255,0.06);  /* slight transparent white */
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.45);
        backdrop-filter: blur(6px);
        color: #ffffff;
    }}
    .small-muted {{
        color: #cfcfcf;
        font-size: 0.9rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------- App header inside a card -------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("## ⚡ Ultra-Fast DuckDuckGo Scraper (best-effort, no API)")
st.markdown("Enter a keyword and how many **unique** site URLs you want. The scraper will aggressively try many query-variations to reach the target.")
st.markdown("</div>", unsafe_allow_html=True)
st.write("")

# ------------- Inputs -------------
with st.container():
    col1, col2 = st.columns([3,1])
    with col1:
        keyword = st.text_input("🔎 Search Keyword", value="caleb james goddard")
    with col2:
        num_results = st.number_input("Target unique sites", min_value=100, max_value=10000, step=100, value=1000)

# ------------- Author / short paragraph -------------
st.markdown("")
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("**About (Author): Ahmed**")
st.markdown(
    "<p class='small-muted'>I am a backend developer (PHP / Laravel), frontend (JS / Bootstrap / HTML / CSS / jQuery) and Python developer. I build reliable scraping & automation tools and organize authentic data pipelines.</p>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)
st.write("")

# ------------- Helper: modifier generator -------------
def modifiers_generator():
    # single letters, double letters, numbers, common short words, and some random tokens
    letters = list(string.ascii_lowercase)
    doubles = [a+b for a in letters for b in letters]
    numbers = [str(i) for i in range(0,100)]
    common = ["blog", "post", "site", "guest", "write", "contribute", "article", "news"]
    # combine iterators but do not run forever — we will break when we reach target
    for item in itertools.chain(letters, doubles, numbers, common):
        yield item
    # if still not enough, yield random tokens (rare)
    while True:
        yield ''.join(random.choices(letters, k=3))

# ------------- Start scraping button -------------
if st.button("🚀 Start (Ultra-Fast, aggressive)"):
    if not keyword or keyword.strip() == "":
        st.error("Please enter a keyword.")
    else:
        st.info(f"Starting aggressive collection for **{keyword}** — target: {num_results} unique sites")
        progress = st.progress(0)
        status = st.empty()
        results = []
        seen = set()

        # We'll use DDGS generator and run many query variants without deliberate sleep (ultra-fast)
        try:
            ddgs = DDGS()
            mod_gen = modifiers_generator()
            batch_count = 0
            max_iterations = 5000  # safety cap so it doesn't run forever
            iter_count = 0

            # Keep requesting until we reach target or hit max_iterations
            while len(seen) < num_results and iter_count < max_iterations:
                mod = next(mod_gen)
                iter_count += 1
                batch_count += 1
                query = f"{keyword} {mod}"

                # fetch up to 100 items per query (DuckDuckGo yields around 50-100)
                try:
                    for r in ddgs.text(query, max_results=100):
                        url = r.get("href") or r.get("url") or ""
                        title = r.get("title") or ""
                        if not url:
                            continue
                        if url not in seen:
                            seen.add(url)
                            results.append({"Title": title.strip(), "URL": url})
                            # update progress live
                            current = len(seen)
                            pct = min(100, int((current / num_results) * 100))
                            progress.progress(pct)
                            status.text(f"Collected {current} / {num_results} unique sites — queries used: {iter_count}")
                            if current >= num_results:
                                break
                except Exception as e:
                    # if one query fails just continue to next modifier
                    status.text(f"Warning: single query failed ({e}). Continuing...")
                    continue

            # done trying
            progress.empty()
            status.empty()

            # final dedup (shouldn't be needed because we used seen), create DataFrame
            df = pd.DataFrame(results).drop_duplicates(subset=["URL"])
            final_count = len(df)

            if final_count >= num_results:
                st.success(f"✅ Success — collected {final_count} unique sites (target reached).")
            else:
                st.warning(f"⚠️ Only {final_count} unique sites collected (target {num_results} not reached). Try a broader keyword or increase variation strategies.")

            # show first 200 results in table
            if final_count > 0:
                st.dataframe(df.head(200))

                # Save files
                excel_file = "duck_results.xlsx"
                csv_file_name = "duck_results.csv"
                df.to_excel(excel_file, index=False)
                csv_data = df.to_csv(index=False).encode("utf-8")

                # Download buttons
                st.download_button("📥 Download CSV", data=csv_data, file_name=csv_file_name, mime="text/csv")
                with open(excel_file, "rb") as f:
                    st.download_button("📥 Download Excel", data=f, file_name=excel_file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info("No results found. Try a simpler or broader keyword.")

            # safety close DDGS
            try:
                ddgs.__exit__(None, None, None)
            except Exception:
                pass

        except Exception as e:
            st.error(f"Fatal error: {e}")

            
