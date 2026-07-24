import streamlit as st
import google.generativeai as genai
import os
import json
import time
from dotenv import load_dotenv

load_dotenv(".env.local")

st.set_page_config(
    page_title="Social Caption Generator",
    layout="centered"
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stTextArea textarea { font-size: 15px; }
    .caption-box {
        background: #f0f4ff;
        border-left: 4px solid #4f46e5;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 15px;
        line-height: 1.6;
    }
    .header-text { color: #4f46e5; font-size: 2rem; font-weight: 700; }
    .sub-text { color: #666; margin-bottom: 1.5rem; }
    .cost-box {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 13px;
        color: #555;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="header-text">Social Caption Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Generate AI-powered social media captions for your products instantly.</p>', unsafe_allow_html=True)

# ── API Key ───────────────────────────────────────────────────────────────────
# Streamlit Cloud injects secrets into os.environ automatically.
api_key = os.environ.get("GEMINI_API_KEY", "")

# If no key found anywhere, show input field
if not api_key:
    st.warning("Please enter your Gemini API Key to get started.")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AQ...")
    if not api_key:
        st.stop()

# ── Caption Generator Logic ───────────────────────────────────────────────────
def generate_captions(description, tone, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.5-flash")

    prompt = f"""
You are a social media expert. Generate exactly 5 unique social media captions for this product.

Product: {description}
Tone: {tone}

Rules:
- Follow the tone strictly (Funny = humorous, Professional = formal, Luxury = premium)
- Each caption must be different and creative
- Add 3-5 relevant hashtags at the end of each caption
- Output ONLY a valid JSON array of 5 strings. No extra text, no code fences.

Example:
["Your caption here #Tag1 #Tag2 #Tag3", "Another caption #Tag4 #Tag5"]
"""

    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            # Clean up common AI formatting mistakes
            text = text.replace("```json", "").replace("```", "").strip()
            captions = json.loads(text)
            if isinstance(captions, list) and len(captions) > 0:
                # Log tokens to console
                input_t = getattr(response.usage_metadata, "prompt_token_count", 0)
                output_t = getattr(response.usage_metadata, "candidates_token_count", 0)
                cost = (input_t / 1_000_000 * 0.075) + (output_t / 1_000_000 * 0.30)
                print(f"[Token Log] Product='{description[:30]}' | Input={input_t} | Output={output_t} | Cost=${cost:.6f}")
                return captions, {"input": input_t, "output": output_t, "cost": cost}
        except Exception as e:
            err = str(e)
            if "429" in err:
                # Rate limit - wait and retry
                countdown = st.empty()
                for s in range(12, 0, -1):
                    countdown.warning(f"API rate limit hit. Retrying in {s} seconds... (attempt {attempt+1}/3)")
                    time.sleep(1)
                countdown.empty()
            else:
                return None, {"error": str(e)}
    return None, {"error": "Failed after 3 retries"}

# ── Main Form ─────────────────────────────────────────────────────────────────
st.divider()

col1, col2 = st.columns([3, 1])
with col1:
    description_input = st.text_area(
        "Product / Service Description",
        placeholder="e.g. Premium handmade leather wallet\n\nFor batch mode: add each product on a new line",
        height=140,
        help="Tip: Enter multiple products on separate lines to use batch mode!"
    )
with col2:
    tone = st.selectbox("Tone", ["Funny", "Professional", "Luxury"])
    num_captions = st.selectbox("Captions", [5, 3, 10], index=0)

generate_btn = st.button("Generate Captions", use_container_width=True, type="primary")

# ── Results ───────────────────────────────────────────────────────────────────
if generate_btn:
    products = [line.strip() for line in description_input.strip().split("\n") if line.strip()]

    if not products:
        st.warning("Please enter at least one product description.")
    else:
        st.markdown("---")
        st.subheader("Generated Captions")

        progress = st.progress(0)
        status = st.empty()

        total_in = 0
        total_out = 0
        total_cost = 0.0

        for i, product in enumerate(products):
            status.info(f"Generating captions for **{product}** ({i+1}/{len(products)})...")

            captions, usage = generate_captions(product, tone, api_key)

            if captions:
                if len(products) > 1:
                    st.markdown(f"### {product}")

                for j, cap in enumerate(captions[:num_captions]):
                    st.markdown(f'<div class="caption-box"><b>Caption {j+1}:</b><br><br>{cap}</div>', unsafe_allow_html=True)

                if usage and "error" not in usage:
                    total_in += usage["input"]
                    total_out += usage["output"]
                    total_cost += usage["cost"]
            elif usage and "error" in usage:
                st.error(f"Error for '{product}': {usage['error']}")

            progress.progress((i + 1) / len(products))

        status.success(f"Done! Generated captions for {len(products)} product(s).")

        # Show cost log at the bottom
        st.markdown(
            f'<div class="cost-box"><b>Token Usage Log</b> — '
            f'Input: {total_in} tokens | Output: {total_out} tokens | '
            f'Estimated Cost: <b>${total_cost:.6f}</b></div>',
            unsafe_allow_html=True
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Built for Qodex Software Internship Task 2 | Powered by Google Gemini AI")
