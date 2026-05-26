import os
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Ensure secure Gemini client routing
if "GEMINI_API_KEY" in os.environ:
    client = genai.Client()
elif "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing Gemini API Key. Configure it to activate the Content Studio.")
    st.stop()

class SocialMediaPostSchema(BaseModel):
    hook_headline: str = Field(description="High-converting, urgent headline designed to make local business owners stop scrolling.")
    simplified_analogy: str = Field(description="Breaking down the complex section of law using a clear, simple everyday example.")
    the_financial_danger: str = Field(description="The exact risk or notice exposure if they choose to ignore this rule or leave it unfiled.")
    the_ksp_solution: str = Field(description="How KSP's diagnostic software handles this problem flawlessly.")
    instagram_linkedin_caption: str = Field(description="A highly optimized, formatted text script complete with line breaks and targeted hashtags.")

st.set_page_config(page_title="KSP Automated Content Studio", page_icon="📱")
st.title("📱 KSP Automated Legal Content Engine")
st.subheader("Transform Complex Slabs, GST Updates & Corporate Laws into High-Conversion Social Posts")

target_statute = st.text_input(
    "Enter the Tax Rule, GST Update, or Corporate Clause to breakdown:",
    placeholder="Example: Section 44ADA Presumptive Tax, Section 17(5) Blocked Credits, Mudra Loans Eligibility"
)

target_audience = st.selectbox(
    "Target Viewer Segment Profile:",
    ["Hyderabad Local Retail Owners & Shopkeepers", "Independent Tech Freelancers & Agency Founders", "Traditional Professionals & Consultants"]
)

if st.button("Generate High-Impact Strategic Content"):
    if not target_statute:
        st.warning("Please specify a baseline regulatory topic parameter.")
    else:
        with st.spinner("Deconstructing legal text into high-impact visual layouts..."):
            try:
                prompt = f"Break down '{target_statute}' for a viewer base of '{target_audience}'."
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=(
                            "You are the Head of Digital Growth Strategy at Kulkarni Strategic Partners. "
                            "Your objective is to translate dry, complex tax sections, corporate law, and GST updates "
                            "into simple, crystal-clear everyday examples. Highlight the intense compliance danger of leaving things unfiled "
                            "and position KSP's diagnostic screen share calls as the ultimate solution."
                        ),
                        response_mime_type="application/json",
                        response_schema=SocialMediaPostSchema,
                        temperature=0.7
                    )
                )
                
                post = SocialMediaPostSchema.model_validate_json(response.text)
                
                st.success("⚡ Strategic Growth Post Blueprint Generated!")
                st.markdown(f"### 🔥 Scroll-Stopping Hook:\n**{post.hook_headline}**")
                
                st.markdown("### 💡 The Simplified Analogy (Complex Law Broken Down):")
                st.info(post.simplified_analogy)
                
                st.markdown("### ⚠️ The Hidden Financial Danger Alert:")
                st.error(post.the_financial_danger)
                
                st.markdown("### 💼 The KSP Position Optimization:")
                st.success(post.the_ksp_solution)
                
                st.markdown("---")
                st.subheader("📝 Ready-to-Copy Instagram & LinkedIn Caption Script")
                st.text_area("Copy Text Output directly for Posting:", value=post.instagram_linkedin_caption, height=350)
                
            except Exception as e:
                st.error(f"Content Synthesis Error: {e}")