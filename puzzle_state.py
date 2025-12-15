# puzzle_state.py
class PuzzleState:
    """八数码状态表示类"""

    def __init__(self, board, parent=None, move=""):
        """
        初始化状态
        Args:
            board: 3x3的二维列表
            parent: 父状态
            move: 从父状态到当前状态的移动方向
        """
        self.board = board
        self.parent = parent
        self.move = move
        self.g = 0 if parent is None else parent.g + 1  # 实际代价
        self.size = 3  # 棋盘大小
        self.goal_board = None  # 初始化时不知道目标状态

    def __eq__(self, other):
        """重载相等运算符"""
        return self.board == other.board

    def __hash__(self):
        """重载哈希函数，用于集合和字典"""
        return hash(str(self.board))

    def __lt__(self, other):
        """重载小于运算符，用于优先队列"""
        # 注意：这里不能直接调用h()，因为我们不知道goal_board
        # 所以我们需要在A*算法中通过元组(f_score, h_score)来排序
        # 这个方法实际上不应该被直接调用，但为了安全起见我们提供一个实现
        return id(self) < id(other)  # 简单的实现，避免错误

    def __str__(self):
        """字符串表示"""
        return '\n'.join([' '.join(map(str, row)) for row in self.board])

    def copy(self):
        """深拷贝状态"""
        new_board = [row[:] for row in self.board]
        new_state = PuzzleState(new_board, self.parent, self.move)
        new_state.g = self.g
        new_state.goal_board = self.goal_board
        return new_state

    def get_position(self, value):
        """获取指定值在棋盘上的位置"""
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == value:
                    return (i, j)
        return None

    def get_blank_position(self):
        """获取空白格位置"""
        return self.get_position(0)

    def is_goal(self, goal_board=None):
        """判断是否达到目标状态"""
        target = goal_board if goal_board else self.goal_board
        if target is None:
            raise ValueError("未指定目标状态")
        return self.board == target

    def get_neighbors(self):
        """生成所有合法后续状态"""
        neighbors = []
        blank_i, blank_j = self.get_blank_position()

        # 四个可能移动方向：上、下、左、右
        directions = [
            (-1, 0, "上"),  # 上
            (1, 0, "下"),  # 下
            (0, -1, "左"),  # 左
            (0, 1, "右")  # 右
        ]

        for di, dj, move_name in directions:
            new_i, new_j = blank_i + di, blank_j + dj

            # 检查移动是否合法
            if 0 <= new_i < self.size and 0 <= new_j < self.size:
                # 复制当前棋盘
                new_board = [row[:] for row in self.board]

                # 交换空白格与目标格
                new_board[blank_i][blank_j], new_board[new_i][new_j] = \
                    new_board[new_i][new_j], new_board[blank_i][blank_j]

                # 创建新状态
                new_state = PuzzleState(new_board, self, move_name)
                new_state.g = self.g + 1
                new_state.goal_board = self.goal_board
                neighbors.append(new_state)

        return neighbors

    def h_misplaced(self, goal_board=None):
        """错位数启发式函数"""
        target = goal_board if goal_board else self.goal_board
        if target is None:
            raise ValueError("未指定目标状态")

        count = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != 0 and self.board[i][j] != target[i][j]:
                    count += 1
        return count

    def h_manhattan(self, goal_board=None):
        """曼哈顿距离启发式函数"""
        target = goal_board if goal_board else self.goal_board
        if target is None:
            raise ValueError("未指定目标状态")

        distance = 0
        # 创建目标位置映射
        goal_positions = {}
        for i in range(self.size):
            for j in range(self.size):
                goal_positions[target[i][j]] = (i, j)

        # 计算曼哈顿距离
        for i in range(self.size):
            for j in range(self.size):
                value = self.board[i][j]
                if value != 0:  # 忽略空白格
                    goal_i, goal_j = goal_positions[value]
                    distance += abs(i - goal_i) + abs(j - goal_j)

        return distance

    def h(self, goal_board=None, heuristic_type="manhattan"):
        """统一调用启发式函数"""
        if heuristic_type == "manhattan":
            return self.h_manhattan(goal_board)
        elif heuristic_type == "misplaced":
            return self.h_misplaced(goal_board)
        else:
            raise ValueError(f"未知的启发式类型: {heuristic_type}")

    def f(self, goal_board=None, heuristic_type="manhattan"):
        """计算f(n) = g(n) + h(n)"""
        return self.g + self.h(goal_board, heuristic_type)