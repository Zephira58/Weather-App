import requests
import random
import tkinter as tk
import threading
import queue
import time
from colorama import Fore, init
from elevenlabs.client import ElevenLabs
from elevenlabs import play

init(autoreset=True)

API_KEY = "[LOADAPIKEY HERE]"
ELEVENLABS_API_KEY = "LOADAPIKEY HERE"

locations = {
    'Maryborough': {'lat': -25.532, 'lon': 152.701},
    'Hervey Bay': {'lat': -25.290, 'lon': 152.844}
}

greetings = [
    "Currently, in {city},",
    "Right now in {city},",
    "At the moment in {city},",
    "Over in {city},",
    "In {city} as of now,",
    "Here in {city},",
    "As it stands in {city},",
    "What’s happening in {city} is,",
    "If you're in {city},",
    "In the city of {city},",
    "Weather-wise in {city},",
    "Presently in {city},",
    "Checking in from {city},",
    "Over at {city},",
    "Right here in {city},",
    "Here in the heart of {city},",
    "In the bustling city of {city},",
    "Looking at {city} right now,",
    "Reporting live from {city},",
    "As of this moment in {city},"
]

temperature_phrases = [
    "the temperature is {temperature} degrees Celsius",
    "it's {temperature} degrees Celsius",
    "we have {temperature} degrees Celsius",
    "the current temperature stands at {temperature} degrees Celsius",
    "you'll find it to be {temperature} degrees Celsius",
    "we’re sitting at {temperature} degrees Celsius",
    "the mercury reads {temperature} degrees Celsius",
    "the thermometer shows {temperature} degrees Celsius",
    "the air temperature is {temperature} degrees Celsius",
    "it measures {temperature} degrees Celsius",
    "the outdoor temperature is {temperature} degrees Celsius",
    "it’s holding steady at {temperature} degrees Celsius",
    "you can expect {temperature} degrees Celsius",
    "we’re experiencing {temperature} degrees Celsius",
    "right now, it’s {temperature} degrees Celsius",
    "it has reached {temperature} degrees Celsius",
    "temperatures are at {temperature} degrees Celsius",
    "the current reading is {temperature} degrees Celsius",
    "it’s clocking in at {temperature} degrees Celsius",
    "the present temperature is {temperature} degrees Celsius"
]

humidity_phrases = [
    "with {humidity}% humidity.",
    "and a humidity level of {humidity}%.",
    "accompanied by {humidity}% humidity.",
    "and the humidity is at {humidity}%.",
    "with humidity levels reaching {humidity}%.",
    "alongside {humidity}% humidity.",
    "with a current humidity of {humidity}%.",
    "as humidity hits {humidity}%.",
    "and the air is {humidity}% humid.",
    "showing a humidity reading of {humidity}%.",
    "recording {humidity}% humidity.",
    "with {humidity}% moisture in the air.",
    "with atmospheric humidity of {humidity}%.",
    "boasting {humidity}% humidity.",
    "holding steady at {humidity}% humidity.",
    "and the humidity percentage is {humidity}%.",
    "registering a humidity of {humidity}%.",
    "with the humidity level currently at {humidity}%.",
    "showcasing {humidity}% humidity.",
    "and a relative humidity of {humidity}%."
]


VERSION = "0.2.0"

lock = threading.Lock()
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
audio_queue = queue.Queue()

def log_message(message, log_file="app_log.txt"):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    full_message = f"[{timestamp}] {message}\n"
    print(Fore.YELLOW + full_message)
    with open(log_file, "a") as file:
        file.write(full_message)

def generate_dynamic_phrase(city, temperature, humidity):
    phrase = f"{random.choice(greetings)} {random.choice(temperature_phrases)} {random.choice(humidity_phrases)}"
    return phrase.format(city=city, temperature=temperature, humidity=humidity)

