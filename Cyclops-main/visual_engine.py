
""" Visual Engine: A Script for camera, emotion recognition, and drowsiness detection."""

import datetime
import os
import cv2
import numpy as np
from silence_tensorflow import silence_tensorflow

silence_tensorflow()
import tensorflow as tf
from pygame import mixer
from voice_engine import speak

mixer.init()

print("Initializing Visual Engine")
speak("Initializing Visual Engine")

# Initialize detector as None
detector = None
face_detection_model_path = "Models/face_detection_yunet_2023mar.onnx"

# Create photos directory if it doesn't exist
photos_dir = "D:\Cyclops\Cyclops-main\Cyclops\photos_taken"
if not os.path.exists(photos_dir):
    os.makedirs(photos_dir)
    print(f"Created directory: {photos_dir}")

try:
    # Load emotion and eye blink models
    emotion_model = tf.keras.models.load_model("Models/model_emo (1).h5")
    eye_blink_model = tf.keras.models.load_model("Models/eye_blink_model.h5")
    print("Emotion and eye blink models loaded successfully.")

    # Initialize face detector
    if os.path.exists(face_detection_model_path):
        detector = cv2.FaceDetectorYN.create(
            face_detection_model_path, "", (1024, 720), 0.9, 0.3, 5000)
        print("Face detector loaded successfully.")
    else:
        print(f"Face detection model not found at {face_detection_model_path}")
except Exception as e:
    print(f"Error loading models: {e}")
    if detector is None:
        print("Face detector could not be initialized. Camera functionality will be limited.")
        speak("Face detector could not be initialized. Camera functionality will be limited.")


