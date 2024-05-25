import streamlit as st
from google.cloud import bigquery
import pandas as pd
from google.oauth2 import service_account
import json
import requests
import datetime

# Service account key details
service_account_info = {
    "type": "service_account",
    "project_id": "cloudproject-424110",
    "private_key_id": "cd884a9677b1eb1f20e4b1fe209eff92636fb73e",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDYg+fLrQz0Xm2W\nYaJWa/Yj1tWNPIbIrofefc3eahQsDzJVymELk+VeHmR6ySeE6rOUHt6z7JmTsul9\nrrDVwtSPlYB8K46rsOCsFcJnMwlFkIPW+O2P0ml1KfCl7ydwm2Cf+Zo6MsYBD4yv\nrQiHKfF89rlMBBpbFDntjMdx4LjqhPEzf5B7AXUaUe9zdz3isrxxb6s7hC7oGkTY\nUl0vvMwAsiNx9vc4rFgTpiF3t71SQEv/DIBnojKay14QB74VzzNCzDTxUEHxF/tL\nZB38TUZVyTi51yxVb+fcAWuanWP+cYX8x9yj9q81k4i/2EKt3CeX2i3jr614gnAL\nVBm8oyOJAgMBAAECggEAIBpcw+MehNw8cPv8g0ZiOlmoE9c53+ca77clD3mYkJjX\nPIezoHEXJP+qI9eQE8HuCwQRvslR0yfHvZIpl6RZ+okvAho+PwBMq89VIhKb6RPe\nrID/zl+jMdNcYmolpalwKAAtKTxuhek9ka29Ejd6ni4B9v6zvrXuyeViDCVHHcR+\n/JHWo9M+bi68mo3aAfmiOmQyqB4xd0XL6k7zN1EdytkkEKRLgj6eSxCqXLiCRUxp\npcqdWjn3VDKHOS/dyJe9vw8rsqP2E8Js9iCHPXbG1k7E12y4IKLfUvPFBVKmAT7X\nR5ITCVF39/v2WjmdPiyeO3TcWaw1Fk4y49uPJhLzRQKBgQD7Yyn+ReO/1RFh15Lo\nNavGXgOT9C2ycXUB6Pl1RM9WP+1ryUBTNU0KanuhYBk3HhwJ/SNjW6XLc+jBC2Ga\nyNUtqzZvLrTG64cpxVDVlWiciPeuo8YWwEAeaFfMaG627Deyy7ATEdTLnuSyNWyw\nF+sdlDG7/iZ80tBCd4Nq55Wm1QKBgQDcfO//2cSmJNZB0fdNJrr2yVlRpOEeEGGC\ntpPbzHARi2U53Hwf6zXtfZD4hI8NrJr+6IAofcSM35zjFwWtr1kNWXCKVnAE1tsq\nHsioZXhbqKumyKufQ9jG//Csvc/73XD74/BrL7vp3CSjEi0mMfdgpcTWLXgZOD7D\nMEkUN5LL5QKBgQCzn4ul8HJn4+rjqpGB8remqg6MbXEpjAA7OSjmLiCoVE1lMwwP\naIp/4s4r5Oqfg5gtWv8qQ5YX5d5t8Z/wZYhNdYUTtJ/fcvPFWQQFWRjCoOu5kbQ9\nFWm7UHtLx2M0uVyjGP/a4GbYh9SJsbrTqIOLQxS2a0c88bV1iMgSXx+DcQKBgHSf\n3S5+mIatC2uLTPzRFKm+vPDzfmOxlHJYcoMbctfE3MkrN7iGaGLzPQBG1YgNGXrl\nrgw84f8FtG1l2woQqtDl0yJJMD1PDGQOHmL8MRqCcDDrCeRXNc2kyUAFsoJtkfqa\niauYdxPu7q4Wyize1xOW+zOyn0jvuDr0SmNYNdyFAoGAHcbvQHzUM4vXkPBus6A0\nfumrfatmYCwVKl8zwUA5NgO/cZrdVIeO75RghYZ8M7kcbE92wSrd6wa2tQBFw6EO\nzXK93b3jSVfV+eKYrx7ZpZLLPx0TRv/2QEQhKJ3yCRj681/LF+Tw8+ZvXE51LdtY\nuwg34ehcKtzQy5aQFF64JlU=\n-----END PRIVATE KEY-----\n",
    "client_email": "cloudproject@cloudproject-424110.iam.gserviceaccount.com",
    "client_id": "115004387933230655429",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/cloudproject-424110.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

credentials = service_account.Credentials.from_service_account_info(service_account_info)

client = bigquery.Client(credentials=credentials, project=credentials.project_id)

def get_data_from_bigquery():
    query = """
    SELECT date, time, indoor_temp, indoor_humidity, outdoor_temp, outdoor_humidity, outdoor_weather
    FROM `cloudproject-424110.weather_data.weather_records`
    ORDER BY date DESC, time DESC
    """
    query_job = client.query(query)
    results = query_job.result()
    return results.to_dataframe()

def get_outdoor_weather(api_key, latitude, longitude):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()
    if 'main' in data and 'weather' in data:
        outdoor_temp = data['main']['temp']
        outdoor_temp_max = data['main']['temp_max']
        outdoor_temp_min = data['main']['temp_min']
        outdoor_humidity = data['main']['humidity']
        weather_icon = data['weather'][0]['icon']
        return outdoor_temp, outdoor_temp_max, outdoor_temp_min, outdoor_humidity, weather_icon
    else:
        return None, None, None, None, None

def get_forecast(api_key, city_name):
    base_url = 'http://api.openweathermap.org/data/2.5/forecast'
    complete_url = f"{base_url}?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(complete_url)
    
    if response.status_code == 200:
        data = response.json()
        forecasts = data['list']
        forecast_data = []
        
        for forecast in forecasts:
            forecast_time = forecast['dt_txt']
            if '12:00:00' in forecast_time:  # Filter for noon forecasts
                temp = forecast['main']['temp']
                temp_min = forecast['main']['temp_min']
                temp_max = forecast['main']['temp_max']
                weather_description = forecast['weather'][0]['description']
                icon = forecast['weather'][0]['icon']
                
                forecast_data.append({
                    'Date': forecast_time,
                    'Day': pd.to_datetime(forecast_time).strftime('%A'),
                    'Temperature': temp,
                    'Min Temp': temp_min,
                    'Max Temp': temp_max,
                    'Description': weather_description,
                    'Icon': f"http://openweathermap.org/img/wn/{icon}.png"
                })
                if len(forecast_data) >= 5:  # Limit to 5 forecasts
                    break
        
        df = pd.DataFrame(forecast_data)
        return df
    else:
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

data = get_data_from_bigquery()

# Your OpenWeatherMap API key
api_key = "dc205f6b07d82ca369a1a66980ea5009"
city_name = 'lausanne'

outdoor_temp, outdoor_temp_max, outdoor_temp_min, outdoor_humidity, weather_icon = get_outdoor_weather(api_key, 46.516, 6.6328)
forecast_df = get_forecast(api_key, city_name)

# CSS to customize appearance
page_bg_img = '''
<style>
.stApp {
    background-image: url("https://imgur.com/QyHdWgV.png");
    background-size: cover;
}

.big-font {
    font-size:50px !important;
}

.container {
    padding: 10px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 5px;
    margin-bottom: 10px;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

st.title("Weather Dashboard")

st.markdown(f'<p class="big-font">{pd.to_datetime("today").strftime("%Y-%m-%d")}</p>', unsafe_allow_html=True)
st.markdown(f'<p class="big-font">{pd.to_datetime("now").strftime("%H:%M")}</p>', unsafe_allow_html=True)

# Use columns to display containers
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.write("### Indoor Data")
    if not data.empty:
        current_data = data.iloc[0]
        st.write(f"Indoor Temperature: {current_data['indoor_temp']} °C")
        st.write(f"Indoor Humidity: {current_data['indoor_humidity']} %")
    else:
        st.write("No data available")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.write("### Outdoor Data")
    if outdoor_temp is not None:
        st.write(f"Current Temperature: {outdoor_temp} °C")
        st.write(f"Max Temperature: {outdoor_temp_max} °C")
        st.write(f"Min Temperature: {outdoor_temp_min} °C")
        st.write(f"Humidity: {outdoor_humidity} %")
        if weather_icon:
            icon_url = f"http://openweathermap.org/img/wn/{weather_icon}@2x.png"
            st.image(icon_url, width=100)
    else:
        st.write("Outdoor Temperature: Data not available")
        st.write("Weather icon not available")
    st.markdown('</div>', unsafe_allow_html=True)

# Add the 5-day forecast section aligned horizontally
st.write("### 5-Day Forecast")
if not forecast_df.empty:
    cols = st.columns(5)
    for i, (index, row) in enumerate(forecast_df.iterrows()):
        with cols[i]:
            st.markdown(f"**{row['Day']}**")
            st.markdown(f"Temp: {row['Temperature']} °C")
            st.image(row['Icon'], width=100)
            if i >= 4:
                break
else:
    st.write("No forecast data available")

st.write("### Historical Data")
columns_to_plot = ['date', 'indoor_temp', 'indoor_humidity']
if 'outdoor_temp_max' in data.columns:
    columns_to_plot.append('outdoor_temp_max')
st.line_chart(data[columns_to_plot].set_index('date'))

st.write("### Historical Data Table")
st.dataframe(data)
