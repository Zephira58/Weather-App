import requests
import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# BOM API details
API_KEY = "28404aee-9318-4163-83bc-d10f744c6e3f"  # Your API key
LATITUDE = -25.2794  # Latitude for Hervey Bay
LONGITUDE = 152.7628  # Longitude for Hervey Bay
BASE_URL = "https://sws-data.sws.bom.gov.au/api/v1/observations"  # Corrected endpoint for observations

# Function to get weather data from BOM API
def get_weather_data():
    response = requests.get(BASE_URL, params={
        'lat': LATITUDE,
        'lon': LONGITUDE,
        'apiKey': API_KEY
    })

    if response.status_code == 200:
        data = response.json()

        # Print the raw response data to check the full structure
        print(json.dumps(data, indent=4))  # Pretty print the data in the terminal to inspect

        if 'observations' in data:
            observation = data['observations'][0]  # Get the first observation

            try:
                temp = observation['air_temperature']  # Air temperature
                humidity = observation['humidity']  # Humidity
                rainfall = observation.get('rainfall', 0)  # Rainfall (if any) in mm
                last_updated = observation['timestamp']

                # Format the last updated time
                last_updated_time = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%fZ")
                last_updated_formatted = last_updated_time.strftime("%d %b %Y, %I:%M %p")

                # Call the function to display the data
                display_weather_data(temp, humidity, rainfall, last_updated_formatted)

                # Schedule the next refresh in 10 minutes (600,000 milliseconds)
                window.after(600000, get_weather_data)

            except KeyError as e:
                print(f"KeyError: Missing key {e} in the data.")
                messagebox.showerror("Error", f"Missing data: {e}")
        else:
            print("Error: Observations data not found.")
            messagebox.showerror("Error", "Weather data not found for the requested location.")
    else:
        print(f"Failed to retrieve weather data. HTTP Status Code: {response.status_code}")
        messagebox.showerror("Error", f"Failed to retrieve weather data. HTTP Status Code: {response.status_code}")

# Function to display the weather data in a Tkinter window
def display_weather_data(temp, humidity, rainfall, last_updated):
    global window
    # Create a new Tkinter window if not already created
    if not 'window' in globals():
        window = tk.Tk()
        window.title("Weather Information")

        # Set window size and background color
        window.geometry("300x350")  # Adjusted height for more space
        window.configure(bg="lightblue")

    # Clear previous labels and display updated data
    for widget in window.winfo_children():
        widget.destroy()

    # Label for current temperature
    temp_label = tk.Label(window, text=f"Current Temperature: {temp}°C", font=("Arial", 14), bg="lightblue")
    temp_label.pack(pady=10)

    # Label for humidity
    humidity_label = tk.Label(window, text=f"Humidity: {humidity}%", font=("Arial", 14), bg="lightblue")
    humidity_label.pack(pady=10)

    # Label for rainfall
    rainfall_label = tk.Label(window, text=f"Rainfall (Last Hour): {rainfall} mm", font=("Arial", 14), bg="lightblue")
    rainfall_label.pack(pady=10)

    # Label for last updated time
    last_updated_label = tk.Label(window, text=f"Last Updated: {last_updated}", font=("Arial", 12), bg="lightblue")
    last_updated_label.pack(pady=10)

    # Start the Tkinter event loop
    window.mainloop()

# Main function to run the program
if __name__ == "__main__":
    get_weather_data()