def visualize(inp, faces, fps, thickness=1):
    """Visualize detected faces on the input image."""
    coords = None
    if faces[1] is not None:
        for idx, face in enumerate(faces[1]):
            coords = face[:-1].astype(np.int32)
            cv2.rectangle(inp, (coords[0], coords[1]), (coords[0] + coords[2], coords[1] + coords[3]), (255, 255, 0),
                          thickness)
    cv2.putText(inp, "Press Q Key to exit. Press A for photo.", (1, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                2)
    return coords


# Function for camera
def show_my_face(get_face=0, click_pic=0):
    """
    Show the user's face using the webcam.
    
    Args:
        get_face (int): If 1, return the face coordinates
        click_pic (int): If 1, take a photo and save it
        
    Returns:
        coords: Face coordinates if get_face=1, otherwise None
    """
    # Check if detector is initialized
    if detector is None:
        print("Face detector is not initialized. Cannot use camera.")
        speak("Face detector is not initialized. Cannot use camera.")
        return None
    
    # Try to access the camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam. Please check your camera connection.")
        speak("Error: Could not open webcam. Please check your camera connection.")
        return None
    
    try:
        while True:
            ret, img = cap.read()
            if not ret or img is None:
                print("Error: Could not read frame from webcam.")
                break
                
            img = cv2.flip(img, 1)
            img = cv2.resize(img, (1024, 720))
            im_sh = img.copy()
            
            faces = detector.detect(img)
            coords = None
            
            if faces[1] is not None:
                coords = visualize(img, faces, 60)

                if get_face == 1:
                    cap.release()
                    cv2.destroyAllWindows()
                    return coords
                    
                # print("You Look Great Today")
                # speak("You Look Great Today")
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('a') or click_pic == 1:
                    print("Clicking Picture")
                    
                    # Create a timestamp-based filename
                    timestamp = datetime.datetime.now()
                    filename = f"face_img_{timestamp.day}_{timestamp.month}_{timestamp.hour}_{timestamp.minute}_{timestamp.second}.png"
                    filepath = os.path.join(os.path.abspath(photos_dir), filename)
                    
                    # Save the image
                    try:
                        cv2.imwrite(filepath, im_sh)
                        print(f"Image saved to {filepath}")
                        
                        # Play camera shutter sound
                        try:
                            mixer.music.load(r'music_and_tones/camera-shutter-6305.mp3')
                            mixer.music.set_volume(0.8)
                            mixer.music.play()
                        except Exception as e:
                            print(f"Error playing camera sound: {e}")
                    except Exception as e:
                        print(f"Error saving image: {e}")

                    if click_pic == 1:
                        break
            
            # Always show the camera view, even if no face is detected
            cv2.imshow("CamView", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except Exception as e:
        print(f"Error in show_my_face: {e}")
    finally:
        # Make sure resources are released
        cap.release()
        cv2.destroyAllWindows()
    
    return coords


# Function for emotion and drowsiness detection
def emotion_identity(no_of_frames=10):
    """
    Detect emotion and eye status.
    
    Args:
        no_of_frames (int): Number of frames to process for detection
        
    Returns:
        list: [emotion, eye_status]
    """
    if detector is None:
        print("Face detector is not initialized. Cannot detect emotions.")
        speak("Face detector is not initialized. Cannot detect emotions.")
        return ["neutral", "open"]

    emotion_list = ['happy', 'sad', 'neutral']
    eye_list = ['closed', 'open']
    emotions = []
    eyes = []
    
    # Try to access the camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam for emotion detection.")
        speak("Error: Could not open webcam for emotion detection.")
        return ["neutral", "open"]
    
    try:
        frames_processed = 0
        while frames_processed < no_of_frames:
            ret, img = cap.read()
            if not ret or img is None:
                print("Error: Could not read frame from webcam during emotion detection.")
                break
                
            img = cv2.flip(img, 1)
            img = cv2.resize(img, (1024, 720))
            
            faces = detector.detect(img)
            
            if faces[1] is not None:
                coords = visualize(img, faces, 60)
                if coords is None:
                    continue
                    
                # Extract face and eye regions
                try:
                    # Get face region
                    face = img[max(0, coords[1]):min(img.shape[0], coords[1] + coords[3]), 
                              max(0, coords[0]):min(img.shape[1], coords[0] + coords[2])]
                    
                    # Get eye region (if eye landmarks are available)
                    if len(coords) > 5:
                        eye = img[max(0, coords[5] - 20):min(img.shape[0], coords[5] + 20), 
                                max(0, coords[4] - 30):min(img.shape[1], coords[4] + 30)]
                    else:
                        # Use upper part of face as fallback for eyes
                        eye_height = coords[3] // 3
                        eye = img[max(0, coords[1]):min(img.shape[0], coords[1] + eye_height), 
                                max(0, coords[0]):min(img.shape[1], coords[0] + coords[2])]
                    
                    # Process face for emotion detection
                    det = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                    det = cv2.resize(det, (48, 48))
                    det = det / 255.0
                    
                    # Process eye for blink detection
                    det_eye = cv2.cvtColor(eye, cv2.COLOR_BGR2GRAY)
                    det_eye = cv2.resize(det_eye, (48, 48))
                    det_eye = det_eye / 255.0
                    
                    # Predict emotion and eye state
                    emotion_pred = emotion_model.predict(det.reshape((-1, 48, 48, 1)), verbose=False)[0]
                    eye_pred = eye_blink_model.predict(det_eye.reshape((-1, 48, 48, 1)), verbose=False)[0]
                    
                    emotions.append(emotion_list[np.argmax(emotion_pred)])
                    eyes.append(eye_list[np.argmax(eye_pred)])
                    
                    frames_processed += 1
                    
                except Exception as e:
                    print(f"Error processing frame for emotion detection: {e}")
                    continue
            
            # Show the camera view with a "press Q to exit" message
            cv2.putText(img, "Detecting emotions... Press Q to exit", (10, 30), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Emotion Detection", img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Error in emotion_identity: {e}")
    finally:
        # Make sure resources are released
        cap.release()
        cv2.destroyAllWindows()
    
    # Process the collected emotions and eye states
    if not emotions:
        print("No faces detected for emotion analysis.")
        return ["neutral", "open"]
        
    happy = emotions.count("happy")
    sad = emotions.count("sad")
    neutral = emotions.count("neutral")
    closed_eye = eyes.count("closed")
    open_eye = eyes.count("open")
    
    # Determine the dominant emotion
    to_send = ["neutral", "open"]
    
    if happy > sad and happy > neutral:
        to_send[0] = "happy"
    elif sad > happy and sad > neutral:
        to_send[0] = "sad"
    else:
        to_send[0] = "neutral"

    # Determine the dominant eye state
    if closed_eye > open_eye:
        to_send[1] = "closed"
    else:
        to_send[1] = "open"

    return to_send
