import cv2
import json
import logging
import os
from PIL import ImageGrab, Image
import google.generativeai as genai
from src.config import DEBUG_DIR
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    'gemini-3.1-flash-lite'
    '',
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        temperature=0.0
    )
)

class VisionEngine:
    def __init__(self):
        self.debug_count = 0

    def capture_screen(self) -> str:
        path = DEBUG_DIR / f"global_state_{self.debug_count}.png"
        screenshot = ImageGrab.grab(all_screens=True)
        screenshot.save(path)
        return str(path)

    def _ask_gemini_vision(self, image_path: str, prompt: str) -> dict:
        logging.info("Sending image slice to Gemini 3.1 Flash Lite...")
        img = Image.open(image_path)
        try:
            response = model.generate_content([prompt, img])
            return json.loads(response.text)
        except Exception as e:
            logging.error(f"Failed to parse JSON from Gemini: {e}")
            return {}

    def ground_icon(self) -> tuple[float, float]:
        self.debug_count += 1
        full_screen_path = self.capture_screen()

        img = cv2.imread(full_screen_path)
        height, width = img.shape[:2]

        # Define the 4 quadrants to beat the resolution downsampling issue
        mid_x, mid_y = width // 2, height // 2
        quadrants = [
            {"name": "Top-Left", "box": (0, 0, mid_x, mid_y)},
            {"name": "Bottom-Left", "box": (0, mid_y, mid_x, height)},
            {"name": "Top-Right", "box": (mid_x, 0, width, mid_y)},
            {"name": "Bottom-Right", "box": (mid_x, mid_y, width, height)}
        ]

        prompt = """
        You are an OS automation assistant inspecting a high-resolution desktop segment.
        Task: Locate the Windows "Notepad" application shortcut icon.

        CRITICAL VISUAL RECOGNITION RULES:
        1. PRIMARY VISUAL: Look for a predominantly BLUE and WHITE icon (typically a blue spiral notebook or a blue square with a white page).
        2. SECONDARY CONFIRMATION: The text label directly underneath the graphic will usually contain the word "Notepad".
        3. EXCLUSIONS: Strictly ignore all yellow folders, image thumbnails, and generic document files.
        4. TARGETING: Return the exact center coordinate of the BLUE/WHITE ICON GRAPHIC itself, completely ignoring the text label.
        
        Return coordinates using a NORMALIZED scale between 0 and 1000 across this image snippet (0,0 is top-left, 1000,1000 is bottom-right).
        
        Return ONLY this JSON format:
        {"status": "FOUND", "x": 500, "y": 500}
        
        If the Notepad icon is not inside this image segment, return exactly:
        {"status": "NOT_FOUND"}
        """

        # Scan quadrants sequentially until the icon is accurately localized
        for quad in quadrants:
            logging.info(f"Scanning {quad['name']} Quadrant for ultra-sharp text resolution...")

            x1, y1, x2, y2 = quad["box"]
            quad_img = img[y1:y2, x1:x2]
            quad_path = str(DEBUG_DIR / f"quad_{quad['name']}_{self.debug_count}.png")
            cv2.imwrite(quad_path, quad_img)

            result = self._ask_gemini_vision(quad_path, prompt)

            if result.get("status") == "FOUND":
                logging.info(f"Target successfully located in {quad['name']} quadrant!")
                # 1. Load full image
                full_img = cv2.imread(full_screen_path)
                h, w = full_img.shape[:2]
                mid_x, mid_y = w // 2, h // 2

                # 2. DRAW QUADRANT GRIDLINES
                # Draw vertical and horizontal lines
                cv2.line(full_img, (mid_x, 0), (mid_x, h), (0, 0, 255), 4)
                cv2.line(full_img, (0, mid_y), (w, mid_y), (0, 0, 255), 4)

                # 3. LABEL QUADRANTS (Text overlay)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(full_img, "TL", (50, 50), font, 2, (0, 0, 255), 2)
                cv2.putText(full_img, "TR", (mid_x + 50, 50), font, 2, (0, 0, 255), 2)
                cv2.putText(full_img, "BL", (50, mid_y + 50), font, 2, (0, 0, 255), 2)
                cv2.putText(full_img, "BR", (mid_x + 50, mid_y + 50), font, 1, (255, 255, 255), 2)

                # 4. ANNOTATE DETECTION (The Red Box)
                global_x = x1 + int((result["x"] / 1000) * (x2 - x1))
                global_y = y1 + int((result["y"] / 1000) * (y2 - y1))
                cv2.rectangle(full_img, (global_x - 30, global_y - 30), (global_x + 30, global_y + 30), (0, 0, 255), 5)

                # 5. Save the final "Global Audit"
                cv2.imwrite(str(DEBUG_DIR / "global_annotated_final.png"), full_img)

                # Convert the normalized coordinates back into quadrant pixels
                quad_w, quad_h = (x2 - x1), (y2 - y1)
                local_x = int((result["x"] / 1000) * quad_w)
                local_y = int((result["y"] / 1000) * quad_h)

                # Project the local quadrant pixels back to full global screen coordinates
                global_x = x1 + local_x
                global_y = y1 + local_y
                # Calculate local pixel coordinates
                local_x = int((result["x"] / 1000) * (x2 - x1))
                local_y = int((result["y"] / 1000) * (y2 - y1))

                # Calculate global absolute pixels
                abs_x = x1 + local_x
                abs_y = y1 + local_y

                #RETURN NORMALIZED FLOAT (0.0 TO 1.0)
                norm_x = abs_x / width
                norm_y = abs_y / height
                return (norm_x, norm_y)



        raise ValueError("Icon 'Notepad' could not be grounded in any screen quadrant.")