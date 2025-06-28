import threading
import sys
import os
import time
from win32 import win32gui, winxpgui, win32api
import win32.lib.win32con as win32con
import keyboard
import tkinter as tk
from tkinter import messagebox

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

class TransparentWindowsApp:
    def __init__(self):
        self.running = True
        self.opacity_step_1 = 10
        self.opacity_step_10 = 255
        self.opacity = 30
        self.icon = None
        
    def change_window_opacity(self):
        """Apply transparency to the currently active window"""
        try:
            # time.sleep(0.1)  # Small delay to ensure we get the right window
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                window_title = win32gui.GetWindowText(hwnd)
                
                # Skip our own windows to prevent crashes
                if any(skip_word in window_title.lower() for skip_word in 
                      ['transparent windows', 'about', 'error', 'message']):
                    print(f"Skipping window: {window_title}")
                    return
                
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                     win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
                winxpgui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), self.opacity, win32con.LWA_ALPHA)
                
                transparency_percent = round((self.opacity / 255) * 100)
                print(f"Applied {transparency_percent}% opacity to: {window_title}")
                
        except Exception as e:
            print(f"Error changing opacity: {e}")
    
    def keyboard_listener(self):
        """Listen for keyboard shortcuts"""
        print("Keyboard listener started. Use Shift + 1-9 to change transparency.")
        
        while self.running:
            try:
                if keyboard.is_pressed('shift'):
                    for num in range(1, 10):
                        key = str(num)
                        if keyboard.is_pressed(key):
                            if num == 1:
                                self.opacity = self.opacity_step_1
                            elif num == 9:
                                self.opacity = self.opacity_step_10
                            else:
                                self.opacity = round(self.opacity_step_1 + ((self.opacity_step_10 - self.opacity_step_1) / 8) * (num - 1))
                            
                            self.change_window_opacity()
                            time.sleep(0.3)  # Prevent multiple triggers
                            break
                
                time.sleep(0.05)  # Prevent excessive CPU usage
                        
            except Exception as e:
                if self.running:
                    print(f"Keyboard listener error: {e}")
                    time.sleep(1)
    
    def create_tray_icon(self):
        """Create a simple icon for the system tray"""
        # Create a 64x64 icon
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw a window icon with transparency effect
        # Outer window
        draw.rectangle([8, 8, 56, 48], fill=(100, 100, 100, 255), outline=(50, 50, 50, 255), width=2)
        # Title bar
        draw.rectangle([8, 8, 56, 20], fill=(50, 100, 200, 255))
        # Inner content with transparency effect
        draw.rectangle([16, 28, 48, 40], fill=(150, 150, 150, 128))
        draw.rectangle([20, 32, 44, 36], fill=(200, 200, 200, 64))
        
        # Add "T" for Transparency
        draw.text((26, 50), "T", fill=(0, 0, 0, 255))
        
        return image
    
    def show_about(self):
        """Show information about the application"""
        def show_dialog():
            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            about_text = """Transparent Windows by Sophia

Keyboard Shortcuts:
• Shift + 1-9: Change window transparency
• 1 = Most transparent (10%)
• 9 = Fully opaque (100%)
• 2-8 = Gradual transparency levels

Usage:
1. Focus on any window
2. Press Shift + number key
3. Window becomes transparent

Right-click the tray icon for options.
The app runs in the background."""
            
            messagebox.showinfo("About Transparent Windows", about_text)
            root.destroy()
        
        # Run dialog in separate thread to avoid blocking
        threading.Thread(target=show_dialog, daemon=True).start()
    
    def reset_all_windows(self):
        """Reset all windows to full opacity"""
        def reset_windows():
            try:
                def enum_window_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                        windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_window_callback, windows)
                
                reset_count = 0
                for hwnd in windows:
                    try:
                        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                             win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
                        winxpgui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0,0,0), 255, win32con.LWA_ALPHA)
                        reset_count += 1
                    except:
                        continue
                
                print(f"Reset {reset_count} windows to full opacity")
                
                # Show confirmation dialog
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("Reset Complete", f"Reset {reset_count} windows to full opacity")
                root.destroy()
                
            except Exception as e:
                print(f"Reset failed: {e}")
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Reset Failed", f"Error: {e}")
                root.destroy()
        
        threading.Thread(target=reset_windows, daemon=True).start()
    
    def quit_app(self):
        """Quit the application"""
        self.running = False
        if self.icon:
            self.icon.stop()
        print("Transparent Windows shutting down...")
        os._exit(0)  # Force exit
    
    def run_system_tray(self):
        """Run the system tray application"""
        if not TRAY_AVAILABLE:
            print("System tray not available. Please install: pip install pillow pystray")
            self.run_console_mode()
            return
        
        try:
            # Create the system tray icon
            image = self.create_tray_icon()
            
            menu = pystray.Menu(
                item('About', self.show_about),
                item('Reset All Windows', self.reset_all_windows),
                pystray.Menu.SEPARATOR,
                item('Quit', self.quit_app)
            )
            
            self.icon = pystray.Icon("TransparentWindows", image, "Transparent Windows - Shift+1-9", menu)
            
            # Start keyboard listener in background
            keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
            keyboard_thread.start()
            
            print("Transparent Windows is running in the system tray.")
            print("Look for the icon in the bottom-right corner of your screen.")
            print("Use Shift + 1-9 to change window transparency.")
            
            # Run the system tray (this blocks until quit)
            self.icon.run()
            
        except Exception as e:
            print(f"System tray error: {e}")
            print("Falling back to console mode...")
            self.run_console_mode()
    
    def run_console_mode(self):
        """Fallback console mode if system tray fails"""
        print("\n" + "="*50)
        print("TRANSPARENT WINDOWS - CONSOLE MODE")
        print("="*50)
        print("Use Shift + 1-9 to change window transparency:")
        print("• 1 = Most transparent (10%)")
        print("• 9 = Fully opaque (100%)")
        print("• 2-8 = Gradual transparency levels")
        print("\nPress Ctrl+C to quit")
        print("="*50)
        
        # Start keyboard listener
        keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        keyboard_thread.start()
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.running = False

def main():
    """Main function to run the application"""
    if os.name != 'nt':
        print("Error: This application only works on Windows.")
        input("Press Enter to exit...")
        return
    
    print("Starting Transparent Windows...")
    
    try:
        app = TransparentWindowsApp()
        app.run_system_tray()
        
    except ImportError as e:
        error_msg = f"Missing required library: {e}\n\nRequired packages:\npip install pywin32 keyboard pillow pystray"
        print(error_msg)
        input("Press Enter to exit...")
        
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        print(error_msg)
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()