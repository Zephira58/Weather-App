import requests
import random
import os
import tkinter as tk
import threading
import queue
from colorama import Fore, init
from elevenlabs.client import ElevenLabs
from elevenlabs import play

init(autoreset=True)

API_KEY = "mPRThPBpIyxQMmzJR8Epbg6taOR5sBkY"
ELEVENLABS_API_KEY = "sk_b75da21ac8a033356d53fc457f1abb267811a4cecdf2a90d"

locations = {
    'Maryborough': {'lat': -25.532, 'lon': 152.701},
    'Hervey Bay': {'lat': -25.290, 'lon': 152.844}
}

phrases = [
    "The temperature is {temperature} degrees Celsius in {city} with {humidity} percent humidity.",
    "Right now, in {city}, it's {temperature} degrees Celsius with {humidity} percent humidity.",
    "At the moment, the temperature in {city} is {temperature} degrees Celsius with humidity at {humidity} percent."
]

VERSION = "0.1.0"

lock = threading.Lock()

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Queue to store the audio tasks
audio_queue = queue.Queue()

def fetch_weather(city, lat, lon):
    print(Fore.YELLOW + f"Fetching weather data for {city}...")
    url = f'https://api.tomorrow.io/v4/timelines'
    params = {
        'location': f'{lat},{lon}',
        'fields': ['temperature', 'humidity'],
        'timesteps': 'current',
        'apikey': API_KEY
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print(Fore.GREEN + f"Successfully fetched data for {city}.")
        data = response.json()
        temperature = data['data']['timelines'][0]['intervals'][0]['values']['temperature']
        humidity = data['data']['timelines'][0]['intervals'][0]['values']['humidity']
        return temperature, humidity
    else:
        print(Fore.RED + f"Error fetching data for {city}. Status code: {response.status_code}")
        return None, None

def play_audio_sequentially():
    while True:
        # Wait until there is an audio task in the queue
        audio_task = audio_queue.get()
        if audio_task is None:
            break  # Exit if None is received (used to stop the thread)
        
        play(audio_task)
        audio_queue.task_done()

def announce_weather_with_11labs(city, temperature, humidity, text_widget, output_file):
    print(Fore.YELLOW + f"Announcing weather for {city} using 11Labs API...")
    phrase = random.choice(phrases).format(city=city, temperature=temperature, humidity=humidity)
    
    text_widget.insert(tk.END, f"{phrase}\n\n")
    text_widget.yview(tk.END)
    
    audio = client.generate(
        text=phrase,
        voice="Charlie",
        model="eleven_multilingual_v2"
    )
    
    # Add the audio task to the queue for sequential processing
    audio_queue.put(audio)
    
    with open(output_file, "a") as file:
        file.write(f"{phrase}\n\n")
    
    print(Fore.GREEN + f"Finished announcing weather for {city}.")

def fetch_and_announce_weather(city, coords, text_widget, output_file):
    temperature, humidity = fetch_weather(city, coords['lat'], coords['lon'])
    if temperature is not None and humidity is not None:
        announce_weather_with_11labs(city, temperature, humidity, text_widget, output_file)

def generate_random_example(text_widget, output_file):
    cities = ['Maryborough', 'Hervey Bay']
    random_city = random.choice(cities)
    random_temp = random.randint(15, 35)
    random_humidity = random.randint(40, 90)
    
    phrase = random.choice(phrases).format(city=random_city, temperature=random_temp, humidity=random_humidity)
    
    text_widget.insert(tk.END, f"{phrase}\n\n")
    text_widget.yview(tk.END)
    
    audio = client.generate(
        text=phrase,
        voice="Charlie",
        model="eleven_multilingual_v2"
    )
    
    # Add the audio task to the queue for sequential processing
    audio_queue.put(audio)

    with open(output_file, "a") as file:
        file.write(f"{phrase}\n\n")

def display_weather():
    print(Fore.YELLOW + "Initializing Tkinter window...")
    print(Fore.CYAN + "-Credits-\nCreator: Zephira\nWebsite: https://zephira.uk/\nVersion: " + VERSION + "\nNote: Heya so I've gone ahead and made this small application under the request of a friend, its entire purpose is to just fetch the current weather in 2 hardcoded locations and use a tts algorithm to speak them aloud, if you wish to check out my work please take a look at my website.\n")
    print(Fore.GREEN + "-Logs-")
    
    window = tk.Tk()
    window.title("Weather Information")
    window.configure(bg="#2e2e2e")
    
    text_widget = tk.Text(window, wrap=tk.WORD, height=10, width=50, font=("Helvetica", 12), fg="white", bg="#2e2e2e", bd=0, insertbackground='white')
    text_widget.pack(padx=20, pady=20)
    
    scrollbar = tk.Scrollbar(window, command=text_widget.yview)
    text_widget.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    output_file = "weather_update.txt"
    
    def on_button_click():
        print(Fore.YELLOW + "Button clicked, starting to fetch weather data...")
        for city, coords in locations.items():
            threading.Thread(target=fetch_and_announce_weather, args=(city, coords, text_widget, output_file), daemon=True).start()
        print(Fore.GREEN + "\nWeather update started.")
    
    def on_random_example_click():
        print(Fore.YELLOW + "Button clicked, displaying random weather example...")
        threading.Thread(target=generate_random_example, args=(text_widget, output_file), daemon=True).start()
        print(Fore.GREEN + "\nRandom example displayed.")
    
    button = tk.Button(window, text="Get Weather Update", command=on_button_click, font=("Helvetica", 12), fg="white", bg="#4CAF50")
    button.pack(padx=20, pady=10)
    
    random_example_button = tk.Button(window, text="Show Random Example", command=on_random_example_click, font=("Helvetica", 12), fg="white", bg="#FF9800")
    random_example_button.pack(padx=20, pady=10)

    window.geometry("500x400")
    
    # Start the audio queue processing thread
    threading.Thread(target=play_audio_sequentially, daemon=True).start()
    
    window.mainloop()

display_weather()
