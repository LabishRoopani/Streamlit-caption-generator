import streamlit as st
import google.generativeai as genai
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

# Configure Streamlit page
st.set_page_config(page_title="Social Caption Generator", page_icon="✨")

st.title("✨ Social Caption Generator")
st.write("Generate engaging social media captions powered by AI.")

# Constants
TONES = ['Funny', 'Professional', 'Luxury']
INPUT_COST_PER_M = 0.075
OUTPUT_COST_PER_M = 0.30

def generate_captions(description, tone):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Missing Gemini API Key. Please add it to your .env.local file.")
        return None, None

    genai.configure(api_key=api_key)
    # Using the working gemini-3.5-flash
    model = genai.GenerativeModel('gemini-3.5-flash')

    prompt = f"""
    You are an expert social media manager.
    Generate exactly 5 distinct social media caption variants for the following product/service.
    
    Product/Service Description: "{description}"
    Desired Tone: {tone}
    
    Guidelines:
    - The captions must strictly follow the requested tone.
    - Each caption must be unique and engaging.
    - Include 3 to 5 relevant hashtags at the end of each caption.
    - Format the output strictly as a JSON array of strings. Do not include markdown blocks like ```json.
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        captions = json.loads(text)
        
        # Extract token usage and calculate cost
        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count
        total_cost = (input_tokens / 1000000 * INPUT_COST_PER_M) + (output_tokens / 1000000 * OUTPUT_COST_PER_M)
        
        # Log to terminal as requested
        print(f"[LOG] Processed: '{description[:30]}...'")
        print(f"[LOG] Tokens - Input: {input_tokens}, Output: {output_tokens}")
        print(f"[LOG] Cost   - ${total_cost:.6f}")
        
        return captions, {"input": input_tokens, "output": output_tokens, "cost": total_cost}
    except Exception as e:
        st.error(f"Error generating captions: {e}")
        return None, None

# Form layout
with st.form("caption_form"):
    description_input = st.text_area(
        "Product / Service Descriptions (Batch mode: One per line)", 
        height=150, 
        placeholder="Premium handmade leather wallet\nNoise-cancelling headphones..."
    )
    
    tone = st.selectbox("Select Tone", TONES)
    submitted = st.form_submit_button("Generate Captions")

if submitted and description_input.strip():
    # Split input into lines for batch mode
    items = [line.strip() for line in description_input.split('\n') if line.strip()]
    
    if items:
        st.write("### Generated Captions")
        
        # Progress bar for batch mode
        progress_bar = st.progress(0)
        progress_text = st.empty()
        
        total_input_tokens = 0
        total_output_tokens = 0
        total_batch_cost = 0.0

        for i, item in enumerate(items):
            progress_text.text(f"Processing item {i+1} of {len(items)}...")
            
            with st.spinner(f"Generating for: {item}"):
                captions, usage = generate_captions(item, tone)
                
                if captions:
                    st.subheader(f"Results for: {item}")
                    for idx, cap in enumerate(captions):
                        st.info(cap)
                    
                    if usage:
                        total_input_tokens += usage["input"]
                        total_output_tokens += usage["output"]
                        total_batch_cost += usage["cost"]
                
                # Small delay to ensure progress bar updates visually
                time.sleep(0.1)
                
            progress_bar.progress((i + 1) / len(items))
            
        progress_text.text("Batch processing complete!")
        
        # Display cost on screen as a bonus
        st.caption(f"**Session Cost Log:** {total_input_tokens} input tokens, {total_output_tokens} output tokens | Estimated Cost: ${total_batch_cost:.6f}")
        
elif submitted:
    st.warning("Please enter at least one product description.")
