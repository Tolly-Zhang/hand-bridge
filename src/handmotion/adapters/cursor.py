import pyautogui

class CursorAdapter:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.is_mouse_down = False

    def printRange(self) -> tuple[int, int]:
        print(f"Screen size: ({self.screen_width}, {self.screen_height})")
        return self.screen_width, self.screen_height

    def get_mouse_position(self) -> tuple[int, int]:
        return pyautogui.position()

    def move_norm(self, x: float, y: float) -> None:
        orig_x, orig_y = x, y
        clamped = False
        if not (0.0 <= x <= 1.0):
            x = min(max(x, 0.0), 1.0)
            clamped = True
        if not (0.0 <= y <= 1.0):
            y = min(max(y, 0.0), 1.0)
            clamped = True
        if clamped:
            print(f"[Cursor Adapter] Warning: move_norm received out-of-bounds values ({orig_x:.4f}, {orig_y:.4f}), clamped to ({x:.4f}, {y:.4f})")

        px = int(x * self.screen_width)
        py = int(y * self.screen_height)
        pyautogui.moveTo(px, py)

    def click_once(self, button: str = "left") -> None:
        pyautogui.click(button=button)

    def double_click(self, button: str = "left", interval: float = 0.25) -> None:
        pyautogui.doubleClick(button=button, interval=interval)

    def mouse_down(self, button: str = "left") -> None:
        pyautogui.mouseDown(button=button)
        self.is_mouse_down = True

    def mouse_up(self, button: str = "left") -> None:
        pyautogui.mouseUp(button=button)
        self.is_mouse_down = False

    def scroll(self, dx: int = 0, dy: int = 0) -> None:
        # pyautogui.scroll scrolls vertically; horizontal scroll is OS-dependent
        if dy != 0:
            pyautogui.scroll(dy)
        if dx != 0:
            try:
                pyautogui.hscroll(dx)
            except AttributeError:
                pass  # hscroll may not be available on all platforms