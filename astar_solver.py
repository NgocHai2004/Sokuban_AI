"""
Thuật toán A* để giải Sokoban
"""
import heapq
from copy import deepcopy

def manhattan_distance(x1, y1, x2, y2):
    """Tính khoảng cách Manhattan"""
    return abs(x1 - x2) + abs(y1 - y2)

def get_goals(grid):
    """Lấy danh sách vị trí đích"""
    goals = []
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c == ".":
                goals.append((x, y))
    return goals

def get_boxes(grid):
    """Lấy danh sách vị trí các thùng"""
    boxes = []
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c in ("$", "*"):
                boxes.append((x, y))
    return tuple(sorted(boxes))  # Sắp xếp để so sánh

def get_player(grid):
    """Lấy vị trí người chơi"""
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c in ("@", "+"):
                return (x, y)
    return None

def is_valid_move(grid, x, y):
    """Kiểm tra vị trí có hợp lệ không"""
    if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
        return False
    return grid[y][x] != "#"

def heuristic(boxes, goals):
    """Heuristic: tổng khoảng cách Manhattan từ các boxes đến goals gần nhất"""
    if not boxes or not goals:
        return 0
    
    # Tính tổng khoảng cách từ mỗi box đến goal gần nhất
    total = 0
    used_goals = set()
    
    for box in boxes:
        min_dist = float('inf')
        best_goal = None
        for goal in goals:
            if goal not in used_goals:
                dist = manhattan_distance(box[0], box[1], goal[0], goal[1])
                if dist < min_dist:
                    min_dist = dist
                    best_goal = goal
        if best_goal:
            total += min_dist
            used_goals.add(best_goal)
    3
    return total

def apply_move(grid, player_pos, dx, dy):
    """Áp dụng nước đi và trả về state mới"""
    new_grid = deepcopy(grid)
    px, py = player_pos
    tx, ty = px + dx, py + dy
    
    # Kiểm tra ô đích
    if not is_valid_move(new_grid, tx, ty):
        return None, None
    
    target = new_grid[ty][tx]
    
    # Nếu là tường
    if target == "#":
        return None, None
    
    # Nếu là thùng, cần đẩy
    if target in ("$", "*"):
        bx, by = tx + dx, ty + dy
        if not is_valid_move(new_grid, bx, by):
            return None, None
        behind = new_grid[by][bx]
        if behind in ("#", "$", "*"):
            return None, None
        
        # Đẩy thùng
        if behind == ".":
            new_grid[by][bx] = "*"  # Thùng trên goal
        else:
            new_grid[by][bx] = "$"  # Thùng trên sàn
        
        # Cập nhật vị trí cũ của thùng
        if target == "$":
            new_grid[ty][tx] = "@"  # Player trên sàn
        else:
            new_grid[ty][tx] = "+"  # Player trên goal
    else:
        # Di chuyển bình thường
        if target == ".":
            new_grid[ty][tx] = "+"  # Player trên goal
        else:
            new_grid[ty][tx] = "@"  # Player trên sàn
    
    # Cập nhật vị trí cũ của player
    old_char = new_grid[py][px]
    if old_char == "@":
        new_grid[py][px] = " "
    elif old_char == "+":
        new_grid[py][px] = "."
    
    new_player = (tx, ty)
    return new_grid, new_player

def is_goal_state(boxes, goals):
    """Kiểm tra đã đạt goal state chưa"""
    if len(boxes) != len(goals):
        return False
    return set(boxes) == set(goals)

def state_to_key(player_pos, boxes):
    """Chuyển state thành key để so sánh"""
    return (player_pos, boxes)

def astar_solve(initial_grid):
    """Thuật toán A* để giải Sokoban"""
    # Khởi tạo
    goals = get_goals(initial_grid)
    initial_boxes = get_boxes(initial_grid)
    initial_player = get_player(initial_grid)
    
    if not initial_player:
        return None
    
    # Priority queue: (f_score, g_score, grid, player_pos, boxes, path)
    open_set = []
    heapq.heappush(open_set, (0, 0, initial_grid, initial_player, initial_boxes, []))
    
    # Đã thăm
    visited = set()
    visited.add(state_to_key(initial_player, initial_boxes))
    
    # Các hướng di chuyển
    directions = [(0, -1, 'U'), (0, 1, 'D'), (-1, 0, 'L'), (1, 0, 'R')]
    
    while open_set:
        f_score, g_score, grid, player_pos, boxes, path = heapq.heappop(open_set)
        
        # Kiểm tra goal state
        if is_goal_state(boxes, goals):
            return path
        
        # Thử các nước đi
        for dx, dy, direction in directions:
            new_grid, new_player = apply_move(grid, player_pos, dx, dy)
            
            if new_grid is None:
                continue
            
            new_boxes = get_boxes(new_grid)
            state_key = state_to_key(new_player, new_boxes)
            
            # Bỏ qua nếu đã thăm
            if state_key in visited:
                continue
            
            visited.add(state_key)
            
            # Tính điểm
            new_g = g_score + 1
            h = heuristic(new_boxes, goals)
            new_f = new_g + h
            
            # Thêm vào queue
            new_path = path + [direction]
            heapq.heappush(open_set, (new_f, new_g, new_grid, new_player, new_boxes, new_path))
    
    return None  # Không tìm thấy giải pháp

def solve_level_1():
    """Giải level 1"""
    from levels import LEVELS
    
    level = LEVELS[0]
    grid = [list(row) for row in level]
    
    print("Đang giải level 1...")
    solution = astar_solve(grid)
    
    if solution:
        print(f"Tìm thấy giải pháp với {len(solution)} bước:")
        print(" -> ".join(solution))
        return solution
    else:
        print("Không tìm thấy giải pháp!")
        return None

if __name__ == "__main__":
    solve_level_1()





