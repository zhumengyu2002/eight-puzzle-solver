# main.py - 简化版本，避免argparse问题
import sys
import tkinter as tk
from tkinter import messagebox


def run_gui():
    """运行图形界面"""
    try:
        from puzzle_gui import PuzzleGUI
        print("启动八数码问题求解器图形界面...")
        app = PuzzleGUI()
        app.run()
        return True
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保以下文件存在:")
        print("  - puzzle_state.py")
        print("  - a_star.py")
        print("  - puzzle_gui.py")
        print("  - utils.py")
        return False
    except Exception as e:
        print(f"运行错误: {e}")
        return False


def run_console():
    """运行命令行模式"""
    try:
        from test_cases import run_single_case, get_test_cases

        test_cases, _ = get_test_cases()

        print("八数码问题求解器 - 命令行测试模式")
        print("=" * 50)

        while True:
            print("\n可用的测试案例:")
            for key in test_cases.keys():
                print(f"  {key}: {test_cases[key]['name']}")

            print("\n命令:")
            print("  all: 测试所有案例")
            print("  gui: 启动图形界面")
            print("  exit: 退出")

            choice = input("\n请选择测试案例或命令: ").strip().lower()

            if choice == "exit":
                print("再见！")
                break
            elif choice == "gui":
                run_gui()
                break
            elif choice == "all":
                print("\n开始测试所有案例...")
                for case_name in test_cases.keys():
                    print(f"\n{'=' * 60}")
                    print(f"测试案例: {test_cases[case_name]['name']}")

                    # 测试曼哈顿距离
                    print(f"\n1. 曼哈顿距离启发式:")
                    run_single_case(case_name, "manhattan")

                    # 测试错位数
                    print(f"\n2. 错位数启发式:")
                    run_single_case(case_name, "misplaced")

                print(f"\n{'=' * 60}")
                print("所有案例测试完成！")

            elif choice in test_cases:
                print("\n选择启发式函数:")
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

    except ImportError as e:
        print(f"导入模块失败: {e}")
        return False


def run_quick_test():
    """快速测试程序"""
    print("八数码问题快速测试")
    print("=" * 50)

    try:
        from utils import create_goal_board, print_board
        from a_star import AStarSolver

        # 简单测试案例
        initial_board = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 0, 8]
        ]

        goal_board = create_goal_board()

        print_board(initial_board, "初始状态")
        print_board(goal_board, "目标状态")

        solver = AStarSolver(initial_board, goal_board)

        print("\n使用曼哈顿距离启发式求解...")
        path, moves, stats = solver.solve("manhattan")

        if stats["solution_found"]:
            print(f" 求解成功！")
            print(f"  扩展节点数: {stats['nodes_expanded']}")
            print(f"  解路径长度: {stats['path_length']} 步")
            print(f"  解路径: {' → '.join(moves)}")
        else:
            print(f" 求解失败: {stats.get('error', '未知错误')}")

        print("\n测试完成！")
        input("按Enter键继续...")

    except Exception as e:
        print(f"测试错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("八数码问题求解器")
    print("=" * 50)

    while True:
        print("\n请选择运行模式:")
        print("1. 图形界面 (推荐)")
        print("2. 命令行测试")
        print("3. 快速测试")
        print("4. 退出")

        choice = input("\n请输入选项 (1-4): ").strip()

        if choice == "1":
            if run_gui():
                break
            else:
                print("启动图形界面失败，请检查错误信息。")
        elif choice == "2":
            run_console()
            break
        elif choice == "3":
            run_quick_test()
            break
        elif choice == "4":
            print("再见！")
            sys.exit(0)
        else:
            print("无效的选择，请重新输入。")


if __name__ == "__main__":
    main()