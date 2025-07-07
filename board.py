import random
from typing import List, Tuple, Set

class Board:
    """Game model: holds state and enforces the rules."""

    EMPTY, OBSTACLE = ".", "#"

    def __init__(
        self,
        rows: int = 5,
        cols: int = 5,
        win_len: int = 4,
        num_obstacles: int = 5,
    ) -> None:
        self._rows = rows
        self._cols = cols
        self._win_len = win_len
        self._num_obstacles = num_obstacles
        
        self._zobrist_keys = {} # Store random numbers for Zobrist hashing
        self._current_zobrist_hash = 0 # Current hash of the board
        self._initialize_zobrist_keys() # New method to init keys
        
        self.reset()

    # -------- public API --------------------------------------------------

    @property
    def rows(self) -> int: return self._rows

    @property
    def cols(self) -> int: return self._cols

    @property
    def current_zobrist_hash(self) -> int:
        return self._current_zobrist_hash

    def reset(self) -> None:
        """Clear the board and randomly place fresh obstacles."""
        self._grid: List[List[str]] = [
            [self.EMPTY for _ in range(self._cols)] for _ in range(self._rows)
        ]
        # Khởi tạo lại _legal để chứa tất cả các ô trống
        self._legal: Set[Tuple[int, int]] = set()
        for r in range(self._rows):
            for c in range(self._cols):
                self._legal.add((r, c))

        self._current_zobrist_hash = 0 # Reset hash
        # Tính toán hash ban đầu cho bàn cờ trống
        for r in range(self._rows):
            for c in range(self._cols):
                self._current_zobrist_hash ^= self._zobrist_keys[Board.EMPTY][(r, c)]

        self._place_obstacles()

    @property
    def legal(self) -> Set[Tuple[int, int]]:
        """Returns a set of coordinates for legal moves."""
        return self._legal

    def is_legal(self, row: int, col: int) -> bool:
        """Checks if a given cell (row, col) is a legal move."""
        return (row, col) in self._legal

    def is_empty(self, row: int, col: int) -> bool:
        """Checks if the cell at (row, col) is empty."""
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            return False
        return self._grid[row][col] == Board.EMPTY

    def place(self, row: int, col: int, symbol: str) -> bool:
        """Attempts to place a symbol. Returns True on success, False otherwise."""
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            return False
        if self._grid[row][col] != self.EMPTY:
            return False

        # Update Zobrist hash: XOR out EMPTY, XOR in new symbol
        self._current_zobrist_hash ^= self._zobrist_keys[Board.EMPTY][(row, col)]
        self._current_zobrist_hash ^= self._zobrist_keys[symbol][(row, col)]

        self._grid[row][col] = symbol
        self._legal.remove((row, col)) # Remove from legal moves
        return True
    
    def undo_place(self, row: int, col: int) -> None: # Đã bỏ tham số 'symbol'
        """Undoes a move, reverting a cell to EMPTY and updating Zobrist hash."""
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            return 

        # Lấy biểu tượng vừa được đặt tại vị trí này
        # Điều này giả định undo_place được gọi ngay sau một thao tác place
        # Và ô đó không trống
        if self._grid[row][col] != Board.EMPTY:
            old_symbol = self._grid[row][col] # Lấy biểu tượng hiện tại trong ô

            # Cập nhật hàm băm Zobrist: XOR biểu tượng cũ ra, XOR EMPTY vào
            self._current_zobrist_hash ^= self._zobrist_keys[old_symbol][(row, col)]
            self._current_zobrist_hash ^= self._zobrist_keys[Board.EMPTY][(row, col)]
            
            self._grid[row][col] = Board.EMPTY
            self._legal.add((row, col)) # Thêm ô trở lại các nước đi hợp lệ

    def is_full(self) -> bool:
        """Are there any empty cells left?"""
        return not bool(self._legal) # Return True if _legal is empty

    def has_winner(self, symbol: str) -> bool:
        """Checks if the given symbol has won."""
        # Check rows, columns, and diagonals
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # H, V, D, Anti-D
        for i in range(self._rows):
            for j in range(self._cols):
                if self._grid[i][j] != symbol:
                    continue
                for di, dj in directions:
                    count, x, y = 1, i + di, j + dj
                    while (
                        0 <= x < self._rows
                        and 0 <= y < self._cols
                        and self._grid[x][y] == symbol
                    ):
                        count += 1
                        if count >= self._win_len:
                            return True
                        x += di
                        y += dj
        return False

    # -------- internal helpers --------------------------------------------
    def _initialize_zobrist_keys(self):
        """Generates random 64-bit integers for Zobrist hashing."""
        self._zobrist_keys[Board.EMPTY] = {}
        self._zobrist_keys["X"] = {}
        self._zobrist_keys["O"] = {}
        for r in range(self._rows):
            for c in range(self._cols):
                self._zobrist_keys[Board.EMPTY][(r, c)] = random.getrandbits(64)
                self._zobrist_keys["X"][(r, c)] = random.getrandbits(64)
                self._zobrist_keys["O"][(r, c)] = random.getrandbits(64)


    def _place_obstacles(self) -> None:
        placed = 0
        while placed < self._num_obstacles:
            i = random.randrange(self._rows)
            j = random.randrange(self._cols)
            if self._grid[i][j] == self.EMPTY:
                self._grid[i][j] = self.OBSTACLE
                self._legal.remove((i, j)) # Obstacles are not legal moves
                # Zobrist hash for obstacles is not typically tracked,
                # as they are static. Only dynamic pieces affect the hash.
                placed += 1