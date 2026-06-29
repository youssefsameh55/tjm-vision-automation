import pyautogui
import pygetwindow as gw
import ctypes
import time
import logging
import os

class OSAgent:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        self.dpi_scale = self._get_dpi_scaling()
        # Track if input is blocked so we can safely unblock on destruction
        self.input_blocked = False

    def _get_dpi_scaling(self) -> float:
        """Calculates exact Windows DPI scaling factor for high-res screens."""
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            scale = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100.0
            logging.info(f"Detected DPI Scaling factor: {scale}")
            return scale
        except Exception as e:
            logging.warning(f"Could not read DPI scaling, defaulting to 1.0. Error: {e}")
            return 1.0

    def set_hardware_input_block(self, block: bool):
        """Forces the Windows OS kernel to completely ignore physical mouse and keyboard inputs."""
        try:
            # Load user32.dll natively
            user32 = ctypes.windll.user32
            # BlockInput returns True if successful
            result = user32.BlockInput(block)
            if result:
                self.input_blocked = block
                logging.info(f"🔒 Hardware Input Block set to: {block}")
            else:
                logging.warning("⚠️ Failed to change Hardware Input Block state. Are you running as Administrator?")
        except Exception as e:
            logging.error(f"Failed to execute kernel input toggle: {e}")

    def dismiss_system_modals(self):
        """
        [THE MODAL SWEEPER]
        Scans active windows for known system environmental disruptors
        and dismisses them before the vision cycle begins.
        """
        logging.info("🧹 Sweeper: Scanning desktop for disruptive system modals...")
        # Blacklist of known intrusive application keywords
        disruptive_keywords = ["antivirus", "update", "notification", "security alert", "low storage"]

        try:
            all_windows = gw.getAllWindows()
            for win in all_windows:
                title = win.title.lower()
                # Check if any blacklisted app is visible on screen
                if any(kw in title for kw in disruptive_keywords) and win.visible:
                    logging.warning(f"🧹 Sweeper Hijack Detected! Attempting to neutralize popup: '{win.title}'")
                    try:
                        win.minimize() # Push to background
                        # Or use win.close() if you want to aggressively kill it
                        logging.info(f"🧹 Sweeper successfully neutralized window: '{win.title}'")
                    except Exception as e:
                        logging.error(f"🧹 Sweeper failed to clear window '{win.title}': {e}")
        except Exception as e:
            logging.error(f"🧹 Sweeper encountered window manager error: {e}")

    def double_click_icon(self, norm_x: float, norm_y: float):
        """Maps 0.0-1.0 percentages to physical screen pixels natively."""
        screen_w, screen_h = pyautogui.size()
        abs_x = int(norm_x * screen_w)
        abs_y = int(norm_y * screen_h)

        logging.info(f"Targeting relative ({norm_x:.2f}, {norm_y:.2f}) -> Physical ({abs_x}, {abs_y})")
        pyautogui.moveTo(abs_x, abs_y, duration=0.3)
        pyautogui.doubleClick()

    def wait_for_window(self, title_keyword: str, timeout: int = 5) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            active_window = gw.getActiveWindow()
            if active_window and title_keyword.lower() in active_window.title.lower():
                return True
            time.sleep(0.5)
        return False

    def inject_text_and_save(self, title: str, body: str, filepath: str):
        content = f"Title: {title}\n\n{body}"

        screen_w, screen_h = pyautogui.size()
        pyautogui.click(screen_w / 2, screen_h / 2)

        logging.info("Clearing canvas to handle Windows session-restore quirks...")
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')

        logging.info("Injecting text payload...")
        pyautogui.write(content, interval=0.01)

        logging.info(f"Forcing 'Save As' dialog for {filepath}")
        pyautogui.hotkey('ctrl', 'shift', 's')
        time.sleep(1)

        pyautogui.write(filepath)
        pyautogui.press('enter')
        time.sleep(1)

        pyautogui.press('left')
        pyautogui.press('enter')

        time.sleep(0.5)
        logging.info("Terminating Notepad process cleanly via recursive tree flag...")
        # Added /t flag to prune the process tree safely
        os.system("taskkill /f /im notepad.exe /t >nul 2>&1")