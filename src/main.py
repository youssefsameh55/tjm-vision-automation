import logging
import os
import time
import pyautogui
import ctypes
import threading
import sys
from pynput import keyboard # Handles background keyboard hooks even during blocks
from src.data_controller import fetch_posts
from src.vision_engine import VisionEngine
from src.os_agent import OSAgent
from src.config import OUTPUT_DIR

# Global flag to signal thread cancellation across components
abort_automation = False
agent_instance = None

def emergency_monitor(key):
    """Listens continuously for the Escape key to break execution loops immediately."""
    global abort_automation, agent_instance
    try:
        if key == keyboard.Key.esc:
            logging.critical("\n🚨 EMERGENCY KILL SWITCH TRIGGERED! ABORTING WORKFLOW... 🚨")
            abort_automation = True

            # Critical Cleanup: Unblock user input immediately before shutting down
            if agent_instance:
                agent_instance.set_hardware_input_block(False)

            # Clean up system states
            os.system("taskkill /f /im notepad.exe /t >nul 2>&1")

            # Force close script execution
            logging.info("System hardware safety released. Exiting application process.")
            os._exit(1)
    except Exception as e:
        print(f"Error in kill switch hook: {e}")

def run_workflow_loop():
    """The automation loop wrapped securely inside a sub-thread execution track."""
    global abort_automation, agent_instance
    logging.info("Starting Desktop Automation Workflow Sub-Thread")

    # Minimize all windows to reveal the desktop to the AI
    logging.info("Minimizing windows to reveal desktop...")
    pyautogui.hotkey('win', 'd')
    time.sleep(1.5)

    posts = fetch_posts(1)
    vision = VisionEngine()
    agent_instance = OSAgent()

    # --- ADVANCED RESILIENCE: LOCK OUT USER INTERFERENCE ---
    # Lock mouse and keyboard actions from interfering with pipeline execution
    agent_instance.set_hardware_input_block(True)

    for i, post in enumerate(posts):
        if abort_automation: break
        logging.info(f"\n--- Processing Post {i+1}/{len(posts)} ---")

        try:
            # --- THE MODAL SWEEPER ---
            # Clear popup anomalies before taking a screenshot
            agent_instance.dismiss_system_modals()

            logging.info("Initiating Vision Grounding phase...")
            start_time = time.time()

            # 1. Ground Icon
            target_x, target_y = vision.ground_icon()
            if abort_automation: break

            grounding_duration = time.time() - start_time
            logging.info(f"✅ Vision Grounding successful! Duration: {grounding_duration:.2f} seconds.")

            # 2. Execute Click
            agent_instance.double_click_icon(target_x, target_y)
            if abort_automation: break

            # 3. Validate OS State
            if not agent_instance.wait_for_window("Notepad"):
                raise RuntimeError("Notepad window failed to appear after double-click.")

            # 4. Inject and Save
            filename = f"post_{post['id']}.txt"
            filepath = os.path.join(OUTPUT_DIR, filename)

            agent_instance.inject_text_and_save(post['title'], post['body'], filepath)

            time.sleep(1)

        except Exception as e:
            fail_duration = time.time() - start_time
            logging.error(f"❌ Workflow failed on post {i+1} after {fail_duration:.2f} seconds: {e}")

            # Safe release input block before launching error popups
            agent_instance.set_hardware_input_block(False)

            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            error_msg = f"Automation Error on Post {i+1}:\n\n{str(e)}\n\nExecution Time: {fail_duration:.2f}s"
            ctypes.windll.user32.MessageBoxW(hwnd, error_msg, "Vision Automation Failure", 0x10 | 0x1000)
            break

    # --- SAFE RELEASE RELEASE ---
    # Restore normal operations when completion state is hit
    if agent_instance:
        agent_instance.set_hardware_input_block(False)
    logging.info("Workflow loop thread finished execution cleanly.")

if __name__ == "__main__":
    # 1. Spin up the Keyboard Hook Listener in the foreground main thread
    listener = keyboard.Listener(on_press=emergency_monitor)
    listener.start()
    logging.info("🛡️ Emergency Kill Switch active. Press [ESC] at any time to instantly abort execution.")

    # 2. Spin up the Automation Engine in a background sub-thread
    automation_thread = threading.Thread(target=run_workflow_loop, daemon=True)
    automation_thread.start()

    # 3. Keep the application awake while processing threads continue
    while automation_thread.is_alive():
        time.sleep(0.1)