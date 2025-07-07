# utils.py  (mới)  -----------------------------
from kivy.graphics import Color, RoundedRectangle

def style_round_button(btn, rgba, radius=15):
    """Áp dụng màu + bo góc cho một Button."""
    # xoá nền mặc định
    btn.background_normal = ''
    btn.background_down   = ''
    btn.background_color  = (0, 0, 0, 0)  # trong suốt

    # vẽ nền bo góc
    with btn.canvas.before:
        Color(*rgba)                     # màu RGBA
        rect = RoundedRectangle(pos=btn.pos,
                                size=btn.size,
                                radius=[radius])

    # cập nhật khi nút thay đổi kích thước / vị trí
    def _update(*_):
        rect.pos  = btn.pos
        rect.size = btn.size
    btn.bind(pos=_update, size=_update)
