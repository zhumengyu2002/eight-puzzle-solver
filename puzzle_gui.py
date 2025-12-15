# puzzle_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import random
from puzzle_state import PuzzleState
from a_star import AStarSolver
from utils import create_goal_board, create_random_board, print_board


class PuzzleGUI:
    """八数码问题图形界面"""

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("八数码问题求解器 - A*算法演示")
        self.window.geometry("800x600")

        # 目标状态
        self.goal_board = create_goal_board()

        # 初始状态
        self.initial_board = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 0, 8]
        ]

        # 当前状态
        self.current_board = [row[:] for row in self.initial_board]

        # 求解结果
        self.solution_path = None
        self.current_step = 0

        # 颜色配置
        self.colors = {
            "tile": "#4A90E2",  # 方块颜色
            "blank": "#F5F5F5",  # 空白格颜色
            "text": "white",  # 文字颜色
            "highlight": "#FF6B6B"  # 高亮颜色
        }

        self.setup_ui()
        self.update_board_display()

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.grid(row=0, column=0, padx=(0, 10), sticky=(tk.N, tk.S))

        # 棋盘显示区域
        board_frame = ttk.LabelFrame(main_frame, text="八数码棋盘", padding="10")
        board_frame.grid(row=0, column=1, sticky=(tk.N, tk.E, tk.S, tk.W))
        board_frame.columnconfigure(0, weight=1)
        board_frame.rowconfigure(0, weight=1)

        # 右侧信息面板
        info_frame = ttk.LabelFrame(main_frame, text="求解信息", padding="10")
        info_frame.grid(row=0, column=2, padx=(10, 0), sticky=(tk.N, tk.S))

        # === 控制面板组件 ===

        # 初始状态设置
        ttk.Label(control_frame, text="初始状态设置:").grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky=tk.W)

        ttk.Button(control_frame, text="随机生成",
                   command=self.randomize_board).grid(row=1, column=0, columnspan=2, pady=2, sticky=tk.EW)

        ttk.Button(control_frame, text="重置为初始",
                   command=self.reset_to_initial).grid(row=2, column=0, columnspan=2, pady=2, sticky=tk.EW)

        # 手动输入按钮
        manual_frame = ttk.Frame(control_frame)
        manual_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Label(manual_frame, text="手动设置:").pack(side=tk.LEFT)

        self.board_entries = []
        for i in range(9):
            entry = ttk.Entry(manual_frame, width=3)
            entry.pack(side=tk.LEFT, padx=1)
            self.board_entries.append(entry)

        ttk.Button(control_frame, text="应用手动设置",
                   command=self.apply_manual_setup).grid(row=4, column=0, columnspan=2, pady=2)

        # 分隔线
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).grid(row=5, column=0, columnspan=2, pady=10, sticky=tk.EW)

        # 算法设置
        ttk.Label(control_frame, text="算法设置:").grid(row=6, column=0, columnspan=2, pady=(0, 5), sticky=tk.W)

        ttk.Label(control_frame, text="启发式函数:").grid(row=7, column=0, sticky=tk.W)
        self.heuristic_var = tk.StringVar(value="manhattan")
        heuristic_combo = ttk.Combobox(control_frame, textvariable=self.heuristic_var,
                                       values=["manhattan", "misplaced"], state="readonly", width=15)
        heuristic_combo.grid(row=7, column=1, padx=(5, 0))

        # 求解按钮
        ttk.Button(control_frame, text="开始求解",
                   command=self.solve_puzzle, style="Accent.TButton").grid(row=8, column=0, columnspan=2, pady=10,
                                                                           sticky=tk.EW)

        # 步骤控制
        ttk.Label(control_frame, text="解路径演示:").grid(row=9, column=0, columnspan=2, pady=(10, 5), sticky=tk.W)

        step_control_frame = ttk.Frame(control_frame)
        step_control_frame.grid(row=10, column=0, columnspan=2, pady=5)

        ttk.Button(step_control_frame, text="◀◀",
                   command=lambda: self.show_step(0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(step_control_frame, text="◀",
                   command=self.prev_step).pack(side=tk.LEFT, padx=2)

        self.step_label = ttk.Label(step_control_frame, text="步骤: 0/0")
        self.step_label.pack(side=tk.LEFT, padx=10)

        ttk.Button(step_control_frame, text="▶",
                   command=self.next_step).pack(side=tk.LEFT, padx=2)
        ttk.Button(step_control_frame, text="▶▶",
                   command=lambda: self.show_step(-1)).pack(side=tk.LEFT, padx=2)

        # === 棋盘显示区域 ===

        # 创建棋盘画布
        self.canvas = tk.Canvas(board_frame, width=300, height=300, bg="white")
        self.canvas.grid(row=0, column=0, sticky=(tk.N, tk.E, tk.S, tk.W))

        # === 信息面板 ===

        # 状态信息
        self.info_text = tk.Text(info_frame, width=30, height=20, wrap=tk.WORD)
        self.info_text.grid(row=0, column=0, sticky=(tk.N, tk.E, tk.S, tk.W))

        # 滚动条
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text.configure(yscrollcommand=scrollbar.set)

        # 底部状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))

    def update_board_display(self):
        """更新棋盘显示"""
        self.canvas.delete("all")

        cell_size = 100
        padding = 5

        for i in range(3):
            for j in range(3):
                x1 = j * cell_size + padding
                y1 = i * cell_size + padding
                x2 = (j + 1) * cell_size - padding
                y2 = (i + 1) * cell_size - padding

                value = self.current_board[i][j]

                # 绘制方块
                if value == 0:  # 空白格
                    fill_color = self.colors["blank"]
                    text_color = "gray"
                    text = ""
                else:
                    fill_color = self.colors["tile"]
                    text_color = self.colors["text"]
                    text = str(value)

                # 绘制圆角矩形
                radius = 10
                self.canvas.create_rectangle(
                    x1 + radius, y1, x2 - radius, y2,
                    fill=fill_color, outline="black", width=2
                )
                self.canvas.create_rectangle(
                    x1, y1 + radius, x2, y2 - radius,
                    fill=fill_color, outline="black", width=2
                )
                self.canvas.create_oval(
                    x1, y1, x1 + 2 * radius, y1 + 2 * radius,
                    fill=fill_color, outline="black", width=2
                )
                self.canvas.create_oval(
                    x2 - 2 * radius, y1, x2, y1 + 2 * radius,
                    fill=fill_color, outline="black", width=2
                )
                self.canvas.create_oval(
                    x1, y2 - 2 * radius, x1 + 2 * radius, y2,
                    fill=fill_color, outline="black", width=2
                )
                self.canvas.create_oval(
                    x2 - 2 * radius, y2 - 2 * radius, x2, y2,
                    fill=fill_color, outline="black", width=2
                )

                # 绘制数字
                if text:
                    self.canvas.create_text(
                        (x1 + x2) / 2, (y1 + y2) / 2,
                        text=text, fill=text_color,
                        font=("Arial", 24, "bold")
                    )

        # 更新信息显示
        self.update_info_display()

    def update_info_display(self):
        """更新信息面板"""
        self.info_text.delete(1.0, tk.END)

        # 显示当前状态
        self.info_text.insert(tk.END, "=== 当前状态 ===\n")
        for row in self.current_board:
            # 确保每个数字占2个字符宽度，空白格显示空格
            line = ""
            for x in row:
                if x == 0:
                    line += "   "  # 3个空格
                else:
                    line += f" {x} "  # 数字前后各一个空格
            self.info_text.insert(tk.END, line + "\n")
        self.info_text.insert(tk.END, "\n")

        # 显示目标状态
        self.info_text.insert(tk.END, "=== 目标状态 ===\n")
        for row in self.goal_board:
            line = ""
            for x in row:
                if x == 0:
                    line += "   "
                else:
                    line += f" {x} "
            self.info_text.insert(tk.END, line + "\n")
        self.info_text.insert(tk.END, "\n")

        # 如果有解路径，显示相关信息
        if self.solution_path:
            self.info_text.insert(tk.END, "=== 求解结果 ===\n")
            self.info_text.insert(tk.END, f"路径长度: {len(self.solution_path) - 1} 步\n")
            self.info_text.insert(tk.END, f"当前步骤: {self.current_step}/{len(self.solution_path) - 1}\n")

            if self.current_step < len(self.solution_path) - 1:
                next_state = self.solution_path[self.current_step + 1]
                self.info_text.insert(tk.END, f"下一步: {next_state.move}\n")

        # 验证当前棋盘的有效性
        self.info_text.insert(tk.END, "\n=== 状态验证 ===\n")

        # 检查棋盘是否有效
        flat_board = [num for row in self.current_board for num in row]
        if len(set(flat_board)) != 9:
            self.info_text.insert(tk.END, " 无效棋盘：数字重复或缺失\n")
        elif set(flat_board) != set(range(9)):
            self.info_text.insert(tk.END, " 无效棋盘：必须包含数字0-8\n")
        else:
            self.info_text.insert(tk.END, " 棋盘有效\n")

            # 计算与目标状态的距离
            if self.current_board == self.goal_board:
                self.info_text.insert(tk.END, " 当前已是目标状态！\n")
            else:
                from puzzle_state import PuzzleState
                state = PuzzleState(self.current_board)
                state.goal_board = self.goal_board

                misplaced = state.h_misplaced(self.goal_board)
                manhattan = state.h_manhattan(self.goal_board)

                self.info_text.insert(tk.END, f"错位数: {misplaced}\n")
                self.info_text.insert(tk.END, f"曼哈顿距离: {manhattan}\n")

                # 检查可解性
                from a_star import AStarSolver
                solver = AStarSolver(self.current_board, self.goal_board)
                if solver.is_solvable(self.current_board):
                    self.info_text.insert(tk.END, " 问题有解\n")
                else:
                    self.info_text.insert(tk.END, " 问题无解（逆序数为奇数）\n")

    def randomize_board(self):
        """随机生成棋盘"""
        self.initial_board = create_random_board(moves=30)
        self.current_board = [row[:] for row in self.initial_board]
        self.solution_path = None
        self.current_step = 0
        self.update_board_display()
        self.status_var.set("已生成随机初始状态")

    def reset_to_initial(self):
        """重置为初始状态"""
        self.current_board = [row[:] for row in self.initial_board]
        self.current_step = 0
        self.update_board_display()
        self.status_var.set("已重置为初始状态")

    def apply_manual_setup(self):
        """应用手动设置"""
        try:
            # 从输入框获取数字
            numbers = []
            for entry in self.board_entries:
                text = entry.get().strip()
                if text == "":
                    numbers.append(0)
                else:
                    numbers.append(int(text))

            # 验证数字范围
            if set(numbers) != set(range(9)):
                messagebox.showerror("错误", "必须包含数字0-8各一次")
                return

            # 转换为3x3棋盘
            new_board = []
            for i in range(0, 9, 3):
                new_board.append(numbers[i:i + 3])

            self.initial_board = new_board
            self.current_board = [row[:] for row in new_board]
            self.solution_path = None
            self.current_step = 0
            self.update_board_display()
            self.status_var.set("已应用手动设置")

        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字(0-8)")

    # 在 puzzle_gui.py 中的 solve_puzzle 方法中修改
    def solve_puzzle(self):
        """求解八数码问题"""
        self.status_var.set("正在求解，请稍候...")
        self.window.update()

        # 创建求解器
        solver = AStarSolver(self.current_board, self.goal_board)

        # 选择启发式函数
        heuristic_type = self.heuristic_var.get()

        # 求解
        path, moves, stats = solver.solve(heuristic_type, max_nodes=100000)

        if stats.get("error"):
            messagebox.showerror("求解失败", stats["error"])
            self.status_var.set("求解失败")
            return

        if path:
            self.solution_path = path
            self.current_step = 0
            self.update_board_display()

            # 显示统计信息
            info = f"求解成功！\n\n"
            info += f"启发式函数: {heuristic_type}\n"
            info += f"扩展节点数: {stats['nodes_expanded']}\n"
            info += f"解路径长度: {stats['path_length']} 步\n"
            info += f"最大开放集大小: {stats['max_open_size']}\n"

            messagebox.showinfo("求解完成", info)
            self.status_var.set(f"求解完成 - {stats['path_length']}步解")
        else:
            messagebox.showerror("求解失败", "未找到解")
            self.status_var.set("求解失败")

    def show_step(self, step_index):
        """显示指定步骤"""
        if not self.solution_path:
            return

        if step_index == -1:  # 最后一步
            self.current_step = len(self.solution_path) - 1
        else:
            self.current_step = max(0, min(step_index, len(self.solution_path) - 1))

        self.current_board = [row[:] for row in self.solution_path[self.current_step].board]
        self.update_board_display()
        self.status_var.set(f"步骤 {self.current_step}/{len(self.solution_path) - 1}")

    def prev_step(self):
        """上一步"""
        if not self.solution_path or self.current_step <= 0:
            return

        self.current_step -= 1
        self.current_board = [row[:] for row in self.solution_path[self.current_step].board]
        self.update_board_display()
        self.status_var.set(f"步骤 {self.current_step}/{len(self.solution_path) - 1}")

    def next_step(self):
        """下一步"""
        if not self.solution_path or self.current_step >= len(self.solution_path) - 1:
            return

        self.current_step += 1
        self.current_board = [row[:] for row in self.solution_path[self.current_step].board]
        self.update_board_display()
        self.status_var.set(f"步骤 {self.current_step}/{len(self.solution_path) - 1}")

    def run(self):
        """运行GUI"""
        self.window.mainloop()