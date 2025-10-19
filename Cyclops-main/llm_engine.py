""" LLM Engine: Script for loading and working with the LLM. Using Mistral7B in this case."""

import datetime
import time
from llama_cpp import Llama
from voice_engine import speak


def llama_message_init(user_details):
    # Initializing LLM Engine
    print("Initializing LLM Engine")
    speak("Initializing LLM Engine")

    try:
        # Create an instance of the Llama model
        LLM = Llama(model_path="D:\Cyclops\Cyclops-main\Cyclops\Models\LLMS\mistral-7b-v0.1.Q3_K_S-002.gguf", n_ctx=3046, verbose=False)
    except Exception as e:
        LLM = None
        print(e)

    current_date = datetime.date.today()

    # Formulate the initial message to guide the assistant
    mess = """
[INST] You are a natural language desktop assistant bot Cyclops. Current year is """ + str(
        current_date) + """ Keep the date in mind while answering. Your duty is to be friendly and supportive. Following are the details of your user.""" + user_details + """. Select a function that is most suitable for the user command(select only one function out of these): 1. show_image(name of object you want to show image of), 2. timer(time in minutes,message to show after timer ends), 3. play_youtube(what topic to search), 4. schedule(day:int,month:int,year:int,message:str), 5. play_game(1.Hangman 2. Jumper 3. Rock-Paper-Scissors), 6. plain_conversation() .End your response with a function. Don't forget to give the function and give it only once.[/INST]
[INST]  What is a black hole cyclops? [/INST]
@Response: A black hole is a region of spacetime where gravity is so strong that nothing, including light and other electromagnetic waves, has enough energy to escape it. #Function:show_image(black hole)*
[INST] What are you doing cyclops? [/INST]
@Response: I am just thinking of all the ways I can help you. #Function:plain_conversation()*
[INST] Cyclops I need to cook eggs can you start a timer? [/INST]
@Response: Don't worry I have set a timer for 2 minutes for some tasty eggs. #Function:timer(2 minutes,Eggs are done)*
[INST] Play some music for this party cyclops? [/INST]
@Response: Don't worry I have you covered. Time to party.#Function:play_youtube(party music)*
[INST] Cyclops remind me to wish my friend on 24th June? [/INST]
@Response: Ok I will add this to the scheduler. #Function:schedule(24, 6, 2023, Friend's birthday wish)*


"""
    return mess, LLM


def llama_response(user_input, message, llm_model):
    # Add user input to the message
    message += "[INST]" + user_input + "[/INST]"

    # Generate a response using the Llama model
    output = llm_model(message, max_tokens=2024, stop=["*", "[INST]"])
    out = output["choices"][0]["text"]

    # Append the generated response to the message
    message += '\n' + out

    return out, message


def format_response(response_to_alter):
    # Extract response and function information from the formatted string
    response_loc = response_to_alter.find('@')
    response_loc_end = response_to_alter.find(':')
    func_loc = response_to_alter.find('#')
    func_loc_end = response_to_alter[func_loc:].find(':')
    response = response_to_alter[response_loc_end + 1:func_loc]
    function = response_to_alter[func_loc:][func_loc_end + 1:]
    return response, function


