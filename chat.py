import streamlit as st
import requests

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
    st.title("Chat with Gemini API")

    st.write("Enter your message below and chat with the Gemini API:")
    user_input = st.text_input("Your Message:")

    api_key = st.text_input("Enter your Gemini API Key:", type="password")

    if st.button("Send"):
        if user_input and api_key:
            response = chat_with_gemini(user_input, api_key)
            st.write("Response from Gemini API:")
            st.write(response)
        else:
            st.error("Please enter both a message and your API key.")

if __name__ == "__main__":
    main()
