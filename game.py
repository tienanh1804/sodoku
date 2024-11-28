import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pygame
import random
import threading
import time


class SudokuGame:
    def __init__(self, root):
        self.root = root
        self.size = 9
        self.time_limit = 300
        self.remaining_time = self.time_limit
        self.difficulty = "Dễ"
        self.cells = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.board = None
        self.solution = None
        self.running = False

        # Khởi tạo âm thanh
        pygame.mixer.init()
        self.sounds = {
            "correct": "correct.mp3",
            "wrong": "wrong.mp3",
            "time_up": "time_up.mp3",
            "hint": "hint.mp3"
        }

        # Tạo giao diện chính
        self.create_main_menu()

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            pygame.mixer.music.load(self.sounds[sound_name])
            pygame.mixer.music.play()

    def create_main_menu(self, background_image_path="anhgame1.jpg"):
        self.root.title("Sudoku Game")
        self.clear_window()

        # Ảnh nền
        self.background_image = ImageTk.PhotoImage(Image.open(background_image_path).resize((800, 600)))
        background_label = tk.Label(self.root, 
                                    image=self.background_image)
        background_label.place(x=0, 
                               y=0, 
                               relwidth=1, 
                               relheight=1)

        # Tiêu đề
        title_label = tk.Label(self.root, 
                               text="Sudoku Game", 
                               font=("Arial", 24), 
                               bg="#ffffff", 
                               fg="#333333")
        title_label.pack(pady=30)


        # Nút chơi
        play_button = tk.Button(
            self.root, text="Chơi", 
            command=self.show_difficulty_selection, 
            font=("Arial", 16),
            width=15, 
            bg="#4CAF50", 
            fg="white"
        )
        play_button.pack(pady=10)

        # Nút thoát
        exit_button = tk.Button(
            self.root, text="Thoát", 
            command=self.root.quit, 
            font=("Arial", 16),
            width=15, 
            bg="#FF5722", 
            fg="white"
        )
        exit_button.pack(pady=10)

    def show_difficulty_selection(self):
        self.clear_window()

        difficulty_label = tk.Label(self.root, 
                                    text="Chọn độ khó", 
                                    font=("Arial", 18))
        difficulty_label.pack(pady=20)
        
        difficulties = ["Dễ", "Trung bình", "Khó", "Rất khó"]
        for difficulty in difficulties:
            button = tk.Button(self.root, 
                               text=difficulty, 
                               font=("Arial", 25),
                               width=15, 
                               bg="#4CAF50", 
                               fg="white", 
                               command=lambda d=difficulty: self.start_game(d))
            button.pack(pady=5)

        back_button = tk.Button(self.root, 
                                text="Quay lại", 
                                command=self.create_main_menu, 
                                font=("Arial", 14), 
                                width=15, 
                                bg="#FF5722", 
                                fg="white")
        back_button.pack(pady=20)

    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.remaining_time = self.time_limit
        self.running = True

        self.clear_window()
        self.create_board()
        self.generate_sudoku_board()

        self.timer_label = tk.Label(self.root, text="Thời gian còn lại: 05:00", font=("Arial", 14))
        self.timer_label.pack(pady=10)
        self.start_timer()

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        check_button = tk.Button(button_frame, text="Kiểm tra", 
                                 command=self.check_solution, 
                                 font=("Arial", 14))
        check_button.grid(row=0, 
                          column=0, 
                          padx=10)

        hint_button = tk.Button(button_frame, 
                                text="Gợi ý", 
                                command=self.hint, 
                                font=("Arial", 14))
        hint_button.grid(row=0, 
                         column=1, 
                         padx=10)

        back_button = tk.Button(button_frame, 
                                text="Quay lại", 
                                command=self.create_main_menu, 
                                font=("Arial", 14))
        back_button.grid(row=0, 
                         column=2, 
                         padx=10)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_board(self):
        frame = tk.Frame(self.root, 
                         bg="black")
        frame.pack(pady=30)

        for i in range(self.size):
            for j in range(self.size):
                cell_frame = tk.Frame(
                    frame,
                    bg="white",
                    highlightbackground="black",
                    highlightthickness=2 if (i % 3 == 0 or j % 3 == 0) else 1,
                    width=50,
                    height=50
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
        # Tạo bảng Sudoku hoàn chỉnh
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solve_sudoku_backtrack(self.board)

        # Sao chép để lưu bài giải
        self.solution = [row[:] for row in self.board]

        # Xóa các ô dựa trên mức độ khó
        cells_to_remove = self.get_cells_to_remove_based_on_difficulty()
        for cell in cells_to_remove:
            i, j = cell
            self.board[i][j] = ''

        # Hiển thị bảng
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != '':
                    self.cells[i][j].insert(0, str(self.board[i][j]))
                    self.cells[i][j].config(state='disabled')

    def solve_sudoku_backtrack(self, board):
        empty_cell = self.find_empty_cell(board)
        if not empty_cell:
            return True
        row, col = empty_cell

        for num in range(1, 10):
            if self.is_valid(board, row, col, num):
                board[row][col] = num
                if self.solve_sudoku_backtrack(board):
                    return True
                board[row][col] = 0
        return False

    def find_empty_cell(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return i, j
        return None

    def is_valid(self, board, row, col, num):
        for i in range(9):
            if board[row][i] == num or board[i][col] == num or \
                    board[row - row % 3 + i // 3][col - col % 3 + i % 3] == num:
                return False
        return True

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

    def start_timer(self):
        def countdown():
            while self.remaining_time > 0 and self.running:
                mins, secs = divmod(self.remaining_time, 60)
                self.timer_label.config(text="Thời gian còn lại: {:02d}:{:02d}".format(mins, secs))
                time.sleep(1)
                self.remaining_time -= 1
            if self.remaining_time == 0:
                self.running = False
                self.play_sound("time_up")
                messagebox.showinfo("Hết giờ", "Bạn đã hết thời gian!")
                self.create_main_menu()

        threading.Thread(target=countdown, daemon=True).start()

    def hint(self):
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if not self.cells[i][j].get()]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.cells[i][j].insert(0, str(self.solution[i][j]))
            self.cells[i][j].config(state='disabled')
            self.play_sound("hint")
        else:
            messagebox.showinfo("Gợi ý", "Không còn ô trống để gợi ý!")

    def check_solution(self):
        correct = True
        for i in range(self.size):
            for j in range(self.size):
                user_input = self.cells[i][j].get()
                if user_input.isdigit() and int(user_input) == self.solution[i][j]:
                    self.cells[i][j].config(bg="lightgreen")
                else:
                    correct = False
                    self.cells[i][j].config(bg="lightcoral")

        if correct:
            self.play_sound("correct")
            messagebox.showinfo("Chúc mừng", "Bạn đã hoàn thành màn chơi!")
        else:
            self.play_sound("wrong")
            self.root.after(2000, self.reset_cell_colors)

    def reset_cell_colors(self):
        for i in range(self.size):
            for j in range(self.size):
                self.cells[i][j].config(bg="white")


# Chạy ứng dụng
root = tk.Tk()
root.geometry("800x600")
game = SudokuGame(root)
root.mainloop()
