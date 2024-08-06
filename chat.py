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
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  
  # Extract text from all paragraphs
  text = ' '.join([p.get_text() for p in soup.find_all('p')])
  
  # Extract links to other pages within the same domain
  links = [urljoin(BASE_URL, a['href']) for a in soup.find_all('a', href=True) 
           if a['href'].startswith('/') or a['href'].startswith(BASE_URL)]
  
  return text, links

# Function to get chatbot response
def get_chatbot_response(prompt, context):
  model = genai.GenerativeModel('gemini-pro')
  response = model.generate_content(f"Context: {context}\n\nUser: {prompt}")
  return response.text

# Initialize session state
if 'content' not in st.session_state:
  st.session_state.content, st.session_state.links = scrape_website(BASE_URL)

# Streamlit UI
st.title("Website Chatbot")

# Chat interface
st.subheader("Chat with your website")
user_input = st.text_input("You:", key="user_input")

if user_input:
  response = get_chatbot_response(user_input, st.session_state.content)
  st.text_area("Chatbot:", value=response, height=200, max_chars=None, key="chatbot_response")

# Display total count of indexed URLs
st.subheader("Website Pages")
st.write(f"Total indexed URLs: {len(st.session_state.links)}")

# Display current content (for debugging)
st.subheader("Current Content")
st.write(st.session_state.content[:500] + "...")  # Display first 500 characters

# Add a button to refresh content
if st.button("Refresh Content"):
  st.session_state.content, st.session_state.links = scrape_website(BASE_URL)
  st.success("Content refreshed from the base URL")
  st.rerun()
