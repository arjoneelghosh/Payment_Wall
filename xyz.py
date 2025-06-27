import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from datetime import datetime

# OpenWeatherMap API key
API_KEY = "51ae582e2c8e6e2c3a7703824ca9f4b4"

# Function to fetch AQI data
def fetch_aqi_data(city):
    GEO_API_URL = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    geo_response = requests.get(GEO_API_URL)

    if geo_response.status_code == 200:
        geo_data = geo_response.json()
        if geo_data:
            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
            AQI_API_URL = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
            aqi_response = requests.get(AQI_API_URL)

            if aqi_response.status_code == 200:
                return geo_data[0], aqi_response.json()
    return None, None

# Input for city name
city = st.text_input("Enter city name to check AQI:")

if city:
    st.write("Fetching AQI data...")
    location_data, aqi_data = fetch_aqi_data(city)

    if location_data and aqi_data:
        # Extract AQI and coordinates
        lat, lon = location_data['lat'], location_data['lon']
        aqi_value = aqi_data['list'][0]['main']['aqi']

        # Simulated historical data
        historical_data = [
            {"hour": i, "AQI": aqi_value + (i % 5)} for i in range(24)
        ]
        df = pd.DataFrame(historical_data)

        # Data Preparation for Forecasting
        st.write("### Forecasting Future AQI Levels")
        df['hour'] = pd.to_datetime(df['hour'], unit='h', origin=pd.Timestamp("2023-01-01"))
        df['hour_num'] = df['hour'].dt.hour

        # Features and Target
        X = df[['hour_num']]
        y = df['AQI']

        # Train-Test Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train Model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Predict Future Values
        future_hours = pd.DataFrame({"hour_num": np.arange(24, 48)})  # Next 24 hours
        future_aqi = model.predict(future_hours)

        # Calculate Confidence Intervals
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        ci = 1.96 * np.sqrt(mse)  # 95% confidence interval

        # Create Forecast DataFrame
        forecast_df = pd.DataFrame({
            "hour": future_hours["hour_num"].to_numpy().flatten(),
            "AQI": future_aqi,
            "lower_bound": future_aqi - ci,
            "upper_bound": future_aqi + ci
        })

        # Visualization of Forecast
        st.write("### Predicted AQI for the Next 24 Hours")
        forecast_fig = px.line(
            forecast_df,
            x="hour",
            y=["AQI", "lower_bound", "upper_bound"],
            labels={"value": "AQI", "hour": "Hour"},
            title="AQI Forecast with Confidence Intervals"
        )
        st.plotly_chart(forecast_fig)

        # Heatmap Visualization
        st.write("### AQI Heatmap")
        m = folium.Map(location=[lat, lon], zoom_start=10)
        folium.CircleMarker(
            location=[lat, lon],
            radius=10,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.7,
            tooltip=f"{city}: Predicted AQI {round(future_aqi[0], 2)}"
        ).add_to(m)
        st_folium(m, width=700, height=500)

    else:
        st.error("Could not fetch AQI data. Please check the city name or API key.")

# Footer
st.write("---")
st.write("Powered by OpenWeatherMap API | Machine Learning with scikit-learn")
