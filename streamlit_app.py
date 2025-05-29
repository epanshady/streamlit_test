import streamlit as st
import requests

# Set the app title 
st.title('Currency') 

# Add a welcome message 
st.write('Exchanger') 

# Create a text input 
widgetuser_input = st.text_input('Enter a custom message:', 'Hello, Streamlit!') 

# Display the customized message 
st.write('Customized Message:', widgetuser_input)

# Add a dropdown for currency selection
currency_choice = st.selectbox('Choose a currency to convert from MYR:', 
                               ['USD', 'EUR', 'GBP', 'AUD', 'CAD', 'JPY'])

# Display the chosen currency
st.write(f'You selected {currency_choice}.')

# API calls based on the selected currency
url = f'https://api.vatcomply.com/rates?base=MYR'

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    if currency_choice in data['rates']:
        rate = data['rates'][currency_choice]
        st.write(f"The exchange rate for MYR to {currency_choice} is: {rate}")
    else:
        st.error(f"Exchange rate for {currency_choice} not found.")
else:
    st.error(f"API call failed with status code: {response.status_code}")




