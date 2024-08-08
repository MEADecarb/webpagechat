import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import hashlib
import schedule
import time
import os

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
@st.cache_data(show_spinner=False)
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

# Function to split content into manageable chunks
def split_content(content, max_size=20000):
    """Splits content into chunks of a specified size for efficient processing.

    Args:
        content (str): The content to be split.
        max_size (int, optional): The maximum size of each chunk in characters. Defaults to 20000.

    Returns:
        list[str]: A list of content chunks.
    """
    return [content[i:i+max_size] for i in range(0, len(content), max_size)]

# Function to hash the prompt and context for caching
def hash_prompt_context(prompt, context):
    return hashlib.sha256(f"{prompt}{context}".encode()).hexdigest()

# Function to get chatbot response
@st.cache_data(show_spinner=False)
def get_chatbot_response_cached(prompt, context):
    model = genai.GenerativeModel('gemini-pro')
    # Replace the following line with the actual API call to get the response
    response = model.generate(prompt, context=context)
    return response

# Function to write content to a text file
def write_content_to_file(content, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Function to scrape and save content
def scrape_and_save_content():
    content, visited_urls = scrape_all_urls(BASE_URL)
    file_path = os.path.join('data', 'website_content.txt')
    write_content_to_file(content, file_path)
    st.success(f"Content scraped and saved to {file_path}")

# Schedule the scraping task to run on the 1st of every month
schedule.every().month.at("00:00").do(scrape_and_save_content)

# Function to run pending scheduled tasks
def run_scheduled_tasks():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Run scheduled tasks in a separate thread
import threading
thread = threading.Thread(target=run_scheduled_tasks)
thread.start()

# Main Streamlit app
def main():
    st.title("Website Scraper and AI Chatbot")
    
    if st.button("Scrape and Save Content"):
        scrape_and_save_content()

    st.write("Scheduled scraping will occur on the 1st of every month.")

if __name__ == "__main__":
    main()
