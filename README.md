# Simple-Mouse-Mover
A robust, low-level mouse automation tool built in Python, designed to simulate human activity in environments such as DirectX-based games and other applications.

HOW TO USE:
Simple Mouse Mover v1.0.8


📦 Installation & Usage

    Download the Simple Mouse Mover.py file
    Place it in any folder you want
    Double-click to run!
    The program will check if you have the neccessary dependancies installed.
    If not, the program will promot you to install them.
    Once installed, the program will open with a simple GUI.
    A config file will be created "m_cfg.txt".
    You can save your configs directly from the app or from the txt file itself.
    Additional: For the best compatibility, run the script as an administrator and set your game to 'Windowed Fullscreen'. This MIGHT NOT be necessary.

WARNING: 

    THIS FILE DOES NOT GUARANTEE THAT IT IS UNDETECATBLE, IT IS NOT MARKETED AS SUCH.
    If used in a game it CAN BE DETECTED by an anti-cheat and result in a BAN.
    Please use at your own risk. Read License for more information.

Key Features:

    DirectInput Integration: Uses pydirectinput to bypass limitations of standard desktop automation, allowing movement to be recognized inside games like Fortnite and other full-screen applications.
    Intelligent Idle Detection: Monitors hardware mouse movement via pynput. The automation only triggers after a randomized period of user inactivity to avoid interrupting active work.
    Persistence Layer: Automatically saves and loads user configurations (movement limits, idle timings, and durations) to a local m_cfg.txt file using JSON serialization.
    Zero-Config Startup: Features an integrated dependency manager that detects missing libraries, prompts the user for installation, and restarts the application automatically.
    Randomized Movement: Randomizes movement vectors, wait times, and movement durations to mimic human input patterns rather than robotic "teleporting."

Technical Implementation:

    Multithreading: Utilizes Python's threading module to run the automation logic and the GUI countdown independently, ensuring a responsive user interface.
    Process Management: Implements subprocess and os.execv logic for seamless self-restarting during the installation phase.
    Error Handling: Robust try-except blocks and traceback logging prevent silent crashes and provide user feedback in the event of permission or environment issues.


License:

This project is licensed under the MIT License - see the LICENSE file for details.
