PYTHON_PATH := C:\Users\Zephi\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\Scripts\pyinstaller.exe
APP_NAME := "weather app v0.1.0"
ICON_PATH := icon.ico
MAIN_SCRIPT := main.py
HIDDEN_IMPORTS := --hidden-import=tkinter --hidden-import=requests --hidden-import=pyttsx3 --hidden-import=random --hidden-import=dotenv.main --hidden-import=os --hidden-import=colorama

install-deps:
	pip install requests pyttsx3 python-dotenv tkinter colorama

build:
	$(PYTHON_PATH) --onefile --name $(APP_NAME) --icon=$(ICON_PATH) $(HIDDEN_IMPORTS) $(MAIN_SCRIPT)

clean:
	rm -rf build dist $(APP_NAME).spec

all: install-deps build

#C:\Users\Zephi\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\Scripts\pyinstaller.exe --onefile --name "weather app v0.1.0" --icon=icon.ico --hidden-import=tkinter --hidden-import=requests --hidden-import=pyttsx3 --hidden-import=random --hidden-import=dotenv.main --hidden-import=os --hidden-import=colorama main.py
