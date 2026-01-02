import pygame
from levels import LEVELS
from astar_solver import astar_solve

# Trạng thái game
MENU = 0
PLAYING = 1

TILE = 48
COLORS = {
    "background": (210, 180, 140),  # Nền gỗ nâu nhạt (light brown wood)
    "wall": (180, 150, 110),  # Tường gỗ nâu nhạt với hiệu ứng 3D (light brown embossed)
    "wall_light": (200, 170, 130),  # Màu sáng cho hiệu ứng 3D
    "wall_dark": (160, 130, 90),  # Màu tối cho hiệu ứng 3D
    "floor": (120, 80, 50),  # Sàn gỗ tối màu (dark brown wooden planks)
    "floor_light": (140, 100, 70),  # Màu sáng cho texture gỗ
    "player_body": (30, 144, 255),  # Quần áo xanh dương (blue overalls)
    "player_hat": (255, 215, 0),  # Mũ vàng (yellow hard hat)
    "box": (139, 69, 19),  # Thùng gỗ nâu (brown wooden crate)
    "box_light": (160, 90, 40),  # Màu sáng cho thùng
    "goal": (50, 205, 50),  # Dấu X xanh lá (green X mark)
    "box_on_goal": (50, 205, 50),  # Thùng xanh lá khi đặt đúng (green crate)
}

def load_level(index):
    grid = [list(row) for row in LEVELS[index]]
    h, w = len(grid), len(grid[0])
    return grid, w, h

def find_player(grid):
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c in ("@", "+"):  # Tìm cả @ và + (nhân vật trên vị trí đích)
                return x, y
    return None

def is_completed(grid):
    return all(c != "$" for row in grid for c in row)

def move(grid, dx, dy):
    px, py = find_player(grid)
    tx, ty = px + dx, py + dy
    # Ô kế
    target = grid[ty][tx]
    if target == "#":
        return
    # Nếu là hộp/ hộp trên đích, cần xem ô sau nữa
    if target in ("$", "*"):
        bx, by = tx + dx, ty + dy
        behind = grid[by][bx]
        if behind in ("#", "$", "*"):
            return  # bị chặn
        # đẩy hộp
        grid[by][bx] = "*" if behind == "." else "$"
        grid[ty][tx] = "@" if target == "$" else "+"  # @ đứng trên floor hoặc goal
    else:
        # ô trống hoặc goal
        grid[ty][tx] = "@" if target == " " else "+"
    # rời ô cũ
    grid[py][px] = " " if grid[py][px] == "@" else "."

def draw_wood_texture(screen, rect, base_color, light_color):
    """Vẽ ô có viền đen đậm"""
    pygame.draw.rect(screen, base_color, rect)
    # Vẽ viền đen đậm
    pygame.draw.rect(screen, (0, 0, 0), rect, 1)

def draw_embossed_block(screen, rect, base_color, light_color, dark_color):
    """Vẽ khối có hiệu ứng 3D embossed"""
    pygame.draw.rect(screen, base_color, rect)
    # Vẽ viền sáng (trên và trái)
    pygame.draw.line(screen, light_color, rect.topleft, rect.topright, 2)
    pygame.draw.line(screen, light_color, rect.topleft, rect.bottomleft, 2)
    # Vẽ viền tối (dưới và phải)
    pygame.draw.line(screen, dark_color, rect.bottomleft, rect.bottomright, 2)
    pygame.draw.line(screen, dark_color, rect.topright, rect.bottomright, 2)

