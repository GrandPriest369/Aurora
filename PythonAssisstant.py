import subprocess
import pyttsx3
import json
import random
import threading
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import pyjokes
import feedparser
import smtplib
import ctypes
import time
import requests
import shutil
from twilio.rest import Client
from clint.textui import progress
from ecapture import ecapture as ec
from bs4 import BeautifulSoup
from urllib.request import urlopen
import nltk
from transformers import pipeline
from transformers import AutoTokenizer
import torch
from gtts import gTTS
import pygame
import tkinter as tk
import queue
import urllib.parse
import psutil
from googletrans import Translator
import asyncio
import pyautogui
import cv2
import mysql.connector
import pygetwindow as gw
import pyperclip
from pygame import mixer
from ctypes import cast, POINTER
import pygame.mixer as mixer
import requests
import pymorphy3
import pyaudio
import AppKit
import g4f

pygame.mixer.init()

message_queue = queue.Queue()

engine = pyttsx3.init('nsss')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

g4f.debug.logging = False
g4f.debug.version_check = False

# Путь к файлу
HISTORY_FILE = 'history.json'

# Проверяем, существует ли файл
if not os.path.exists(HISTORY_FILE):
    # Создаем файл и записываем в него пустой список в формате JSON
    with open(HISTORY_FILE, 'w', encoding='utf-8') as file:
        json.dump([], file)
    print(f"Файл {HISTORY_FILE} был создан.")
else:
    print(f"Файл {HISTORY_FILE} уже существует.") 

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 7:
        speak("Приятной ночи Сэр!")
    elif hour <= 12:
        speak("Доброе утро Сэр !")
    elif hour >= 12 and hour < 18:
        speak("Доброго дня Сэр !")
    else:
        speak("Доброго вечера Сэр !")

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="ru-RU")
        print(f"User said: {query}\n")
    except Exception as e:
        print(e)
        print("Unable to Recognize your voice")
        return "none"

    if (query.lower().startswith('аврора')):
        return query.lower()
    else:
        return "none"

def handle_wikipedia(command):
    speak("Открываю Википедию...")
    query = command.replace("википедия", "").strip()
    results = wikipedia.summary(query, sentences=3)
    speak("Согласно Википедии")
    print(results)
    speak(results)

stop_listening = True
is_text_input_mode = False
listen_thread = None

def speak(text):
    tts = gTTS(text=text, lang='ru')
    filename = "temp.mp3"
    tts.save(filename)
    os.system(f"afplay {filename}")
    time.sleep(1) 


# Пути для macOS
music_dir = "/Users/eduardnazipov/Music"  # Исправленный путь к музыке
image_path = '/Users/eduardnazipov/Desktop/image.png'  # Пример пути для macOS

IGNORED_FILES = {'desktop.ini', 'thumbs.db'}

def get_music_files(directory):
    music_files = []
    for file in os.listdir(directory):
        if file.lower() not in IGNORED_FILES and file.lower().endswith(('.mp3', '.wav', '.ogg', '.mpeg')):
            music_files.append(file)
    return music_files

# Получаем список музыкальных файлов
music_dir = "/Users/eduardnazipov/Desktop/Music"
songs = get_music_files(music_dir)

if not songs:
    print("В папке с музыкой нет поддерживаемых файлов.")
    speak("В папке с музыкой нет поддерживаемых файлов.")

is_music_paused = False
current_song_index = 0

def play_next_song():
    global current_song_index, is_music_paused
    if not songs:
        print("Нет доступных музыкальных файлов.")
        speak("Нет доступных музыкальных файлов.")
        return

    if current_song_index >= len(songs):
        current_song_index = 0  # Начинаем с начала, если дошли до конца списка

    current_song = songs[current_song_index]
    song_path = os.path.join(music_dir, current_song)
    print(f"Attempting to play: {song_path}")

    # Воспроизведение музыки
    try:
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        is_music_paused = False
        current_song_index += 1
    except pygame.error as e:
        print(f"Ошибка при воспроизведении файла {current_song}: {e}")
        speak(f"Не удалось воспроизвести файл {current_song}.")
        current_song_index += 1

