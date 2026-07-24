import streamlit as st
import google.generativeai as genai
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables (works locally)
load_dotenv(".env.local")

# Configure Streamlit page
st.set_page_config(
    page_title="Social Caption Generator",
    page_icon="✨",
    layout="centered"
)

# Constants
TONES = ['Funny', 'Professional', 'Luxury']
INPUT_COST_PER_M = 0.075   # $0.075 per 1M input tokens
OUTPUT_COST_PER_M = 0.30   # $0.30  per 1M output tokens
MAX_RETRIES = 3
RETRY_DELAY = 12  # seconds between retries on rate limit


def get_api_key():
    """
    Retrieve the API key from Streamlit Secrets (cloud deployment)
    or fall back to the local .env.local file for local development.
    """
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.environ.get("GEMINI_API_KEY", "")


def generate_captions(description: str, tone: str):
    """
    Call the Gemini API to generate 5 social media captions.
    Includes retry logic for rate limit errors (429).
    Returns (captions: list, usage: dict) or (None, None) on failure.
    """
    api_key = get_api_key()
    if not api_key:
        st.error("⚠️ Missing Gemini API Key. Add it to Streamlit Secrets or your .env.local file.")
        return None, None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.5-flash")

    prompt = f"""
    You are an expert social media manager.
    Generate exactly 5 distinct social media caption variants for the following product/service.

    Product/Service Description: "{description}"
    Desired Tone: {tone}

    Guidelines:
    - Each caption must strictly follow the requested tone.
    - Each caption must be unique and engaging.
    - Include 3 to 5 relevant hashtags at the end of each caption.
    - Return ONLY a JSON array of 5 strings. No markdown, no code fences.

    Example format:
    ["Caption one with hashtags #Tag1 #Tag2", "Caption two #Tag3 #Tag4"]
    """

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = model.generate_content(prompt)
            raw_text = response.text.replace("```json", "").replace("```", "").strip()
            captions = json.loads(raw_text)

            if not isinstance(captions, list):
                raise ValueError("Response is not a list.")

            # Token usage & cost calculation
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)
            total_cost = (
                (input_tokens / 1_000_000) * INPUT_COST_PER_M
                + (output_tokens / 1_000_000) * OUTPUT_COST_PER_M
            )

            # Log to terminal / server console
            print(f"[LOG] Item: '{description[:40]}'")
            print(f"[LOG] Tokens  → Input: {input_tokens} | Output: {output_tokens}")
            print(f"[LOG] Cost    → ${total_cost:.6f}")

            return captions, {
                "input": input_tokens,
                "output": output_tokens,
                "cost": total_cost,
            }

        except Exception as err:
            err_str = str(err)
            # Rate limit hit – wait and retry
            if "429" in err_str and attempt < MAX_RETRIES:
                wait_msg = st.empty()
                for remaining in range(RETRY_DELAY, 0, -1):
                    wait_msg.warning(
                        f"⏳ Rate limit reached. Retrying in {remaining}s "
                        f"(attempt {attempt}/{MAX_RETRIES})..."
                    )
                    time.sleep(1)
                wait_msg.empty()
            else:
                st.error(f"❌ Error generating captions: {err}")
                return None, None

    st.error("❌ Failed after multiple retries. Please wait a moment and try again.")
    return None, None


# ─── UI ───────────────────────────────────────────────────────────────────────

st.title("✨ Social Caption Generator")
st.write("Generate engaging social media captions powered by Google Gemini AI.")
st.divider()

with st.form("caption_form"):
    description_input = st.text_area(
        label="📝 Product / Service Descriptions",
        height=160,
        placeholder=(
            "For a single product, type one line.\n"
            "For batch mode, add one product per line:\n\n"
            "Premium handmade leather wallet\n"
            "Noise-cancelling wireless headphones"
        ),
    )
    tone = st.selectbox("🎭 Select Tone", TONES)
    submitted = st.form_submit_button("🚀 Generate Captions", use_container_width=True)

# ─── Processing ───────────────────────────────────────────────────────────────

if submitted:
    items = [line.strip() for line in description_input.split("\n") if line.strip()]

    if not items:
        st.warning("⚠️ Please enter at least one product description.")
    else:
        st.subheader("📣 Generated Captions")

        progress_bar = st.progress(0)
        status_text = st.empty()

        total_input_tokens = 0
        total_output_tokens = 0
        total_batch_cost = 0.0

        for i, item in enumerate(items):
            status_text.info(f"Processing {i + 1} of {len(items)}: *{item}*")

            captions, usage = generate_captions(item, tone)

            if captions:
                if len(items) > 1:
                    st.markdown(f"#### 🔖 {item}")

                for caption in captions:
                    st.success(caption)

                if usage:
                    total_input_tokens += usage["input"]
                    total_output_tokens += usage["output"]
                    total_batch_cost += usage["cost"]

            progress_bar.progress((i + 1) / len(items))

        status_text.success("✅ Batch processing complete!")

        # Cost summary
        st.divider()
        st.caption(
            f"**📊 Session Token Log** — "
            f"Input: {total_input_tokens} tokens | "
            f"Output: {total_output_tokens} tokens | "
            f"Estimated Cost: **${total_batch_cost:.6f}**"
        )

# ─── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption("Qodex Software Internship Task | Built with Streamlit & Google Gemini AI")
