# utils.py
import random
import time
from typing import List, Tuple


def create_goal_board(size=3):
    """创建目标状态棋盘"""
    board = []
    num = 1
    for i in range(size):
        row = []
        for j in range(size):
            if i == size - 1 and j == size - 1:
                row.append(0)  # 最后一个位置是空白格
            else:
                row.append(num)
                num += 1
        board.append(row)
    return board


def create_random_board(size=3, moves=20):
    """通过随机移动生成合法的随机初始状态"""
    goal_board = create_goal_board(size)
    current_state = goal_board

    # 将二维列表转换为可修改的格式
    current_state = [list(row) for row in current_state]

    for _ in range(moves):
        # 找到空白格位置
        blank_i, blank_j = None, None
        for i in range(size):
            for j in range(size):
                if current_state[i][j] == 0:
                    blank_i, blank_j = i, j
                    break

        # 获取可能的移动方向
        possible_moves = []
        if blank_i > 0:
            possible_moves.append((-1, 0))  # 上
        if blank_i < size - 1:
            possible_moves.append((1, 0))  # 下
        if blank_j > 0:
            possible_moves.append((0, -1))  # 左
        if blank_j < size - 1:
            possible_moves.append((0, 1))  # 右

        # 随机选择一个方向移动
        di, dj = random.choice(possible_moves)
        new_i, new_j = blank_i + di, blank_j + dj

        # 交换空白格与相邻格
        current_state[blank_i][blank_j], current_state[new_i][new_j] = \
            current_state[new_i][new_j], current_state[blank_i][blank_j]

    return current_state


def print_board(board, title=""):
    """美观地打印棋盘"""
    if title:
        print(f"\n{title}:")

    print("+" + "---+" * len(board[0]))
    for row in board:
        print("|", end="")
        for cell in row:
            if cell == 0:
                print("   |", end="")
            else:
                print(f" {cell:2}|", end="")
        print("\n+" + "---+" * len(board[0]))


def board_to_string(board):
    """将棋盘转换为字符串表示"""
    lines = []
    for row in board:
        line = " ".join(str(cell) if cell != 0 else " " for cell in row)
        lines.append(line)
    return "\n".join(lines)


def validate_board(board, size=3):
    """验证棋盘是否有效"""
    if len(board) != size:
        return False
    for row in board:
        if len(row) != size:
            return False

    # 检查是否包含所有数字0-8
    numbers = set()
    for row in board:
        for cell in row:
            numbers.add(cell)

    expected_numbers = set(range(size * size))
    return numbers == expected_numbers


def measure_performance(initial_board, goal_board, heuristic_type, runs=3):
    """测量算法性能"""
    from a_star import AStarSolver

    times = []
    nodes_list = []

    for _ in range(runs):
        solver = AStarSolver(initial_board, goal_board)

        start_time = time.time()
        _, _, stats = solver.solve(heuristic_type)
        end_time = time.time()

        times.append(end_time - start_time)
        if stats.get("solution_found"):
            nodes_list.append(stats["nodes_expanded"])

    if times:
        avg_time = sum(times) / len(times)
        avg_nodes = sum(nodes_list) / len(nodes_list) if nodes_list else 0
        return avg_time, avg_nodes
    return None, None