def play_music(command):
    global is_music_paused
    if not songs:
        print("Нет доступных музыкальных файлов.")
        speak("Нет доступных музыкальных файлов.")
        return

    play_next_song()  # Начинаем воспроизведение первой песни

    # Ожидание команд управления
    while True:
        command = takeCommand()
        handle_command(command)

        if "пауза" in command:
            pause_music(command)
        elif "продолжить" in command:
            continue_music(command)
        elif "следующая" in command:
            next_song(command)
        elif "выключи музыку" in command:
            off_music(command)
            break
        elif "громкость" in command:
            try:
                # Извлекаем уровень громкости из команды (например, "громкость на 50")
                volume_level = int(command.split("на")[1].strip()) / 100
                set_volume(command, volume_level)
            except Exception as e:
                print(f"Ошибка при установке громкости: {e}")
                speak("Не удалось установить громкость.")

        # Проверка завершения текущей песни
        if not pygame.mixer.music.get_busy() and not is_music_paused:
            play_next_song()

def pause_music(command):
    global is_music_paused
    print(f"Состояние паузы до паузы: {is_music_paused}")
    if not is_music_paused:
        pygame.mixer.music.pause()
        is_music_paused = True
        speak("Музыка на паузе")
    else:
        print(f"Состояние паузы после паузы: {is_music_paused}")

def continue_music(command):
    global is_music_paused
    print(f"Состояние паузы до продолжения: {is_music_paused}")
    if is_music_paused:
        pygame.mixer.music.unpause()
        is_music_paused = False
    else:
        speak("Музыка не на паузе.")
    print(f"Состояние паузы после продолжения: {is_music_paused}")

def next_song(command):
    global current_song_index
    pygame.mixer.music.stop()  # Останавливаем текущую песню
    play_next_song()  # Воспроизводим следующую


    pygame.mixer.music.stop()
    current_song = random.choice(songs)
    song_path = os.path.join(music_dir, current_song)
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()
    is_music_paused = False

def off_music(command):
    global is_music_paused
    pygame.mixer.music.stop()
    is_music_paused = False  # Сбрасываем состояние паузы
    speak("Выключаю музыку")


def set_volume(command, volume_level=None):
    if volume_level is None:
        if "максимум" in command:
            volume_level = 100
        elif "минимум" in command:
            volume_level = 0
        else:
            try:
                volume_level = int(command.split("на")[1].strip())
            except (IndexError, ValueError):
                return

    # Установка громкости через AppleScript
    os.system(f"osascript -e 'set volume output volume {volume_level}'")
    speak(f"Громкость установлена на {volume_level}%")

def play_system_sound(file_path):
    sound = AppKit.NSSound.alloc().initWithContentsOfFile_byReference_(file_path, True)
    sound.play()

def tell_time(command):
    strTime = datetime.datetime.now().strftime("%H:%M:%S")
    speak(f"Сэр, время сейчас {strTime}")

def exit_program(command):
    speak("Спасибо вам за провёденное время")
    exit()

def shutdown_computer(command):
    speak("Подождите секунду! Ваша система находится на пути к завершению работы")
    subprocess.call('shutdown /p /f')    

def get_weather(command):
    app_key = "e1345894395637103f48499c1920686d"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    speak("Пожалуйста, назовите город.")
    city_name = takeCommand()

    morph = pymorphy3.MorphAnalyzer()
    try:
        parsed_city = morph.parse(city_name)[0]
        city_name_datv = parsed_city.inflect({"loct"}).word
    except Exception as e:
        print(f"Ошибка при склонении города: {e}")
        city_name_datv = city_name

    complete_url = base_url + "appid=" + app_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]
        current_temperature_kelvin = y["temp"]
        current_temperature_celsius = current_temperature_kelvin - 273.15
        current_temperature_celsius = round(current_temperature_celsius, 2)
        speak(f"Температура в {city_name_datv} составляет {current_temperature_celsius} градусов Цельсия.")
    else:
        speak("Город не найден.")

def open_youtube():
    webbrowser.open("https://www.youtube.com")

def open_telegram():
    webbrowser.open("https://web.telegram.org")

def search_youtube(command):
    search_query = command.replace("найди в поиске", "").strip()
    if search_query:
            encoded_query = urllib.parse.quote(search_query)
            webbrowser.open(f"https://www.youtube.com/results?search_query={encoded_query}")
    else:
        speak("Пожалуйста, укажите, что искать.")

