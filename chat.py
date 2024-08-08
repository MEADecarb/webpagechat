import streamlit as st
import requests
from bs4 import BeautifulSoup

# Function to scrape the webpage
def scrape_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract relevant information (customize based on the webpage structure)
    # For demonstration, let's extract all paragraphs
    paragraphs = soup.find_all('p')
    content = ' '.join([p.get_text() for p in paragraphs])
    return content

# Function to interact with Gemini API
def chat_with_gemini(message, api_key):
    url = "https://api.gemini.com/v1/chat"  # Update with the correct endpoint
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": message
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Streamlit app
def main():
    st.title("Chat with the Maryland Energy Administration Webpage")

    st.write("Enter your message below and chat with the Maryland Energy Administration webpage:")
    user_input = st.text_input("Your Message:")

    api_key = st.text_input("Enter your Gemini API Key:", type="password")

    if st.button("Send"):
        if user_input and api_key:
            # Scrape the webpage
            webpage_content = scrape_webpage("https://energy.maryland.gov/Pages/default.aspx")
            st.write("Extracted Webpage Content:")
            st.write(webpage_content)
            
            # Send user input and scraped content to Gemini API
            full_message = f"Webpage Content: {webpage_content}\nUser Message: {user_input}"
            response = chat_with_gemini(full_message, api_key)
            st.write("Response from Gemini API:")
            st.write(response)
        else:
            st.error("Please enter both a message and your API key.")

if __name__ == "__main__":
    main()
