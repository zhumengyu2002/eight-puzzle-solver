# test_cases.py
import unittest
from a_star import AStarSolver
from utils import create_goal_board


def get_test_cases():
    """获取预设的测试案例"""

    goal_board = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]
    ]

    test_cases = {
        # 简单案例：2步解
        "easy": {
            "board": [
                [1, 2, 3],
                [4, 5, 6],
                [7, 0, 8]
            ],
            "name": "简单案例（2步解）",
            "expected_steps": 2
        },

        # 中等案例：10-15步解
        "medium": {
            "board": [
                [1, 0, 3],
                [4, 2, 6],
                [7, 5, 8]
            ],
            "name": "中等案例（10-15步解）",
            "expected_steps": 12
        },

        # 困难案例：需要更多步数
        "hard": {
            "board": [
                [8, 7, 6],
                [5, 4, 3],
                [2, 1, 0]
            ],
            "name": "困难案例（20+步解）",
            "expected_steps": 26
        },

        # 边缘案例：已经完成
        "solved": {
            "board": [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 0]
            ],
            "name": "已解决案例",
            "expected_steps": 0
        },

        # 自定义案例：可修改
        "custom1": {
            "board": [
                [2, 8, 3],
                [1, 6, 4],
                [7, 0, 5]
            ],
            "name": "自定义案例1",
            "expected_steps": 15
        }
    }

    return test_cases, goal_board


def get_case_by_name(name):
    """按名称获取测试案例"""
    test_cases, goal_board = get_test_cases()
    if name in test_cases:
        return test_cases[name]["board"], goal_board
    return None, goal_board


# ==================== 单元测试 ====================
class TestEightPuzzle(unittest.TestCase):
    """八数码问题单元测试"""

    def test_easy_case_manhattan(self):
        """测试简单案例 - 曼哈顿距离"""
        test_cases, goal_board = get_test_cases()
        easy_board = test_cases["easy"]["board"]

        solver = AStarSolver(easy_board, goal_board)
        path, moves, stats = solver.solve("manhattan")

        self.assertTrue(stats["solution_found"])
        self.assertEqual(stats["path_length"], 2)

    def test_easy_case_misplaced(self):
        """测试简单案例 - 错位数启发式"""
        test_cases, goal_board = get_test_cases()
        easy_board = test_cases["easy"]["board"]

        solver = AStarSolver(easy_board, goal_board)
        path, moves, stats = solver.solve("misplaced")

        self.assertTrue(stats["solution_found"])
        self.assertEqual(stats["path_length"], 2)

    def test_medium_case_manhattan(self):
        """测试中等案例 - 曼哈顿距离"""
        test_cases, goal_board = get_test_cases()
        medium_board = test_cases["medium"]["board"]

        solver = AStarSolver(medium_board, goal_board)
        path, moves, stats = solver.solve("manhattan")

        self.assertTrue(stats["solution_found"])
        self.assertGreater(stats["nodes_expanded"], 0)

    def test_solvability_check(self):
        """测试可解性检查"""
        test_cases, goal_board = get_test_cases()
        solver = AStarSolver(test_cases["easy"]["board"], goal_board)

        # 测试可解状态
        solvable_board = [[1, 2, 3], [4, 5, 6], [7, 0, 8]]
        self.assertTrue(solver.is_solvable(solvable_board))

        # 测试不可解状态
        unsolvable_board = [[1, 2, 3], [4, 5, 6], [8, 7, 0]]
        self.assertFalse(solver.is_solvable(unsolvable_board))

    def test_heuristic_values(self):
        """测试启发式函数值计算"""
        from puzzle_state import PuzzleState

        # 创建状态
        board = [[1, 2, 3], [4, 5, 6], [7, 0, 8]]
        goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

        state = PuzzleState(board)

        # 测试曼哈顿距离
        manhattan_h = state.h_manhattan(goal)
        self.assertEqual(manhattan_h, 1)  # 数字8需要移动1步

        # 测试错位数
        misplaced_h = state.h_misplaced(goal)
        self.assertEqual(misplaced_h, 1)  # 只有数字8位置不对


