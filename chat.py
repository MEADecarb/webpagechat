import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configure the Gemini API using Streamlit secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Set the base URL of your website
BASE_URL = "https://energy.maryland.gov/Pages/default.aspx"

# Function to scrape website content
def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from all paragraphs
        text = ' '.join([p.get_text() for p in soup.find_all('p')])
        
        # Extract links to other pages within the same domain
        links = [urljoin(BASE_URL, a['href']) for a in soup.find_all('a', href=True) 
                 if a['href'].startswith('/') or a['href'].startswith(BASE_URL)]
        
        return text, links
    except requests.RequestException as e:
        st.error(f"Failed to scrape {url}: {e}")
        return "", []

# Function to scrape all indexed URLs
def scrape_all_urls(base_url):
    all_content = ""
    visited_urls = set()
    urls_to_visit = [base_url]

    while urls_to_visit:
        url = urls_to_visit.pop(0)
        if url not in visited_urls:
            visited_urls.add(url)
            content, links = scrape_website(url)
            all_content += f"\n\nContent from {url}:\n{content}"
            urls_to_visit.extend([link for link in links if link not in visited_urls])

    return all_content, list(visited_urls)

# Function to get chatbot response
def get_chatbot_response(prompt, context):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"Context: {context}\n\nUser: {prompt}")
    return response.text

# Initialize session state
if 'all_content' not in st.session_state:
    st.session_state.all_content, st.session_state.all_urls = scrape_all_urls(BASE_URL)

# Streamlit UI
st.title("Website Chatbot")

# Chat interface
st.subheader("Chat with your website")
user_input = st.text_input("You:", key="user_input")

if user_input:
    response = get_chatbot_response(user_input, st.session_state.all_content)
    st.text_area("Chatbot:", value=response, height=200, max_chars=None, key="chatbot_response")

# Display total count of indexed URLs
st.subheader("Website Pages")
st.write(f"Total indexed URLs: {len(st.session_state.all_urls)}")

# Display current content (for debugging)
st.subheader("Current Content")
st.write(st.session_state.all_content[:500] + "...")  # Display first 500 characters

# Add a button to refresh content
if st.button("Refresh Content"):
    st.session_state.all_content, st.session_state.all_urls = scrape_all_urls(BASE_URL)
    st.success("Content refreshed from all indexed URLs")
    st.experimental_rerun()
