# collect_data.py - 修复版
from a_star import AStarSolver
from utils import create_goal_board, print_board
import time


def collect_performance_data():
    """收集性能数据"""
    print("八数码问题A*算法性能数据收集")
    print("=" * 60)

    goal_board = create_goal_board()

    # 修正测试案例 - 使用已知正确的案例
    test_cases = [
        ("1步解", [[1, 2, 3], [4, 5, 6], [7, 0, 8]]),
        ("2步解", [[1, 2, 3], [4, 5, 6], [0, 7, 8]]),
        ("3步解", [[1, 2, 3], [4, 5, 0], [7, 8, 6]]),
        ("5步解", [[1, 2, 0], [4, 5, 3], [7, 8, 6]]),
        ("8步解", [[0, 1, 2], [4, 5, 3], [7, 8, 6]]),
        ("10步解", [[1, 3, 5], [4, 2, 0], [7, 8, 6]]),
        ("12步解", [[1, 0, 3], [4, 2, 6], [7, 5, 8]]),
        ("15步解", [[2, 8, 3], [1, 6, 4], [7, 0, 5]]),
        ("困难", [[8, 7, 6], [5, 4, 3], [2, 1, 0]]),
    ]

    print(f"{'案例':<10} {'启发式':<12} {'节点数':<10} {'时间(ms)':<10} {'步数':<6}")
    print("-" * 60)

    results = []

    for name, board in test_cases:
        # 先显示棋盘
        print(f"\n{name}:")
        print_board(board, "初始状态")

        solver = AStarSolver(board, goal_board)

        # 检查可解性
        if not solver.is_solvable(board):
            print(f"   该状态无解，跳过")
            continue

        for heuristic in ["manhattan", "misplaced"]:
            start_time = time.time()
            path, moves, stats = solver.solve(heuristic, max_nodes=100000)
            end_time = time.time()

            # 安全地检查是否有解
            if stats and stats.get("solution_found", False):
                time_ms = (end_time - start_time) * 1000
                print(f"  {heuristic:<12} {stats['nodes_expanded']:<10} "
                      f"{time_ms:<10.2f} {stats['path_length']:<6}")

                results.append({
                    'case': name,
                    'steps': stats['path_length'],
                    'heuristic': heuristic,
                    'nodes': stats['nodes_expanded'],
                    'time': time_ms
                })
            else:
                error_msg = stats.get('error', '未知错误') if stats else '无返回结果'
                print(f"  {heuristic:<12} {'失败':<10} {'-':<10} {'-':<6} ({error_msg})")

    print("=" * 60)

    # 分析结果
    if results:
        print("\n性能对比分析:")
        print(f"{'案例':<10} {'曼哈顿':<8} {'错位数':<8} {'效率比':<8}")
        print("-" * 40)

        # 按案例分组
        cases_data = {}
        for r in results:
            if r['case'] not in cases_data:
                cases_data[r['case']] = {}
            cases_data[r['case']][r['heuristic']] = r['nodes']

        for case_name in sorted(cases_data.keys()):
            manhattan_nodes = cases_data[case_name].get('manhattan', 0)
            misplaced_nodes = cases_data[case_name].get('misplaced', 0)

            if manhattan_nodes > 0 and misplaced_nodes > 0:
                efficiency = misplaced_nodes / manhattan_nodes
                print(f"{case_name:<10} {manhattan_nodes:<8} {misplaced_nodes:<8} {efficiency:<8.2f}")

        # 总体统计
        manhattan_results = [r for r in results if r['heuristic'] == 'manhattan']
        misplaced_results = [r for r in results if r['heuristic'] == 'misplaced']

        if manhattan_results and misplaced_results:
            avg_manhattan = sum(r['nodes'] for r in manhattan_results) / len(manhattan_results)
            avg_misplaced = sum(r['nodes'] for r in misplaced_results) / len(misplaced_results)

            print("-" * 40)
            print(f"{'平均':<10} {avg_manhattan:<8.1f} {avg_misplaced:<8.1f} "
                  f"{avg_misplaced / avg_manhattan:<8.2f}")

            print(f"\n结论：曼哈顿距离启发式平均效率是错位数的 "
                  f"{avg_misplaced / avg_manhattan:.2f} 倍")


def verify_solution_lengths():
    """验证解路径长度"""
    print("\n" + "=" * 60)
    print("解路径长度验证")
    print("=" * 60)

    goal_board = create_goal_board()

    # 手动验证几个案例
    verification_cases = [
        ("案例1", [[1, 2, 3], [4, 5, 6], [7, 0, 8]], 1),
        ("案例2", [[1, 2, 3], [4, 5, 6], [0, 7, 8]], 2),
        ("案例3", [[1, 2, 3], [4, 5, 0], [7, 8, 6]], 3),
        ("案例4", [[1, 2, 0], [4, 5, 3], [7, 8, 6]], 5),
        ("案例5", [[1, 0, 3], [4, 2, 6], [7, 5, 8]], 12),
    ]

    for name, board, expected in verification_cases:
        print(f"\n{name}:")
        print_board(board, "初始状态")

        solver = AStarSolver(board, goal_board)
        path, moves, stats = solver.solve("manhattan")

        if stats.get("solution_found", False):
            actual = stats['path_length']
            print(f"  预期步数: {expected}")
            print(f"  实际步数: {actual}")
            print(f"  解路径: {' → '.join(moves)}")

            if actual == expected:
                print(f"   步数正确")
            else:
                print(f"   步数错误")

                # 显示详细步骤
                print(f"  详细步骤:")
                for i, state in enumerate(path):
                    move = state.move if i > 0 else "初始"
                    print(f"    步骤{i}: {move}")
                    for row in state.board:
                        print(f"      {' '.join(str(x) if x != 0 else ' ' for x in row)}")
        else:
            print(f"   求解失败: {stats.get('error', '未知错误')}")


if __name__ == "__main__":
    # 先验证解路径长度
    verify_solution_lengths()

    print("\n" + "=" * 60)
    print("开始收集性能数据...")
    print("=" * 60)

    collect_performance_data()