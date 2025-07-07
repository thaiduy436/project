# themes.py
from pathlib import Path

class Theme:
    def __init__(self, name: str):
        # Đảm bảo tên theme hợp lệ để tránh lỗi đường dẫn
        valid_themes = ["wood", "fire", "water", "metal", "earth"] # Thêm các theme mới
        if name not in valid_themes:
            print(f"Warning: Theme '{name}' not found. Defaulting to 'wood'.")
            name = "wood" # Mặc định về theme gỗ nếu tên không hợp lệ

        self.name = name  # Thêm thuộc tính name để lưu tên theme
        base = Path("assets") / name
        self.bg = str(base / "bg.png")
        self.cell_bg = str(base / "cell.png")
        self.x_icon = str(base / "x.png")
        self.o_icon = str(base / "o.png")
        self.obs_icon = str(base / "obstacle.png")