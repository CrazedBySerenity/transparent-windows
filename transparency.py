from win32 import win32gui, winxpgui, win32api
import win32.lib.win32con as win32con
import keyboard

running = True

opacity_step_1 = 30

opacity_step_10 = 255

opacity = 30

def changePaintOpacity():
    hwnd = win32gui.FindWindow(None, "Untitled - Paint")  ## The caption of my empty notepad (MetaPad)

    win32gui.SetWindowLong (hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong (hwnd, win32con.GWL_EXSTYLE ) | win32con.WS_EX_LAYERED )
    winxpgui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), opacity, win32con.LWA_ALPHA)

while True:
    event = keyboard.read_event()
    if event.name == '1' and event.event_type == 'down':
        opacity = opacity_step_1
        changePaintOpacity()
        print('made transparent')
    if event.name == '9' and event.event_type == 'down':
        opacity = opacity_step_10
        changePaintOpacity()
        print('made opaque')