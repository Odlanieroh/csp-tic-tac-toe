"""
Tic Tac Toe Game using Constraint Satisfaction Problem (CSP) and GUI
=====================================================================

This implementation uses CSP principles to model the game:
- Variables: 9 board cells (0-8)
- Domain: {X, O, empty}
- Constraints:
    1. Each cell can hold only one value
    2. Players alternate turns
    3. Win condition: 3 in a row/column/diagonal
    4. No move on occupied cells
    
The AI uses CSP with constraint propagation and Minimax to find optimal moves.
"""

import tkinter as tk
from tkinter import font


class TicTacToeCSP:
    """
    Constraint Satisfaction Problem formulation for Tic Tac Toe.
    
    Variables: cells 0..8
    Domain: {'X', 'O', ' '}
    Constraints:
        - Unary: cell must be empty to place a mark
        - Binary: alternating turns
        - Global: winning lines (rows, cols, diagonals)
    """
    
    # All winning lines (rows, columns, diagonals) - these are our CSP constraints
    WINNING_LINES = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],   # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],   # columns
        [0, 4, 8], [2, 4, 6]                # diagonals
    ]
    
    def __init__(self):
        # Initialize 9 variables (cells), each with domain {'X', 'O', ' '}
        self.board = [' '] * 9
        self.current_player = 'X'  # Human starts as X
    
    def get_legal_moves(self, board):
        """Return cells that satisfy the 'empty' unary constraint."""
        return [i for i, cell in enumerate(board) if cell == ' ']
    
    def check_winner(self, board):
        """Check global constraint: any winning line completed?"""
        for line in self.WINNING_LINES:
            a, b, c = line
            if board[a] == board[b] == board[c] != ' ':
                return board[a], line
        if ' ' not in board:
            return 'Tie', None
        return None, None
    
    def is_terminal(self, board):
        """Check if the state violates no constraints but has no more moves."""
        winner, _ = self.check_winner(board)
        return winner is not None
    
    # ---------- CSP-based heuristic evaluation ----------
    def evaluate_line(self, board, line, player):
        """
        Evaluate a single line using CSP constraint logic.
        Count how close we are to satisfying the 'three-in-a-row' constraint.
        """
        opponent = 'O' if player == 'X' else 'X'
        values = [board[i] for i in line]
        
        player_count = values.count(player)
        opponent_count = values.count(opponent)
        
        # If opponent already in line, this line cannot satisfy our winning constraint
        if opponent_count > 0 and player_count > 0:
            return 0
        if player_count == 3:
            return 100
        if player_count == 2 and opponent_count == 0:
            return 10
        if player_count == 1 and opponent_count == 0:
            return 1
        if opponent_count == 3:
            return -100
        if opponent_count == 2 and player_count == 0:
            return -10
        if opponent_count == 1 and player_count == 0:
            return -1
        return 0
    
    def evaluate_board(self, board, player):
        """Sum the satisfaction of constraints across all winning lines."""
        return sum(self.evaluate_line(board, line, player) for line in self.WINNING_LINES)
    
    # ---------- Constraint Propagation: Find forced moves ----------
    def find_forced_move(self, board, player):
        """
        Apply constraint propagation (like AC-3 arc consistency) to find
        a cell that is forced by the current constraints:
        1. Winning move (complete the row/col/diag constraint)
        2. Blocking move (prevent opponent from satisfying their constraint)
        """
        opponent = 'O' if player == 'X' else 'X'
        
        # Check for a winning move first (satisfies our goal constraint immediately)
        for move in self.get_legal_moves(board):
            test_board = board.copy()
            test_board[move] = player
            winner, _ = self.check_winner(test_board)
            if winner == player:
                return move, "win"
        
        # Block opponent's winning move (prevents violation of our goal)
        for move in self.get_legal_moves(board):
            test_board = board.copy()
            test_board[move] = opponent
            winner, _ = self.check_winner(test_board)
            if winner == opponent:
                return move, "block"
        
        return None, None
    
    # ---------- Minimax with Alpha-Beta (for optimal play) ----------
    def minimax(self, board, depth, is_maximizing, alpha, beta, ai_player):
        """
        Minimax search through the CSP state space with alpha-beta pruning.
        Used as a complete search when constraint propagation is insufficient.
        """
        human_player = 'O' if ai_player == 'X' else 'X'
        winner, _ = self.check_winner(board)
        
        if winner == ai_player:
            return 10 - depth
        if winner == human_player:
            return depth - 10
        if winner == 'Tie':
            return 0
        
        if is_maximizing:
            max_eval = -float('inf')
            for move in self.get_legal_moves(board):
                board[move] = ai_player
                eval_score = self.minimax(board, depth + 1, False, alpha, beta, ai_player)
                board[move] = ' '
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_legal_moves(board):
                board[move] = human_player
                eval_score = self.minimax(board, depth + 1, True, alpha, beta, ai_player)
                board[move] = ' '
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
    
    def get_best_move(self, board, ai_player='O'):
        """
        Get the best AI move using a 2-tier CSP strategy:
        1. Constraint propagation (fast, finds forced moves)
        2. Minimax search (complete search when no forced move exists)
        """
        # Tier 1: Try constraint propagation for forced moves
        forced_move, reason = self.find_forced_move(board, ai_player)
        if forced_move is not None:
            return forced_move, reason
        
        # Tier 2: Full minimax search
        best_score = -float('inf')
        best_move = None
        for move in self.get_legal_moves(board):
            board[move] = ai_player
            score = self.minimax(board, 0, False, -float('inf'), float('inf'), ai_player)
            board[move] = ' '
            if score > best_score:
                best_score = score
                best_move = move
        return best_move, "optimal"


