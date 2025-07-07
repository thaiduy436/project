import collections
import math
import random
import time
from typing import List, Optional, Tuple

from board import Board

# Constants for Transposition Table node types (optional, but good for robustness)
EXACT, LOWER_BOUND, UPPER_BOUND = 0, 1, 2


class MinimaxAI:
    """Minimax AI implementation for Tic Tac Toe with adjustable difficulty."""

    def __init__(self, difficulty: str = "medium"):
        self.difficulty = difficulty
        self.max_depth = self._get_max_depth()

        # Q-learning for easy mode
        if self.difficulty == "easy":
            self.q_table = collections.defaultdict(lambda: [0.0] * (Board().rows * Board().cols))
            self.learning_rate = 0.1
            self.discount_factor = 0.9
            self.exploration_rate = 0.4
            self.exploration_decay = 0.995
            self.min_exploration_rate = 0.05
            self.last_state = None
            self.last_action = None

        # Giới hạn thời gian tìm kiếm cho mỗi nước đi (giây)
        if self.difficulty == "hard":
            self.search_time_limit = 5.0  # Tăng đáng kể thời gian cho hard để tìm kiếm sâu hơn
        elif self.difficulty == "medium":
            self.search_time_limit = 1.0
        elif self.difficulty == "easy":
            self.search_time_limit = 0.1
        else:  # 'fast' mode or any other, for instant play
            self.search_time_limit = 0.01 # Rất nhỏ để đảm bảo không có suy nghĩ

        self.start_time = 0
        self.transposition_table = {}

    def _get_max_depth(self) -> int:
        """Set search depth based on difficulty."""
        if self.difficulty == "easy":
            return 0  # Q-learning doesn't use depth
        elif self.difficulty == "medium":
            return 4
        elif self.difficulty == "hard":
            return 10  # Tăng độ sâu hơn nữa cho hard, IDS và TT sẽ quản lý
        else: # 'fast' mode
            return 0 # No search depth needed, just pick a random move

    def get_best_move(self, board: Board, ai_symbol: str, human_symbol: str) -> Optional[Tuple[int, int]]:
        """Get the best move using Iterative Deepening Search."""
        if self.difficulty == "easy":
            return self._get_q_learning_move(board, ai_symbol, human_symbol)
        
        # New 'fast' mode: AI plays instantly by picking a random legal move
        if self.difficulty == "fast":
            legal_moves = list(board._legal)
            return random.choice(legal_moves) if legal_moves else None

        self.start_time = time.time()
        best_move_overall = None

        # Determine search radius for the top level of get_best_move
        # Tăng search_radius cho chế độ hard để AI xem xét nhiều nước đi hơn
        search_radius_for_get_best_move = 4 if self.difficulty == "hard" else 2

        # Iterative Deepening Loop
        for current_depth in range(1, self.max_depth + 1):
            if time.time() - self.start_time > self.search_time_limit:
                break  # Time limit exceeded, stop deeper search

            current_best_score = -math.inf
            current_best_move = None

            relevant_moves = self._get_relevant_moves(board, search_radius=search_radius_for_get_best_move) #
            if not relevant_moves:
                relevant_moves = list(board._legal)
                if not relevant_moves:
                    return None

            # Sort moves using heuristic for better Alpha-Beta pruning (most promising moves first)
            relevant_moves.sort(
                key=lambda move: self._evaluate_move_potential(board, move, ai_symbol, human_symbol), reverse=True
            )

            # If a best move was found in a shallower search, prioritize it
            if best_move_overall and best_move_overall in relevant_moves:
                relevant_moves.remove(best_move_overall)
                relevant_moves.insert(0, best_move_overall)

            # Initialize current_best_move if relevant_moves is not empty
            if relevant_moves:
                current_best_move = relevant_moves[0]

            for move in relevant_moves:
                if time.time() - self.start_time > self.search_time_limit:
                    break  # Time limit exceeded during move iteration at current depth

                board.place(move[0], move[1], ai_symbol) #
                score = self._minimax(board, current_depth - 1, -math.inf, math.inf, False, ai_symbol, human_symbol) #
                board.undo_place(move[0], move[1]) #

                if score > current_best_score:
                    current_best_score = score
                    current_best_move = move

            if current_best_move:
                best_move_overall = current_best_move
            else:
                pass

        return best_move_overall if best_move_overall else (random.choice(list(board._legal)) if board._legal else None)

    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, maximizing_player: bool, ai_symbol: str, human_symbol: str) -> float:
        """Minimax algorithm with Alpha-Beta Pruning and Transposition Table."""

        # Check time limit
        if time.time() - self.start_time > self.search_time_limit:
            return self._evaluate_board(board, ai_symbol, human_symbol) #

        # Use Zobrist hash from board object
        board_hash = board.current_zobrist_hash #

        # Transposition table lookup (key includes player to differentiate identical board states for different players)
        tt_key = (board_hash, maximizing_player) #

        if tt_key in self.transposition_table: #
            stored_score, stored_depth, stored_type = self.transposition_table[tt_key] #

            if stored_depth >= depth:
                if stored_type == EXACT: #
                    return stored_score
                elif stored_type == LOWER_BOUND and stored_score > alpha: #
                    alpha = stored_score
                elif stored_type == UPPER_BOUND and stored_score < beta: #
                    beta = stored_score

                if alpha >= beta: #
                    return stored_score

        # Terminal conditions (win, loss, draw, max depth)
        if board.has_winner(ai_symbol): #
            return 1000000000 + depth
        if board.has_winner(human_symbol): #
            return -1000000000 - depth
        if board.is_full(): #
            return 0
        if depth == 0:
            return self._evaluate_board(board, ai_symbol, human_symbol) #

        # Determine search radius for deeper minimax calls
        # Tăng search_radius cho các cấp độ sâu hơn của minimax trong chế độ hard
        search_radius_for_minimax = 3 if self.difficulty == "hard" else 1 
        legal_moves_for_eval = self._get_relevant_moves(board, search_radius=search_radius_for_minimax) #
        if not legal_moves_for_eval:
            legal_moves_for_eval = list(board._legal)
            if not legal_moves_for_eval:
                return self._evaluate_board(board, ai_symbol, human_symbol) #

        # Sort moves for better pruning
        if maximizing_player:
            legal_moves_for_eval.sort(
                key=lambda move: self._evaluate_move_potential(board, move, ai_symbol, human_symbol), reverse=True
            )
        else:
            legal_moves_for_eval.sort(
                key=lambda move: self._evaluate_move_potential(board, move, human_symbol, ai_symbol), reverse=True
            )

        best_score_at_node = -math.inf if maximizing_player else math.inf
        node_type = EXACT

        for move in legal_moves_for_eval:
            if time.time() - self.start_time > self.search_time_limit:
                return self._evaluate_board(board, ai_symbol, human_symbol) #

            board.place(move[0], move[1], ai_symbol if maximizing_player else human_symbol) #

            eval_score = self._minimax(board, depth - 1, alpha, beta, not maximizing_player, ai_symbol, human_symbol) #

            board.undo_place(move[0], move[1]) #

            if maximizing_player:
                best_score_at_node = max(best_score_at_node, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    node_type = LOWER_BOUND #
                    break
            else:  # minimizing_player
                best_score_at_node = min(best_score_at_node, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    node_type = UPPER_BOUND #
                    break

        # Store result in transposition table
        self.transposition_table[tt_key] = (best_score_at_node, depth, node_type) #
        return best_score_at_node

    def _evaluate_board(self, board: Board, ai_symbol: str, human_symbol: str) -> float:
        """
        Improved evaluation function, heavily prioritizing immediate threats and blocks.
        """
        score = 0

        # Weights for different lengths of lines
        weights = {}
        for i in range(1, board._win_len):  # Corrected: board.win_len -> board._win_len
            weights[i] = 10 ** (i * 2)

        # Special, very high weights for immediate win threats (N-1) and strong threats (N-2)
        threat_score_n_minus_1 = 100_000_000 #
        threat_score_n_minus_2 = 10_000_000 #

        directions = [(1, 0), (0, 1), (1, 1), (1, -1)] #

        for r in range(board.rows): #
            for c in range(board.cols): #
                if board._grid[r][c] == Board.OBSTACLE: #
                    continue

                for dr, dc in directions: #
                    # Evaluate lines for AI
                    ai_count = 0
                    human_count = 0
                    empty_count = 0

                    for k in range(board._win_len):  # Corrected: board.win_len -> board._win_len
                        nr, nc = r + k * dr, c + k * dc

                        if not (0 <= nr < board.rows and 0 <= nc < board.cols):
                            ai_count = -math.inf
                            break

                        cell_val = board._grid[nr][nc] #

                        if cell_val == ai_symbol: #
                            ai_count += 1
                        elif cell_val == human_symbol: #
                            human_count += 1
                            break
                        elif cell_val == Board.EMPTY: #
                            empty_count += 1
                        elif cell_val == Board.OBSTACLE: #
                            ai_count = -math.inf
                            break

                    if human_count == 0 and ai_count > 0: #
                        if ai_count + empty_count >= board._win_len:  # Corrected: board.win_len -> board._win_len
                            if ai_count == board._win_len - 1 and empty_count >= 1:  # Corrected: board.win_len -> board._win_len
                                score += threat_score_n_minus_1
                            elif ai_count == board._win_len - 2 and empty_count >= 2:  # Corrected: board.win_len -> board._win_len
                                score += threat_score_n_minus_2
                            else:
                                score += weights.get(ai_count, 0)

                    # Evaluate lines for Human (for defensive scoring - negative impact)
                    ai_count = 0
                    human_count = 0
                    empty_count = 0

                    for k in range(board._win_len):  # Corrected: board.win_len -> board._win_len
                        nr, nc = r + k * dr, c + k * dc

                        if not (0 <= nr < board.rows and 0 <= nc < board.cols):
                            human_count = -math.inf
                            break

                        cell_val = board._grid[nr][nc] #

                        if cell_val == human_symbol: #
                            human_count += 1
                        elif cell_val == ai_symbol: #
                            ai_count += 1
                            break
                        elif cell_val == Board.EMPTY: #
                            empty_count += 1
                        elif cell_val == Board.OBSTACLE: #
                            human_count = -math.inf
                            break

                    if ai_count == 0 and human_count > 0: #
                        if human_count + empty_count >= board._win_len:  # Corrected: board.win_len -> board._win_len
                            if human_count == board._win_len - 1 and empty_count >= 1:  # Corrected: board.win_len -> board._win_len
                                score -= threat_score_n_minus_1 * 1.5 #
                            elif human_count == board._win_len - 2 and empty_count >= 2:  # Corrected: board.win_len -> board._win_len
                                score -= threat_score_n_minus_2 * 1.5 #
                            else:
                                score -= weights.get(human_count, 0) * 1.5 #

        return score

    def _evaluate_move_potential(self, board: Board, move: Tuple[int, int], player_symbol: str, opponent_symbol: str) -> float:
        """
        Evaluates the potential of a single move without full minimax search.
        Used for initial move ordering. Prioritizes moves that immediately
        create lines, block opponent lines, or are near existing pieces/center.
        """
        r, c = move

        if not board.is_empty(r, c):
            return -math.inf

        board.place(r, c, player_symbol) #
        score = self._evaluate_board(board, player_symbol, opponent_symbol) #
        board.undo_place(r, c) #

        # Bonus for adjacency to existing pieces
        adj_bonus = 0
        directions_adj = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)] #
        for dr, dc in directions_adj: #
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < board.rows
                and 0 <= nc < board.cols
                and (board._grid[nr][nc] != Board.EMPTY and board._grid[nr][nc] != Board.OBSTACLE)
            ):
                adj_bonus += 1

        score += adj_bonus * 5 #

        # Bonus for moves near the center, especially on large boards
        center_row = board.rows // 2 #
        center_col = board.cols // 2 #
        dist_from_center = abs(r - center_row) + abs(c - center_col) #
        max_dist = (board.rows // 2) + (board.cols // 2) #
        if max_dist > 0:
            center_bonus = (max_dist - dist_from_center) / max_dist * 50 #
            score += center_bonus

        return score

    def _get_relevant_moves(self, board: Board, search_radius: int = 2) -> List[Tuple[int, int]]:
        """
        Returns a list of empty cells that are adjacent to already placed pieces
        within a given search_radius. Handles empty board as well.
        """
        relevant_moves = set()

        occupied_cells = sum(
            1
            for r in range(board.rows)
            for c in range(board.cols)
            if board._grid[r][c] != Board.EMPTY and board._grid[r][c] != Board.OBSTACLE
        )

        total_playable_cells = board.rows * board.cols - board._num_obstacles

        if total_playable_cells > 0 and occupied_cells / total_playable_cells < 0.1:
            center_row = board.rows // 2
            center_col = board.cols // 2
            initial_search_radius = max(2, min(board.rows, board.cols) // 4)
            for r_offset in range(-initial_search_radius, initial_search_radius + 1):
                for c_offset in range(-initial_search_radius, initial_search_radius + 1):
                    nr, nc = center_row + r_offset, center_col + c_offset
                    if 0 <= nr < board.rows and 0 <= nc < board.cols and board.is_empty(nr, nc):
                        relevant_moves.add((nr, nc))

            if relevant_moves:
                return sorted(list(relevant_moves))
            else:
                return sorted(list(board._legal)) if board._legal else []

        for r in range(board.rows):
            for c in range(board.cols):
                cell_val = board._grid[r][c]
                if cell_val != Board.EMPTY and cell_val != Board.OBSTACLE:
                    for row_offset in range(-search_radius, search_radius + 1):
                        for col_offset in range(-search_radius, search_radius + 1):  # Corrected loop
                            nr, nc = r + row_offset, c + col_offset
                            if 0 <= nr < board.rows and 0 <= nc < board.cols and board.is_empty(nr, nc):
                                relevant_moves.add((nr, nc))

        if not relevant_moves:
            return sorted(list(board._legal)) if board._legal else []

        return sorted(list(relevant_moves))

    # Q-learning related methods (keep as is for easy mode)
    def _get_state_representation(self, board: Board) -> Tuple[str, ...]:
        """Convert board state to hashable tuple for Q-table."""
        return tuple(cell for row in board._grid for cell in row)

    def _get_q_learning_move(self, board: Board, ai_symbol: str, human_symbol: str) -> Optional[Tuple[int, int]]:
        state = self._get_state_representation(board)
        legal_moves = list(board._legal)

        if not legal_moves:
            return None

        # Epsilon-greedy strategy
        if random.uniform(0, 1) < self.exploration_rate:
            move = random.choice(legal_moves)
        else:
            q_values = self.q_table[state]

            legal_q_values = []
            legal_actions = []
            for r, c in legal_moves:
                action_idx = r * board.cols + c
                legal_q_values.append(q_values[action_idx])
                legal_actions.append((r, c))

            if not legal_actions:
                move = random.choice(list(board._legal))
            else:
                max_q_value = -math.inf
                best_legal_moves = []
                for i, qv in enumerate(legal_q_values):
                    if qv > max_q_value:
                        max_q_value = qv
                        best_legal_moves = [legal_actions[i]]
                    elif qv == max_q_value:
                        best_legal_moves.append(legal_actions[i])
                move = random.choice(best_legal_moves)

        self.last_state = state
        self.last_action = move
        self.exploration_rate = max(self.min_exploration_rate, self.exploration_rate * self.exploration_decay)
        return move

    def update_q_table(self, old_board: Board, new_board: Board, ai_symbol: str, human_symbol: str, reward: float):
        """Update Q-table. (Requires external call from controller for full learning)"""
        if self.difficulty != "easy" or self.last_state is None or self.last_action is None:
            return

        old_state = self.last_state
        action_row, action_col = self.last_action
        action_idx = action_row * new_board.cols + action_col

        new_state = self._get_state_representation(new_board)
        current_q_value = self.q_table[old_state][action_idx]

        next_legal_moves_indices = []
        for r, c in new_board._legal:
            next_legal_moves_indices.append(r * new_board.cols + c)

        if next_legal_moves_indices:
            max_next_q = max(self.q_table[new_state][idx] for idx in next_legal_moves_indices)
        else:
            max_next_q = 0.0

        updated_q_value = current_q_value + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q_value
        )
        self.q_table[old_state][action_idx] = updated_q_value

        self.last_state = None
        self.last_action = None

    def get_reward(self, board: Board, ai_symbol: str, human_symbol: str) -> float:
        if board.has_winner(ai_symbol):
            return 1.0
        if board.has_winner(human_symbol):
            return -1.0
        if board.is_full():
            return 0.5
        return 0.0