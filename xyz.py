
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
