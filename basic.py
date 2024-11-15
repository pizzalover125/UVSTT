import speech_recognition as sr
import keyboard
import time
from datetime import datetime
import json
import os
from colorama import init, Fore, Back, Style

class SpeechTyper:
    def __init__(self):
        # Initialize colorama for cross-platform color support
        init(autoreset=True)
        
        self.config = {
            'language': 'en-US',
            'pause_key': 'f9',
            'exit_key': 'ctrl+c',
            'typing_delay': 0.1,
            'auto_capitalize': True,
            'auto_punctuate': True,
            'log_errors': True
        }
        self.is_paused = False
        self.recognizer = sr.Recognizer()
        self.load_config()
        
    def load_config(self):
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    self.config.update(json.load(f))
        except Exception as e:
            self.log_error(f"Error loading config: {e}")

    def save_config(self):
        try:
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.log_error(f"Error saving config: {e}")

    def log_error(self, error_message):
        if self.config['log_errors']:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('error_log.txt', 'a') as f:
                f.write(f"[{timestamp}] {error_message}")

            print(f"{Fore.RED}[{timestamp}] {error_message}{Style.RESET_ALL}")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        status = f"{Fore.YELLOW}Paused{Style.RESET_ALL}" if self.is_paused else f"{Fore.GREEN}Resumed{Style.RESET_ALL}"
        print(f"{status} speech recognition. Press {Fore.CYAN}{self.config['pause_key']}{Style.RESET_ALL} to {('resume' if self.is_paused else 'pause')}...")

    def type_text(self, text):
        if self.config['auto_capitalize']:
            text = '. '.join(s.capitalize() for s in text.split('. '))
            
        if self.config['auto_punctuate']:
            if not text.rstrip()[-1] in '.!?':
                text += '.'
        
        print(f"{Fore.GREEN}Recognized: {text}{Style.RESET_ALL}")
        
        for char in text:
            keyboard.write(char)
            time.sleep(self.config['typing_delay'])

        keyboard.write(" ")

    def listen_and_type(self):
        print(f"{Fore.CYAN}{Style.BRIGHT}UniversalSpeechToText{Style.RESET_ALL}")
        print(f"Press {Fore.CYAN}{self.config['pause_key']}{Style.RESET_ALL} to pause/resume")
        print(f"Press {Fore.CYAN}{self.config['exit_key']}{Style.RESET_ALL} to exit")
        print(f"{Fore.WHITE}Speak into your microphone...{Style.RESET_ALL}")
        
        keyboard.on_press_key(self.config['pause_key'], lambda _: self.toggle_pause())
        
        while True:
            if not self.is_paused:
                with sr.Microphone() as source:
                    try:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        
                        text = self.recognizer.recognize_google(audio, language=self.config['language'])
                        
                        if text.lower() in ['new line', 'newline', 'line break']:
                            keyboard.press_and_release('enter')
                            print(f"{Fore.BLUE}Action: New line{Style.RESET_ALL}")
                        elif text.lower() == 'delete line':
                            keyboard.press_and_release('home, shift+end, backspace')
                            print(f"{Fore.BLUE}Action: Delete line{Style.RESET_ALL}")
                        else:
                            self.type_text(text)
                            
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        print(f"{Fore.YELLOW}Could not understand audio{Style.RESET_ALL}")
                    except sr.RequestError as e:
                        error_msg = f"Could not request results: {e}"
                        print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
                        self.log_error(error_msg)
                    except Exception as e:
                        error_msg = f"Unexpected error: {e}"
                        print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
                        self.log_error(error_msg)
            else:
                time.sleep(0.1)
    
if __name__ == "__main__":
    typer = SpeechTyper()
    try:
        typer.listen_and_type()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Exiting...{Style.RESET_ALL}")
    finally:
        typer.save_config()

