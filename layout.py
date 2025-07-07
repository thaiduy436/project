# layout.py
from __future__ import annotations
from typing import Optional, Tuple

from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.graphics import Rectangle

from controller import GameController, GameState, GameObserver
from board import Board
from themes import Theme
from sound_manager import SoundManager
from widgets_board import BoardWidget, CELL_SIZE
from utils import style_round_button


class TicTacToeLayout(FloatLayout):
    status_message = StringProperty("X's turn")

    def __init__(self, controller: GameController, theme: Theme, **kwargs):
        super().__init__(**kwargs)
        
        self._controller = controller
        self._board = controller.getBoard()
        self._theme = theme
        
        # Khởi tạo SoundManager với theme và kiểm tra
        self._sounds = SoundManager(theme.name)
        if not self._sounds.bg:
            print(f"Warning: No background music loaded for theme {theme.name}")
        else:
            print(f"Background music for {theme.name} is ready")
        self._controller.add_observer(self)

        # Background
        with self.canvas.before:
            self._bg = Rectangle(source=self._theme.bg, pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg) 
        
        # Board
        self._grid = BoardWidget(self._board, self._on_cell, self._theme)
        self.add_widget(self._grid)
        # pos_hint sẽ được đặt trong _update_board_layout

        # Status Label
        self._status = Label(
            text=self.status_message,
            font_size="20sp",
            size_hint=(1, None),
            height="40dp",
            color=(1, 1, 1, 1)
        )
        self.add_widget(self._status)
        self.bind(status_message=self._status.setter("text"))

        # Restart Button
        self._restart_button = Button(text='Chơi lại', size_hint=(0.2, None), height="50dp")
        self._restart_button.bind(on_release=self._on_restart)
        style_round_button(self._restart_button, (0.2, 0.6, 0.8, 1))
        self._restart_button.opacity = 0
        self._restart_button.disabled = True
        self.add_widget(self._restart_button)

        # Home Button
        self._home_button = Button(text='Trang chủ', size_hint=(0.2, None), height="50dp")
        self._home_button.bind(on_release=self._go_home)
        style_round_button(self._home_button, (0.8, 0.2, 0.2, 1))
        self.add_widget(self._home_button)
        
        # Cập nhật bố cục ban đầu và liên kết với sự kiện thay đổi kích thước cửa sổ
        self._update_board_layout(self.size, self.pos)
        self.bind(size=self._update_board_layout)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    # ------------------------- layout logic ------------------------------- #
    def _update_board_layout(self, *args):
        size = self.size

        status_bar_height = self._status.height
        button_height = self._restart_button.height
        
        vertical_padding = Window.height * 0.02

        available_height_for_board = size[1] - status_bar_height - button_height - (2 * vertical_padding)
        available_width_for_board = size[0]

        optimal_cell_size_w = available_width_for_board / self._board.cols if self._board.cols > 0 else 1
        optimal_cell_size_h = available_height_for_board / self._board.rows if self._board.rows > 0 else 1
        
        scaled_cell_size = min(optimal_cell_size_w, optimal_cell_size_h)
        
        min_abs_cell_size = 50
        scaled_cell_size = max(scaled_cell_size, min_abs_cell_size)

        self._grid.size = (self._board.cols * scaled_cell_size, self._board.rows * scaled_cell_size)
        
        for cell in self._grid.children:
            cell.size = (scaled_cell_size, scaled_cell_size)
            
        board_area_bottom = button_height + vertical_padding
        board_area_top = size[1] - status_bar_height - vertical_padding
        
        board_center_y_in_pixels = board_area_bottom + (board_area_top - board_area_bottom) / 2
        
        self._grid.pos_hint = {'center_x': 0.5, 'center_y': board_center_y_in_pixels / size[1]}

        self._status.pos_hint = {'center_x': 0.5, 'top': 1}

        self._home_button.pos_hint = {'x': 0.02, 'y': 0.01}
        self._restart_button.pos_hint = {'right': 0.98, 'y': 0.01}

    # --------------------------- UI events -------------------------------- #
    def _on_cell(self, row, col):
        self._controller.play(row, col)
        if self._sounds.tap:
            self._sounds.play_tap()

    def _on_restart(self, *_):
        self._controller.reset()
        self._grid.reset(self._board)
        if self._sounds.bg:
            self._sounds.bg.play()
            print("Restart: Background music restarted")
        self._hide_restart()

    # ------------------- GameObserver callbacks --------------------------- #
    def on_board_change(self, coords: Tuple[int, int], symbol: str) -> None:
        self._grid.update_cell(coords, symbol)
        if self._sounds.tap:
            self._sounds.play_tap()

    def on_state_change(self, state: GameState, next_turn: Optional[str]) -> None:
        if state is GameState.IN_PROGRESS:
            self.status_message = f"{next_turn}'s turn"
            self._hide_restart()
        else:
            self.status_message = (
                "Draw!" if state is GameState.DRAW else f"{state.name.split('_')[0]} wins!"
            )
            if state is GameState.DRAW and self._sounds.draw:
                self._sounds.play_draw()
            elif self._sounds.win:
                self._sounds.play_win()
            self._end_game()

        self._status.text = self.status_message

    # --------------------------- helpers ---------------------------------- #
    def _end_game(self):
        Clock.schedule_once(lambda *_: self._show_restart(), 1)

    def _show_restart(self):
        self._restart_button.opacity = 1
        self._restart_button.disabled = False

    def _hide_restart(self):
        self._restart_button.opacity = 0
        self._restart_button.disabled = True

    def _go_home(self, *args):
        from kivy.app import App
        app = App.get_running_app()
        app.go_home()
        # Không dừng âm thanh ngay lập tức, chỉ khi rời màn hình
        # if self._sounds.bg and self._sounds.bg.state == 'play':
        #     self._sounds.bg.stop()

    def on_leave(self, *args):
        # Dừng âm thanh khi rời màn hình game
        if self._sounds.bg and self._sounds.bg.state == 'play':
            self._sounds.bg.stop()
            print("Game screen left: Background music stopped")

    def on_enter(self, *args):
        # Phát lại âm thanh khi vào màn hình game
        if self._sounds.bg and self._sounds.bg.state != 'play':
            self._sounds.bg.play()
            print("Game screen entered: Background music started")