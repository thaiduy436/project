# app.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button

from board import Board
from controller import GameController
from themes import Theme
from layout import TicTacToeLayout
from homescreen import HomeScreen
from utils import style_round_button

# ------------------------------------------------------------------ #
# Cập nhật hàm create_game để nhận các tham số mới
def create_game(mode: str = "friend", difficulty: str = "medium", element: str = "wood",
                rows: int = 5, cols: int = 5, win_len: int = 4, num_obstacles: int = 5) -> TicTacToeLayout:
    # Truyền các tham số này vào hàm khởi tạo của Board
    board      = Board(rows=rows, cols=cols, win_len=win_len, num_obstacles=num_obstacles)
    controller = GameController(board, mode, difficulty)
    theme      = Theme(element)
    return TicTacToeLayout(controller, theme)

# ------------------------------------------------------------------ #
class GameScreen(Screen):
    """Screen that contains the game."""
    
    # Cập nhật __init__ của GameScreen để nhận các tham số mới
    def __init__(self, mode: str, difficulty: str = None, rows: int = 5, cols: int = 5,
                 win_len: int = 4, num_obstacles: int = 5, element: str = "wood", **kwargs):   
        super().__init__(**kwargs)
        # Tạo game widget với các tham số mới
        self.game_widget = create_game(mode, difficulty, element, rows, cols, win_len, num_obstacles)
        self.add_widget(self.game_widget)

    def on_enter(self, *args):
        # Đảm bảo game được reset khi vào màn hình game
        self.game_widget._controller.reset()
        self.game_widget._grid.reset(self.game_widget._board) # Reset grid visuals
        self.game_widget.status_message = "X's turn" # Reset status message
        if self.game_widget._controller._mode == "bot" and self.game_widget._controller._current == self.game_widget._controller._ai_symbol:
            # Nếu là lượt của AI ngay từ đầu, cho AI đi
            self.game_widget._controller._make_ai_move(0)


class TicTacToeApp(App):
    """Main application class."""

    def build(self):
        self.sm = ScreenManager(transition=FadeTransition())
        self.sm.add_widget(HomeScreen(name='home'))
        return self.sm

    # ------------------------------------------------------------------ #
    # Cập nhật hàm start_game để nhận các tham số mới
    def start_game(self, mode: str, difficulty: str = None, rows: int = 5, cols: int = 5,
                   win_len: int = 4, num_obstacles: int = 5, element: str = "wood"):
        
        # Remove old game screen if it exists
        if self.sm.has_screen('game'):
            old_screen = self.sm.get_screen('game')
            # Stop sounds before removing
            if hasattr(old_screen, 'game_widget') and hasattr(old_screen.game_widget, '_sounds'):
                if old_screen.game_widget._sounds.bg:
                    old_screen.game_widget._sounds.bg.stop()
            self.sm.remove_widget(old_screen)
        
        # Create new game screen with new parameters, including element
        game_screen = GameScreen(mode, difficulty, rows=rows, cols=cols, win_len=win_len, num_obstacles=num_obstacles, element=element, name='game')
        self.sm.add_widget(game_screen)
        
        # Switch to game screen
        self.sm.current = 'game'
    
    def go_home(self):
        """Return to home screen."""
        # Stop any playing sounds
        if self.sm.has_screen('game'):
            game_screen = self.sm.get_screen('game')
            if hasattr(game_screen, 'game_widget') and hasattr(game_screen.game_widget, '_sounds'):
                if game_screen.game_widget._sounds.bg:
                    game_screen.game_widget._sounds.bg.stop()
        
        self.sm.current = 'home'

    def on_stop(self):
        # Clean up background music if still playing
        if self.sm.current == 'game' and self.sm.has_screen('game'):
            game_screen = self.sm.get_screen('game')
            if hasattr(game_screen, 'game_widget') and hasattr(game_screen.game_widget, '_sounds'):
                if game_screen.game_widget._sounds.bg:
                    game_screen.game_widget._sounds.bg.stop()