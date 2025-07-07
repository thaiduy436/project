# sound_manager.py
from kivy.core.audio import SoundLoader
import os

class SoundManager:
    """Load & reuse background / SFX once."""
    def __init__(self, theme: str = "wood"):
        # Đã điều chỉnh đường dẫn để trỏ đúng vào thư mục 'assets/sounds'
        # Giả sử thư mục 'sounds' nằm trong thư mục 'assets'
        base_path = os.path.join("assets", "sounds")
        
        bg_path = os.path.join(base_path, f"{theme}.ogg")
        tap_path = os.path.join(base_path, "click.wav")
        win_path = os.path.join(base_path, "win.wav")
        draw_path = os.path.join(base_path, "draw.wav")

        self.bg = SoundLoader.load(bg_path)
        if not self.bg:
            print(f"Failed to load background music: {bg_path}. File exists: {os.path.exists(bg_path)}")
        else:
            print(f"Successfully loaded background music: {bg_path}")
        self.tap = SoundLoader.load(tap_path)
        if not self.tap:
            print(f"Failed to load tap sound: {tap_path}. File exists: {os.path.exists(tap_path)}")
        else:
            print(f"Successfully loaded tap sound: {tap_path}")
        self.win = SoundLoader.load(win_path)
        if not self.win:
            print(f"Failed to load win sound: {win_path}. File exists: {os.path.exists(win_path)}")
        else:
            print(f"Successfully loaded win sound: {win_path}")
        self.draw = SoundLoader.load(draw_path)
        if not self.draw:
            print(f"Failed to load draw sound: {draw_path}. File exists: {os.path.exists(draw_path)}")
        else:
            print(f"Successfully loaded draw sound: {draw_path}")

        for s in (self.bg, self.tap, self.win, self.draw):
            if s:
                s.volume = 1.0  # Đặt âm lượng tối đa

        if self.bg:
            self.bg.loop = True
            self.bg.play()
            print(f"Background music started playing from: {self.bg.source}. State: {self.bg.state}")

    # helper wrappers --------------------------------------------------
    def play_tap(self):   self._safe(self.tap)
    def play_win(self):   self._safe(self.win)
    def play_draw(self):  self._safe(self.draw)

    def _safe(self, s):
        if s: s.play()