translator = Translator()
loop = asyncio.get_event_loop()

async def joke():
    joke = pyjokes.get_joke()
    joke_result = await translator.translate(joke, dest='ru')
    speak(joke_result.text)

def handle_joke_command():
    loop.run_until_complete(joke())

current_message = ""
stop_listening = False
image_path = r'/Users/eduardnazipov/Desktop/Aurora_Assistant/Поле_ввода.png'
lock = threading.Lock()
is_text_input_mode = False  # Флаг для отслеживания режима ввода текста

def start_text_input_mode():
    global current_message, stop_listening, is_text_input_mode
    with lock:
        current_message = ""
        stop_listening = True  # Останавливаем прослушивание команд
        is_text_input_mode = True  # Входим в режим ввода текста

    click_input_field(image_path)  # Укажите путь к изображению поля ввода

    speak("Начинаю ввод текста. Пожалуйста, говорите.")  # Уведомление о начале ввода
    
    # Запускаем прослушивание текста в отдельном потоке
    listening_thread = threading.Thread(target=listen_for_text_input, daemon=True)
    listening_thread.start()

def click_input_field(image_path):
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=0.8)
        if location is not None:
            center_x, center_y = pyautogui.center(location)
            pyautogui.click(center_x, center_y)
            speak("Поле ввода найдено и кликнуто.")
            time.sleep(1)  # Увеличена задержка
        else:
            speak("Поле ввода не найдено. Проверьте изображение и его соответствие.")
            stop_listening = True
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        stop_listening = True

def activate_telegram_window():
    os.system("open -a Telegram")  # Открытие через системную команду
    time.sleep(1)

def listen_for_text_input():
    global current_message, stop_listening, is_text_input_mode
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Аврора: Готова к прослушиванию текста...")
        silence_start_time = time.time()

        while is_text_input_mode:
            try:
                audio = recognizer.listen(source, timeout=2)
                text = recognizer.recognize_google(audio, language='ru-RU').strip()
                print(f"Распознано: '{text}'")

                if text:
                    if current_message == "":
                        current_message = text
                    else:
                        current_message += f", {text}"
                    pyperclip.copy(current_message)
                    print(f"Добавлено в текст: {current_message}")
                    print(f"Текст в буфере: {pyperclip.paste()}")

                    # Очистка поля ввода и вставка текста
                    try:
                        pyautogui.hotkey('ctrl', 'a')  # Выделить всё
                        pyautogui.press('backspace')   # Удалить текст
                        pyautogui.hotkey('ctrl', 'v')  # Вставить текст
                        time.sleep(0.5)  # Задержка для вставки
                    except Exception as e:
                        print(f"Ошибка при вставке текста: {e}")

                    silence_start_time = time.time()  # Сбрасываем таймер молчания

            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"Произошла ошибка при распознавании: {e}")

            # Проверяем, прошло ли 3 секунды молчания
            if time.time() - silence_start_time > 3:
                with lock:
                    is_text_input_mode = False
                speak("Ввод текста завершен из-за молчания.")
                break

    with lock:
        is_text_input_mode = False
        print("Режим ввода текста завершен, возвращаемся к прослушиванию команд.")
    start_listening()
  
def send_message():
    global current_message
    if current_message.strip():  # Проверяем, что сообщение не пустое
        print(f"Отправляю сообщение: {current_message}")
        pyautogui.press('enter')  # Нажимаем Enter для отправки сообщения
        current_message = ""  # Очистка текущего сообщения после отправки

        # Очистка поля ввода
        time.sleep(0.1)  # Небольшая задержка, чтобы убедиться, что сообщение отправлено
        pyautogui.hotkey('ctrl', 'a')  # Выделить всё
        pyautogui.press('backspace')  # Удалить текст
    else:
        speak("Нет сообщения для отправки.")

def delete_message():
    global current_message
    current_message = ""  # Очистка текущего сообщения
    print("Сообщение очищено.")
    
    # Используем комбинацию клавиш для удаления текста из поля ввода
    pyautogui.hotkey('ctrl', 'a')  # Выделяем всё
    pyautogui.press('delete')

