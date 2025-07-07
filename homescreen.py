# homescreen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle, Color, Line
from kivy.animation import Animation
from kivy.properties import NumericProperty, ObjectProperty
from kivy.app import App
from kivy.metrics import dp
from kivy.core.text import LabelBase
from utils import style_round_button
from themes import Theme

# Register Segoe UI Emoji font
LabelBase.register(name='SegoeUIEmoji', fn_regular='assets/fonts/segoeuiemoji.ttf')

class HomeScreen(Screen):
    """Home screen for Tic Tac Toe with visual indication of selected buttons."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_theme = "wood"  # Default theme
        self.theme_obj = Theme(self.current_theme)  # Initialize theme
        self.current_mode = "friend"
        self.current_difficulty = "medium"
        self.selected_mode_btn = ObjectProperty(None)
        self.selected_difficulty_btn = ObjectProperty(None)
        self.selected_theme_btn = ObjectProperty(None)

        # Main layout with full screen utilization
        self.root = FloatLayout(size_hint=(1, 1))

        # Themed background with gradient overlay
        with self.root.canvas.before:
            Color(0, 0, 0, 0.3)  # Subtle dark overlay for contrast
            self.bg = Rectangle(source=self.theme_obj.bg, pos=self.root.pos, size=self.root.size)
        self.root.bind(size=self._update_bg, pos=self._update_bg)

        # Main content layout with balanced proportions
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20), size_hint=(0.8, 0.9), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        # Title with enhanced visibility
        title_container = FloatLayout(size_hint=(1, 0.15))
        with title_container.canvas.before:
            Color(0.1, 0.5, 0.7, 0.2)  # Subtle gradient background
            Rectangle(pos=title_container.pos, size=title_container.size)
        title_shadow = Label(
            text='[b][color=ff0000]Tic Tac Toe[/color][/b]',
            font_size='40sp',
            markup=True,
            color=(0, 0, 0, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            pos=(dp(3), -dp(3))
        )
        title = Label(
            text='[b][color=ffcc00]Tic Tac Toe[/color][/b]',
            font_size='40sp',
            markup=True,
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        title_container.add_widget(title_shadow)
        title_container.add_widget(title)

        # Mode selection section
        mode_label = Label(
            text='[b]Select Game Mode[/b]',
            font_size='18sp',
            markup=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(40)
        )
        mode_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint=(1, None), height=dp(60))
        btn_friend = Button(text='Play with Friend')
        btn_bot = Button(text='Play with Bot')
        btn_friend.bind(on_release=lambda x: self._set_mode("friend", btn_friend))
        btn_bot.bind(on_release=lambda x: self._set_mode("bot", btn_bot))
        self._style_button(btn_friend, (0.2, 0.6, 0.8, 1))
        self._style_button(btn_bot, (0.2, 0.6, 0.8, 1))
        mode_layout.add_widget(btn_friend)
        mode_layout.add_widget(btn_bot)

        # Difficulty selection section
        self.difficulty_label = Label(
            text='[b]Bot Difficulty[/b]',
            font_size='18sp',
            markup=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(40)
        )
        self.difficulty_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint=(1, None), height=dp(60))
        btn_easy = Button(text='Easy')
        btn_medium = Button(text='Medium')
        btn_hard = Button(text='Hard')
        btn_easy.bind(on_release=lambda x: self._set_difficulty("easy", btn_easy))
        btn_medium.bind(on_release=lambda x: self._set_difficulty("medium", btn_medium))
        btn_hard.bind(on_release=lambda x: self._set_difficulty("hard", btn_hard))
        for btn in [btn_easy, btn_medium, btn_hard]:
            self._style_button(btn, (0.4, 0.7, 0.9, 1))
        self.difficulty_layout.add_widget(btn_easy)
        self.difficulty_layout.add_widget(btn_medium)
        self.difficulty_layout.add_widget(btn_hard)

        # Board customization section
        grid_settings_label = Label(
            text='[b]Customize Board[/b]',
            font_size='18sp',
            markup=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(40)
        )
        grid_settings_layout = GridLayout(cols=2, spacing=dp(10), size_hint=(1, None), height=dp(140))
        self.rows_input = TextInput(hint_text='Rows (5)', input_type='number', multiline=False, font_size='14sp', padding=dp(5), size_hint_y=None, height=dp(35))
        self.columns_input = TextInput(hint_text='Columns (5)', input_type='number', multiline=False, font_size='14sp', padding=dp(5), size_hint_y=None, height=dp(35))
        self.win_length_input = TextInput(hint_text='Win Length (4)', input_type='number', multiline=False, font_size='14sp', padding=dp(5), size_hint_y=None, height=dp(35))
        self.obstacles_input = TextInput(hint_text='Obstacles (5)', input_type='number', multiline=False, font_size='14sp', padding=dp(5), size_hint_y=None, height=dp(35))

        grid_settings_layout.add_widget(Label(text='Rows:', color=(1, 1, 1, 1), font_size='14sp'))
        grid_settings_layout.add_widget(self.rows_input)
        grid_settings_layout.add_widget(Label(text='Columns:', color=(1, 1, 1, 1), font_size='14sp'))
        grid_settings_layout.add_widget(self.columns_input)
        grid_settings_layout.add_widget(Label(text='Win Length:', color=(1, 1, 1, 1), font_size='14sp'))
        grid_settings_layout.add_widget(self.win_length_input)
        grid_settings_layout.add_widget(Label(text='Obstacles:', color=(1, 1, 1, 1), font_size='14sp'))
        grid_settings_layout.add_widget(self.obstacles_input)

        # Theme selection section
        theme_label = Label(
            text='[b]Select Element Theme[/b]',
            font_size='18sp',
            markup=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(40)
        )
        spacer = Label(size_hint_y=None, height=dp(20))  # Spacer for separation
        self.theme_layout = GridLayout(cols=5, spacing=dp(10), size_hint=(1, None), height=dp(70))
        themes = [
            ("wood", "🌿 Wood", (0.30, 0.69, 0.31, 1)),  # Forest green
            ("fire", "🔥 Fire", (0.96, 0.26, 0.21, 1)),  # Fiery red
            ("water", "🌊 Water", (0.13, 0.59, 0.95, 1)),  # Ocean blue
            ("earth", "🏔️ Earth", (0.55, 0.43, 0.39, 1)),  # Soil brown
            ("metal", "⚙️ Metal", (0.69, 0.75, 0.78, 1))  # Silver-gray
        ]
        for theme, text, color in themes:
            btn = Button(
                text=f'[b]{text}[/b]',
                markup=True,
                shorten=True,
                shorten_from='right',
                font_name='SegoeUIEmoji',
                size_hint_x=0.18
            )
            btn.bind(on_release=lambda x, t=theme, b=btn: self._set_theme(t, b))
            self._style_button(btn, color)
            btn.bind(on_press=lambda instance, c=color: self._on_theme_press(instance, c))
            self.theme_layout.add_widget(btn)

        # Start game button section
        start_button = Button(
            text='[b][color=ffffff]Start Game[/color][/b]',
            size_hint=(1, None),
            height=dp(80),
            font_size='24sp',
            markup=True,
            background_color=(0, 0, 0, 0)  # Transparent background for custom gradient
        )
        with start_button.canvas.before:
            Color(0.1, 0.8, 0.3, 1)  # Gradient start color (dark green)
            self.start_bg1 = Rectangle(pos=start_button.pos, size=start_button.size)
            Color(1, 0.9, 0.3, 1)  # Gradient end color (bright yellow)
            self.start_bg2 = Rectangle(pos=start_button.pos, size=start_button.size)
        start_button.bind(pos=self._update_start_bg, size=self._update_start_bg)
        start_button.bind(on_release=self._start_game)
        start_button.bind(on_enter=self._on_start_enter)
        start_button.bind(on_leave=self._on_start_leave)
        start_button.bind(on_press=self._on_start_press)
        with start_button.canvas.after:
            Color(1, 1, 0.8, 0.8)  # Glow effect
            self.start_glow = Line(rectangle=(start_button.x, start_button.y, start_button.width, start_button.height), width=4)
            start_button.bind(pos=self._update_start_glow, size=self._update_start_glow)

        # Add widgets to main layout
        main_layout.add_widget(title_container)
        main_layout.add_widget(mode_label)
        main_layout.add_widget(mode_layout)
        main_layout.add_widget(self.difficulty_label)
        main_layout.add_widget(self.difficulty_layout)
        main_layout.add_widget(grid_settings_label)
        main_layout.add_widget(grid_settings_layout)
        main_layout.add_widget(spacer)
        main_layout.add_widget(theme_label)
        main_layout.add_widget(self.theme_layout)
        main_layout.add_widget(start_button)

        self.root.add_widget(main_layout)
        self.add_widget(self.root)

        # Initialize UI state with selection indicators
        self._set_mode("friend", next(btn for btn in mode_layout.children if "Friend" in btn.text))
        self._set_difficulty("medium", next(btn for btn in self.difficulty_layout.children if "Medium" in btn.text))
        self._set_theme("wood", next(btn for btn in self.theme_layout.children if "Wood" in btn.text))
        self._update_bg()  # Ensure initial background is set

    def _style_button(self, button, color):
        """Apply themed styling and animations to buttons."""
        style_round_button(button, color, radius=dp(15))
        button.font_size = '14sp'
        button.bind(on_enter=self._on_button_enter, on_leave=self._on_button_leave, on_press=self._on_button_press)

    def _on_button_enter(self, instance):
        """Scale up and add glow effect on hover by adjusting size."""
        original_size = instance.size
        new_size = (original_size[0] * 1.05, original_size[1] * 1.05)
        Animation(size=new_size, opacity=0.9, t='out_quad', d=0.2).start(instance)

    def _on_button_leave(self, instance):
        """Scale down and remove glow effect when hover ends by resetting size."""
        original_size = instance.size
        Animation(size=original_size, opacity=1.0, t='out_quad', d=0.2).start(instance)

    def _on_button_press(self, instance):
        """Flash effect on button press for non-theme buttons."""
        original_color = instance.background_color
        Animation(background_color=(1, 1, 1, 0.5), d=0.1).start(instance)
        Animation(background_color=original_color, d=0.1).start(instance)

    def _on_theme_press(self, instance, original_color):
        """Custom press effect for theme buttons with size adjustment and color flash."""
        original_size = instance.size
        new_size = (original_size[0] * 0.95, original_size[1] * 0.95)
        Animation(background_color=(1, 1, 1, 0.7), size=new_size, d=0.1).start(instance)
        Animation(background_color=original_color, size=original_size, d=0.1).start(instance)

    def _update_button_selection(self, button, selected_border_color=(1, 1, 0, 1)):
        """Update visual indication of selected button with a border."""
        with button.canvas.after:
            if hasattr(button, 'selection_border'):
                button.canvas.after.remove(button.selection_border)
            if hasattr(button, 'selection_color'):
                button.canvas.after.remove(button.selection_color)
            button.selection_color = Color(*selected_border_color)
            button.selection_border = Line(rectangle=(button.x, button.y, button.width, button.height), width=2, dash_offset=0)
            button.bind(pos=self._update_border_position, size=self._update_border_size)

    def _clear_button_selection(self, button):
        """Clear the selection border and color from a button."""
        if hasattr(button, 'selection_border'):
            button.unbind(pos=self._update_border_position, size=self._update_border_size)
            button.canvas.after.remove(button.selection_border)
            del button.selection_border
        if hasattr(button, 'selection_color'):
            button.canvas.after.remove(button.selection_color)
            del button.selection_color

    def _update_border_position(self, button, pos):
        """Update the border position when button moves."""
        if hasattr(button, 'selection_border'):
            button.selection_border.rectangle = (pos[0], pos[1], button.width, button.height)

    def _update_border_size(self, button, size):
        """Update the border size when button resizes."""
        if hasattr(button, 'selection_border'):
            button.selection_border.rectangle = (button.x, button.y, size[0], size[1])

    def _update_bg(self, *args):
        """Update background with current theme."""
        if hasattr(self, 'bg') and hasattr(self, 'theme_obj'):
            self.theme_obj = Theme(self.current_theme)
            self.bg.source = self.theme_obj.bg
            self.bg.pos = self.root.pos
            self.bg.size = self.root.size

    def _set_mode(self, mode, button):
        """Update game mode and indicate selected mode button."""
        self.current_mode = mode
        if self.selected_mode_btn and self.selected_mode_btn != button:
            self._clear_button_selection(self.selected_mode_btn)
        self._update_button_selection(button)
        self.selected_mode_btn = button
        self.difficulty_label.opacity = 0 if mode == "friend" else 1
        self.difficulty_label.height = dp(0) if mode == "friend" else dp(40)
        self.difficulty_layout.opacity = 0 if mode == "friend" else 1
        self.difficulty_layout.height = dp(0) if mode == "friend" else dp(60)
        self.root.do_layout() if self.root.parent else None

    def _set_difficulty(self, difficulty, button):
        """Set bot difficulty and indicate selected difficulty button."""
        self.current_difficulty = difficulty
        if self.selected_difficulty_btn and self.selected_difficulty_btn != button:
            self._clear_button_selection(self.selected_difficulty_btn)
        self._update_button_selection(button)
        self.selected_difficulty_btn = button

    def _set_theme(self, theme, button):
        """Set theme and indicate selected theme button."""
        if self.selected_theme_btn and self.selected_theme_btn != button:
            self._clear_button_selection(self.selected_theme_btn)
        self.current_theme = theme
        self._update_button_selection(button)
        self.selected_theme_btn = button
        self._update_bg()

    def _start_game(self, *args):
        """Validate inputs and start the game."""
        app = App.get_running_app()
        mode = self.current_mode
        difficulty = self.current_difficulty if mode == "bot" else None
        selected_theme = self.current_theme

        try:
            rows = int(self.rows_input.text) if self.rows_input.text else 5
            columns = int(self.columns_input.text) if self.columns_input.text else 5
            win_length = int(self.win_length_input.text) if self.win_length_input.text else 4
            obstacles = int(self.obstacles_input.text) if self.obstacles_input.text else 5
        except ValueError:
            self._show_error_popup("Input Error", "Please enter valid integers for all fields.")
            return

        if rows <= 0 or columns <= 0 or win_length <= 0 or obstacles < 0:
            self._show_error_popup("Invalid Values", "Values must be greater than 0 (except obstacles, which can be 0).")
            return
        if win_length > rows and win_length > columns:
            self._show_error_popup("Logic Error", "Win Length cannot exceed both Rows and Columns.")
            return
        if obstacles >= (rows * columns):
            self._show_error_popup("Logic Error", "Too many Obstacles; not enough empty cells to play.")
            return

        app.start_game(mode, difficulty, element=selected_theme, rows=rows, cols=columns, win_len=win_length, num_obstacles=obstacles)

    def _show_error_popup(self, title, message):
        """Show themed error popup."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        content.add_widget(Label(text=message, halign='center', color=(1, 1, 1, 1), font_size='14sp'))
        close_btn = Button(text='OK', size_hint=(1, None), height=dp(40))
        self._style_button(close_btn, (0.8, 0.2, 0.2, 1))
        content.add_widget(close_btn)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.3),
            auto_dismiss=False,
            title_color=(1, 1, 1, 1),
            title_size='18sp',
            background=self.theme_obj.bg
        )
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def _update_start_bg(self, instance, value):
        """Update the gradient background of the start button."""
        self.start_bg1.pos = instance.pos
        self.start_bg1.size = instance.size
        self.start_bg2.pos = instance.pos
        self.start_bg2.size = instance.size

    def _update_start_glow(self, instance, value):
        """Update the glow effect of the start button."""
        self.start_glow.rectangle = (instance.x, instance.y, instance.width, instance.height)

    def _on_start_enter(self, instance):
        """Scale up effect when hovering over the start button."""
        Animation(size=(instance.width * 1.1, instance.height * 1.1), duration=0.2, t='out_quad').start(instance)

    def _on_start_leave(self, instance):
        """Scale down effect when leaving the start button."""
        Animation(size=(instance.width / 1.1, instance.height / 1.1), duration=0.2, t='out_quad').start(instance)

    def _on_start_press(self, instance):
        """Flash effect when pressing the start button."""
        Animation(background_color=(1, 1, 1, 0.7), duration=0.1).start(instance)
        Animation(background_color=(0, 0, 0, 0), duration=0.1).start(instance)