import customtkinter as ctk
from tkinter import simpledialog, messagebox
from brain import *  # Importing the existing brain.py functionalities
from voice_engine import speak  # Import speak function to make Cyclops talk
from scheduler_engine import add_schedule, check_schedule, schedule_remover, create_file
from visual_engine import show_my_face, emotion_identity  # Import visual engine functions
from music_engine import play_music, play_youtube_video  # Import music engine functions
import datetime
import time
import threading 
import os
import csv
import random
from news_engine import get_news_world
# Set the appearance mode and color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Initialize the main application window
# Movement Manager class to handle all bot movements
class CyclopsUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cyclops Desktop Assistant")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.random_movement_active = False
        self.emotion_detection_active = False
        # Initialize camera lock for thread safety
        self.camera_lock = threading.Lock()
        
        self.initialize_assistant()
        self.create_widgets()
        self.create_visual_controls()  # Add visual controls
        self.initialize_pir_sensor()   # Initialize PIR sensor in background
    def initialize_assistant(self):
        """Initialize the assistant with user preferences and LLM model"""
        try:
            if os.path.exists("user_pref.txt"):
                with open('user_pref.txt', 'r') as f:
                    lines = f.readlines()
                    
                    # Look for the line that starts with "Name: "
                    self.user_name = "User"  # Default value
                    for line in lines:
                        if line.strip().startswith("Name:"):
                            # Extract the name after "Name: "
                            self.user_name = line.strip().split("Name:")[1].strip()
                            break
                            
                    print(f"Loaded user name: {self.user_name}")
            else:
                self.user_name = "User"
                print("user_pref.txt not found, using default name")

            # Initialize LLM model
            self.message, self.llama_model = llama_message_init(USER_DETAILS)
            
            # Load camera configuration if that function exists
            if hasattr(self, 'load_camera_config'):
                self.load_camera_config()
        except Exception as e:
            print(f"Error initializing assistant: {e}")
            self.user_name = "User"
            # Still try to initialize LLM even if there was an error with the user name
            self.message, self.llama_model = llama_message_init(USER_DETAILS)

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)

        self.welcome_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Welcome, {self.user_name}!",
            font=("Arial", 24, "bold"),
            text_color="#2E86C1"
        )
        self.welcome_label.pack(pady=(20, 10))

        self.chat_area = ctk.CTkScrollableFrame(self.main_frame, width=800, height=400)
        self.chat_area.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        self.input_textbox = ctk.CTkTextbox(
            self.main_frame,
            width=600,
            height=50,
            font=("Arial", 14),
            wrap=ctk.WORD,
            fg_color="#FFFFFF",
            text_color="#000000",
            border_width=2,
            border_color="#3498DB"
        )
        self.input_textbox.pack(pady=(10, 20), padx=20)
        self.input_textbox.bind("<Return>", self.process_command)

        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(pady=(10, 20))

        buttons = [
            ("🎵 Play Music", self.play_music, "#3498DB", "#2980B9"),
            ("⏹️ Stop Music", self.stop_music, "#9B59B6", "#8E44AD"),
            ("⏰ Set Timer", self.set_timer, "#E67E22", "#D35400"),
            ("📝 Add Note", self.add_note, "#27AE60", "#229954"),                        
            ("📅 Schedule", self.schedule_manager, "#8E44AD", "#7D3C98"),
            ("⏻ Shutdown", self.shutdown, "#E74C3C", "#C0392B"),
             ("🔍 Motion Sensor", self.motion_sensor_settings, "#34495E", "#2C3E50")  # Added motion sensor button
        ]

        for i, (text, command, fg_color, hover_color) in enumerate(buttons):
            button = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                font=("Arial", 14),
                fg_color=fg_color,
                hover_color=hover_color
            )
            button.grid(row=0, column=i, padx=5, pady=5)

    def create_visual_controls(self):
        """Create controls for the visual engine features"""
        visual_frame = ctk.CTkFrame(self.main_frame)
        visual_frame.pack(pady=(5, 20))

        visual_label = ctk.CTkLabel(
            visual_frame,
            text="Camera Controls:",
            font=("Arial", 16, "bold"),
            text_color="#2E86C1"
        )
        visual_label.grid(row=0, column=0, columnspan=5, pady=(5, 10))

        # Camera buttons (optional, but keeping them for manual control)
        camera_buttons = [
            ("📷 Take Photo", self.take_photo, "#1ABC9C", "#16A085"),
            ("👁️ Check Me", self.check_appearance, "#F39C12", "#E67E22"),
            ("😊 Detect Emotion", self.detect_emotion, "#3498DB", "#2980B9"),
            ("🎭 Toggle Emotion Tracking", self.toggle_emotion_detection, "#9B59B6", "#8E44AD"),
            ("🌡️ Check Temperature", self.check_temperature, "#2E86C1", "#2874A6"),
            ("📰 News", self.news_manager, "#1ABC9C", "#16A085"),  # Added News button
            ("🎮 Play Game", self.play_game, "#E74C3C", "#C0392B") 
            
        ]

        for i, (text, command, fg_color, hover_color) in enumerate(camera_buttons):
            button = ctk.CTkButton(
                visual_frame,
                text=text,
                command=command,
                font=("Arial", 14),
                fg_color=fg_color,
                hover_color=hover_color
            )
            button.grid(row=1, column=i, padx=6, pady=6)

    def add_chat_bubble(self, text, is_user=True):
        bubble_frame = ctk.CTkFrame(
            self.chat_area,
            corner_radius=15,
            fg_color="#3498DB" if is_user else "#2C3E50",
        )
        bubble_frame.pack(fill=ctk.X, padx=5, pady=5, anchor="e" if is_user else "w")

        bubble_label = ctk.CTkLabel(
            bubble_frame,
            text=text,
            font=("Arial", 14),
            text_color="#FFFFFF" if is_user else "#ECF0F1",
            wraplength=600,
            justify="left"
        )
        bubble_label.pack(padx=10, pady=10)

        self.chat_area._parent_canvas.yview_moveto(1.0)

        if not is_user:
            threading.Thread(target=speak, args=(text.replace("Cyclops:", "").strip(),), daemon=True).start()

    def process_command(self, event=None):
        command = self.input_textbox.get("1.0", ctk.END).strip().lower()
        self.input_textbox.delete("1.0", ctk.END)

        if not command:
            return

        self.add_chat_bubble(f"You: {command}", is_user=True)
        
        # Check for "Hey Cyclops, take photo" or similar commands
        if self.handle_direct_commands(command):
            return # Exit early after handling the photo command

        # Existing command processing
        try:
            send_data("Processing", LOOP_ARD)
        except Exception as e:
            print(f"Error sending motion command: {e}")
        response, function, self.message = LLM_answer(command, self.message, self.llama_model)

            
      
        self.add_chat_bubble(f"Cyclops: {response}", is_user=False)

        if function:
            try:
                if "play_youtube" in function or "play_music" in function:
                   send_data("thinking", LOOP_ARD)
                elif "timer" in function:
                    send_data("clock", LOOP_ARD)
                    send_data("thinking", LOOP_ARD)
                elif "schedule" in function:
                    send_data("#Scheduler", LOOP_ARD)
                    send_data("thinking", LOOP_ARD)
                elif "show_image" in function:
                    send_data("#" + response, LOOP_ARD)
                else:
                    send_data("thinking", LOOP_ARD)
                    
                llm_interpreter(function, response)
            except Exception as e:
                print(f"Error during function execution: {e}")
                try:
                    send_data("idle", LOOP_ARD)
                except:
                    pass
    def handle_direct_commands(self,command) :
        if any(phrase in command.lower() for phrase in ["hello cyclops", "hey cyclops"]):
            self.add_chat_bubble(f"Cyclops: Hello {self.user_name}! How can I help you today?", is_user=False)
            return True
        if any(phrase in command for phrase in ["take photo", "take a photo", "take picture", "capture image"]) :
            self.take_photo()
            return True
        
        if any(phrase in command for phrase in ["check me", "how do i look", "check appearance", "see me"]):
            self.check_appearance()
            return True
            
        # Emotion detection commands
        if any(phrase in command for phrase in ["detect emotion", "analyze emotion", "how am i feeling", "check emotion"]):
            self.detect_emotion()
            return True
            
        # Toggle emotion tracking
        if any(phrase in command for phrase in ["start emotion tracking", "begin emotion tracking", "track emotions"]):
            if not self.emotion_detection_active:
                self.toggle_emotion_detection()
            return True
            # Temperature commands - new addition
        if any(phrase in command for phrase in ["check temperature", "what's the temperature", "how hot is it", "how cold is it", "weather"]):
            self.check_temperature()
            return True
            
        if any(phrase in command for phrase in ["stop emotion tracking", "end emotion tracking", "disable emotion tracking"]):
            if self.emotion_detection_active:
                self.toggle_emotion_detection()
            return True
        
        if any(phrase in command for phrase in ["previous note", "last note", "read my note", "show my note", "tell me my note"]):
             self.tell_previous_note()
             return True
            
    # Schedule commands
        if any(phrase in command for phrase in ["open schedule", "show schedule", "view schedule", "manage schedule","make schedule"]):
            self.schedule_manager()
            return True
            
        if any(phrase in command for phrase in ["check schedule", "today's schedule", "what's on today", "my schedule", "tell me my schedule"]):
            self.tell_todays_schedule()
            return True
            
                
        if any(phrase in command for phrase in ["stop moving", "stop motion", "end movement"]):
            if self.random_movement_active:
                self.toggle_random_movements()
            return True
        if "play music" in command or "play song" in command or "play track" in command:
        # Check if a specific song is requested
            if any(phrase in command for phrase in ["play song", "play track"]) or "by" in command:
                # Extract song name - this is a simple extraction, could be improved
                song_name = command.replace("play song", "").replace("play track", "").replace("play music", "").strip()
                if song_name:
                    self.add_chat_bubble(f"Cyclops: Playing {song_name}...", is_user=False)
                    try :
                        send_data("sine",LOOP_ARD)
                        send_data(f"#Now Playing: {song_name[:16]}", LOOP_ARD)  # Limit to 16 chars for LCD
                    except Exception as e:
                        print(f"Error sending LCD command: {e}")
                    self.dancing = True
                    threading.Thread(target=self.dance_animation, args=(song_name,), daemon=True).start()
                    play_youtube_video(song_name)
                    return True
            
            # Check for genre if no specific song is detected
            genre = None
            for music_type in ["techno", "pop", "rock", "jazz", "classical"]:
                if music_type in command:
                    genre = music_type
                    break
            
            if genre:

                self.add_chat_bubble(f"Cyclops: Playing {genre} music...", is_user=False)
            # Send command to display sinewave on LCD
                try:
                    send_data("sine", LOOP_ARD)
                    send_data(f"#Now Playing: {genre} music", LOOP_ARD)
                except Exception as e:
                    print(f"Error sending LCD command: {e}")
                    
                self.dancing = True
                threading.Thread(target=self.dance_animation, args=(genre,), daemon=True).start()
                play_music(genre)
            else:
                self.play_music()  # Will prompt for genre or song
            return True
            
        if "set timer" in command or "start timer" in command:
            # Try to extract minutes from the command
            import re
            minutes_match = re.search(r'(\d+)\s*(?:minute|min|m)s?', command)
            if minutes_match:
                minutes = int(minutes_match.group(1))
                try:
                    send_data("clock", LOOP_ARD)
                except Exception as e:
                    print(f"Error sending data to Arduino: {e}")
                self.add_chat_bubble(f"Cyclops: Timer set for {minutes} minutes.", is_user=False)
                threading.Thread(target=self.run_timer, args=(minutes, "Text command timer"), daemon=True).start()
            else:
                self.set_timer()  # Will prompt for duration
            return True
            
        # Note commands
        if "add note" in command or "create note" in command or "new note" in command:
            self.add_note()
            return True
            
        # Schedule commands
        if any(phrase in command for phrase in ["open schedule", "show schedule", "view schedule", "manage schedule","make schedule"]):
            self.schedule_manager()
            return True
            
        if "check schedule" in command or "today's schedule" in command:
            self.check_schedule()
            return True
        if any(phrase in command for phrase in ["enable motion detection", "activate motion sensor", "turn on motion sensor"]):
            try:
                send_data("motion_on", LOOP_ARD)
                self.add_chat_bubble("Cyclops: Motion detection activated. I'll respond when I detect movement.", is_user=False)
            except Exception as e:
                print(f"Error enabling motion detection: {e}")
            return True
        
        if any(phrase in command for phrase in ["disable motion detection", "deactivate motion sensor", "turn off motion sensor"]):
            try:
                send_data("motion_off", LOOP_ARD)
                self.add_chat_bubble("Cyclops: Motion detection deactivated.", is_user=False)
            except Exception as e:
                print(f"Error disabling motion detection: {e}")
            return True
        
        if any(phrase in command for phrase in ["news", "latest news", "what's happening", "current events"]):
            # Only open the news manager dialog if no specific news type is mentioned
            if not any(specific in command for specific in ["world", "global", "international", "science", "scientific", "space"]):
                self.news_manager()
            else:
                # If world news is mentioned, call that method directly
                if any(phrase in command for phrase in ["world news", "global news", "international news"]):
                    self.get_world_news()
                # If science news is mentioned, call that method directly
                elif any(phrase in command for phrase in ["science news", "scientific news", "space news"]):
                    self.get_science_news()
            return True
            
        # Shutdown command
        if any(phrase in command for phrase in ["shutdown", "turn off", "power off", "exit"]):
            self.shutdown()
            return True
        if any(phrase in command for phrase in ["play game", "start game", "launch game"]):
            self.play_game()
            return True
        
        if "play hangman" in command:
            self.play_hangman()
            return True
        
        if any(phrase in command for phrase in ["play rock paper scissors", "play rps"]):
            self.play_rps()
            return True
            
        # No direct command matched
        return False

    def take_photo(self):
        """Take a photo using the camera"""
        try:
            self.add_chat_bubble("Cyclops: Preparing to take a photo...", is_user=False)
            send_data("camera", LOOP_ARD)
            threading.Thread(target=self.capture_photo_thread, daemon=True).start()
        except Exception as e:
            self.add_chat_bubble(f"Cyclops: Error activating camera: {str(e)}", is_user=False)
            print(f"Error in take_photo: {e}")

    def capture_photo_thread(self):
        """Thread function to capture photo without blocking UI"""
        try:
            with self.camera_lock:
                show_my_face(get_face=0, click_pic=1)
            self.root.after(0, lambda: self.add_chat_bubble(
                "Cyclops: Photo taken and saved in the photos_taken directory!", is_user=False))
          
            time.sleep(2)  # Show happy movement briefl
            
        except Exception as e:
            print(f"Error in capture_photo_thread: {e}")
            self.root.after(0, lambda: self.add_chat_bubble(
                f"Cyclops: Error taking photo: {str(e)}", is_user=False))
           
            time.sleep(2)
          
    def check_appearance(self):
        """Check user's appearance using the camera"""
        try:
            self.add_chat_bubble("Cyclops: Let me see how you look...", is_user=False)
            send_data("camera", LOOP_ARD)
            threading.Thread(target=self.check_appearance_thread, daemon=True).start()
        except Exception as e:
            self.add_chat_bubble(f"Cyclops: Error activating camera: {str(e)}", is_user=False)
            print(f"Error in check_appearance: {e}")

    def check_appearance_thread(self):
        """Thread function to check appearance without blocking UI"""
        try:
            with self.camera_lock:
                result = show_my_face()
            try:
                send_data("idle", LOOP_ARD)
                if result is not None:
                    send_data("happy", LOOP_ARD)
                    self.root.after(0, lambda: self.add_chat_bubble(
                        "Cyclops: I've checked your appearance. You look great today!", is_user=False))
                else:
                 
                    self.root.after(0, lambda: self.add_chat_bubble(
                        "Cyclops: I couldn't detect your face. Please make sure you're visible to the camera.", is_user=False))
                time.sleep(2)  # Show emotion movement briefly
             
            except Exception as e:
                print(f"Error setting idle state: {e}")
        except Exception as e:
            print(f"Error in check_appearance_thread: {e}")
            self.root.after(0, lambda: self.add_chat_bubble(
                f"Cyclops: Error checking appearance: {str(e)}", is_user=False))
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass

    def detect_emotion(self):
        """Detect user's emotion using the visual engine"""
        try:
            self.add_chat_bubble("Cyclops: Analyzing your emotions...", is_user=False)
            send_data("#Analyzing Emotions", LOOP_ARD)
            threading.Thread(target=self.detect_emotion_thread, daemon=True).start()
        except Exception as e:
            self.add_chat_bubble(f"Cyclops: Error starting emotion detection: {str(e)}", is_user=False)
            print(f"Error in detect_emotion: {e}")

    def detect_emotion_thread(self):
        """Thread function to detect emotion without blocking UI"""
        try:
            with self.camera_lock:
                emotion, eye_status = emotion_identity()
            self.root.after(0, lambda: self.process_detected_emotion(emotion, eye_status))
        except Exception as e:
            print(f"Error in detect_emotion_thread: {e}")
            self.root.after(0, lambda: self.add_chat_bubble(
                f"Cyclops: Error detecting emotion: {str(e)}", is_user=False))
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass
    def handle_drowsy_state(self):
        """Handle drowsy state detection with power nap timer option"""
        try:
            # Send drowsy state to Arduino
            send_data("#Zzzz Zzzzz", LOOP_ARD)
            
            # Inform user about drowsy state
            self.add_chat_bubble("Cyclops: You are drowsy. Please do some stretching or take a power nap.", is_user=False)
            
            # Create a frame for power nap timer option
            nap_frame = ctk.CTkFrame(self.chat_area)
            nap_frame.pack(fill=ctk.X, padx=5, pady=5, anchor="w")
            
            # Ask about setting a power nap timer
            nap_label = ctk.CTkLabel(
                nap_frame,
                text="Should I set a power nap timer for 25 minutes?",
                font=("Arial", 14),
                text_color="#ECF0F1"
            )
            nap_label.pack(padx=10, pady=5)
            
            # Create buttons for yes/no response
            button_frame = ctk.CTkFrame(nap_frame, fg_color="transparent")
            button_frame.pack(pady=5)
            
            def set_power_nap():
                try:
                    send_data("clock", LOOP_ARD)
                    nap_frame.destroy()
                    self.add_chat_bubble("Cyclops: Setting a 25-minute power nap timer.", is_user=False)
                    threading.Thread(target=self.run_timer, args=(25, "Power nap"), daemon=True).start()
                except Exception as e:
                    print(f"Error setting power nap timer: {e}")
                    self.add_chat_bubble(f"Cyclops: Error setting timer: {str(e)}", is_user=False)
            
            def decline_power_nap():
                nap_frame.destroy()
                self.add_chat_bubble(
                    "Cyclops: Ok then, I am not setting a timer. But please remember body requires some maintenance to keep going.", 
                    is_user=False
                )
            
            # Yes button
            yes_button = ctk.CTkButton(
                button_frame,
                text="Yes",
                command=set_power_nap,
                font=("Arial", 14),
                fg_color="#27AE60",
                hover_color="#229954",
                width=100
            )
            yes_button.grid(row=0, column=0, padx=10, pady=5)
            
            # No button
            no_button = ctk.CTkButton(
                button_frame,
                text="No",
                command=decline_power_nap,
                font=("Arial", 14),
                fg_color="#E74C3C",
                hover_color="#C0392B",
                width=100
            )
            no_button.grid(row=0, column=1, padx=10, pady=5)
            
        except Exception as e:
            print(f"Error in handle_drowsy_state: {e}")
            self.add_chat_bubble(f"Cyclops: Error handling drowsy state: {str(e)}", is_user=False)
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass

    def process_detected_emotion(self, emotion, eye_status):
        """Process and respond to the detected emotion"""
        try:
            self.add_chat_bubble(f"Cyclops: I detect you're feeling {emotion}. Your eyes are {eye_status}.", is_user=False)
            if emotion == 'happy' and eye_status == 'open':
                send_data("happy", LOOP_ARD)
                self.add_chat_bubble("Cyclops: You look happy! That's great to see!", is_user=False)
            elif emotion == 'sad' and eye_status == 'open':
                self.handle_sad_emotion()
            elif eye_status == 'closed':
                # Call the new function to handle drowsy state
                self.handle_drowsy_state()
            else:
                send_data("idle", LOOP_ARD)
                self.add_chat_bubble("Cyclops: Thanks for letting me analyze your emotions.", is_user=False)
        except Exception as e:
            print(f"Error in process_detected_emotion: {e}")
            self.add_chat_bubble(f"Cyclops: Error processing emotion: {str(e)}", is_user=False)
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass

    def toggle_emotion_detection(self):
        """Toggle continuous emotion detection on/off"""
        self.emotion_detection_active = not self.emotion_detection_active
        if self.emotion_detection_active:
            self.add_chat_bubble("Cyclops: Emotion tracking activated. I'll monitor your emotions periodically.", is_user=False)
            threading.Thread(target=self.continuous_emotion_detection, daemon=True).start()
        else:
            self.add_chat_bubble("Cyclops: Emotion tracking deactivated.", is_user=False)

    def continuous_emotion_detection(self):
        """Thread function for continuous emotion detection"""
        try:
            while self.emotion_detection_active:
                if not self.dancing:
                    with self.camera_lock:
                        emotion, eye_status = emotion_identity(5)
                    if emotion != 'neutral' or eye_status == 'closed':
                        self.root.after(0, lambda e=emotion, es=eye_status: 
                                       self.process_detected_emotion(e, es))
                for _ in range(300):
                    if not self.emotion_detection_active:
                        break
                    time.sleep(1)
        except Exception as e:
            print(f"Error in continuous_emotion_detection: {e}")
            self.emotion_detection_active = False
            self.root.after(0, lambda: self.add_chat_bubble(
                f"Cyclops: Error in emotion tracking: {str(e)}", is_user=False))

    def random_movement_thread(self):
        try:
            moves = ["rotate1", "rotate2", "sine", "@90", "@120", "@150"]
            wait_time = 0
            while self.random_movement_active:
                if not self.dancing and wait_time <= 0:
                    if random.random() < 0.3:
                        move = random.choice(moves)
                        try:
                            send_data(move, 1)
                            wait_time = random.randint(20, 40) if move in ["rotate1", "rotate2", "sine"] else random.randint(10, 20)
                        except Exception as e:
                            print(f"Error sending movement command: {e}")
                if wait_time > 0:
                    wait_time -= 1
                time.sleep(1)
        except Exception as e:
            print(f"Error in random_movement_thread: {e}")
            self.random_movement_active = False

    def shutdown(self):
        """Enhanced shutdown with natural movements"""
        self.random_movement_active = False
        self.dancing = False
        self.emotion_detection_active = False
        
        # Execute a special shutdown sequence
        try:
            self.add_chat_bubble("Cyclops: Shutting down... Goodbye!", is_user=False)
            
            send_data("sad", LOOP_ARD)
            send_data("angry",LOOP_ARD)
            send_data("shutdown", LOOP_ARD)
        except Exception as e:
            print(f"Error during shutdown sequence: a{e}")
            
        # Stop the movement manager
        
        # Delay the actual shutdown to allow the sequence to complete
        self.root.after(2000, self.root.destroy)


    def play_music(self):
        """Enhanced play_music method that uses the music_engine functionality"""
        # Ask user if they want to play a specific song or a genre
        choice_dialog = ctk.CTkToplevel(self.root)
        choice_dialog.title("Play Music")
        choice_dialog.geometry("400x200")
        choice_dialog.transient(self.root)
        choice_dialog.grab_set()
        
        title_label = ctk.CTkLabel(
            choice_dialog,
            text="What would you like to play?",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(20, 20))
        
        def play_specific_song():
            choice_dialog.destroy()
            song_name = simpledialog.askstring("Play Song", "Enter song name and artist (e.g., Sunflower by Post Malone):")
            if song_name:
                self.add_chat_bubble(f"Cyclops: Playing {song_name}...", is_user=False)
                # Send command to display sinewave on LCD
                try:
                    send_data("sine", LOOP_ARD)
                    send_data(f"#Now Playing: {song_name[:16]}", LOOP_ARD)  # Limit to 16 chars for LCD
                except Exception as e:
                    print(f"Error sending LCD command: {e}")
                    
                self.dancing = True
                threading.Thread(target=self.dance_animation, args=(song_name,), daemon=True).start()
                # Use the imported play_youtube_video function from music_engine
                play_youtube_video(song_name)
            else:
                self.add_chat_bubble("Cyclops: No song selected.", is_user=False)
            
        def play_genre():
            choice_dialog.destroy()
            genre = simpledialog.askstring("Play Music Genre", "Enter music genre (e.g., techno, pop, rock, classical):")
            if genre:
                self.add_chat_bubble(f"Cyclops: Playing {genre} music...", is_user=False)
                # Send command to display sinewave on LCD
                try:
                    send_data("sine", LOOP_ARD)
                    send_data(f"#Now Playing: {genre} music", LOOP_ARD)
                except Exception as e:
                    print(f"Error sending LCD command: {e}")
                    
                self.dancing = True
                threading.Thread(target=self.dance_animation, args=(genre,), daemon=True).start()
                # Use the imported play_music function from music_engine
                play_music(genre.lower())
            else:
                self.add_chat_bubble("Cyclops: No genre selected. Playing default music.", is_user=False)
                # Send command to display sinewave on LCD
                try:
                    send_data("sine", LOOP_ARD)
                    send_data("#Now Playing: Pop music", LOOP_ARD)
                except Exception as e:
                    print(f"Error sending LCD command: {e}")
                    
                self.dancing = True
                threading.Thread(target=self.dance_animation, args=("pop",), daemon=True).start()
                # Use the imported play_music function with default genre
                play_music("pop")
        
        # Create buttons for each option
        song_button = ctk.CTkButton(
            choice_dialog,
            text="Play Specific Song",
            command=play_specific_song,
            font=("Arial", 14),
            fg_color="#3498DB",
            hover_color="#2980B9"
        )
        song_button.pack(pady=10, padx=20, fill=ctk.X)
        
        genre_button = ctk.CTkButton(
            choice_dialog,
            text="Play Music Genre",
            command=play_genre,
            font=("Arial", 14),
            fg_color="#9B59B6",
            hover_color="#8E44AD"
        )
        genre_button.pack(pady=10, padx=20, fill=ctk.X)

    def stop_music(self):
        """Stop music playback and close any open browser windows"""
        self.dancing = False
        try:
            # Stop any playing music through mixer
            mixer.music.stop()
            
            # Close any browser windows that might be open for music playback
            try:
                import psutil
                import os
                import signal
                import time
                
                # Get current time
                current_time = time.time()
                
                # Look for recently started browser processes (within last 60 seconds)
                # This helps target only browsers likely opened by our app
                browser_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                    try:
                        # Check if it's a browser and was recently started
                        if (any(browser in proc.info['name'].lower() for browser in 
                            ['chrome', 'firefox', 'msedge', 'brave', 'opera']) and
                            (current_time - proc.info['create_time']) < 120):  # Less than 60 seconds old
                            # Store the process info
                            browser_processes.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                        # Skip processes we can't access
                        continue
                
                # If recent browser processes were found
                if browser_processes:
                    # Ask for confirmation before closing browsers
                    confirm_frame = ctk.CTkFrame(self.chat_area)
                    confirm_frame.pack(fill=ctk.X, padx=5, pady=5, anchor="w")
                    
                    confirm_label = ctk.CTkLabel(
                        confirm_frame,
                        text=f"Close {len(browser_processes)} browser windows playing music?",
                        font=("Arial", 14),
                        text_color="#ECF0F1"
                    )
                    confirm_label.pack(padx=10, pady=5)
                    
                    button_frame = ctk.CTkFrame(confirm_frame, fg_color="transparent")
                    button_frame.pack(pady=5)
                    
                    def close_browsers():
                        closed_count = 0
                        for proc in browser_processes:
                            try:
                                # Try to terminate the process
                                if os.name == 'nt':  # Windows
                                    import subprocess
                                    subprocess.run(['taskkill', '/F', '/PID', str(proc.info['pid'])], 
                                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                else:  # Unix/Linux/Mac
                                    os.kill(proc.info['pid'], signal.SIGTERM)
                                
                                print(f"Closed browser process: {proc.info['name']} (PID: {proc.info['pid']})")
                                closed_count += 1
                            except Exception as e:
                                print(f"Error closing browser: {e}")
                        
                        confirm_frame.destroy()
                        if closed_count > 0:
                            self.add_chat_bubble(f"Cyclops: Closed {closed_count} browser windows.", is_user=False)
                    
                    def cancel_close():
                        confirm_frame.destroy()
                    
                    yes_button = ctk.CTkButton(
                        button_frame,
                        text="Yes",
                        command=close_browsers,
                        font=("Arial", 14),
                        fg_color="#27AE60",
                        hover_color="#229954",
                        width=100
                    )
                    yes_button.grid(row=0, column=0, padx=10, pady=5)
                    
                    no_button = ctk.CTkButton(
                        button_frame,
                        text="No",
                        command=cancel_close,
                        font=("Arial", 14),
                        fg_color="#E74C3C",
                        hover_color="#C0392B",
                        width=100
                    )
                    no_button.grid(row=0, column=1, padx=10, pady=5)
                else:
                    # No recent browser processes found
                    print("No recent browser processes found to close")
            except ImportError:
                self.add_chat_bubble("Cyclops: Could not close browser windows. psutil module not found.", is_user=False)
                print("psutil module not found. Cannot close browser windows.")
            except Exception as e:
                print(f"Error in browser management: {e}")
            
            # Reset Arduino state
            send_data("idle", LOOP_ARD)
            
            # Notify user
            self.add_chat_bubble("Cyclops: Music stopped.", is_user=False)
            speak("Music stopped")
        except Exception as e:
            print(f"Error stopping music: {e}")
            self.add_chat_bubble(f"Cyclops: Error stopping music: {str(e)}", is_user=False)

    def set_timer(self):
        timer_duration = simpledialog.askinteger("Set Timer", "Enter timer duration (in minutes):", minvalue=1, maxvalue=60)
        if timer_duration:
            try:
                send_data("clock", LOOP_ARD)
            except Exception as e:
                print(f"Error sending data to Arduino: {e}")
            self.add_chat_bubble(f"Cyclops: Timer set for {timer_duration} minutes.", is_user=False)
            threading.Thread(target=self.run_timer, args=(timer_duration, "User-defined timer"), daemon=True).start()
        else:
            self.add_chat_bubble("Cyclops: Timer not set.", is_user=False)

 
    def run_timer(self, duration_minutes, message):
        try:
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60)
            total_seconds = duration_minutes * 60
            
            # Calculate update interval (1/3 of total time)
            update_interval = total_seconds // 3
            
            # Ensure we have at least one update even for very short timers
            if update_interval < 1:
                update_interval = 1
                
            speak(f"{duration_minutes} minutes timer set")
            
            # Track when we last updated the display
            last_update_time = start_time
            last_update_seconds = total_seconds
            
            while time.time() < end_time:
                current_time = time.time()
                remaining = end_time - current_time
                elapsed_since_update = current_time - last_update_time
                
                # Update display at calculated intervals or when less than 10 seconds remain
                if (last_update_seconds - int(remaining) >= update_interval) or remaining <= 10:
                    mins, secs = divmod(int(remaining), 60)
                    self.root.after(0, lambda rm=mins, rs=secs: self.update_countdown_display(rm, rs))
                    last_update_time = current_time
                    last_update_seconds = int(remaining)
                    
                time.sleep(1)
                
            self.root.after(0, self.timer_completed)
        except Exception as e:
            print(f"Error in timer thread: {e}")
            self.root.after(0, lambda: self.add_chat_bubble(f"Cyclops: Timer error occurred: {str(e)}", is_user=False))

    def update_countdown_display(self, mins, secs):
        countdown_str = f"Time remaining: {mins:02d}:{secs:02d}"
        self.add_chat_bubble(f"Cyclops: {countdown_str}", is_user=False)

    def timer_completed(self):
        try:
            self.add_chat_bubble("Cyclops: Timer ended! Playing notification...", is_user=False)
            mixer.music.load('music_and_tones/tropical-summer-music-112842.mp3')
            mixer.music.set_volume(1)
            mixer.music.play(-1)
            stop_frame = ctk.CTkFrame(self.chat_area)
            stop_frame.pack(pady=10)
            stop_button = ctk.CTkButton(stop_frame, text="Stop Timer", command=self.stop_timer_sound, font=("Arial", 14), fg_color="#E74C3C", hover_color="#C0392B")
            stop_button.pack(padx=10, pady=10)
            threading.Thread(target=self.listen_for_stop, daemon=True).start()
        except Exception as e:
            print(f"Error completing timer: {e}")
            self.add_chat_bubble(f"Cyclops: Error in timer completion: {str(e)}", is_user=False)

    def listen_for_stop(self):
        try:
            for attempt in range(20):
                audio_input = get_audio(1)
                if audio_input and "stop" in audio_input.lower():
                    self.root.after(0, self.stop_timer_sound)
                    break
                time.sleep(1)
            else:
                self.root.after(0, self.stop_timer_sound)
                self.root.after(0, lambda: self.add_chat_bubble("Cyclops: Timer stopped automatically.", is_user=False))
        except Exception as e:
            print(f"Error in voice listener: {e}")
            self.root.after(0, self.stop_timer_sound)

    def dance_animation(self, genre):
        """Thread function to make Cyclops dance while music is playing"""
        try:
            dance_moves = ["rotate1", "rotate2", "sine", "@90", "@120", "@150"]
            lcd_wave_patterns = ["sine", "sine", "sine"]
            lcd_update_counter = 0
            
            while self.dancing:
                # Send physical movement command
                move = random.choice(dance_moves)
                try:
                    send_data(move, LOOP_ARD)
                except Exception as e:
                    print(f"Error sending dance move: {e}")
                
                # Periodically update the LCD wave pattern for visual effect
                lcd_update_counter += 1
                if lcd_update_counter >= 3:  # Update LCD every 3 dance moves
                    try:
                        # Send a different wave pattern to create animation effect
                        wave_pattern = random.choice(lcd_wave_patterns)
                        send_data(wave_pattern, LOOP_ARD)
                    except Exception as e:
                        print(f"Error sending LCD wave pattern: {e}")
                    lcd_update_counter = 0
                    
                time.sleep(random.uniform(1.5, 3.0))
        except Exception as e:
            print(f"Error in dance animation: {e}")
            self.dancing = False
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass

    def stop_timer_sound(self):
        try:
            mixer.music.stop()
            self.add_chat_bubble("Cyclops: Timer stopped.", is_user=False)
            speak("Timer stopped")
        except Exception as e:
            print(f"Error stopping timer sound: {e}")
    def handle_sad_emotion(self):
        """Handle sad emotion detection with LLM-based cheering up"""
        try:
            # Send sad state to Arduino
            send_data("sad", LOOP_ARD)
            
            # Inform user that Cyclops detected sadness
            self.add_chat_bubble("Cyclops: You look sad. Let me think of how to cheer you up...", is_user=False)
            
            # Create a progress indicator in the chat area
            progress_frame = ctk.CTkFrame(self.chat_area)
            progress_frame.pack(fill=ctk.X, padx=5, pady=5, anchor="w")
            
            progress_label = ctk.CTkLabel(
                progress_frame,
                text="Thinking of ways to cheer you up...",
                font=("Arial", 14),
                text_color="#ECF0F1"
            )
            progress_label.pack(padx=10, pady=10)
            
            # Run the LLM query in a separate thread to avoid blocking UI
            threading.Thread(target=self.get_cheer_up_response, args=(progress_frame,), daemon=True).start()
            
        except Exception as e:
            print(f"Error in handle_sad_emotion: {e}")
            self.add_chat_bubble(f"Cyclops: Error handling sad emotion: {str(e)}", is_user=False)
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass

    def get_cheer_up_response(self, progress_frame=None):
        """Get a response from LLM to cheer up the user"""
        try:
            # Get response from LLM
            response, function, self.message = LLM_answer("I am feeling sad cyclopes cheer me up","yes" ,
                                                        self.message, 
                                                        self.llama_model)
            
            # Remove progress indicator if it exists
            if progress_frame:
                self.root.after(0, progress_frame.destroy)
            
            # Display the response in the chat
            self.root.after(0, lambda: self.add_chat_bubble(f"Cyclops: {response}", is_user=False))
            
            # Execute any function returned by LLM
            if function:
                try:
                    llm_interpreter(function, response)
                except Exception as e:
                    print(f"Error executing LLM function: {e}")
            
            # Reset Arduino state
            try:
                send_data("idle", LOOP_ARD)
            except Exception as e:
                print(f"Error setting idle state: {e}")
                
        except Exception as e:
            print(f"Error in get_cheer_up_response: {e}")
            self.root.after(0, lambda: self.add_chat_bubble(
                f"Cyclops: I'm sorry, I couldn't think of a way to cheer you up right now. Error: {str(e)}", 
                is_user=False))
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass

    def add_note(self):
        note_title = simpledialog.askstring("Add Note", "Enter the title of your note:")
        if not note_title:
            self.add_chat_bubble("Cyclops: Note not added. Title missing.", is_user=False)
            return
        try:
            send_data("note", LOOP_ARD)
        except:
            pass
        note_dialog = ctk.CTkToplevel(self.root)
        note_dialog.title(f"Add Note: {note_title}")
        note_dialog.geometry("600x400")
        note_dialog.transient(self.root)
        note_dialog.grab_set()
        instructions = ctk.CTkLabel(note_dialog, text="Enter your note content below. Click Save when finished.", font=("Arial", 14))
        instructions.pack(pady=(20, 10))
        note_content = ctk.CTkTextbox(note_dialog, width=550, height=250, font=("Arial", 14), wrap=ctk.WORD)
        note_content.pack(padx=20, pady=10)

        def save_note():
            content = note_content.get("1.0", ctk.END).strip()
            if not content:
                messagebox.showwarning("Empty Note", "Note content cannot be empty.")
                return
            if not os.path.exists("notes"):
                os.makedirs("notes")
            note_date = datetime.datetime.now()
            file_path = f"notes/{note_title}_{note_date.day}.txt"
            with open(file_path, "w") as f:
                f.write(f"{note_title} : {note_date}\n{content}")
            with open("working_deets.txt", "w") as f:
                f.writelines(['Previous_Note_path: \n', file_path])
            note_dialog.destroy()
            self.add_chat_bubble(f"Cyclops: Note '{note_title}' has been saved successfully.", is_user=False)
            speak(f"Note {note_title} has been saved successfully.")

        def cancel_note():
            note_dialog.destroy()
            self.add_chat_bubble("Cyclops: Note creation cancelled.", is_user=False)
            speak("Note creation cancelled.")

        button_frame = ctk.CTkFrame(note_dialog)
        button_frame.pack(pady=20)
        save_button = ctk.CTkButton(button_frame, text="Save Note", command=save_note, font=("Arial", 14), fg_color="#27AE60", hover_color="#229954")
        save_button.grid(row=0, column=0, padx=10)
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=cancel_note, font=("Arial", 14), fg_color="#E74C3C", hover_color="#C0392B")
        cancel_button.grid(row=0, column=1, padx=10)
        self.root.wait_window(note_dialog)

    def schedule_manager(self):
        try:
            send_data("#Scheduler", LOOP_ARD)
        except:
            pass
        schedule_dialog = ctk.CTkToplevel(self.root)
        schedule_dialog.title("Schedule Manager")
        schedule_dialog.geometry("800x600")
        schedule_dialog.transient(self.root)
        schedule_dialog.grab_set()
        tab_view = ctk.CTkTabview(schedule_dialog)
        tab_view.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        tab_view.add("Today's Schedule")
        tab_view.add("Add Schedule")
        tab_view.add("View All Schedules")
        create_file()
        today_frame = tab_view.tab("Today's Schedule")
        today_schedule = check_schedule()
        today_label = ctk.CTkLabel(today_frame, text="Today's Schedule", font=("Arial", 18, "bold"))
        today_label.pack(pady=(20, 10))
        schedule_text = ctk.CTkTextbox(today_frame, width=700, height=400, font=("Arial", 14), wrap=ctk.WORD)
        schedule_text.pack(padx=20, pady=10)
        schedule_text.insert("1.0", today_schedule)
        schedule_text.configure(state="disabled")
        add_frame = tab_view.tab("Add Schedule")
        add_label = ctk.CTkLabel(add_frame, text="Add New Schedule", font=("Arial", 18, "bold"))
        add_label.pack(pady=(20, 10))
        form_frame = ctk.CTkFrame(add_frame)
        form_frame.pack(pady=20, padx=20, fill=ctk.X)
        date_frame = ctk.CTkFrame(form_frame)
        date_frame.pack(fill=ctk.X, pady=10)
        date_label = ctk.CTkLabel(date_frame, text="Date:", font=("Arial", 14))
        date_label.grid(row=0, column=0, padx=10, pady=10)
        day_var = ctk.StringVar(value=str(datetime.date.today().day))
        month_var = ctk.StringVar(value=str(datetime.date.today().month))
        year_var = ctk.StringVar(value=str(datetime.date.today().year))
        day_entry = ctk.CTkEntry(date_frame, width=50, textvariable=day_var, font=("Arial", 14))
        day_entry.grid(row=0, column=1, padx=5, pady=10)
        day_label = ctk.CTkLabel(date_frame, text="Day", font=("Arial", 12))
        day_label.grid(row=1, column=1, padx=5)
        month_entry = ctk.CTkEntry(date_frame, width=50, textvariable=month_var, font=("Arial", 14))
        month_entry.grid(row=0, column=2, padx=5, pady=10)
        month_label = ctk.CTkLabel(date_frame, text="Month", font=("Arial", 12))
        month_label.grid(row=1, column=2, padx=5)
        year_entry = ctk.CTkEntry(date_frame, width=80, textvariable=year_var, font=("Arial", 14))
        year_entry.grid(row=0, column=3, padx=5, pady=10)
        year_label = ctk.CTkLabel(date_frame, text="Year", font=("Arial", 12))
        year_label.grid(row=1, column=3, padx=5)
        note_label = ctk.CTkLabel(form_frame, text="Schedule Note:", font=("Arial", 14))
        note_label.pack(anchor="w", padx=10, pady=(20, 5))
        note_entry = ctk.CTkTextbox(form_frame, width=700, height=200, font=("Arial", 14), wrap=ctk.WORD)
        note_entry.pack(padx=10, pady=5)

        def save_schedule():
            try:
                day = int(day_var.get())
                month = int(month_var.get())
                year = int(year_var.get())
                note = note_entry.get("1.0", ctk.END).strip()
                if not note:
                    messagebox.showwarning("Empty Note", "Schedule note cannot be empty.")
                    return
                datetime.date(year, month, day)
                add_schedule(day, month, year, note)
                speak_text = f"Schedule added successfully for {day} {month} {year}."
                threading.Thread(target=speak, args=(speak_text,), daemon=True).start()
                messagebox.showinfo("Success", "Schedule added successfully!")
                note_entry.delete("1.0", ctk.END)
                today = datetime.date.today()
                if day == today.day and month == today.month and year == today.year:
                    schedule_text.configure(state="normal")
                    schedule_text.delete("1.0", ctk.END)
                    schedule_text.insert("1.0", check_schedule())
                    schedule_text.configure(state="disabled")
                refresh_all_schedules()
            except ValueError as e:
                messagebox.showerror("Invalid Input", f"Please check your date input: {e}")
                speak("Invalid date input. Please check your date.")

        add_button = ctk.CTkButton(form_frame, text="Add Schedule", command=save_schedule, font=("Arial", 14), fg_color="#27AE60", hover_color="#229954")
        add_button.pack(pady=20)
        all_frame = tab_view.tab("View All Schedules")
        all_label = ctk.CTkLabel(all_frame, text="All Scheduled Events", font=("Arial", 18, "bold"))
        all_label.pack(pady=(20, 10))
        list_frame = ctk.CTkScrollableFrame(all_frame, width=700, height=400)
        list_frame.pack(padx=20, pady=10, fill=ctk.BOTH, expand=True)

        def refresh_all_schedules():
            for widget in list_frame.winfo_children():
                widget.destroy()
            with open('scheduler.csv', 'r') as csvfile:
                csv_reader = list(csv.reader(csvfile))
            if len(csv_reader) <= 2:
                no_schedules = ctk.CTkLabel(list_frame, text="No schedules found.", font=("Arial", 14))
                no_schedules.pack(pady=20)
                return
            header_frame = ctk.CTkFrame(list_frame)
            header_frame.pack(fill=ctk.X, padx=5, pady=5)
            headers = ["Date", "Note", "Actions"]
            widths = [150, 400, 100]
            for i, header in enumerate(headers):
                header_label = ctk.CTkLabel(header_frame, text=header, font=("Arial", 14, "bold"), width=widths[i])
                header_label.grid(row=0, column=i, padx=5, pady=5)
            for i, row in enumerate(csv_reader[2:], 1):
                try:
                    day = int(row[1])
                    month = int(row[2])
                    year = int(row[3])
                    note = row[4]
                    schedule_frame = ctk.CTkFrame(list_frame)
                    schedule_frame.pack(fill=ctk.X, padx=5, pady=2)
                    date_str = f"{day:02d}/{month:02d}/{year}"
                    date_label = ctk.CTkLabel(schedule_frame, text=date_str, font=("Arial", 14), width=widths[0])
                    date_label.grid(row=0, column=0, padx=5, pady=5)
                    note_label = ctk.CTkLabel(schedule_frame, text=note, font=("Arial", 14), width=widths[1], anchor="w")
                    note_label.grid(row=0, column=1, padx=5, pady=5)
                    def create_delete_function(row_id):
                        return lambda: delete_schedule(row_id)
                    delete_button = ctk.CTkButton(schedule_frame, text="Delete", command=create_delete_function(row[0]), font=("Arial", 12), fg_color="#E74C3C", hover_color="#C0392B", width=widths[2])
                    delete_button.grid(row=0, column=2, padx=5, pady=5)
                except (ValueError, IndexError):
                    continue

        def delete_schedule(row_id):
            try:
                with open('scheduler.csv', 'r') as csvfile:
                    csv_reader = list(csv.reader(csvfile))
                updated_rows = [row for row in csv_reader if row[0] != row_id]
                with open('scheduler.csv', 'w', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerows(updated_rows)
                refresh_all_schedules()
                schedule_text.configure(state="normal")
                schedule_text.delete("1.0", ctk.END)
                schedule_text.insert("1.0", check_schedule())
                schedule_text.configure(state="disabled")
                speak("Schedule deleted successfully.")
                messagebox.showinfo("Success", "Schedule deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete schedule: {e}")
                speak("Failed to delete schedule.")

        refresh_button = ctk.CTkButton(all_frame, text="Refresh Schedules", command=refresh_all_schedules, font=("Arial", 14), fg_color="#3498DB", hover_color="#2980B9")
        refresh_button.pack(pady=10)
        refresh_all_schedules()

    def check_schedule(self):
        try:
            send_data("#Scheduler", LOOP_ARD)
        except:
            pass
        schedule = check_schedule()
        if schedule and schedule != "No noted schedule today.":
            self.add_chat_bubble(f"Cyclops: Your schedule for today:\n{schedule}", is_user=False)
        else:
            self.add_chat_bubble("Cyclops: No schedule found for today.", is_user=False)

    def check_temperature(self):
        """Check and display the current temperature"""
        try:
            # Display a message to indicate temperature checking is in progress
            self.add_chat_bubble("Cyclops: Checking temperature...", is_user=False)
            
            # Send the existing "temph" command to Arduino
            send_data("temph", LOOP_ARD)
            
            # Start a thread to simulate getting temperature data
            # This allows the UI to remain responsive while "waiting" for temperature data
            threading.Thread(target=self.display_temperature_info, daemon=True).start()
        except Exception as e:
            self.add_chat_bubble(f"Cyclops: Error checking temperature: {str(e)}", is_user=False)
            print(f"Error in check_temperature: {e}")

    def display_temperature_info(self):
        """Display temperature information after a short delay"""
        try:
            # Wait a moment to simulate processing time
            time.sleep(2)
            
            # Get current date and time
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Create a formatted temperature message
            # This assumes the Arduino is handling the actual temperature reading
            temp_message = (
                f"🌡️ Temperature Check at {current_time} on {current_date}\n"
                f"Check the screen on my body\n"
            )
            
            # Display the temperature message
            self.add_chat_bubble(f"Cyclops: {temp_message}", is_user=False)
                
        except Exception as e:
            print(f"Error displaying temperature info: {e}")
            self.add_chat_bubble(f"Cyclops: Error displaying temperature information: {str(e)}", is_user=False)
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass
    def play_game(self):
        """Open a dialog to select and play a game"""
        try:
            self.add_chat_bubble("Cyclops: Let's play a game! What would you like to play?", is_user=False)
            send_data("game", LOOP_ARD)
            
            # Create a game selection dialog
            game_dialog = ctk.CTkToplevel(self.root)
            game_dialog.title("Select a Game")
            game_dialog.geometry("400x300")
            game_dialog.transient(self.root)
            game_dialog.grab_set()
            
            # Add a title label
            title_label = ctk.CTkLabel(
                game_dialog,
                text="Choose a Game to Play",
                font=("Arial", 18, "bold"),
                text_color="#2E86C1"
            )
            title_label.pack(pady=(20, 30))
            
            # Create buttons for each game
            games = [
                ("Hangman", self.play_hangman, "#3498DB", "#2980B9"),
                ("Rock Paper Scissors", self.play_rps, "#9B59B6", "#8E44AD"),
            ]
            
            for text, command, fg_color, hover_color in games:
                # Create a closure to handle the button command
                def create_command(cmd, dialog):
                    return lambda: [dialog.destroy(), cmd()]
                
                button = ctk.CTkButton(
                    game_dialog,
                    text=text,
                    command=create_command(command, game_dialog),
                    font=("Arial", 16),
                    fg_color=fg_color,
                    hover_color=hover_color,
                    height=40
                )
                button.pack(pady=10, padx=20, fill=ctk.X)
            
            # Add a cancel button
            cancel_button = ctk.CTkButton(
                game_dialog,
                text="Cancel",
                command=game_dialog.destroy,
                font=("Arial", 14),
                fg_color="#E74C3C",
                hover_color="#C0392B"
            )
            cancel_button.pack(pady=(20, 10))
            
        except Exception as e:
            self.add_chat_bubble(f"Cyclops: Error launching game menu: {str(e)}", is_user=False)
            print(f"Error in play_game: {e}")

    def play_hangman(self):
        """Launch the Hangman game"""
        try:
            self.add_chat_bubble("Cyclops: Starting Hangman game...", is_user=False)
            # Run the game in a separate thread to avoid blocking the UI
            threading.Thread(target=self.run_hangman_game, daemon=True).start()
        except Exception as e:
            self.add_chat_bubble(f"Cyclops: Error starting Hangman: {str(e)}", is_user=False)
            print(f"Error in play_hangman: {e}")

    def run_hangman_game(self):
        """Run the Hangman game in a separate thread"""
        try:
           
            hangman_game = HangmanGame()
            hangman_game.start_hangman()
            # Clean up after game ends
            try:
                import pygame
                pygame.quit()
            except:
                pass
            self.root.after(0, lambda: self.add_chat_bubble("Cyclops: Hangman game ended. Hope you had fun!", is_user=False))
        except Exception as e:
            print(f"Error running Hangman game: {e}")
            self.root.after(0, lambda: self.add_chat_bubble(f"Cyclops: Error in Hangman game: {str(e)}", is_user=False))

    def play_rps(self):
        """Launch the Rock Paper Scissors game"""
        try:
            self.add_chat_bubble("Cyclops: Starting Rock Paper Scissors game...", is_user=False)
            # Run the game in a separate thread to avoid blocking the UI
            threading.Thread(target=self.run_rps_game, daemon=True).start()
        except Exception as e:
            self.add_chat_bubble(f"Cyclops: Error starting Rock Paper Scissors: {str(e)}", is_user=False)
            print(f"Error in play_rps: {e}")

    def run_rps_game(self):
        """Run the Rock Paper Scissors game in a separate thread with UI integration"""
        try:
            # Send the game command to Arduino
            send_data("game", LOOP_ARD)
            
            # Create a UI-friendly version of the game
            self.start_rps_game_ui(3)  # 5 rounds
            
            self.root.after(0, lambda: self.add_chat_bubble("Cyclops: Rock Paper Scissors game ended. Hope you had fun!", is_user=False))
        except Exception as e:
            print(f"Error running Rock Paper Scissors game: {e}")
            self.root.after(0, lambda: self.add_chat_bubble(f"Cyclops: Error in Rock Paper Scissors game: {str(e)}", is_user=False))

    def start_rps_game_ui(self, no_of_plays):
        """UI-friendly version of the Rock Paper Scissors game"""
        from silence_tensorflow import silence_tensorflow
        silence_tensorflow()
        import random
        import time
        from ultralytics import YOLO
        import cv2
        
        # Initialize the game
        self.root.after(0, lambda: self.add_chat_bubble("Cyclops: Initializing Game Engine...", is_user=False))
        labels = ["Rock", "Paper", "Scissors"]
        model = YOLO("Models/best.pt", verbose=False)
        
        self.root.after(0, lambda: self.add_chat_bubble("Cyclops: Starting Rock Paper Scissors Game!", is_user=False))
        player_score = 0
        computer_score = 0
        threshold = 0.55
        
        # Loop through the specified number of plays
        for i in range(0, no_of_plays):
            # Update UI with current turn
            turn_msg = f"Turn {i+1}. Show your Rock, Paper, or Scissors gesture to the camera."
            self.root.after(0, lambda m=turn_msg: self.add_chat_bubble(f"Cyclops: {m}", is_user=False))
            time.sleep(1)  # Small delay to ensure message is seen
            
            cap = cv2.VideoCapture(0)
            computer_choice = labels[random.randint(0, 2)]
            ret, frame = cap.read()
            player_choice_list = []
            
            # Create a UI window to show the camera feed
            cv2.namedWindow("Rock Paper Scissors", cv2.WINDOW_NORMAL)
            
            # Capture multiple frames for robust object detection
            for _ in range(0, 15):
                ret, frame = cap.read()
                if not ret:
                    continue
                    
                frame = cv2.flip(frame, 1)
                results = model(frame, verbose=False)[0]
                
                # Iterate over detected objects and choose the label with the highest count
                for result in results.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = result
                    if score > threshold:
                        player_choice_list.append(labels[int(class_id)])
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
                        cv2.putText(frame, labels[int(class_id)], (int(x1), int(y1 - 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0), 3, cv2.LINE_AA)
                        break
                
                # Display the frame
                cv2.imshow("Rock Paper Scissors", frame)
                cv2.waitKey(1)
            
            # Determine the player's choice based on the label count
            rock_no = player_choice_list.count("Rock")
            paper_no = player_choice_list.count("Paper")
            scissors_no = player_choice_list.count("Scissors")
            
            if not player_choice_list:
                player_choice = "None"
            elif rock_no >= paper_no and rock_no >= scissors_no:
                player_choice = "Rock"
            elif paper_no >= rock_no and paper_no >= scissors_no:
                player_choice = "Paper"
            else:
                player_choice = "Scissors"
            
            # Display choices in UI
            self.root.after(0, lambda: self.add_chat_bubble(f"Cyclops: I chose {computer_choice}", is_user=False))
            self.root.after(0, lambda: self.add_chat_bubble(f"Cyclops: You chose {player_choice}", is_user=False))
            
            time.sleep(1)  # Small delay between messages
            
            # Determine winner and update scores
            result_msg = ""
            if player_choice == "None":
                result_msg = "Did you even make a move?"
            elif player_choice == computer_choice:
                result_msg = "It's a draw!"
            else:
                # Determine winner
                player_wins = (
                    (player_choice == "Rock" and computer_choice == "Scissors") or
                    (player_choice == "Paper" and computer_choice == "Rock") or
                    (player_choice == "Scissors" and computer_choice == "Paper")
                )
                
                if player_wins:
                    player_score += 1
                    result_msg = "You win this round!"
                else:
                    computer_score += 1
                    result_msg = "I win this round!"
            
            # Display round result
            self.root.after(0, lambda: self.add_chat_bubble(f"Cyclops: {result_msg}", is_user=False))
            time.sleep(1)  # Small delay between rounds
            
            # Display current score after each round
            self.root.after(0, lambda: self.add_chat_bubble(
                f"Cyclops: Current score - You: {player_score}, Me: {computer_score}", is_user=False))
            time.sleep(1)
            
            # Release video capture and close windows
            cap.release()
            cv2.destroyAllWindows()
        
        # Announce the final results
        if player_score > computer_score:
            final_msg = "Congratulations, you won the game!"
        elif computer_score > player_score:
            final_msg = "Too bad, better luck next time."
        else:
            final_msg = "That is a draw. We both make good rivals."
        
        self.root.after(0, lambda: self.add_chat_bubble(
            f"Cyclops: Game over! Final score - You: {player_score}, Me: {computer_score}", is_user=False))
        self.root.after(0, lambda: self.add_chat_bubble(f"Cyclops: {final_msg}", is_user=False))
    
    def news_manager(self):
        """Opens a dialog to select and get different types of news"""
        try:
            send_data("#News", LOOP_ARD)
        except Exception as e:
            print(f"Error sending data to Arduino: {e}")
            
        # Create a news selection dialog
        news_dialog = ctk.CTkToplevel(self.root)
        news_dialog.title("News Manager")
        news_dialog.geometry("400x300")
        news_dialog.transient(self.root)
        news_dialog.grab_set()
        
        # Add a title label
        title_label = ctk.CTkLabel(
            news_dialog,
            text="Choose News Category",
            font=("Arial", 18, "bold"),
            text_color="#2E86C1"
        )
        title_label.pack(pady=(20, 30))
        
        # Create buttons for each news category
        news_options = [
            ("World News", self.get_world_news, "#3498DB", "#2980B9"),
            ("Science News", self.get_science_news, "#9B59B6", "#8E44AD"),
            # Add more news categories here if needed
        ]
        
        for text, command, fg_color, hover_color in news_options:
            # Create a closure to handle the button command
            def create_command(cmd, dialog):
                return lambda: [dialog.destroy(), cmd()]
            
            button = ctk.CTkButton(
                news_dialog,
                text=text,
                command=create_command(command, news_dialog),
                font=("Arial", 16),
                fg_color=fg_color,
                hover_color=hover_color,
                height=40
            )
            button.pack(pady=10, padx=20, fill=ctk.X)
        
        # Add a cancel button
        cancel_button = ctk.CTkButton(
            news_dialog,
            text="Cancel",
            command=news_dialog.destroy,
            font=("Arial", 14),
            fg_color="#E74C3C",
            hover_color="#C0392B"
        )
        cancel_button.pack(pady=(20, 10))
        
 
    def get_world_news(self):
        """Fetch and display world news headlines"""
        try:
            self.add_chat_bubble("Cyclops: Fetching world news headlines...", is_user=False)
            send_data("happy", LOOP_ARD)
            
            # Create a progress indicator in the chat area
            news_progress_frame = ctk.CTkFrame(self.chat_area)
            news_progress_frame.pack(fill=ctk.X, padx=5, pady=5, anchor="w")
            
            news_progress_label = ctk.CTkLabel(
                news_progress_frame,
                text="Loading news... Please wait.",
                font=("Arial", 14),
                text_color="#ECF0F1"
            )
            news_progress_label.pack(padx=10, pady=10)
            
            # Run the news fetching in a separate thread to avoid blocking UI
            threading.Thread(target=self.fetch_world_news_thread, args=(news_progress_frame,), daemon=True).start()
        except Exception as e:
            self.add_chat_bubble(f"Cyclops: Error starting world news: {str(e)}", is_user=False)
            print(f"Error in get_world_news: {e}")
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass

    def fetch_world_news_thread(self, progress_frame=None):
        """Thread function to fetch world news without blocking UI"""
        try:
            # Capture both print output and news headlines
            import io
            from contextlib import redirect_stdout
            import requests
            from bs4 import BeautifulSoup
            
            # Remove progress indicator if it exists
            if progress_frame:
                self.root.after(0, progress_frame.destroy)
            
            # Fetch news directly to display in UI
            news_list = []
            try:
                # Make a GET request to the specified URL
                url = 'https://globalnews.ca/world/'
                response = requests.get(url)

                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all news headlines using BeautifulSoup
                headlines = soup.find('body').find_all("span", attrs={'class': 'c-posts__headlineText'})
                
                # Create a formatted news display
                news_display = "🌍 **WORLD NEWS HEADLINES** 🌍\n\n"
                count = 0
                # Iterate through headlines
                for x in headlines[10:min(20, len(headlines))]:
                    txt = x.text.strip()
                    # Check if the headline is already in the list to avoid repetition
                    if txt in news_list:
                        continue
                    news_list.append(txt)
                    news_display += f"• {txt}\n\n"
                    count +=1
                    if count >=3 :
                        break
                
                # Display the news in the chat
                self.root.after(0, lambda: self.add_chat_bubble(
                    f"Cyclops: {news_display}", is_user=False))
                
                # Now run the original function which will speak the news
                f = io.StringIO()
                with redirect_stdout(f):
                    get_news_world()  # This function speaks the news
                
            except requests.RequestException as e:
                # Handle request-related exceptions
                error_msg = f"Error fetching world news: {e}"
                print(error_msg)
                self.root.after(0, lambda: self.add_chat_bubble(
                    f"Cyclops: {error_msg}", is_user=False))
                speak("Error fetching world news. Please check your internet connection.")
            
            # Signal completion and reset Arduino state
            self.root.after(0, lambda: self.add_chat_bubble(
                "Cyclops: World news headlines have been read out.", is_user=False))
            try:
                send_data("idle", LOOP_ARD)
            except Exception as e:
                print(f"Error setting idle state: {e}")
        except Exception as e:
            print(f"Error in fetch_world_news_thread: {e}")
            self.root.after(0, lambda: self.add_chat_bubble(
                f"Cyclops: Error fetching world news: {str(e)}", is_user=False))
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass
    
    def motion_sensor_settings(self):
        """Open motion sensor settings dialog"""
        try:
            settings_dialog = ctk.CTkToplevel(self.root)
            settings_dialog.title("Motion Sensor Settings")
            settings_dialog.geometry("400x300")
            settings_dialog.transient(self.root)
            settings_dialog.grab_set()
            
            # Add a title label
            title_label = ctk.CTkLabel(
                settings_dialog,
                text="PIR Motion Sensor Control",
                font=("Arial", 18, "bold"),
                text_color="#2E86C1"
            )
            title_label.pack(pady=(20, 30))
            
            # Create a frame for the settings
            info_frame = ctk.CTkFrame(settings_dialog)
            info_frame.pack(fill=ctk.X, padx=20, pady=10)
            
            info_label = ctk.CTkLabel(
                info_frame,
                text="The PIR motion sensor detects movement\nand activates Cyclops automatically.",
                font=("Arial", 14),
                justify="center"
            )
            info_label.pack(pady=15)
            
            # Buttons frame
            buttons_frame = ctk.CTkFrame(settings_dialog)
            buttons_frame.pack(fill=ctk.X, padx=20, pady=20)
            
            def enable_motion_detection():
                try:
                    send_data("motion_on", LOOP_ARD)
                    self.add_chat_bubble("Cyclops: Motion detection activated. I'll respond when I detect movement.", is_user=False)
                    settings_dialog.destroy()
                except Exception as e:
                    print(f"Error enabling motion detection: {e}")
            
            def disable_motion_detection():
                try:
                    send_data("motion_off", LOOP_ARD)
                    self.add_chat_bubble("Cyclops: Motion detection deactivated.", is_user=False)
                    settings_dialog.destroy()
                except Exception as e:
                    print(f"Error disabling motion detection: {e}")
            
            # Enable button
            enable_button = ctk.CTkButton(
                buttons_frame,
                text="Enable Motion Detection",
                command=enable_motion_detection,
                font=("Arial", 14),
                fg_color="#27AE60",
                hover_color="#229954"
            )
            enable_button.pack(pady=10, fill=ctk.X)
            
            # Disable button
            disable_button = ctk.CTkButton(
                buttons_frame,
                text="Disable Motion Detection",
                command=disable_motion_detection,
                font=("Arial", 14),
                fg_color="#E74C3C",
                hover_color="#C0392B"
            )
            disable_button.pack(pady=10, fill=ctk.X)
            
            # Close button
            close_button = ctk.CTkButton(
                settings_dialog,
                text="Close",
                command=settings_dialog.destroy,
                font=("Arial", 14),
                fg_color="#7F8C8D",
                hover_color="#95A5A6"
            )
            close_button.pack(pady=10)
            
        except Exception as e:
            self.add_chat_bubble(f"Cyclops: Error opening motion sensor settings: {str(e)}", is_user=False)
            print(f"Error in motion_sensor_settings: {e}")
  
    def get_science_news(self):
        """Fetch and display science news headlines"""
        try:
            self.add_chat_bubble("Cyclops: Fetching science news headlines...", is_user=False)
            send_data("happy", LOOP_ARD)
            
            # Create a progress indicator in the chat area
            news_progress_frame = ctk.CTkFrame(self.chat_area)
            news_progress_frame.pack(fill=ctk.X, padx=5, pady=5, anchor="w")
            
            news_progress_label = ctk.CTkLabel(
                news_progress_frame,
                text="Loading science news... Please wait.",
                font=("Arial", 14),
                text_color="#ECF0F1"
            )
            news_progress_label.pack(padx=10, pady=10)
            
            # Run the news fetching in a separate thread to avoid blocking UI
            threading.Thread(target=self.fetch_science_news_thread, args=(news_progress_frame,), daemon=True).start()
        except Exception as e:
            self.add_chat_bubble(f"Cyclops: Error starting science news: {str(e)}", is_user=False)
            print(f"Error in get_science_news: {e}")
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass

    def fetch_science_news_thread(self, progress_frame=None):
        """Thread function to fetch science news without blocking UI"""
        try:
            # Capture both print output and news headlines
            import io
            from contextlib import redirect_stdout
            import requests
            from bs4 import BeautifulSoup
            
            # Remove progress indicator if it exists
            if progress_frame:
                self.root.after(0, progress_frame.destroy)
            
            # Fetch news directly to display in UI
            try:
                # Make a GET request to the specified URL
                url = 'https://www.sciencenews.org/topic/space'
                response = requests.get(url)

                # Parse the HTML content
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find science news headlines using BeautifulSoup
                headlines = soup.find('body').find_all("p", attrs={'class': 'post-item-river__excerpt___SWLb7'})
                
                # Create a formatted news display
                news_display = "🔬 **SCIENCE NEWS HEADLINES** 🔬\n\n"
                
                # Iterate through headlines and display the first few
                for x in headlines[0:min(3, len(headlines))]:
                    txt = x.text.strip()
                    news_display += f"• {txt}\n\n"
                
                # Display the news in the chat
                self.root.after(0, lambda: self.add_chat_bubble(
                    f"Cyclops: {news_display}", is_user=False))
                
                # Now run the original function which will speak the news
                f = io.StringIO()
                with redirect_stdout(f):
                    get_news_science()  # This function speaks the news
                
            except requests.RequestException as e:
                # Handle request-related exceptions
                error_msg = f"Error fetching science news: {e}"
                print(error_msg)
                self.root.after(0, lambda: self.add_chat_bubble(
                    f"Cyclops: {error_msg}", is_user=False))
                speak("Error fetching science news. Please check your internet connection.")
            
            # Signal completion and reset Arduino state
            self.root.after(0, lambda: self.add_chat_bubble(
                "Cyclops: Science news headlines have been read out.", is_user=False))
            try:
                send_data("idle", LOOP_ARD)
            except Exception as e:
                print(f"Error setting idle state: {e}")
        except Exception as e:
            print(f"Error in fetch_science_news_thread: {e}")
            self.root.after(0, lambda: self.add_chat_bubble(
                f"Cyclops: Error fetching science news: {str(e)}", is_user=False))
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass
            
    def initialize_pir_sensor(self):
        """Initialize the PIR motion sensor without disturbing LCD display"""
        try:
            # Create a separate thread for PIR initialization
            threading.Thread(target=self._pir_init_thread, daemon=True).start()
            self.add_chat_bubble("Cyclops: Motion sensor initializing in background...", is_user=False)
        except Exception as e:
            print(f"Error initializing PIR sensor: {e}")
            self.add_chat_bubble("Cyclops: Failed to initialize motion sensor.", is_user=False)
    def tell_todays_schedule(self):
        """Retrieve and speak today's schedule"""
        try:
            send_data("#Scheduler", LOOP_ARD)
            schedule = check_schedule()
            
            if schedule and schedule != "No noted schedule today.":
                self.add_chat_bubble(f"Cyclops: Your schedule for today:\n{schedule}", is_user=False)
                # The add_chat_bubble method already calls speak() internally
            else:
                self.add_chat_bubble("Cyclops: You don't have any scheduled events for today.", is_user=False)
        except Exception as e:
            print(f"Error retrieving today's schedule: {e}")
            self.add_chat_bubble(f"Cyclops: I encountered an error while checking your schedule: {str(e)}", is_user=False)
            try:
                send_data("idle", LOOP_ARD)
            except:
                pass

    def tell_previous_note(self):
        """Retrieve and speak the content of the previous note"""
        try:
            # Check if working_deets.txt exists and contains the previous note path
            if os.path.exists("working_deets.txt"):
                with open("working_deets.txt", "r") as f:
                    lines = f.readlines()
                    
                # Find the line with the previous note path
                note_path = None
                for line in lines:
                    if line.startswith("Previous_Note_path:"):
                        parts = line.strip().split(":", 1)
                        if len(parts) > 1 and parts[1].strip():
                            note_path = parts[1].strip()
                        break
                
                if note_path and os.path.exists(note_path):
                    # Read the note content
                    with open(note_path, "r") as note_file:
                        note_content = note_file.read()
                    
                    # Extract title from the filename
                    note_title = os.path.basename(note_path).split("_")[0]
                    
                    # Display and speak the note
                    self.add_chat_bubble(f"Cyclops: Here's your previous note titled '{note_title}':\n\n{note_content}", is_user=False)
                else:
                    # If the specific note path doesn't exist, try to find the most recent note in the notes directory
                    notes_dir = "D:\\Cyclops\\Cyclops-main\\Cyclops\\notes"
                    if os.path.exists(notes_dir):
                        note_files = [os.path.join(notes_dir, f) for f in os.listdir(notes_dir) if f.endswith('.txt')]
                        if note_files:
                            # Sort by modification time, newest first
                            note_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                            latest_note = note_files[0]
                            
                            # Read the latest note
                            with open(latest_note, "r") as note_file:
                                note_content = note_file.read()
                            
                            # Extract title from the filename
                            note_title = os.path.basename(latest_note).split("_")[0]
                            
                            # Update the working_deets.txt file with the latest note path
                            with open("working_deets.txt", "w") as f:
                                f.write(f"Previous_Note_path: {latest_note}")
                            
                            # Display and speak the note
                            self.add_chat_bubble(f"Cyclops: Here's your most recent note titled '{note_title}':\n\n{note_content}", is_user=False)
                        else:
                            self.add_chat_bubble("Cyclops: I couldn't find any notes in the notes directory.", is_user=False)
                    else:
                        self.add_chat_bubble("Cyclops: The notes directory doesn't exist. Try creating a note first.", is_user=False)
            else:
                # If working_deets.txt doesn't exist, try to find the most recent note in the notes directory
                notes_dir = "D:\\Cyclops\\Cyclops-main\\Cyclops\\notes"
                if os.path.exists(notes_dir):
                    note_files = [os.path.join(notes_dir, f) for f in os.listdir(notes_dir) if f.endswith('.txt')]
                    if note_files:
                        # Sort by modification time, newest first
                        note_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                        latest_note = note_files[0]
                        
                        # Read the latest note
                        with open(latest_note, "r") as note_file:
                            note_content = note_file.read()
                        
                        # Extract title from the filename
                        note_title = os.path.basename(latest_note).split("_")[0]
                        
                        # Create the working_deets.txt file with the latest note path
                        with open("working_deets.txt", "w") as f:
                            f.write(f"Previous_Note_path: {latest_note}")
                        
                        # Display and speak the note
                        self.add_chat_bubble(f"Cyclops: Here's your most recent note titled '{note_title}':\n\n{note_content}", is_user=False)
                    else:
                        self.add_chat_bubble("Cyclops: I couldn't find any notes in the notes directory.", is_user=False)
                else:
                    self.add_chat_bubble("Cyclops: The notes directory doesn't exist. Try creating a note first.", is_user=False)
        except Exception as e:
            print(f"Error retrieving previous note: {e}")
            self.add_chat_bubble(f"Cyclops: I encountered an error while retrieving your previous note: {str(e)}", is_user=False)
    def _pir_init_thread(self):
        """Thread function to handle PIR sensor initialization"""
        try:
            # Send a special command to Arduino that won't use the LCD
            # This command should be implemented in the Arduino code
            send_data("pir_init_silent", 1)
            
            # Wait for initialization (typically PIR sensors need 30-60 seconds)
            time.sleep(2)  # Reduced for testing, adjust based on actual sensor
            
            # Notify user that initialization is complete
            self.root.after(0, lambda: self.add_chat_bubble(
                "Cyclops: Motion sensor initialized successfully.", is_user=False))
            
            # Set default state (usually off until explicitly enabled)
            send_data("motion_off", 1)
        except Exception as e:
            print(f"Error in PIR initialization thread: {e}")
            self.root.after(0, lambda: self.add_chat_bubble(
                f"Cyclops: Error during motion sensor initialization: {str(e)}", is_user=False))


if __name__ == "__main__":
    root = ctk.CTk()
    app = CyclopsUI(root)
    root.mainloop()