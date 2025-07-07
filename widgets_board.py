# widgets_board.py
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.properties import StringProperty
from typing import Callable, Tuple # Thêm Tuple
from themes import Theme # Import Theme

# CELL_SIZE bây giờ là một giá trị danh nghĩa. Kích thước thực tế sẽ được xác định bởi layout.py
CELL_SIZE = 10 # px – Đây chỉ là kích thước ban đầu/placeholder. Kích thước thật sẽ do layout.py quyết định


class XOCell(ButtonBehavior, Image):
    mark = StringProperty('')

    # Thêm tham số theme vào __init__
    def __init__(self, row: int, col: int, on_press_cb: Callable[[int, int], None], theme: Theme, **kw):
        super().__init__(**kw)
        self.row, self.col = row, col
        self._on_press_cb = on_press_cb
        self._theme = theme # Lưu đối tượng theme

        # Sử dụng theme để đặt nguồn ảnh
        self.source = self._theme.cell_bg # Ô trống
        self.allow_stretch = True
        self.keep_ratio = False
        self.size_hint = (None, None)
        self.size = (CELL_SIZE, CELL_SIZE) # Sẽ được ghi đè ngay lập tức bởi layout.py

    def on_release(self):
        self._on_press_cb(self.row, self.col)

    def set_mark(self, symbol: str): # Đổi kiểu dữ liệu của symbol thành str
        if symbol == "X":
            self.source = self._theme.x_icon
        elif symbol == "O":
            self.source = self._theme.o_icon
        elif symbol == "#": # Xử lý chướng ngại vật
            self.source = self._theme.obs_icon
        else:
            self.source = self._theme.cell_bg


class BoardWidget(GridLayout):
    """Visualizes the board state using a grid of XOCells."""

    def __init__(self, board, on_cell_cb: Callable[[int, int], None], theme: Theme, **kwargs):
        super().__init__(**kwargs)
        self.rows = board.rows
        self.cols = board.cols
        self._on_cell_cb = on_cell_cb
        self._theme = theme # Lưu đối tượng theme
        
        self.spacing = 0
        
        self.size_hint = (None, None)
        # Kích thước ban đầu dựa trên CELL_SIZE danh nghĩa, sẽ được điều chỉnh bởi layout.py
        self.size = (CELL_SIZE * board.cols,
                     CELL_SIZE * board.rows)

        self._cells = {}
        # Lặp qua số hàng và cột thực tế của đối tượng board
        for i in range(board.rows):
            for j in range(board.cols):
                # Truyền đối tượng theme vào XOCell
                c = XOCell(i, j, self._on_cell_cb, self._theme)
                self.add_widget(c)
                self._cells[(i, j)] = c

        # DI CHUYỂN CÁC DÒNG NÀY VÀO ĐÂY:
        # Điều này đảm bảo lớp BoardWidget đã được định nghĩa đầy đủ trước khi các dòng này thực thi,
        # ngăn ngừa các vấn đề import vòng tròn liên quan đến cơ chế nội bộ của Kivy.
        Window.minimum_width  = CELL_SIZE * board.cols
        Window.minimum_height = CELL_SIZE * board.rows

    # ------------------- public API dùng trong layout ---------------------
    def reset(self, board):
        # Duyệt qua tất cả các ô trong _cells
        for (i, j), cell in self._cells.items(): 
            # Đảm bảo chỉ cập nhật các ô nằm trong phạm vi của bảng hiện tại
            if 0 <= i < board.rows and 0 <= j < board.cols:
                cell.set_mark(board._grid[i][j]) # Cập nhật trạng thái ô từ board model
            else:
                # Xử lý các ô không còn tồn tại nếu bảng nhỏ hơn trước đó
                # Trong trường hợp này, vì BoardWidget được khởi tạo lại mỗi khi tạo game mới,
                # thì sẽ không có cells nào nằm ngoài phạm vi.
                pass 

    def update_cell(self, coords: Tuple[int, int], symbol: str): # Đổi kiểu dữ liệu của coords thành Tuple[int, int] và symbol thành str
        self._cells[coords].set_mark(symbol)