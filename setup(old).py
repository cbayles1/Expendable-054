from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name = "NewGame" , 
    version = "1.0" ,
    options={"build_exe": {"packages":["pygame", "time", "random", "os", 'base64', 'io', 'sys'],
        "include_files":[
            "audio/grapple.wav", "audio/jump.wav", "audio/powerup.wav", "audio/gun.wav", "audio/damage.wav", "audio/parachute.wav", "audio/glass.wav", "audio/levels.wav", "audio/menu.wav", "audio/boss.wav", "audio/wind.wav", "vt323.ttf", "userPrefs"
        ]}},
    executables = [Executable("main.py")])