def fetch_weather(city, lat, lon):
    log_message(f"Fetching weather data for {city}...")
    url = f'https://api.tomorrow.io/v4/timelines'
    params = {
        'location': f'{lat},{lon}',
        'fields': ['temperature', 'humidity'],
        'timesteps': 'current',
        'apikey': API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        log_message(f"Successfully fetched data for {city}.")
        data = response.json()
        temperature = data['data']['timelines'][0]['intervals'][0]['values']['temperature']
        humidity = data['data']['timelines'][0]['intervals'][0]['values']['humidity']
        return temperature, humidity
    else:
        log_message(f"Error fetching data for {city}. Status code: {response.status_code}", log_file="error_log.txt")
        return None, None

def play_audio_sequentially():
    while True:
        audio_task = audio_queue.get()
        if audio_task is None:
            break
        play(audio_task)
        audio_queue.task_done()

def announce_weather_with_11labs(city, temperature, humidity, text_widget, output_file):
    log_message(f"Announcing weather for {city} using 11Labs API...")
    phrase = generate_dynamic_phrase(city, temperature, humidity)
    
    text_widget.insert(tk.END, f"{phrase}\n\n")
    text_widget.yview(tk.END)

    audio = client.generate(
        text=phrase,
        voice="Charlie",
        model="eleven_multilingual_v2"
    )

    log_message(f"Generated speech for {city} with temperature {temperature}°C and humidity {humidity}%. Using voice model Charlie.")
    audio_queue.put(audio)

    with open(output_file, "a") as file:
        file.write(f"{phrase}\n\n")

    log_message(f"Finished announcing weather for {city}.")

def fetch_and_announce_weather(city, coords, text_widget, output_file):
    temperature, humidity = fetch_weather(city, coords['lat'], coords['lon'])
    if temperature is not None and humidity is not None:
        announce_weather_with_11labs(city, temperature, humidity, text_widget, output_file)

def generate_random_example(text_widget, output_file):
    cities = list(locations.keys())
    random_city = random.choice(cities)
    random_temp = random.randint(15, 35)
    random_humidity = random.randint(40, 90)

    phrase = generate_dynamic_phrase(random_city, random_temp, random_humidity)

    log_message(f"Generating random weather example for {random_city}...")

    text_widget.insert(tk.END, f"{phrase}\n\n")
    text_widget.yview(tk.END)

    audio = client.generate(
        text=phrase,
        voice="Charlie",
        model="eleven_multilingual_v2"
    )

    log_message(f"Generated random speech for {random_city} with temperature {random_temp}°C and humidity {random_humidity}%. Using voice model Charlie.")
    audio_queue.put(audio)

    with open(output_file, "a") as file:
        file.write(f"{phrase}\n\n")

def display_weather():
    log_message(Fore.CYAN + "-Credits-\nCreator: Zephira\nWebsite: https://zephira.uk/\nVersion: " + VERSION + "\n")
    log_message(Fore.GREEN + "-Logs-")

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
        log_message("Button clicked, starting to fetch weather data...")
        for city, coords in locations.items():
            threading.Thread(target=fetch_and_announce_weather, args=(city, coords, text_widget, output_file), daemon=True).start()
        log_message("Weather update started.")

    def on_random_example_click():
        log_message("Button clicked, displaying random weather example...")
        threading.Thread(target=generate_random_example, args=(text_widget, output_file), daemon=True).start()
        log_message("Random example displayed.")

    button = tk.Button(window, text="Get Weather Update", command=on_button_click, font=("Helvetica", 12), fg="white", bg="#4CAF50")
    button.pack(padx=20, pady=10)

    random_example_button = tk.Button(window, text="Show Random Example", command=on_random_example_click, font=("Helvetica", 12), fg="white", bg="#FF9800")
    random_example_button.pack(padx=20, pady=10)

    window.geometry("500x400")

    threading.Thread(target=play_audio_sequentially, daemon=True).start()

    window.mainloop()

display_weather()
