#!.venv\scripts\pythonw.exe
import pystray
import time
import PIL.Image
from datetime import datetime
from functools import partial
from configparser import ConfigParser
from tkinter import Tk, Label, Button, W, E, Menu

from services.table_order import TableOrder
from services.table_result import TableResult
from services.cleanup import CleanUp
from services.email import Email

from hclab2.log import setup_logger


# DEFINE TASK TO ARRAY OF THREADS
threads = [
  {"task" : "TableOrder", "title" : "Uploader Order"},
  {"task" : "TableResult", "title" : "Uploader Result"},
  {"task" : "Email", "title" : "Auto Email"},
  {"task" : "CleanUp", "title" : "Clean Up Manager"}
]


today = datetime.today().strftime("%Y%m%d")
logger = setup_logger("main", f"main_{today}")

config = ConfigParser()
config.read('application.ini')


# DEFINE CONTAINER VARIABLES
objects = dict()
labels = dict()
buttons = dict()

image = PIL.Image.open("img\launcher.png")

window = Tk()
window.title("Taskloader")
window.geometry("700x300")
window.resizable(0,0)

menubar = Menu(window)
window.config(menu=menubar)


def kill_all_services():
  for key in objects:
    object = objects[key]

    if object.is_alive():
      logger.info(f"Stopping {key} service..")
      object.stop()
      object.message.queue.clear()
      object.join()

  for key in buttons:
    button = buttons[key]
    if button["text"] == "Started":
      button.config(text="Start")
      button.config(bg="red", fg="white")

  for key in labels:
    label = labels[key]
    label.config(text="Stopped")
      

def start_all_services():
  for index, thread in enumerate(threads):

    label_name = "label" + str(index)
    label = labels[label_name]

    button_name = "button" + str(index)
    button = buttons[button_name]
    
    button.config(text="Start")
    on_click(thread["task"], button, label)

def restart_services():
  kill_all_services()
  time.sleep(3)
  start_all_services()


# WINDOW FUNCTION
# ==========================================
def on_exit():
  kill_all_services()
  window.destroy()

def on_enter(button, _):
  if button["text"] == "Started":
    button.config(text="Stop")
    button.config(bg="red", fg="white")


def on_leave(button, _):
  if button["text"] == "Stop":
    button.config(text="Started")
    button.config(bg="green", fg="white")


def on_click(task, button, label):

  object = None

  if button["text"] == "Start":
    logger.info(f"Starting {task} service..")
    button.config(text="Starting")
    label.config(text="Starting...")
    object = globals()[task](config) # create instance
    objects.update({task : object}) # contain object to dictionary
    object.start() # start thread of the object
    button.config(text="Started")
    button.config(bg="green", fg="white")

  elif button["text"] == "Stop":
    button.config(text="Stopping")
    object = objects[task] # assign object
    
    # stop current thread's object
    object.stop()
    object.message.queue.clear()
    object.join()
    objects.pop(task) 

    label.config(text="Stopped")
    button.config(text="Start")
    button.config(bg="red", fg="white")

def show_messages():

  for index, thread in enumerate(threads):

    label_name = "label" + str(index)
    label = labels[label_name]

    task = thread["task"]

    if task in objects:
      message = "Waiting..."
      object = objects[task]

      try:
        if not object.message.empty():
          message = object.message.get()
      
      except Exception as e:
        logger.error(e)
        
      label.config(text=message)
    
  window.after(500,show_messages)
# ==========================================


# TRAY ICON FUNCTION 
# ==========================================
def show_window(icon, _):
  icon.stop()
  window.after(0,window.deiconify)

def quit_laucher(icon, _):
  kill_all_services()
  icon.stop()
  window.destroy()

def restart(icon, _):
  show_window(icon, _)
  restart_services()

def withdraw_window():
  window.withdraw()
  icon = pystray.Icon("launcher", image,"HCLAB Launcher", menu=pystray.Menu(
    pystray.MenuItem("Show", show_window, default=True),
    pystray.MenuItem("Restart All Services", restart),
    pystray.Menu.SEPARATOR,
    pystray.MenuItem("Stop All Services", kill_all_services),
    pystray.Menu.SEPARATOR,
    pystray.MenuItem("Exit", quit_laucher)
  ))
  icon.run()
# ==========================================


file_menu = Menu(menubar, tearoff=False)
file_menu.add_command(label="Iconify", command=withdraw_window)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=on_exit)
menubar.add_cascade(label="File", menu=file_menu)

action_menu = Menu(menubar, tearoff=False)
action_menu.add_command(label="Restart All Services", command=restart_services)
action_menu.add_separator()
action_menu.add_command(label="Stop All Services", command=kill_all_services)
menubar.add_cascade(label="Action", menu=action_menu)


for index, thread in enumerate(threads) : 

  _thread_name = Label(window, width="20", height="2", anchor="w", font=("Arial", 10,"bold"), borderwidth=2, relief="groove")
  _thread_name.grid(row=index+1, column=2, padx=3, pady=5, sticky=W+E)
  _thread_name.config(text=thread["title"])

  _key_message = "label" + str(index)
  _value_message = Label(window, width="50", height="2", text="Initiate", anchor="w", font=("Arial",10,"bold"), borderwidth=2, relief="groove")
  _value_message.grid(row=index+1, column=3, padx=3, pady=5, sticky=W+E)
  labels.update({_key_message:_value_message})

  _key_button = "button" + str(index)
  _value_button = Button(window,text="Start", width="7", font=("Arial",10,"bold"))
  _value_button.grid(row=index+1, column=1, padx=3, pady=5, sticky=W+E)
  buttons.update({_key_button:_value_button})

  _value_button.config(command=partial(on_click, thread["task"], _value_button, _value_message))
  _value_button.bind("<Enter>", partial(on_enter, _value_button))
  _value_button.bind("<Leave>", partial(on_leave, _value_button))

window.grid_columnconfigure(0,minsize=20)
window.grid_rowconfigure(0,minsize=20)

window.after(5000,show_messages)

window.protocol('WM_DELETE_WINDOW', withdraw_window)
window.mainloop()

for key in objects:

  object = objects[key]

  if object.is_alive():
    object.stop()
    object.message.queue.clear()
    object.join()