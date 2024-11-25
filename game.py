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
        
        # Khởi tạo giao diện chính với ảnh nền và nút "Chơi"
        self.create_main_menu()

    def create_main_menu(self):
        self.root.title("Sudoku Game")
        
        # Ảnh nền
        self.background_image = Image.open("anhgame.jpg")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.background_image = self.background_image.resize((screen_width, screen_height), Image.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(self.root, image=self.background_photo)
        self.background_label.place(x=1, y=1, relwidth=1, relheight=1)
        
        # Nút Chơi
        self.play_button = tk.Button(self.root, text="Chơi", command=self.show_difficulty_selection, font=("Arial", 16))
        self.play_button.place(relx=0.5, rely=0.5, anchor="center")
        
        # Thông tin trò chơi
        self.info_label = tk.Label(self.root, text="Chào mừng bạn đến với trò chơi Sudoku!\nChọn độ khó để bắt đầu.", font=("Arial", 12), bg="lightblue")
        self.info_label.place(relx=0.5, rely=0.7, anchor="center")

    def show_difficulty_selection(self):
        # Xóa giao diện chính và chuyển sang màn hình chọn độ khó
        self.background_label.place_forget()
        self.play_button.place_forget()
        self.info_label.place_forget()
        
        # Chọn độ khó
        self.difficulty_label = tk.Label(self.root, text="Chọn độ khó", font=("Arial", 18))
        self.difficulty_label.pack(pady=20)
        
        difficulties = ["Dễ", "Trung bình", "Khó", "Rất khó"]
        for difficulty in difficulties:
            button = tk.Button(self.root, text=difficulty, font=("Arial", 14), command=lambda d=difficulty: self.start_game(d))
            button.pack(pady=5)

    def start_game(self, difficulty):
        # Lưu độ khó và chuyển sang trò chơi
        self.difficulty = difficulty
        self.clear_window()
        self.create_board()
        self.generate_sudoku_board()
        
        # Thời gian đếm ngược
        self.timer_label = tk.Label(self.root, text="Thời gian còn lại: {} giây".format(self.remaining_time))
        self.timer_label.grid(row=self.size+1, column=0, columnspan=5)
        self.start_timer()
        
        # Nút chức năng
        self.check_button = tk.Button(self.root, text="Kiểm tra", command=self.check_solution)
        self.check_button.grid(row=self.size+1, column=5, columnspan=2)
        self.hint_button = tk.Button(self.root, text="Gợi ý", command=self.hint)
        self.hint_button.grid(row=self.size+1, column=7, columnspan=2)
        self.next_button = tk.Button(self.root, text="Chơi màn tiếp", command=self.next_level)
        self.next_button.grid(row=self.size+2, column=3, columnspan=3)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_board(self):
        for i in range(self.size):
            for j in range(self.size):
                cell = tk.Entry(self.root, width=3, font=('Arial', 18), justify='center')
                cell.grid(row=i, column=j, padx=1, pady=1)
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
                messagebox.showinfo("Thua cuộc", "Hết thời gian! Bạn đã thua.")
                self.reset_game()

        threading.Thread(target=countdown).start()

    def hint(self):
        selected_cell = self.root.focus_get()
        row, col = None, None

        for i in range(self.size):
            for j in range(self.size):
                if self.cells[i][j] == selected_cell:
                    row, col = i, j
                    break

        if row is not None and col is not None and not self.cells[row][col].get():
            # Gợi ý cho ô đang chọn
            self.cells[row][col].insert(0, str(self.solution[row][col]))
            self.cells[row][col].config(state='disabled')
        else:
            # Gợi ý ô trống ngẫu nhiên
            empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if not self.cells[i][j].get()]
            if empty_cells:
                i, j = random.choice(empty_cells)
                self.cells[i][j].insert(0, str(self.solution[i][j]))
                self.cells[i][j].config(state='disabled')
            else:
                messagebox.showinfo("Gợi ý", "Không có ô trống để gợi ý!")

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
            self.next_button.config(state='normal')

        # Đặt lại màu sau 2 giây
        self.root.after(2000, self.reset_cell_colors)

    def reset_cell_colors(self):
        for i in range(self.size):
            for j in range(self.size):
                self.cells[i][j].config(bg="white")

    def next_level(self):
        self.remaining_time = self.time_limit
        difficulty_levels = ["Dễ", "Trung bình", "Khó", "Rất khó"]
        current_level = difficulty_levels.index(self.difficulty)
        self.difficulty = difficulty_levels[min(current_level + 1, len(difficulty_levels) - 1)]
        self.start_game(self.difficulty)

    def reset_game(self):
        self.running = False
        self.clear_window()
        self.create_main_menu()

root = tk.Tk()
root.geometry("800x800")  # Đặt kích thước cửa sổ
game = SudokuGame(root)
root.mainloop()
