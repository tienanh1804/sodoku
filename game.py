import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  
import random
import time
import threading

class SudokuGame:
    def __init__(self, root):
        self.root = root
        self.size = 9
        self.time_limit = 300
        self.remaining_time = self.time_limit
        self.difficulty = "Easy"
        self.cells = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.solution = None
        self.running = False
        self.timer_thread = None

        # Khởi tạo giao diện chính
        self.create_main_menu()

    def create_main_menu(self):
        self.root.title("Sudoku Game")
        self.clear_window()

        # Tiêu đề
        title_label = tk.Label(self.root, text="Sudoku Game", font=("Arial", 24))
        title_label.pack(pady=20)

        # Nút chơi
        play_button = tk.Button(self.root, text="Chơi", command=self.show_difficulty_selection, font=("Arial", 16))
        play_button.pack(pady=20)

    def show_difficulty_selection(self):
        self.clear_window()

        # Tiêu đề
        difficulty_label = tk.Label(self.root, text="Chọn độ khó", font=("Arial", 18))
        difficulty_label.pack(pady=20)

        # Các nút độ khó
        difficulties = ["Dễ", "Trung bình", "Khó", "Rất khó"]
        for difficulty in difficulties:
            button = tk.Button(self.root, text=difficulty, font=("Arial", 14), command=lambda d=difficulty: self.start_game(d))
            button.pack(pady=5)

        # Nút quay lại
        back_button = tk.Button(self.root, text="Quay lại", command=self.create_main_menu, font=("Arial", 14))
        back_button.pack(pady=20)

    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.remaining_time = self.time_limit
        self.running = True

        self.clear_window()
        self.create_board()
        self.generate_sudoku_board()

        # Bộ đếm giờ
        self.timer_label = tk.Label(self.root, text="Thời gian còn lại: 05:00", font=("Arial", 14))
        self.timer_label.pack(pady=10)
        self.start_timer()

        # Nút chức năng
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        check_button = tk.Button(button_frame, text="Kiểm tra", command=self.check_solution, font=("Arial", 14))
        check_button.grid(row=0, column=0, padx=10)

        hint_button = tk.Button(button_frame, text="Gợi ý", command=self.hint, font=("Arial", 14))
        hint_button.grid(row=0, column=1, padx=10)

        next_button = tk.Button(button_frame, text="Màn kế tiếp", command=self.next_level, font=("Arial", 14))
        next_button.grid(row=0, column=2, padx=10)

        back_button = tk.Button(button_frame, text="Quay lại", command=self.create_main_menu, font=("Arial", 14))
        back_button.grid(row=0, column=3, padx=10)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_board(self):
        frame = tk.Frame(self.root, bg="black")
        frame.pack(pady=20)

        for i in range(self.size):
            for j in range(self.size):
                cell_frame = tk.Frame(
                    frame, 
                    bg="white", 
                    highlightbackground="black",
                    highlightthickness=2 if (i % 3 == 0 or j % 3 == 0) else 1,
                    width=50, height=50
                )
                cell_frame.grid(row=i, column=j, padx=1, pady=1)

                cell = tk.Entry(
                    cell_frame, 
                    width=2, 
                    font=('Arial', 18), 
                    justify='center', 
                    bg="lightyellow"
                )
                cell.pack(expand=True, fill="both")
                self.cells[i][j] = cell

    def generate_sudoku_board(self):
        self.solution = self.solve_sudoku()
        self.board = [[self.solution[i][j] for j in range(self.size)] for i in range(self.size)]

        cells_to_remove = self.get_cells_to_remove_based_on_difficulty()
        for cell in cells_to_remove:
            i, j = cell
            self.board[i][j] = ''
        
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != '':
                    self.cells[i][j].insert(0, str(self.board[i][j]))
                    self.cells[i][j].config(state='disabled')

    def get_cells_to_remove_based_on_difficulty(self):
        if self.difficulty == "Dễ":
            cells_to_remove = 30
        elif self.difficulty == "Trung bình":
            cells_to_remove = 40
        elif self.difficulty == "Khó":
            cells_to_remove = 50
        else:
            cells_to_remove = 60
        return random.sample([(i, j) for i in range(self.size) for j in range(self.size)], cells_to_remove)

    def solve_sudoku(self):
        return [[(i * 3 + i // 3 + j) % 9 + 1 for j in range(9)] for i in range(9)]

    def start_timer(self):
        def countdown():
            while self.remaining_time > 0 and self.running:
                mins, secs = divmod(self.remaining_time, 60)
                self.timer_label.config(text="Thời gian còn lại: {:02d}:{:02d}".format(mins, secs))
                time.sleep(1)
                self.remaining_time -= 1
            if self.remaining_time == 0:
                self.running = False
                messagebox.showinfo("Hết giờ", "Bạn đã hết thời gian!")
                self.show_end_menu()

        self.timer_thread = threading.Thread(target=countdown)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def show_end_menu(self):
        self.clear_window()

        message = tk.Label(self.root, text="Thời gian đã hết!", font=("Arial", 18))
        message.pack(pady=20)

        retry_button = tk.Button(self.root, text="Chơi lại", command=lambda: self.start_game(self.difficulty), font=("Arial", 14))
        retry_button.pack(pady=10)

        main_menu_button = tk.Button(self.root, text="Quay lại màn hình chính", command=self.create_main_menu, font=("Arial", 14))
        main_menu_button.pack(pady=10)

    def hint(self):
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if not self.cells[i][j].get()]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.cells[i][j].insert(0, str(self.solution[i][j]))
            self.cells[i][j].config(state='disabled')
        else:
            messagebox.showinfo("Gợi ý", "Không còn ô trống để gợi ý!")

    def check_solution(self):
        correct = True
        for i in range(self.size):
            for j in range(self.size):
                user_input = self.cells[i][j].get()
                if user_input and user_input.isdigit() and int(user_input) == self.solution[i][j]:
                    self.cells[i][j].config(bg="lightgreen")
                else:
                    correct = False
                    self.cells[i][j].config(bg="lightcoral")

        if correct:
            messagebox.showinfo("Chúc mừng", "Bạn đã hoàn thành màn chơi!")
        else:
            self.root.after(2000, self.reset_cell_colors)

    def reset_cell_colors(self):
        for i in range(self.size):
            for j in range(self.size):
                self.cells[i][j].config(bg="white")

    def next_level(self):
        difficulty_levels = ["Dễ", "Trung bình", "Khó", "Rất khó"]
        current_level = difficulty_levels.index(self.difficulty)
        self.difficulty = difficulty_levels[min(current_level + 1, len(difficulty_levels) - 1)]
        self.start_game(self.difficulty)

root = tk.Tk()
game = SudokuGame(root)
root.mainloop()