def save_to_history(command, response):
    """Сохраняет команду и ответ в историю"""
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as file:
            history = json.load(file)
    except FileNotFoundError:
        history = []

    history.append({"command": command, "response": response})

    with open(HISTORY_FILE, 'w', encoding='utf-8') as file:
        json.dump(history, file, indent=4, ensure_ascii=False)

def get_history():
    """Получает историю запросов"""
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as file:
            history = json.load(file)
    except FileNotFoundError:
        history = []
    return history

def handle_command(command):
    global current_message, is_text_input_mode
    if is_text_input_mode:
        speak("Команда игнорируется, так как ИИ находится в режиме ввода текста.")
        return
    
    command = command.lower().strip()
    print(f"Обработка команды: {command}")
    message_queue.put(f"Команда: {command}\n")

    actions = {
        "википедия": handle_wikipedia,
        "открой youtube": open_youtube,
        "включи музыку": play_music,
        "пауза": pause_music,
        "продолжить": continue_music,
        "следующая": next_song,
        "выключить музыку": off_music,
        "громкость": set_volume,
        "время": tell_time,
        "открой браузер": lambda: os.system('open -a "Safari"'),
        "как ты": lambda: speak("Я в порядке! Спасибо за беспокойство!"),
        "расскажи шутку": handle_joke_command,
        "завершить работу": on_closing,
        "открой telegram": open_telegram,
        "кто ты": lambda: speak("Я Аврора, голосовой ассистент созданный тобой!"),
        "выключить компьютер": shutdown_computer,
        "где находится": lambda cmd: open_google_maps(cmd.replace("где находится", "").strip()),
        "погода": get_weather,
        "открой презентацию": lambda: os.system('open -a "Keynote"'),
        "найди в поиске": search_youtube,
        "текст": start_text_input_mode,
        "отправить": send_message,
        "очистить": delete_message,
    }

    command_found = False

    for key in actions:
        if key in command:
            print(f"Команда найдена: {key}")
            command_found = True
            if callable(actions[key]):
                if actions[key].__code__.co_argcount == 0:
                    actions[key]()
                else:
                    actions[key](command)
            break

    if command_found:
        user_id = "user_1"  
        insert_command(user_id, command)
    else:
        if (command.lower().startswith('аврора')):
            """Обрабатывает команду, используя историю запросов"""
            # Получаем историю запросов
            history = get_history()

            # Подготавливаем сообщения с историей запросов
            messages = [
                {"role": "system", "content": "всегда возвращай короткий ответ. отвечай коротко. ограничь ответ 130 символами. ограничь ответ 100 токенами. отправляй короткий ответ, не теряя общего смысла ответа."},
            ]
            for item in history:
                messages.append({"role": "user", "content": item["command"]})
                messages.append({"role": "assistant", "content": item["response"]})
                messages.append({"role":"system","content":"всегда возвращай короткий ответ. отвечай коротко. ограничь ответ 130 символами. ограничь ответ 100 токенами. отправляй короткий ответ, не теряя общего смысла ответа."})

            # Добавляем текущий запрос
            messages.append({"role": "user", "content": command[7:]})

            # Отправляем запрос и получаем ответ
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=messages,
            )

            # Сохраняем текущий запрос и ответ в историю
            save_to_history(command[7:], response)

            print(response)

            # Выводим ответ в текстовое поле
            output_text.insert(tk.END, f"Аврора: {response}\n")

            return command.lower()

            # response = g4f.ChatCompletion.create(
            #     model=g4f.models.gpt_4,
            #     messages=[
            #         {"role": "system", "content": "всегда возвращай короткий ответ. отвечай коротко. ограничь ответ 130 символами. ограничь ответ 100 токенами. отправляй короткий ответ, не теряя общего смысла ответа."},
            #         {"role": "user", "content": command[7:]}
            #     ],
            # )  
            # speak(response)
            # output_text.insert(tk.END, f"Аврора: {response}\n")
            # return command.lower()
        else:
            return "none"