def draw_grid(screen, grid, offset_y=0, offset_x=0):
    # Vẽ theo từng lớp để tránh chồng chất
    # offset_y: offset để tránh các nút ở trên
    # offset_x: offset để căn giữa map theo chiều ngang
    # Lớp 1: Vẽ sàn và tường
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            rect = pygame.Rect(x * TILE + offset_x, y * TILE + offset_y, TILE, TILE)
            if c == "#":
                # Vẽ tường gỗ với hiệu ứng 3D embossed
                draw_embossed_block(screen, rect, COLORS["wall"], 
                                   COLORS["wall_light"], COLORS["wall_dark"])
            else:
                # Vẽ sàn gỗ với texture
                draw_wood_texture(screen, rect, COLORS["floor"], COLORS["floor_light"])
    
    # Lớp 2: Vẽ dấu X đích (luôn ở dưới các phần tử khác)
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
            # Chỉ vẽ dấu X nếu là vị trí đích trống hoặc có nhân vật/thùng trên đó
            if c in (".", "+", "*"):
                rect = pygame.Rect(x * TILE + offset_x, y * TILE + offset_y, TILE, TILE)
                center_x, center_y = rect.center
                size = TILE // 3
                # Vẽ dấu X màu xanh lá
                pygame.draw.line(screen, COLORS["goal"], 
                               (center_x - size, center_y - size),
                               (center_x + size, center_y + size), 5)
                pygame.draw.line(screen, COLORS["goal"], 
                               (center_x - size, center_y + size),
                               (center_x + size, center_y - size), 5)
    
    # Lớp 3: Vẽ thùng (sau dấu X đích)
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            rect = pygame.Rect(x * TILE + offset_x, y * TILE + offset_y, TILE, TILE)
            if c in ("$", "*"):
                box_rect = rect.inflate(-8, -8)
                if c == "*":
                    # Thùng đã đặt đúng - màu xanh lá
                    pygame.draw.rect(screen, COLORS["box_on_goal"], box_rect)
                    pygame.draw.rect(screen, (30, 150, 30), box_rect, 2)
                    # Vẽ dấu X trên thùng
                    center_x, center_y = box_rect.center
                    size_x = box_rect.width // 4
                    pygame.draw.line(screen, (255, 255, 255), 
                                   (center_x - size_x, center_y - size_x),
                                   (center_x + size_x, center_y + size_x), 3)
                    pygame.draw.line(screen, (255, 255, 255), 
                                   (center_x - size_x, center_y + size_x),
                                   (center_x + size_x, center_y - size_x), 3)
                else:
                    # Thùng gỗ nâu với hiệu ứng 3D
                    pygame.draw.rect(screen, COLORS["box"], box_rect)
                    # Viền sáng
                    pygame.draw.line(screen, COLORS["box_light"], 
                                   box_rect.topleft, box_rect.topright, 2)
                    pygame.draw.line(screen, COLORS["box_light"], 
                                   box_rect.topleft, box_rect.bottomleft, 2)
                    # Viền tối
                    pygame.draw.line(screen, (100, 50, 0), 
                                   box_rect.bottomleft, box_rect.bottomright, 2)
                    pygame.draw.line(screen, (100, 50, 0), 
                                   box_rect.topright, box_rect.bottomright, 2)
                    # Vẽ pattern X trên mặt thùng (màu sáng hơn)
                    center_x, center_y = box_rect.center
                    size_x = box_rect.width // 3
                    pygame.draw.line(screen, COLORS["box_light"], 
                                   (center_x - size_x, center_y - size_x),
                                   (center_x + size_x, center_y + size_x), 3)
                    pygame.draw.line(screen, COLORS["box_light"], 
                                   (center_x - size_x, center_y + size_x),
                                   (center_x + size_x, center_y - size_x), 3)
    
    # Lớp 4: Vẽ nhân vật (luôn ở trên cùng)
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            rect = pygame.Rect(x * TILE + offset_x, y * TILE + offset_y, TILE, TILE)
            if c in ("@", "+"):
                center_x, center_y = rect.center
                # Vẽ thân người (quần áo xanh dương)
                body_radius = TILE // 3
                pygame.draw.circle(screen, COLORS["player_body"], 
                                 (center_x, center_y + 4), body_radius)
                # Vẽ mũ bảo hiểm vàng
                hat_rect = pygame.Rect(center_x - TILE // 4, center_y - TILE // 3,
                                     TILE // 2, TILE // 4)
                pygame.draw.rect(screen, COLORS["player_hat"], hat_rect)
                pygame.draw.rect(screen, (200, 150, 0), hat_rect, 2)
                # Vẽ mặt
                pygame.draw.circle(screen, (255, 220, 177), 
                                 (center_x, center_y), body_radius - 4)
                # Vẽ mắt
                pygame.draw.circle(screen, (0, 0, 0), 
                                 (center_x - 4, center_y - 2), 2)
                pygame.draw.circle(screen, (0, 0, 0), 
                                 (center_x + 4, center_y - 2), 2)

class Button:
    """Lớp nút bấm với styling đẹp"""
    def __init__(self, x, y, width, height, text, color=(100, 150, 200), hover_color=(120, 170, 220)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen, font):
        """Vẽ nút với shadow và hiệu ứng đẹp"""
        # Kiểm tra nút có nằm trong màn hình không
        screen_rect = screen.get_rect()
        if not self.rect.colliderect(screen_rect):
            # Nếu nút nằm ngoài màn hình, điều chỉnh vị trí
            if self.rect.right > screen_rect.right:
                self.rect.right = screen_rect.right - 10
            if self.rect.bottom > screen_rect.bottom:
                self.rect.bottom = screen_rect.bottom - 10
        
        color = self.hover_color if self.is_hovered else self.color
        
        # Vẽ shadow
        shadow_rect = self.rect.move(3, 3)
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height))
        shadow_surface.set_alpha(80)
        shadow_surface.fill((0, 0, 0))
        screen.blit(shadow_surface, shadow_rect)
        
        # Vẽ nút với gradient
        pygame.draw.rect(screen, color, self.rect)
        
        # Vẽ highlight trên cùng
        highlight_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height // 3)
        highlight_color = tuple(min(255, c + 30) for c in color)
        pygame.draw.rect(screen, highlight_color, highlight_rect)
        
        # Vẽ viền
        border_color = (255, 255, 255) if self.is_hovered else (200, 200, 200)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Vẽ text với shadow
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        # Text shadow
        shadow_text = font.render(self.text, True, (0, 0, 0))
        shadow_rect = text_rect.move(2, 2)
        screen.blit(shadow_text, shadow_rect)
        
        # Text chính
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        """Kiểm tra chuột có hover không"""
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos):
        """Kiểm tra nút có được click không"""
        return self.rect.collidepoint(pos)

