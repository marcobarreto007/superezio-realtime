import pyautogui
import tempfile
import os
from datetime import datetime

# ======================================================
# Ferramentas de Controle do Sistema - "Mãos e Olhos"
# ======================================================

def move_mouse_to(x: int, y: int) -> str:
    """
    Moves the mouse cursor to the specified (x, y) coordinates on the screen.

    Args:
        x (int): The x-coordinate to move to.
        y (int): The y-coordinate to move to.
    
    Returns:
        str: A confirmation message.
    """
    try:
        pyautogui.moveTo(x, y, duration=0.25)
        return f"Mouse moved to ({x}, {y})."
    except Exception as e:
        return f"Error moving mouse: {e}"

def click_at(x: int, y: int, button: str = 'left') -> str:
    """
    Performs a mouse click at the specified (x, y) coordinates.

    Args:
        x (int): The x-coordinate to click at.
        y (int): The y-coordinate to click at.
        button (str): The mouse button to click ('left', 'right', 'middle'). Defaults to 'left'.
    
    Returns:
        str: A confirmation message.
    """
    try:
        pyautogui.click(x, y, button=button)
        return f"{button.capitalize()} click performed at ({x}, {y})."
    except Exception as e:
        return f"Error performing click: {e}"

def type_text(text: str) -> str:
    """
    Types the given text at the current cursor position.

    Args:
        text (str): The text to type.
    
    Returns:
        str: A confirmation message.
    """
    try:
        pyautogui.write(text, interval=0.05)
        return f"Typed text: '{text[:30]}...'"
    except Exception as e:
        return f"Error typing text: {e}"

def take_screenshot() -> str:
    """
    Takes a screenshot of the entire screen and saves it to a temporary file.

    Returns:
        str: The path to the saved screenshot file.
    """
    try:
        # Create a temporary file to save the screenshot
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(temp_dir, f"superezio_screenshot_{timestamp}.png")
        
        screenshot = pyautogui.screenshot()
        screenshot.save(file_path)
        
        return f"Screenshot saved to {file_path}"
    except Exception as e:
        return f"Error taking screenshot: {e}"

# Lista de ferramentas para registro
SYSTEM_CONTROL_TOOLS = [
    {
        "name": "move_mouse_to",
        "description": "Moves the mouse cursor to a specific (x, y) coordinate on the screen.",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "The target x-coordinate."},
                "y": {"type": "integer", "description": "The target y-coordinate."}
            },
            "required": ["x", "y"]
        },
        "function": move_mouse_to
    },
    {
        "name": "click_at",
        "description": "Performs a mouse click at a specific (x, y) coordinate.",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "The x-coordinate to click at."},
                "y": {"type": "integer", "description": "The y-coordinate to click at."},
                "button": {"type": "string", "enum": ["left", "right", "middle"], "description": "The mouse button to use."}
            },
            "required": ["x", "y"]
        },
        "function": click_at
    },
    {
        "name": "type_text",
        "description": "Types a given string of text at the current cursor location.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text to be typed."}
            },
            "required": ["text"]
        },
        "function": type_text
    },
    {
        "name": "take_screenshot",
        "description": "Takes a screenshot of the entire screen and returns the path to the saved image file.",
        "parameters": {"type": "object", "properties": {}},
        "function": take_screenshot
    }
]
