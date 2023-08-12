from win32 import win32gui, winxpgui, win32api
import win32.lib.win32con as win32con
import keyboard

running = True

opacity_step_1 = 30

opacity_step_10 = 255

opacity = 30

def changeWindowOpacity():
    hwnd = win32gui.FindWindow(None, win32gui.GetWindowText(win32gui.GetForegroundWindow()))

    win32gui.SetWindowLong (hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong (hwnd, win32con.GWL_EXSTYLE ) | win32con.WS_EX_LAYERED )
    winxpgui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), opacity, win32con.LWA_ALPHA)

while True:
    event = keyboard.read_event()
    if keyboard.is_pressed('shift'):
        if keyboard.is_pressed('1') and event.event_type == 'down':
            opacity = opacity_step_1
            changeWindowOpacity()
            print('made transparent')

        if keyboard.is_pressed('2') and event.event_type == 'down':
            opacity = round(((opacity_step_10 - opacity_step_1) / 8 )* 2)
            changeWindowOpacity()
            print('updated transparency')

        if keyboard.is_pressed('3')  and event.event_type == 'down':
            opacity = round(((opacity_step_10 - opacity_step_1) / 8 )* 3)
            changeWindowOpacity()
            print('updated transparency')

        if keyboard.is_pressed('4') and event.event_type == 'down':
            opacity = round(((opacity_step_10 - opacity_step_1) / 8 )* 4)
            changeWindowOpacity()
            print('updated transparency')

        if keyboard.is_pressed('5') and event.event_type == 'down':
            opacity = round(((opacity_step_10 - opacity_step_1) / 8 )* 5)
            changeWindowOpacity()
            print('updated transparency')

        if keyboard.is_pressed('6') and event.event_type == 'down':
            opacity = round(((opacity_step_10 - opacity_step_1) / 8 )* 6)
            changeWindowOpacity()
            print('updated transparency')

        if keyboard.is_pressed('7') and event.event_type == 'down':
            opacity = round(((opacity_step_10 - opacity_step_1) / 8 )* 7)
            changeWindowOpacity()
            print('updated transparency')

        if keyboard.is_pressed('8') and event.event_type == 'down':
            opacity = round(((opacity_step_10 - opacity_step_1) / 8 )* 8)
            changeWindowOpacity()
            print('updated transparency')

        if keyboard.is_pressed('9') and event.event_type == 'down':
            opacity = opacity_step_10
            changeWindowOpacity()
            print('made opaque')