def draw_menu(screen, font, level_buttons):
    """Vẽ màn hình menu chọn level"""
    screen.fill(COLORS["background"])
    
    # Tiêu đề
    title_font = pygame.font.SysFont(None, 72)
    title = title_font.render("SOKUBAN", True, (255, 0, 0))
    title_rect = title.get_rect(center=(screen.get_width() // 2, 120))
    screen.blit(title, title_rect)
    
    # Vẽ các nút level
    subtitle = font.render("Select Level:", True, (0, 0, 0))
    subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, 200))
    screen.blit(subtitle, subtitle_rect)
    
    for button in level_buttons:
        button.draw(screen, font)

def draw_game_ui(screen, font, reset_button, menu_button, solve_button, level_idx):
    """Vẽ UI khi đang chơi với panel đẹp"""
    UI_HEIGHT = 80
    screen_width = screen.get_width()
    
    # Vẽ panel trên cùng với gradient và shadow
    panel_rect = pygame.Rect(0, 0, screen_width, UI_HEIGHT)
    
    # Vẽ shadow
    shadow_rect = pygame.Rect(0, UI_HEIGHT, screen_width, 5)
    shadow_surface = pygame.Surface((screen_width, 5))
    shadow_surface.set_alpha(100)
    shadow_surface.fill((0, 0, 0))
    screen.blit(shadow_surface, shadow_rect)
    
    # Vẽ background panel với gradient
    pygame.draw.rect(screen, (50, 50, 60), panel_rect)
    pygame.draw.rect(screen, (70, 70, 80), pygame.Rect(0, 0, screen_width, UI_HEIGHT // 2))
    
    # Vẽ viền dưới panel
    pygame.draw.line(screen, (100, 100, 110), (0, UI_HEIGHT - 1), (screen_width, UI_HEIGHT - 1), 2)
    
    # Vẽ thông tin level
    level_text = font.render(f"Level {level_idx + 1}", True, (255, 255, 255))
    screen.blit(level_text, (20, UI_HEIGHT // 2 - level_text.get_height() // 2))
    
    # Vẽ các nút
    reset_button.draw(screen, font)
    menu_button.draw(screen, font)
    solve_button.draw(screen, font)

def main():
    pygame.init()
    
    # Tạo màn hình menu với kích thước cố định
    MENU_WIDTH = 1000
    MENU_HEIGHT = 800
    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.display.set_caption("Sokoban")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    
    # Trạng thái game
    game_state = MENU
    level_idx = 0
    grid = None
    w, h = 0, 0
    
    # Tạo các nút level cho menu
    level_buttons = []
    button_width = 300
    button_height = 70
    button_spacing = 80
    start_x = MENU_WIDTH // 2 - button_width // 2
    start_y = 250
    
    for i in range(len(LEVELS)):
        y = start_y + i * button_spacing
        button = Button(start_x, y, button_width, button_height, 
                       f"Level {i + 1}", 
                       color=(100, 150, 200), 
                       hover_color=(120, 170, 220))
        level_buttons.append(button)
    
    # Nút chơi lại và thoát (khi đang chơi) - sẽ được căn giữa khi load level
    reset_button = Button(0, 15, 130, 50, "Replay", 
                         color=(200, 100, 100), 
                         hover_color=(240, 130, 130))
    menu_button = Button(0, 15, 130, 50, "Menu", 
                        color=(150, 150, 150), 
                        hover_color=(180, 180, 180))
    solve_button = Button(0, 15, 130, 50, "Solve", 
                         color=(100, 200, 100), 
                         hover_color=(130, 230, 130))
    
    # Biến cho solver
    solution = None
    solution_step = 0
    auto_play = False
    last_move_time = 0

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == MENU:
                    # Kiểm tra click vào nút level
                    for i, button in enumerate(level_buttons):
                        if button.is_clicked(mouse_pos):
                            level_idx = i
                            grid, w, h = load_level(level_idx)
                            # Tăng chiều cao màn hình để có không gian cho các nút
                            UI_HEIGHT = 80
                            screen_width = max(w * TILE + 40, 400)  # Đảm bảo màn hình đủ rộng
                            screen = pygame.display.set_mode((screen_width, h * TILE + UI_HEIGHT + 60))
                            # Căn giữa các nút
                            button_width = 130
                            button_height = 50
                            button_spacing = 15
                            # Tất cả các level đều có nút Solve
                            num_buttons = 3
                            total_width = button_width * num_buttons + button_spacing * (num_buttons - 1)
                            start_x = (screen_width - total_width) // 2
                            button_y = 15
                            reset_button.rect = pygame.Rect(start_x, button_y, button_width, button_height)
                            menu_button.rect = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height)
                            solve_button.rect = pygame.Rect(start_x + (button_width + button_spacing) * 2, button_y, button_width, button_height)
                            # Reset solver
                            solution = None
                            solution_step = 0
                            auto_play = False
                            game_state = PLAYING
                            break
                
                elif game_state == PLAYING:
                    # Kiểm tra click vào nút chơi lại
                    if reset_button.is_clicked(mouse_pos):
                        grid, w, h = load_level(level_idx)
                        solution = None
                        solution_step = 0
                        auto_play = False
                    # Kiểm tra click vào nút thoát
                    elif menu_button.is_clicked(mouse_pos):
                        game_state = MENU
                        screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
                        solution = None
                        solution_step = 0
                        auto_play = False
                    # Kiểm tra click vào nút Solve (tất cả các level)
                    elif solve_button.is_clicked(mouse_pos):
                        if solution is None:
                            # Chạy solver
                            print(f"Đang giải level {level_idx + 1} bằng A*...")
                            grid_copy = [list(row) for row in grid]
                            solution = astar_solve(grid_copy)
                            if solution:
                                print(f"Tìm thấy giải pháp: {len(solution)} bước")
                                solution_step = 0
                                auto_play = True
                            else:
                                print("Không tìm thấy giải pháp!")
                        else:
                            # Bật/tắt auto play
                            auto_play = not auto_play
            
            if event.type == pygame.KEYDOWN:
                if game_state == PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        game_state = MENU
                        screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
                    if event.key in (pygame.K_r, pygame.K_BACKSPACE):
                        grid, w, h = load_level(level_idx)  # reset level
                    if event.key == pygame.K_n:
                        level_idx = (level_idx + 1) % len(LEVELS)
                        grid, w, h = load_level(level_idx)
                        UI_HEIGHT = 80
                        screen_width = max(w * TILE + 40, 400)
                        screen = pygame.display.set_mode((screen_width, h * TILE + UI_HEIGHT + 60))
                        # Căn giữa các nút
                        button_width = 130
                        button_height = 50
                        button_spacing = 15
                        num_buttons = 3
                        total_width = button_width * num_buttons + button_spacing * (num_buttons - 1)
                        start_x = (screen_width - total_width) // 2
                        button_y = 15
                        reset_button.rect = pygame.Rect(start_x, button_y, button_width, button_height)
                        menu_button.rect = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height)
                        solve_button.rect = pygame.Rect(start_x + (button_width + button_spacing) * 2, button_y, button_width, button_height)
                        solution = None
                        solution_step = 0
                        auto_play = False
                    if event.key == pygame.K_p:
                        level_idx = (level_idx - 1) % len(LEVELS)
                        grid, w, h = load_level(level_idx)
                        UI_HEIGHT = 80
                        screen_width = max(w * TILE + 40, 400)
                        screen = pygame.display.set_mode((screen_width, h * TILE + UI_HEIGHT + 60))
                        # Căn giữa các nút
                        button_width = 130
                        button_height = 50
                        button_spacing = 15
                        num_buttons = 3
                        total_width = button_width * num_buttons + button_spacing * (num_buttons - 1)
                        start_x = (screen_width - total_width) // 2
                        button_y = 15
                        reset_button.rect = pygame.Rect(start_x, button_y, button_width, button_height)
                        menu_button.rect = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height)
                        solve_button.rect = pygame.Rect(start_x + (button_width + button_spacing) * 2, button_y, button_width, button_height)
                        solution = None
                        solution_step = 0
                        auto_play = False
                    if event.key in (pygame.K_UP, pygame.K_w):
                        move(grid, 0, -1)
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        move(grid, 0, 1)
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        move(grid, -1, 0)
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        move(grid, 1, 0)
        
        # Vẽ màn hình
        if game_state == MENU:
            # Cập nhật hover cho các nút
            for button in level_buttons:
                button.check_hover(mouse_pos)
            draw_menu(screen, font, level_buttons)
        
        elif game_state == PLAYING:
            # Cập nhật hover cho các nút
            reset_button.check_hover(mouse_pos)
            menu_button.check_hover(mouse_pos)
            solve_button.check_hover(mouse_pos)
            
            # Tự động chạy giải pháp
            if auto_play and solution and solution_step < len(solution):
                # Chờ một chút trước khi thực hiện bước tiếp theo
                import time
                current_time = time.time()
                
                if current_time - last_move_time > 0.5:  # 0.5 giây mỗi bước
                    direction = solution[solution_step]
                    direction_map = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}
                    if direction in direction_map:
                        dx, dy = direction_map[direction]
                        move(grid, dx, dy)
                    solution_step += 1
                    last_move_time = current_time
                    
                    # Dừng nếu hoàn thành
                    if solution_step >= len(solution) or is_completed(grid):
                        auto_play = False
            
            # Vẽ game với offset để tránh các nút và căn giữa
            screen.fill(COLORS["background"])
            UI_HEIGHT = 80
            # Tính toán offset_x để căn giữa map
            screen_width = screen.get_width()
            map_width = len(grid[0]) * TILE if grid else 0
            offset_x = (screen_width - map_width) // 2
            draw_grid(screen, grid, offset_y=UI_HEIGHT, offset_x=offset_x)
            
            # Vẽ UI panel đẹp với tất cả nút
            draw_game_ui(screen, font, reset_button, menu_button, solve_button, level_idx)
            
            # Thông báo hoàn thành với style đẹp
            if is_completed(grid):
                # Vẽ panel thông báo
                msg_y = h * TILE + UI_HEIGHT + 10
                msg_rect = pygame.Rect(10, msg_y, screen_width - 20, 40)
                pygame.draw.rect(screen, (50, 200, 50), msg_rect)
                pygame.draw.rect(screen, (30, 150, 30), msg_rect, 2)
                
                # Text với shadow
                text = font.render("Hoan thanh! Nhan N de choi level tiep theo", True, (255, 255, 255))
                text_rect = text.get_rect(center=msg_rect.center)
                shadow_text = font.render("Hoan thanh! Nhan N de choi level tiep theo", True, (0, 0, 0))
                screen.blit(shadow_text, text_rect.move(2, 2))
                screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()