def insert_command(user_id, command):
    try:
        conn = mysql.connector.connect(
            host='MacBook-Pro-Eduard.local',
            user='root',
            password='18081227',
            database='Aurora_database'
        )

        cursor = conn.cursor()

        # Вставляем новую команду
        cursor.execute('INSERT INTO history (user_id, command) VALUES (%s, %s)', (user_id, command))


        # Проверяем количество записей
        cursor.execute('SELECT COUNT(*) FROM history')
        count = cursor.fetchone()[0]
        
        # Если записей больше 25, удаляем самую старую
        if count > 25:
            cursor.execute('CREATE TEMPORARY TABLE temp_ids AS SELECT id FROM history ORDER BY timestamp ASC LIMIT 1')
            cursor.execute('DELETE FROM history WHERE id IN (SELECT id FROM temp_ids)')

        conn.commit()
        
    except mysql.connector.Error as err:
        print(f"Ошибка: {err}")
    finally:
        cursor.close()
        conn.close()

def open_google_maps(command):
    # Удаляем ключевую фразу и лишние пробелы
    location = command.replace("где находится", "").strip()
    
    # Если location пустой (например, сказали просто "где находится")
    if not location:
        speak("Пожалуйста, укажите место для поиска")
        return
    
    encoded_location = urllib.parse.quote_plus(location)
    webbrowser.open(f"https://www.google.com/maps/place/{encoded_location}")

def update_output_text(text):
    message_queue.put(text)

def listen():
    global stop_listening
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        while not stop_listening:
            try:
                # Обновляем интерфейс и консоль
                print("Аврора: Слушаю...")  # В консоль
                message_queue.put("Аврора: Слушаю...\n")  # В интерфейс
                
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
                command = recognizer.recognize_google(audio, language='ru-RU')
                
                print(f"Распознано: {command}")  # В консоль
                message_queue.put(f"Вы: {command}\n")  # В интерфейс
                
                if not is_text_input_mode:
                    handle_command(command)
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                print("Не удалось распознать речь")  # В консоль
                message_queue.put("Аврора: Не расслышала команду.\n")
            except sr.RequestError as e:
                print(f"Ошибка сервиса: {e}")  # В консоль
                message_queue.put("Аврора: Ошибка сервиса распознавания.\n")
            except Exception as e:
                print(f"Критическая ошибка: {e}")  # В консоль
                message_queue.put(f"Аврора: Критическая ошибка: {str(e)[:50]}...\n")

def check_queue():
    try:
        while True:
            message = message_queue.get_nowait()
            output_text.insert(tk.END, message)
            output_text.see(tk.END)
    except queue.Empty:
        pass

    root.after(100, check_queue)

def start_listening():
    global stop_listening, is_text_input_mode, listen_thread
    stop_listening = False
    is_text_input_mode = False
    
    # Если поток не запущен или завершился - создаём новый
    if not hasattr(start_listening, "listen_thread") or not start_listening.listen_thread.is_alive():
        start_listening.listen_thread = threading.Thread(target=listen, daemon=True)
        start_listening.listen_thread.start()
    
    update_output_text("Начато прослушивание...\n")

def stop_listening_function():
    global stop_listening
    stop_listening = True
    output_text.insert(tk.END, "Прослушивание остановлено.\n")

def on_closing():
    global stop_listening
    stop_listening = True
    if hasattr(start_listening, "listen_thread"):
        start_listening.listen_thread.join(timeout=1)  # Ожидаем завершения потока
    root.destroy()

root = tk.Tk()
root.title("Голосовой Ассистент Аврора")
root.geometry("1200x800")
root.configure(bg="#2E2E2E")

title_label = tk.Label(root, text="Voice Assistant Aurora", bg="#2E2E2E", fg="#FFFFFF", font=("Yu Gothic Light", 16))
title_label.pack(pady=10)

output_text = tk.Text(root, height=20, width=70, bg="#F5DEB3", fg="#000000", font=("Yu Gothic Light", 12))
output_text.pack(pady=10)

start_button = tk.Button(root, text="Начать прослушивание", command=start_listening, bg="#4CAF50", fg="#FFFFFF", font=("Yu Gothic Light", 12))
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Остановить прослушивание", command=stop_listening_function, bg="#F44336", fg="#FFFFFF", font=("Yu Gothic Light", 12))
stop_button.pack(pady=5)

stop_listening = False

# Запуск прослушивания в отдельном потоке
threading.Thread(target=listen, daemon=True).start()

root.protocol("WM_DELETE_WINDOW", on_closing)

if __name__ == "__main__":
    wishMe()
    root.after(100, check_queue)
    root.mainloop()