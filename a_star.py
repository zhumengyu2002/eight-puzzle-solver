# a_star.py
import heapq
from typing import List, Tuple, Optional
from puzzle_state import PuzzleState


class AStarSolver:
    """A*搜索算法求解器"""

    def __init__(self, initial_board, goal_board):
        """
        初始化求解器
        Args:
            initial_board: 初始状态棋盘
            goal_board: 目标状态棋盘
        """
        self.initial_state = PuzzleState(initial_board)
        self.goal_board = goal_board
        self.goal_state = PuzzleState(goal_board)

        # 设置目标状态
        self.initial_state.goal_board = goal_board
        self.goal_state.goal_board = goal_board

    def is_solvable(self, board):
        """检查八数码问题是否有解（基于排列逆序数）"""
        # 将二维列表展平为一维，排除空白格(0)
        flat_board = [num for row in board for num in row if num != 0]

        # 计算逆序数
        inversions = 0
        n = len(flat_board)

        for i in range(n):
            for j in range(i + 1, n):
                if flat_board[i] > flat_board[j]:
                    inversions += 1

        # 对于3x3八数码，逆序数为偶数时有解
        return inversions % 2 == 0

    def reconstruct_path(self, came_from, current_state):
        """重建从初始状态到目标状态的路径"""
        path = []
        moves = []

        while current_state is not None:
            path.append(current_state)
            if current_state.move:  # 初始状态没有移动方向
                moves.append(current_state.move)
            current_state = came_from.get(current_state)

        path.reverse()
        moves.reverse()

        return path, moves

    def solve(self, heuristic_type="manhattan", max_nodes=50000):
        """
        执行A*搜索
        Args:
            heuristic_type: 启发式函数类型 ("manhattan" 或 "misplaced")
            max_nodes: 最大扩展节点数限制
        Returns:
            solution_path: 解路径（状态列表）
            moves: 移动序列
            stats: 统计信息字典
        """
        if not self.is_solvable(self.initial_state.board):
            return None, None, {"error": "该初始状态无解"}

        # 初始化数据结构
        open_set = []  # 优先队列，存储元组 (f_score, h_score, state)
        open_dict = {}  # 快速查找
        closed_set = set()  # 已访问集合

        # 初始化起始状态
        start_h = self.initial_state.h(self.goal_board, heuristic_type)
        start_f = self.initial_state.g + start_h

        # 使用元组 (f_score, h_score, state) 来确保正确排序
        # 当f_score相同时，优先选择h_score较小的
        heapq.heappush(open_set, (start_f, start_h, self.initial_state))
        open_dict[self.initial_state] = start_f

        came_from = {}  # 记录父节点
        g_score = {self.initial_state: 0}  # 实际代价

        # 统计信息
        nodes_expanded = 0
        max_open_size = 1

        while open_set and nodes_expanded < max_nodes:
            # 获取f值最小的状态
            current_f, current_h, current_state = heapq.heappop(open_set)

            # 如果该状态已在closed_set中，跳过
            if current_state in closed_set:
                continue

            # 检查是否达到目标
            if current_state.board == self.goal_board:
                path, moves = self.reconstruct_path(came_from, current_state)
                stats = {
                    "nodes_expanded": nodes_expanded,
                    "path_length": len(path) - 1,
                    "solution_found": True,
                    "max_open_size": max_open_size,
                    "final_f": current_f
                }
                return path, moves, stats

            # 标记为已访问
            closed_set.add(current_state)
            nodes_expanded += 1

            # 生成邻居状态
            for neighbor in current_state.get_neighbors():
                # 设置邻居的目标状态
                neighbor.goal_board = self.goal_board

                # 如果邻居已在closed_set中，跳过
                if neighbor in closed_set:
                    continue

                # 计算从起始状态到邻居的实际代价
                tentative_g = g_score[current_state] + 1

                # 如果找到更优路径或邻居不在open_set中
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    # 更新路径信息
                    came_from[neighbor] = current_state
                    g_score[neighbor] = tentative_g

                    # 计算h值和f值
                    neighbor_h = neighbor.h(self.goal_board, heuristic_type)
                    f_score = tentative_g + neighbor_h

                    # 添加到open_set
                    if neighbor not in open_dict or f_score < open_dict[neighbor]:
                        heapq.heappush(open_set, (f_score, neighbor_h, neighbor))
                        open_dict[neighbor] = f_score

            # 更新最大open_set大小
            max_open_size = max(max_open_size, len(open_set))

        # 搜索失败（达到节点限制或无解）
        stats = {
            "nodes_expanded": nodes_expanded,
            "path_length": 0,
            "solution_found": False,
            "max_open_size": max_open_size,
            "error": f"达到最大节点限制 ({max_nodes}) 或问题无解"
        }
        return None, None, stats