def run_all_tests():
    """运行所有测试"""
    print("开始运行单元测试...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEightPuzzle)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_single_case(case_name, heuristic_type="manhattan"):
    """运行单个测试案例"""
    test_cases, goal_board = get_test_cases()

    if case_name not in test_cases:
        print(f"错误: 未找到案例 '{case_name}'")
        return False

    board = test_cases[case_name]["board"]
    expected_steps = test_cases[case_name]["expected_steps"]

    print(f"\n{'=' * 60}")
    print(f"测试案例: {test_cases[case_name]['name']}")
    print(f"启发式函数: {heuristic_type}")
    print(f"{'=' * 60}")

    # 打印初始状态
    print("初始状态:")
    for row in board:
        print("  " + " ".join(str(x) if x != 0 else " " for x in row))

    print("\n目标状态:")
    for row in goal_board:
        print("  " + " ".join(str(x) if x != 0 else " " for x in row))

    # 创建求解器
    solver = AStarSolver(board, goal_board)

    # 检查可解性
    if not solver.is_solvable(board):
        print("\n 该状态无解！")
        return False

    # 求解
    import time
    start_time = time.time()
    path, moves, stats = solver.solve(heuristic_type)
    end_time = time.time()

    if stats["solution_found"]:
        print(f"\n 求解成功！")
        print(f"  扩展节点数: {stats['nodes_expanded']}")
        print(f"  解路径长度: {stats['path_length']} 步")
        print(f"  预期步数: {expected_steps} 步")
        print(f"  运行时间: {(end_time - start_time) * 1000:.2f} ms")
        print(f"  最大开放集大小: {stats['max_open_size']}")

        # 验证步数
        if expected_steps > 0:
            if stats['path_length'] == expected_steps:
                print(f"  步数符合预期")
            else:
                print(f"   步数不符预期 (预期: {expected_steps}, 实际: {stats['path_length']})")

        # 显示解路径（仅对简单案例）
        if stats['path_length'] <= 5:
            print(f"\n解路径: {' → '.join(moves)}")

        return True
    else:
        print(f"\n 求解失败: {stats.get('error', '未知错误')}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 运行单元测试
        success = run_all_tests()
        sys.exit(0 if success else 1)
    else:
        # 交互式测试
        print("八数码问题测试程序")
        print("=" * 50)

        # 获取所有测试案例
        test_cases, _ = get_test_cases()

        while True:
            print("\n可用的测试案例:")
            for key in test_cases.keys():
                print(f"  {key}: {test_cases[key]['name']}")

            print("\n命令:")
            print("  all: 测试所有案例")
            print("  exit: 退出程序")

            choice = input("\n请选择测试案例或命令: ").strip().lower()

            if choice == "exit":
                print("再见！")
                break
            elif choice == "all":
                print("\n开始测试所有案例...")
                results = []
                for case_name in test_cases.keys():
                    for heuristic in ["manhattan", "misplaced"]:
                        success = run_single_case(case_name, heuristic)
                        results.append((case_name, heuristic, success))

                # 统计结果
                total = len(results)
                passed = sum(1 for _, _, success in results if success)
                print(f"\n{'=' * 60}")
                print(f"测试完成: {passed}/{total} 通过")
                print(f"{'=' * 60}")

            elif choice in test_cases:
                print("\n启发式函数选项:")
                print("  1. manhattan (曼哈顿距离)")
                print("  2. misplaced (错位数)")
                heuristic_choice = input("请选择启发式函数 (1或2): ").strip()

                if heuristic_choice == "1":
                    heuristic_type = "manhattan"
                elif heuristic_choice == "2":
                    heuristic_type = "misplaced"
                else:
                    heuristic_type = "manhattan"

                run_single_case(choice, heuristic_type)
            else:
                print("无效的选择！")