class TicTacToeGUI:
    """Tkinter GUI for the Tic Tac Toe game."""
    
    # Color palette
    BG_COLOR = "#1e1e2e"
    BOARD_COLOR = "#313244"
    BUTTON_COLOR = "#45475a"
    BUTTON_HOVER = "#585b70"
    X_COLOR = "#f38ba8"       # pink
    O_COLOR = "#89b4fa"       # blue
    WIN_COLOR = "#a6e3a1"     # green highlight
    TEXT_COLOR = "#cdd6f4"
    ACCENT = "#f9e2af"         # yellow
    
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe — CSP AI")
        self.root.configure(bg=self.BG_COLOR)
        self.root.resizable(False, False)
        
        self.csp = TicTacToeCSP()
        self.human = 'X'
        self.ai = 'O'
        self.game_over = False
        self.scores = {'You': 0, 'AI': 0, 'Ties': 0}
        
        self.pending_ai = None
        self.buttons = []
        self._build_ui()
    
    def _build_ui(self):
        # Title
        title_font = font.Font(family="Helvetica", size=22, weight="bold")
        title = tk.Label(
            self.root, text="Tic Tac Toe",
            font=title_font, fg=self.ACCENT, bg=self.BG_COLOR
        )
        title.pack(pady=(15, 2))
        
        subtitle = tk.Label(
            self.root, text="Constraint Satisfaction AI",
            font=("Helvetica", 10, "italic"),
            fg=self.TEXT_COLOR, bg=self.BG_COLOR
        )
        subtitle.pack(pady=(0, 10))
        
        # Status label
        self.status_label = tk.Label(
            self.root, text="Your turn (X)",
            font=("Helvetica", 13, "bold"),
            fg=self.TEXT_COLOR, bg=self.BG_COLOR
        )
        self.status_label.pack(pady=5)
        
        # Board frame
        board_frame = tk.Frame(self.root, bg=self.BOARD_COLOR, padx=8, pady=8)
        board_frame.pack(padx=20, pady=10)
        
        cell_font = font.Font(family="Helvetica", size=36, weight="bold")
        for i in range(9):
            row, col = divmod(i, 3)
            btn = tk.Button(
                board_frame, text=" ",
                font=cell_font, width=3, height=1,
                bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR,
                activebackground=self.BUTTON_HOVER,
                relief="flat", bd=0,
                command=lambda idx=i: self.human_move(idx)
            )
            btn.grid(row=row, column=col, padx=4, pady=4)
            btn.bind("<Enter>", lambda e, b=btn: self._on_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._on_hover(b, False))
            self.buttons.append(btn)
        
        # Scoreboard
        score_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        score_frame.pack(pady=10)
        
        self.score_label = tk.Label(
            score_frame,
            text=self._score_text(),
            font=("Helvetica", 11),
            fg=self.TEXT_COLOR, bg=self.BG_COLOR
        )
        self.score_label.pack()
        
        # Info label (shows AI reasoning)
        self.info_label = tk.Label(
            self.root, text="",
            font=("Helvetica", 9, "italic"),
            fg=self.ACCENT, bg=self.BG_COLOR
        )
        self.info_label.pack(pady=2)
        
        # Control buttons
        btn_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        btn_frame.pack(pady=12)
        
        new_game_btn = tk.Button(
            btn_frame, text="New Game",
            font=("Helvetica", 11, "bold"),
            bg=self.ACCENT, fg=self.BG_COLOR,
            activebackground="#f5c77e",
            relief="flat", padx=18, pady=6,
            command=self.reset_game
        )
        new_game_btn.pack(side="left", padx=5)
        
        reset_score_btn = tk.Button(
            btn_frame, text="Reset Score",
            font=("Helvetica", 11),
            bg=self.BUTTON_COLOR, fg=self.TEXT_COLOR,
            activebackground=self.BUTTON_HOVER,
            relief="flat", padx=18, pady=6,
            command=self.reset_scores
        )
        reset_score_btn.pack(side="left", padx=5)
    
    def _on_hover(self, btn, entering):
        if btn['state'] == 'disabled':
            return
        btn.config(bg=self.BUTTON_HOVER if entering else self.BUTTON_COLOR)
    
    def _score_text(self):
        return f"  You: {self.scores['You']}   |   AI: {self.scores['AI']}   |   Ties: {self.scores['Ties']}  "
    
    def human_move(self, idx):
        if self.game_over or self.csp.board[idx] != ' ':
            return
        
        self._place(idx, self.human, self.X_COLOR)
        winner, line = self.csp.check_winner(self.csp.board)
        
        if winner:
            self._end_game(winner, line)
            return
        
        self.status_label.config(text="AI is thinking…")
        self.info_label.config(text="")
        # Disable board during AI turn
        for b in self.buttons:
            b.config(state='disabled')
        self.pending_ai = self.root.after(400, self.ai_move)
    
    def ai_move(self):
        self.pending_ai = None
        if self.game_over:
            return
        move, reason = self.csp.get_best_move(self.csp.board, self.ai)
        
        # Map reason to human-readable explanation
        reason_text = {
            "win": "AI found a winning move (constraint satisfied)",
            "block": "AI blocked your threat (constraint propagation)",
            "optimal": "AI used minimax search over CSP state space"
        }.get(reason, "AI made a move")
        
        self._place(move, self.ai, self.O_COLOR)
        self.info_label.config(text=reason_text)
        
        winner, line = self.csp.check_winner(self.csp.board)
        if winner:
            self._end_game(winner, line)
            return
        
        # Re-enable empty cells
        for i, b in enumerate(self.buttons):
            if self.csp.board[i] == ' ':
                b.config(state='normal')
        
        self.status_label.config(text="Your turn (X)")
    
    def _place(self, idx, player, color):
        self.csp.board[idx] = player
        self.buttons[idx].config(
            text=player, fg=color, state='disabled',
            disabledforeground=color
        )
    
    def _end_game(self, winner, line):
        self.game_over = True
        for b in self.buttons:
            b.config(state='disabled')
        
        if winner == self.human:
            self.scores['You'] += 1
            msg = "You won! 🎉"
        elif winner == self.ai:
            self.scores['AI'] += 1
            msg = "AI wins!"
        else:
            self.scores['Ties'] += 1
            msg = "It's a tie!"
        
        # Highlight winning line
        if line:
            for i in line:
                self.buttons[i].config(
                    bg=self.WIN_COLOR,
                    disabledforeground=self.BG_COLOR
                )
        
        self.status_label.config(text=msg)
        self.score_label.config(text=self._score_text())
        self.info_label.config(text="Click 'New Game' to play again")
    
    def reset_game(self):
        if self.pending_ai is not None:
            self.root.after_cancel(self.pending_ai)
            self.pending_ai = None
        self.csp = TicTacToeCSP()
        self.game_over = False
        for b in self.buttons:
            b.config(
                text=" ", bg=self.BUTTON_COLOR,
                fg=self.TEXT_COLOR, state='normal',
                disabledforeground=self.TEXT_COLOR
            )
        self.status_label.config(text="Your turn (X)")
        self.info_label.config(text="")
    
    def reset_scores(self):
        self.scores = {'You': 0, 'AI': 0, 'Ties': 0}
        self.score_label.config(text=self._score_text())
        self.reset_game()


def main():
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()