def LLM_answer(user_prompt, message, llama_model):
    if "daw win aye" in user_prompt.lower():
        response = """
        Dr. Win Aye has a doctorate from Multimedia University, Malaysia, and is the Rector of MIIT. 
        She received her B.C.Tech. (Bachelor of Computer Technology) and M.C.Tech. (Master of Computer Technology) degrees 
        from the University of Computer Studies, Yangon (UCSY) in 1995 and 1999, respectively.

        Dr. Win Aye has five years of teaching experience at the University of Computer Studies, Yangon. 
        She has been an administrator throughout most of her career in academia, first at the University of Computer Studies, Mandalay, 
        and now at MIIT. Her research interests include control engineering, multicast transmission, multicast security, and network security.
        """
        function = ""
        return response, function, message 

    elif "miit" in user_prompt.lower():
        response = """
        Myanmar Institute of Information Technology (MIIT) is a technological university located in Chanmyathazi Township, Mandalay, Myanmar. 
        It was set up as a National Centre of Excellence in 2015 as a result of a Memorandum of Understanding between the Government of the Republic of the Union of Myanmar and the Government of the Republic of India. 
        MIIT currently offers Bachelor of Engineering degrees in Computer Science and Engineering and Electronics and Communications Engineering.
        """
        function = ""
        return response, function, message
    
    elif "u soe paing" in user_prompt.lower():
        response = """
        U Soe Paing is a lecturer at MIIT. He completed his master’s degree in Computer Technology from Computer University (Mandalay), Myanmar. 
        He also holds a postgraduate diploma in English from Mandalay University of Foreign Languages, Myanmar.
        
        Education:
        - Post Graduate Diploma in English, Mandalay University of Foreign Languages, Myanmar (2023)
        - Master of Computer Technology, Computer University (Mandalay), Myanmar (2012)
        - Bachelor of Computer Technology (Hons.), Computer University (Myitkyina), Myanmar (2010)
        - Bachelor of Computer Technology, Computer University (Myitkyina), Myanmar (2009)

        Thesis Title: “LUCIFER BLOCK CIPHER ENCRYPTION WITH COMPRESSION AND ERROR DETECTION”
        """
        function = ""
        return response, function, message

    elif "daw nu wah" in user_prompt.lower():
        response = """
        She is a facilitator/teacher who successfully awarded a Doctor of Philosophy in Information Technology. 
        She is currently teaching at the Faculty of Computer System and Technology, Myanmar Institute of Information Technology, Mandalay.

        Education:
        - Ph.D. (Information Technology), University of Computer Studies, Yangon
        - M.C.Tech. (Computer Technology), University of Computer Studies, Mandalay
        - B.C.Tech.(Hons.) (Computer Technology), University of Computer Studies, Mandalay
        - PG. Diploma in VLSI, CDAC-ACTS (Pune), India
        - Diploma in Technology (Electronic), Mandalay Technological University
        """
        function = ""
        return response, function, message
    
    elif "daw khaing nyunt myaing" in user_prompt.lower():
        response = """
        She graduated from Mandalay University with a specialization in Physics (B.Sc. Hons) and Nuclear Physics (M.Sc.) in 1998. 
        She obtained her Ph.D. in Nuclear Technology from Yangon Technology University in 2003. 
        Her career has been focused on teaching and research in the field of Nuclear Technology. 
        She has given lectures for undergraduate and postgraduate courses, supervised Ph.D. and M.Sc. candidates, and conducted research in the areas of Nuclear Technology Applications, Nuclear Security, Radiation Safety, Environmental Radiation Monitoring, and Nuclear Imaging CT Scanning.

        Education:
        - B.Sc. (Hons) in Physics
        - M.Sc. in Nuclear Physics
        - Ph.D. in Nuclear Technology
        """
        function = ""
        return response, function, message
       
    elif "creator" in user_prompt.lower() or "who made you" in user_prompt.lower():
        response = """
        My creators are the brilliant minds behind my existence.  
        They are:  
        Shwe Min Lu  
        Phone Moe Htet  
        Myo Thura Tun  
        Kyaw Lin  
        Yu Thet Htar Oo  
        May Phoo Khant  
        Yin Myat Noe Oo  
        and Ei Thuzar Nwe.  
        With their dedication and expertise, they have shaped me into what I am today.  
        I am grateful for their creativity and effort!

        """
        function = ""
        return response, function, message
    
    else:
        # Measure the time taken for LLM to generate a response
        start = time.time()
        out, message = llama_response(user_prompt, message, llama_model)
        respon, func = format_response(out)
        end = time.time()
        print("TIME TAKEN", (end - start))
        return respon, func, message
