import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Game state
game_state = "menu"  # "menu", "playing", "shop", "ai_menu", or "survival"

# Persistent total points
total_player_points = 0
total_opponent_points = 0

DURATION_OPTIONS = [5, 10, 15, 20]  # Seconds
duration_index = 0  # Default to first option

# Fonts
font = pygame.font.SysFont('calibri', 74)
timer_font = pygame.font.SysFont('calibri', 48)
button_font = pygame.font.SysFont('calibri', 50)
side_font = pygame.font.SysFont('calibri', 36)
# Game over message font (bolder and larger)
gameover_font = pygame.font.SysFont('calibri', 90, bold=True)

# Difficulty settings
difficulties = {
    "Easy": {"ball_speed": 4, "paddle_speed": 6},
    "Medium": {"ball_speed": 8, "paddle_speed": 8},
    "Hard": {"ball_speed": 12, "paddle_speed": 12}
}

# Button setup
button_width, button_height = 250, 80
button_spacing = 30
num_buttons = len(difficulties)
total_buttons_height = num_buttons * button_height + (num_buttons - 1) * button_spacing
button_y_start = HEIGHT // 2 - total_buttons_height // 2 + 40  # +40 for a bit more space below the title
difficulty_buttons = []
for i, diff in enumerate(difficulties):
    rect = pygame.Rect(
        WIDTH // 2 - button_width // 2,
        button_y_start + i * (button_height + button_spacing),
        button_width,
        button_height
    )
    difficulty_buttons.append((diff, rect))

# Colors (move up so they're available for button setup)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHTBLUE = (173, 216, 230)
WOOD_BROWN = (139, 69, 19)  # A classic wood brown
WOOD_BROWN_LIGHT = (205, 133, 63)
SOFT_BLUE = (100, 160, 255)
BALL_OUTLINE_COLOR = (220, 220, 220)

# Shop button setup
shop_button = pygame.Rect(30, HEIGHT - 80, 180, 50)
# AI mode button setup
ai_button = pygame.Rect(WIDTH - 210, HEIGHT - 80, 180, 50)
# Survival mode button setup
survival_button = pygame.Rect(WIDTH // 2 - 90, HEIGHT - 80, 180, 50)
shop_back_button_font = pygame.font.SysFont('calibri', 40, bold=True)
shop_back_button_text = shop_back_button_font.render("Back", True, WHITE)
shop_back_button_width = shop_back_button_text.get_width() + 40
shop_back_button_height = shop_back_button_text.get_height() + 20
shop_back_button = pygame.Rect(20, 20, shop_back_button_width, shop_back_button_height)
# Randomize button setup (to the right of back button)
shop_randomize_button_text = shop_back_button_font.render("Randomize", True, WHITE)
shop_randomize_button_width = shop_randomize_button_text.get_width() + 40
shop_randomize_button_height = shop_randomize_button_text.get_height() + 20
shop_randomize_button = pygame.Rect(shop_back_button.right + 20, 20, shop_randomize_button_width,
                                    shop_randomize_button_height)
# Shop pagination
shop_page = 0
BALLS_PER_PAGE = 6

# Paddle and ball settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
paddle_speed = 7
BALL_SIZE = 20
ball_speed = 5  # Constant ball speed
ball_speed_x, ball_speed_y = ball_speed, 0  # Start horizontally

# Positions
player = pygame.Rect(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
opponent = pygame.Rect(WIDTH - 20, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Score
player_score = 0
opponent_score = 0

# Buttons for game over
restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)
# Make back_button size fit the text better and use a smaller font
back_button_font = pygame.font.SysFont('calibri', 40)
back_button_text = back_button_font.render("Back to Menu", True, (255, 255, 255))
back_button_width = back_button_text.get_width() + 40
back_button_height = back_button_text.get_height() + 20
back_button = pygame.Rect(WIDTH // 2 - back_button_width // 2, HEIGHT // 2 + 80, back_button_width, back_button_height)

clock = pygame.time.Clock()

# Timer settings
GAME_DURATION = 20  # seconds
start_time = pygame.time.get_ticks()
game_over = False

# AI settings
ai_difficulty = "Medium"  # AI difficulty level
ai_reaction_delay = 0  # Frames of delay for AI reaction
is_ai_mode = False  # Track if we're in AI mode
ai_reaction_counter = 0  # Counter for AI reaction timing

# Survival mode settings
is_survival_mode = False  # Track if we're in survival mode
survival_paddles = []  # List of moving paddles
survival_score = 0  # Survival mode score
survival_time = 0  # Time survived
survival_difficulty = "Medium"  # Survival difficulty level
PADDLE_SPAWN_RATE = 120  # Frames between paddle spawns
paddle_spawn_counter = 0
MAX_PADDLES_ON_SCREEN = 3  # Maximum paddles allowed on screen at once

# Ball color shop
shop_colors = [
    {"name": "White", "color": (255, 255, 255), "price": 0, "bonus_points": 0},
    {"name": "Red", "color": (200, 0, 0), "price": 5, "bonus_points": 1},
    {"name": "Green", "color": (0, 200, 0), "price": 10, "bonus_points": 2},
    {"name": "Blue", "color": (0, 0, 200), "price": 15, "bonus_points": 3},
    {"name": "Yellow", "color": (200, 200, 0), "price": 20, "bonus_points": 4},
    {"name": "Light Blue", "color": (100, 170, 170), "price": 25, "bonus_points": 5},
    {"name": "Sparkly", "color": (255, 140, 0), "price": 40, "bonus_points": 6},
]
selected_ball_color = (255, 255, 255)  # Default white

# Track purchased colors
purchased_colors = {tuple(item["color"]): (item["price"] == 0) for item in shop_colors}

# Sparkle trail settings
SPARKLY_COLOR = (255, 140, 0)
sparkle_trail = []  # List of (x, y) positions
SPARKLE_TRAIL_LENGTH = 20


def reset_game():
    global player, opponent, ball, ball_speed_x, ball_speed_y, start_time, game_over, player_score, opponent_score
    player.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
    opponent.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
    # Randomize ball spawn position near center
    offset_x = random.randint(-40, 40)
    offset_y = random.randint(-40, 40)
    ball.center = (WIDTH // 2 + offset_x, HEIGHT // 2 + offset_y)
    # Simple ball initialization - mostly horizontal with slight vertical component
    sign_x = random.choice([-1, 1])
    ball_speed_x = sign_x * ball_speed
    ball_speed_y = random.randint(-2, 2)  # Small random vertical component
    start_time = pygame.time.get_ticks()
    game_over = False
    player_score = 0
    opponent_score = 0
    # Do NOT reset total_player_points or total_opponent_points here!


# Helper to get bonus points for selected ball
def get_selected_ball_bonus():
    for item in shop_colors:
        if tuple(item["color"]) == tuple(selected_ball_color):
            return item.get("bonus_points", 0)
    return 0


# AI paddle movement function
def move_ai_paddle():
    global opponent, ai_reaction_counter
    # Predict where the ball will be when it reaches the AI's side
    if ball_speed_x > 0:  # Ball moving toward AI
        # Calculate time to reach AI side
        time_to_reach = (WIDTH - ball.right) / ball_speed_x if ball_speed_x > 0 else 0
        # Predict ball's y position
        predicted_y = ball.centery + ball_speed_y * time_to_reach

        # Add prediction error based on difficulty
        if ai_difficulty == "Easy":
            # Easy AI: Moderate prediction errors - should hit about half the time
            predicted_y += random.randint(-35, 35)
            if random.random() < 0.05:  # 5% chance to not move at all
                return
        elif ai_difficulty == "Medium":
            # Medium AI: Moderate prediction errors
            predicted_y += random.randint(-25, 25)
        # Hard AI: Perfect prediction (no error)

        # Move AI paddle toward predicted position
        target_y = predicted_y - PADDLE_HEIGHT // 2

        # Add reaction delay based on difficulty
        if ai_difficulty == "Easy":
            reaction_delay = 5  # Moderate reaction delay
        elif ai_difficulty == "Medium":
            reaction_delay = 4  # Medium reaction
        else:  # Hard
            reaction_delay = 1  # Fast reaction

        # Apply reaction delay
        if ai_reaction_counter < reaction_delay:
            ai_reaction_counter += 1
            return
        ai_reaction_counter = 0

        # Move paddle with speed based on difficulty
        ai_speed = difficulties[ai_difficulty]["paddle_speed"]

        # Add some randomness to movement for more human-like behavior
        if ai_difficulty == "Easy":
            ai_speed = max(1, ai_speed - random.randint(0, 2))  # Slightly slower, less erratic
        elif ai_difficulty == "Medium":
            ai_speed = max(1, ai_speed - random.randint(0, 1))  # Slightly slower

        if opponent.centery < target_y and opponent.bottom < HEIGHT:
            opponent.y += ai_speed
        elif opponent.centery > target_y and opponent.top > 0:
            opponent.y -= ai_speed


# Survival mode functions
def spawn_survival_paddle():
    global survival_paddles
    # Randomly choose which side to spawn from
    side = random.choice(["top", "bottom", "left", "right"])

    # Set speed and size based on difficulty
    if survival_difficulty == "Easy":
        speed = 3  # Increased from 2
        spawn_rate = 140  # Faster spawn rate (was 180)
        paddle_length = 90  # Slightly bigger (was 80)
        max_paddles = 1  # Only one paddle at a time
    elif survival_difficulty == "Medium":
        speed = 4  # Increased from 3
        spawn_rate = 100  # Faster spawn rate (was 120)
        paddle_length = 100  # Same length for all paddles
        max_paddles = 2  # Up to two paddles at a time
    else:  # Hard
        speed = 6  # Much faster
        spawn_rate = 60  # Much faster spawn rate
        paddle_length = 120  # Same length for all paddles
        max_paddles = 4  # Up to four paddles at a time

    # Check if we can spawn more paddles
    if len(survival_paddles) >= max_paddles:
        return spawn_rate

    # Calculate paddle dimensions based on direction
    if side in ["top", "bottom"]:
        # Vertical paddles (horizontal movement)
        paddle_width, paddle_height = 15, paddle_length
    else:
        # Horizontal paddles (vertical movement)
        paddle_width, paddle_height = paddle_length, 15

    # Calculate spawn position to target the ball
    if side == "top":
        # Spawn above screen, target ball's x position
        target_x = ball.centerx - paddle_width // 2
        target_x = max(0, min(WIDTH - paddle_width, target_x))  # Keep within screen bounds
        paddle = pygame.Rect(target_x, -paddle_height, paddle_width, paddle_height)
        speed_x, speed_y = 0, speed
    elif side == "bottom":
        # Spawn below screen, target ball's x position
        target_x = ball.centerx - paddle_width // 2
        target_x = max(0, min(WIDTH - paddle_width, target_x))  # Keep within screen bounds
        paddle = pygame.Rect(target_x, HEIGHT, paddle_width, paddle_height)
        speed_x, speed_y = 0, -speed
    elif side == "left":
        # Spawn left of screen, target ball's y position
        target_y = ball.centery - paddle_height // 2
        target_y = max(0, min(HEIGHT - paddle_height, target_y))  # Keep within screen bounds
        paddle = pygame.Rect(-paddle_width, target_y, paddle_width, paddle_height)
        speed_x, speed_y = speed, 0
    else:  # right
        # Spawn right of screen, target ball's y position
        target_y = ball.centery - paddle_height // 2
        target_y = max(0, min(HEIGHT - paddle_height, target_y))  # Keep within screen bounds
        paddle = pygame.Rect(WIDTH, target_y, paddle_width, paddle_height)
        speed_x, speed_y = -speed, 0

    survival_paddles.append({"rect": paddle, "speed_x": speed_x, "speed_y": speed_y})
    return spawn_rate


def update_survival_paddles():
    global survival_paddles, survival_score
    for paddle in survival_paddles[:]:
        paddle["rect"].x += paddle["speed_x"]
        paddle["rect"].y += paddle["speed_y"]

        # Remove paddles that are off screen
        if (paddle["rect"].right < 0 or paddle["rect"].left > WIDTH or
                paddle["rect"].bottom < 0 or paddle["rect"].top > HEIGHT):
            survival_paddles.remove(paddle)
            survival_score += 1  # Score for surviving each paddle


def check_survival_collision():
    global survival_paddles
    for paddle in survival_paddles:
        if ball.colliderect(paddle["rect"]):
            return True
    return False


while True:
    if game_state == "menu":
        screen.fill(LIGHTBLUE)
        title = button_font.render("Select Difficulty", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Draw wooden frame (thick border)
        frame_thickness = 24
        pygame.draw.rect(screen, WOOD_BROWN, (0, 0, WIDTH, HEIGHT), frame_thickness)
        pygame.draw.rect(screen, WOOD_BROWN_LIGHT,
                         (frame_thickness, frame_thickness, WIDTH - 2 * frame_thickness, HEIGHT - 2 * frame_thickness),
                         6)

        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()

        for diff, rect in difficulty_buttons:
            pygame.draw.rect(screen, SOFT_BLUE, rect, border_radius=14)
            pygame.draw.rect(screen, WHITE, rect, 4, border_radius=14)
            text = button_font.render(diff, True, WHITE)
            screen.blit(text, (rect.x + (rect.width - text.get_width()) // 2,
                               rect.y + (rect.height - text.get_height()) // 2))
        # Draw the shop button
        pygame.draw.rect(screen, (0, 180, 100), shop_button)
        shop_text = button_font.render("Shop", True, WHITE)
        screen.blit(shop_text, (shop_button.x + (shop_button.width - shop_text.get_width()) // 2,
                                shop_button.y + (shop_text.get_height() - shop_text.get_height()) // 2))
        # Check for AI button hover
        ai_button_hovered = ai_button.collidepoint(mouse_pos)

        # Draw the AI mode button
        ai_button_color = (200, 0, 120) if ai_button_hovered else (180, 0, 100)
        pygame.draw.rect(screen, ai_button_color, ai_button)
        ai_text = button_font.render("AI Mode", True, WHITE)
        screen.blit(ai_text, (ai_button.x + (ai_button.width - ai_text.get_width()) // 2,
                              ai_button.y + (ai_text.get_height() - ai_text.get_height()) // 2))

        # Draw hover message for AI mode button
        if ai_button_hovered:
            # Use a smaller font for the hover message
            hover_font = pygame.font.SysFont('calibri', 24)
            hover_text = hover_font.render("Play vs AI - No coins from AI points", True, (0, 0, 0))
            # Position the hover text above the button to avoid overlap with survival button
            hover_x = ai_button.x + (ai_button.width - hover_text.get_width()) // 2
            hover_y = ai_button.y - hover_text.get_height() - 10

            # Keep message within screen bounds
            if hover_x < 10:
                hover_x = 10
            elif hover_x + hover_text.get_width() > WIDTH - 10:
                hover_x = WIDTH - hover_text.get_width() - 10
            if hover_y < 10:
                hover_y = ai_button.bottom + 10  # Move below button if not enough space above

            # Draw background for hover text
            hover_bg = pygame.Rect(hover_x - 10, hover_y - 5, hover_text.get_width() + 20, hover_text.get_height() + 10)
            pygame.draw.rect(screen, (255, 255, 255), hover_bg, border_radius=8)
            pygame.draw.rect(screen, (0, 0, 0), hover_bg, 2, border_radius=8)
            screen.blit(hover_text, (hover_x, hover_y))

        # Draw the survival mode button
        survival_button_hovered = survival_button.collidepoint(mouse_pos)
        survival_button_color = (200, 100, 0) if survival_button_hovered else (180, 80, 0)
        pygame.draw.rect(screen, survival_button_color, survival_button)
        survival_text = button_font.render("Survival", True, WHITE)
        screen.blit(survival_text, (survival_button.x + (survival_button.width - survival_text.get_width()) // 2,
                                    survival_button.y + (survival_text.get_height() - survival_text.get_height()) // 2))

        # Draw hover message for survival mode button
        if survival_button_hovered:
            hover_font = pygame.font.SysFont('calibri', 24)
            hover_text = hover_font.render("Control ball, avoid paddles", True, (0, 0, 0))
            # Position the hover text to the left of the button
            hover_x = survival_button.x - hover_text.get_width() - 15
            hover_y = survival_button.y + (survival_button.height - hover_text.get_height()) // 2
            # Draw background for hover text
            hover_bg = pygame.Rect(hover_x - 10, hover_y - 5, hover_text.get_width() + 20, hover_text.get_height() + 10)
            pygame.draw.rect(screen, (255, 255, 255), hover_bg, border_radius=8)
            pygame.draw.rect(screen, (0, 0, 0), hover_bg, 2, border_radius=8)
            screen.blit(hover_text, (hover_x, hover_y))
        # Draw coin visual for currency
        currency = total_player_points + total_opponent_points
        coin_radius = 20
        coin_x = WIDTH - 20 - coin_radius
        coin_y = 20 + coin_radius
        pygame.draw.circle(screen, (255, 215, 0), (coin_x, coin_y), coin_radius)
        coin_symbol = side_font.render("$", True, (255, 255, 255))
        screen.blit(coin_symbol, (coin_x - coin_symbol.get_width() // 2, coin_y - coin_symbol.get_height() // 2))
        currency_text = side_font.render(str(currency), True, (0, 0, 0))
        space_between = 16
        currency_text_x = coin_x - coin_radius - space_between - currency_text.get_width()
        currency_text_y = coin_y - currency_text.get_height() // 2
        screen.blit(currency_text, (currency_text_x, currency_text_y))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for diff, rect in difficulty_buttons:
                    if rect.collidepoint(mouse_pos):
                        # Set speeds based on difficulty
                        ball_speed = difficulties[diff]["ball_speed"]
                        ball_speed_x = ball_speed
                        ball_speed_y = 0
                        paddle_speed = difficulties[diff]["paddle_speed"]
                        # Reset positions and scores
                        reset_game()
                        game_state = "playing"
                        is_ai_mode = False  # Regular 2-player mode
                if shop_button.collidepoint(mouse_pos):
                    game_state = "shop"
                if ai_button.collidepoint(mouse_pos):
                    game_state = "ai_menu"
                if survival_button.collidepoint(mouse_pos):
                    game_state = "survival_menu"
        continue  # Skip the rest of the loop until a difficulty is chosen

    if game_state == "shop":
        screen.fill(LIGHTBLUE)
        title = button_font.render("Ball Color Shop", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Draw wooden frame (thick border)
        frame_thickness = 24
        pygame.draw.rect(screen, WOOD_BROWN, (0, 0, WIDTH, HEIGHT), frame_thickness)
        pygame.draw.rect(screen, WOOD_BROWN_LIGHT,
                         (frame_thickness, frame_thickness, WIDTH - 2 * frame_thickness, HEIGHT - 2 * frame_thickness),
                         6)

        # Pagination logic
        total_pages = (len(shop_colors) + BALLS_PER_PAGE - 1) // BALLS_PER_PAGE
        start_idx = shop_page * BALLS_PER_PAGE
        end_idx = min(start_idx + BALLS_PER_PAGE, len(shop_colors))
        page_colors = shop_colors[start_idx:end_idx]

        # Grid settings (neater)
        cols = 3
        rows = 2
        ball_radius = 36
        grid_h_spacing = 200  # horizontal space between centers
        grid_v_spacing = 150  # vertical space between centers
        grid_start_x = WIDTH // 2 - ((cols - 1) * grid_h_spacing) // 2
        grid_start_y = 220

        shop_buttons = []
        hovered_ball = None
        mouse_pos = pygame.mouse.get_pos()
        for idx, item in enumerate(page_colors):
            row = idx // cols
            col = idx % cols
            ball_x = grid_start_x + col * grid_h_spacing
            ball_y = grid_start_y + row * grid_v_spacing
            rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
            # Draw the ball color
            pygame.draw.circle(screen, item["color"], (ball_x, ball_y), ball_radius)
            # Draw border for selected
            if tuple(item["color"]) == tuple(selected_ball_color):
                pygame.draw.circle(screen, (255, 215, 0), (ball_x, ball_y), ball_radius + 4, 4)
            # Draw border for owned but not selected
            elif purchased_colors.get(tuple(item["color"]), False):
                pygame.draw.circle(screen, (0, 200, 0), (ball_x, ball_y), ball_radius + 2, 2)
            # Draw price below (with coin visual)
            price_y = ball_y + ball_radius + 10
            price_text = side_font.render(f"{item['price']}", True, BLACK)
            coin_radius_small = 12
            coin_x = ball_x + price_text.get_width() // 2 + coin_radius_small + 6
            coin_y = price_y + price_text.get_height() // 2
            screen.blit(price_text, (ball_x - price_text.get_width() // 2, price_y))
            pygame.draw.circle(screen, (255, 215, 0), (coin_x, coin_y), coin_radius_small)
            coin_symbol_small = side_font.render("$", True, (255, 255, 255))
            screen.blit(coin_symbol_small,
                        (coin_x - coin_symbol_small.get_width() // 2, coin_y - coin_symbol_small.get_height() // 2))
            # If owned, show 'Owned'
            if purchased_colors.get(tuple(item["color"]), False):
                owned_text = side_font.render("Owned", True, (0, 128, 0))
                screen.blit(owned_text, (ball_x - owned_text.get_width() // 2, ball_y + ball_radius + 35))
            shop_buttons.append((item, rect, ball_x, ball_y))
            # Detect hover
            if rect.collidepoint(mouse_pos):
                hovered_ball = (item, ball_x, ball_y)

        # Draw effect info popup if hovering over a ball
        if hovered_ball:
            item, ball_x, ball_y = hovered_ball
            effect_lines = []
            if item.get("bonus_points", 0) > 0:
                effect_lines.append(f"+{item['bonus_points']} pts/goal")
            else:
                effect_lines.append("No bonus effect")
            # You can add more effects here in the future
            # Popup box settings
            popup_width = 180
            popup_height = 40 + 30 * len(effect_lines)
            popup_x = ball_x + ball_radius + 30
            popup_y = ball_y - popup_height // 2
            # Keep popup inside screen
            if popup_x + popup_width > WIDTH:
                popup_x = ball_x - ball_radius - 30 - popup_width
            # Draw popup background
            pygame.draw.rect(screen, (255, 255, 255), (popup_x, popup_y, popup_width, popup_height), border_radius=16)
            pygame.draw.rect(screen, (0, 128, 255), (popup_x, popup_y, popup_width, popup_height), 3, border_radius=16)
            # Draw effect text
            for i, line in enumerate(effect_lines):
                effect_text = side_font.render(line, True, (0, 0, 0))
                screen.blit(effect_text,
                            (popup_x + (popup_width - effect_text.get_width()) // 2, popup_y + 20 + i * 30))

        # Draw pagination arrows if needed (softer blue with white outline)
        arrow_size = 50
        arrow_y = HEIGHT // 2
        arrow_color = SOFT_BLUE
        # Left arrow
        if shop_page > 0:
            left_arrow = pygame.Rect(60, arrow_y - arrow_size // 2, arrow_size, arrow_size)
            pygame.draw.polygon(screen, arrow_color, [
                (left_arrow.right, left_arrow.top),
                (left_arrow.left, left_arrow.centery),
                (left_arrow.right, left_arrow.bottom)
            ])
            pygame.draw.polygon(screen, WHITE, [
                (left_arrow.right, left_arrow.top),
                (left_arrow.left, left_arrow.centery),
                (left_arrow.right, left_arrow.bottom)
            ], 4)
        else:
            left_arrow = None
        # Right arrow
        if shop_page < total_pages - 1:
            right_arrow = pygame.Rect(WIDTH - 60 - arrow_size, arrow_y - arrow_size // 2, arrow_size, arrow_size)
            pygame.draw.polygon(screen, arrow_color, [
                (right_arrow.left, right_arrow.top),
                (right_arrow.right, right_arrow.centery),
                (right_arrow.left, right_arrow.bottom)
            ])
            pygame.draw.polygon(screen, WHITE, [
                (right_arrow.left, right_arrow.top),
                (right_arrow.right, right_arrow.centery),
                (right_arrow.left, right_arrow.bottom)
            ], 4)
        else:
            right_arrow = None

        # Back button
        # Draw shadow
        shadow_offset = 3
        shadow_rect = shop_back_button.move(shadow_offset, shadow_offset)
        pygame.draw.rect(screen, (80, 120, 180), shadow_rect, border_radius=14)
        # Draw button
        pygame.draw.rect(screen, SOFT_BLUE, shop_back_button, border_radius=14)
        pygame.draw.rect(screen, WHITE, shop_back_button, 4, border_radius=14)
        # Draw text
        screen.blit(shop_back_button_text,
                    (shop_back_button.x + (shop_back_button.width - shop_back_button_text.get_width()) // 2,
                     shop_back_button.y + (shop_back_button.height - shop_back_button_text.get_height()) // 2))
        # Randomize button (same style, to the right of back button)
        randomize_shadow_rect = shop_randomize_button.move(shadow_offset, shadow_offset)
        pygame.draw.rect(screen, (80, 120, 180), randomize_shadow_rect, border_radius=14)
        pygame.draw.rect(screen, SOFT_BLUE, shop_randomize_button, border_radius=14)
        pygame.draw.rect(screen, WHITE, shop_randomize_button, 4, border_radius=14)
        screen.blit(shop_randomize_button_text, (shop_randomize_button.x + (
                shop_randomize_button.width - shop_randomize_button_text.get_width()) // 2,
                                                 shop_randomize_button.y + (
                                                         shop_randomize_button.height - shop_randomize_button_text.get_height()) // 2))
        # Show the randomized ball visual to the right of the randomize button
        visual_ball_radius = 32
        visual_ball_x = shop_randomize_button.right + 40 + visual_ball_radius
        visual_ball_y = shop_randomize_button.y + shop_randomize_button.height // 2
        pygame.draw.circle(screen, selected_ball_color, (visual_ball_x, visual_ball_y), visual_ball_radius)
        # Draw border for clarity
        pygame.draw.circle(screen, WHITE, (visual_ball_x, visual_ball_y), visual_ball_radius + 3, 3)
        # Draw coin/currency as before
        currency = total_player_points + total_opponent_points
        coin_radius = 20
        coin_x = WIDTH - 20 - coin_radius
        coin_y = 20 + coin_radius
        pygame.draw.circle(screen, (255, 215, 0), (coin_x, coin_y), coin_radius)
        coin_symbol = side_font.render("$", True, (255, 255, 255))
        screen.blit(coin_symbol, (coin_x - coin_symbol.get_width() // 2, coin_y - coin_symbol.get_height() // 2))
        currency_text = side_font.render(str(currency), True, (0, 0, 0))
        space_between = 16
        currency_text_x = coin_x - coin_radius - space_between - currency_text.get_width()
        currency_text_y = coin_y - currency_text.get_height() // 2
        screen.blit(currency_text, (currency_text_x, currency_text_y))
        pygame.display.flip()

        # Shop event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for item, rect, _, _ in shop_buttons:
                    if rect.collidepoint(mouse_pos):
                        color_tuple = tuple(item["color"])
                        if purchased_colors.get(color_tuple, False):
                            selected_ball_color = item["color"]
                        elif currency >= item["price"]:
                            selected_ball_color = item["color"]
                            purchased_colors[color_tuple] = True
                            spent = item["price"]
                            if total_player_points >= spent:
                                total_player_points -= spent
                            else:
                                spent -= total_player_points
                                total_player_points = 0
                                total_opponent_points = max(0, total_opponent_points - spent)
                # Randomize button click
                if shop_randomize_button.collidepoint(mouse_pos):
                    if currency >= 1:
                        # Deduct 1 coin
                        if total_player_points >= 1:
                            total_player_points -= 1
                        else:
                            total_opponent_points = max(0, total_opponent_points - 1)
                        # Randomly select any RGB color
                        selected_ball_color = (
                            random.randint(0, 255),
                            random.randint(0, 255),
                            random.randint(0, 255)
                        )
                # Pagination arrow clicks
                if left_arrow and left_arrow.collidepoint(mouse_pos):
                    shop_page = max(0, shop_page - 1)
                if right_arrow and right_arrow.collidepoint(mouse_pos):
                    shop_page = min(total_pages - 1, shop_page + 1)
                if shop_back_button.collidepoint(mouse_pos):
                    game_state = "menu"
        continue  # Skip the rest of the loop while in shop

    if game_state == "ai_menu":
        screen.fill(LIGHTBLUE)
        title = button_font.render("Select AI Difficulty", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Draw wooden frame (thick border)
        frame_thickness = 24
        pygame.draw.rect(screen, WOOD_BROWN, (0, 0, WIDTH, HEIGHT), frame_thickness)
        pygame.draw.rect(screen, WOOD_BROWN_LIGHT,
                         (frame_thickness, frame_thickness, WIDTH - 2 * frame_thickness, HEIGHT - 2 * frame_thickness),
                         6)

        for diff, rect in difficulty_buttons:
            pygame.draw.rect(screen, SOFT_BLUE, rect, border_radius=14)
            pygame.draw.rect(screen, WHITE, rect, 4, border_radius=14)
            text = button_font.render(diff, True, WHITE)
            screen.blit(text, (rect.x + (rect.width - text.get_width()) // 2,
                               rect.y + (rect.height - text.get_height()) // 2))

        # Back button
        pygame.draw.rect(screen, SOFT_BLUE, shop_back_button, border_radius=14)
        pygame.draw.rect(screen, WHITE, shop_back_button, 4, border_radius=14)
        screen.blit(shop_back_button_text,
                    (shop_back_button.x + (shop_back_button.width - shop_back_button_text.get_width()) // 2,
                     shop_back_button.y + (shop_back_button.height - shop_back_button_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for diff, rect in difficulty_buttons:
                    if rect.collidepoint(mouse_pos):
                        # Set AI difficulty and speeds
                        ai_difficulty = diff
                        ball_speed = difficulties[diff]["ball_speed"]
                        ball_speed_x = ball_speed
                        ball_speed_y = 0
                        paddle_speed = difficulties[diff]["paddle_speed"]
                        # Reset positions and scores
                        reset_game()
                        game_state = "playing"
                        is_ai_mode = True  # AI mode
                if shop_back_button.collidepoint(mouse_pos):
                    game_state = "menu"
        continue  # Skip the rest of the loop while in AI menu

    if game_state == "survival_menu":
        screen.fill(LIGHTBLUE)
        title = button_font.render("Select Survival Difficulty", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Draw wooden frame (thick border)
        frame_thickness = 24
        pygame.draw.rect(screen, WOOD_BROWN, (0, 0, WIDTH, HEIGHT), frame_thickness)
        pygame.draw.rect(screen, WOOD_BROWN_LIGHT,
                         (frame_thickness, frame_thickness, WIDTH - 2 * frame_thickness, HEIGHT - 2 * frame_thickness),
                         6)

        for diff, rect in difficulty_buttons:
            pygame.draw.rect(screen, SOFT_BLUE, rect, border_radius=14)
            pygame.draw.rect(screen, WHITE, rect, 4, border_radius=14)
            text = button_font.render(diff, True, WHITE)
            screen.blit(text, (rect.x + (rect.width - text.get_width()) // 2,
                               rect.y + (rect.height - text.get_height()) // 2))

        # Back button
        pygame.draw.rect(screen, SOFT_BLUE, shop_back_button, border_radius=14)
        pygame.draw.rect(screen, WHITE, shop_back_button, 4, border_radius=14)
        screen.blit(shop_back_button_text,
                    (shop_back_button.x + (shop_back_button.width - shop_back_button_text.get_width()) // 2,
                     shop_back_button.y + (shop_back_button.height - shop_back_button_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for diff, rect in difficulty_buttons:
                    if rect.collidepoint(mouse_pos):
                        # Start survival mode with selected difficulty
                        survival_difficulty = diff
                        is_survival_mode = True
                        is_ai_mode = False
                        reset_game()
                        survival_paddles.clear()
                        survival_score = 0
                        survival_time = 0
                        paddle_spawn_counter = 0
                        # Center the ball and give it a slow speed
                        ball.center = (WIDTH // 2, HEIGHT // 2)
                        ball_speed = 4
                        ball_speed_x, ball_speed_y = 0, 0
                        game_state = "playing"
                if shop_back_button.collidepoint(mouse_pos):
                    game_state = "menu"
        continue  # Skip the rest of the loop while in survival menu

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if restart_button.collidepoint(mouse_pos):
                reset_game()
            if back_button.collidepoint(mouse_pos):
                game_state = "menu"
                reset_game()
                game_over = False

    # Timer logic
    elapsed = (pygame.time.get_ticks() - start_time) // 1000  # seconds
    time_left = max(0, GAME_DURATION - elapsed)

    # Game over check and update total points
    if time_left == 0 and not game_over:
        game_over = True
        total_player_points += player_score
        # Only add opponent points to total if not in AI mode
        if not is_ai_mode:
            total_opponent_points += opponent_score

        # Only allow movement and ball if game is not over
    if not game_over:
        keys = pygame.key.get_pressed()

        if is_survival_mode:
            # Survival mode: Player controls the ball
            ball_speed = 4
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                ball_speed_y = -ball_speed
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                ball_speed_y = ball_speed
            else:
                ball_speed_y = 0

            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                ball_speed_x = -ball_speed
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                ball_speed_x = ball_speed
            else:
                ball_speed_x = 0

                # Update survival mode
            survival_time += 1
            paddle_spawn_counter += 1

            # Get spawn rate based on difficulty
            if survival_difficulty == "Easy":
                spawn_rate = 140  # Faster spawn rate
            elif survival_difficulty == "Medium":
                spawn_rate = 100  # Faster spawn rate
            else:  # Hard
                spawn_rate = 60  # Much faster for hard mode

            if paddle_spawn_counter >= spawn_rate:
                spawn_survival_paddle()
                paddle_spawn_counter = 0
            update_survival_paddles()

            # Check for collision with survival paddles
            if check_survival_collision():
                game_over = True
                # Convert survival score to coins (1 point = 1 coin)
                total_player_points += survival_score

        else:
            # Regular modes: Player controls paddles
            # Left paddle (W/S) - always player controlled
            if keys[pygame.K_w] and player.top > 0:
                player.y -= paddle_speed
            if keys[pygame.K_s] and player.bottom < HEIGHT:
                player.y += paddle_speed

            # Right paddle - AI controlled if in AI mode, otherwise player controlled
            if is_ai_mode:
                # AI controls the right paddle
                move_ai_paddle()
            else:
                # Player controls both paddles (original mode)
                if keys[pygame.K_UP] and opponent.top > 0:
                    opponent.y -= paddle_speed
                if keys[pygame.K_DOWN] and opponent.bottom < HEIGHT:
                    opponent.y += paddle_speed

                # Ball movement
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Sparkle trail update (for Sparkly ball in all modes)
        if tuple(selected_ball_color) == SPARKLY_COLOR:
            sparkle_trail.append(ball.center)
            if len(sparkle_trail) > SPARKLE_TRAIL_LENGTH:
                sparkle_trail.pop(0)
        else:
            sparkle_trail.clear()

        # Collision with top/bottom (only in regular modes)
        if not is_survival_mode:
            if ball.top <= 0:
                ball.top = 0  # Ensure ball doesn't go above screen
                ball_speed_y = abs(ball_speed_y)  # Force downward movement
            elif ball.bottom >= HEIGHT:
                ball.bottom = HEIGHT  # Ensure ball doesn't go below screen
                ball_speed_y = -abs(ball_speed_y)  # Force upward movement

                # Collision with paddles (only in regular modes)
        if not is_survival_mode:
            # Only check paddle collision if ball is moving toward the paddle
            if ball.colliderect(player) and ball_speed_x < 0:
                ball.left = player.right  # Move ball just outside the paddle
                # Calculate hit position: -1 (top) to 1 (bottom)
                rel = ((ball.centery - player.centery) / (PADDLE_HEIGHT / 2))
                # Simple bounce physics - reverse x direction and adjust y based on hit position
                ball_speed_x = abs(ball_speed_x)  # Move right
                ball_speed_y = int(rel * ball_speed * 0.6)  # Reduced multiplier for less extreme angles
                # Ensure minimum vertical movement
                if abs(ball_speed_y) < 2:
                    ball_speed_y = 2 if ball_speed_y >= 0 else -2
            if ball.colliderect(opponent) and ball_speed_x > 0:
                ball.right = opponent.left  # Move ball just outside the paddle
                rel = ((ball.centery - opponent.centery) / (PADDLE_HEIGHT / 2))
                ball_speed_x = -abs(ball_speed_x)  # Move left
                ball_speed_y = int(rel * ball_speed * 0.6)  # Reduced multiplier for less extreme angles
                if abs(ball_speed_y) < 2:
                    ball_speed_y = 2 if ball_speed_y >= 0 else -2

        # Survival mode wall collision (game over)
        if is_survival_mode:
            if ball.top <= 0 or ball.bottom >= HEIGHT or ball.left <= 0 or ball.right >= WIDTH:
                game_over = True
                total_player_points += survival_score

        # Clamp ball position within play area after any collision
        if ball.top < 0:
            ball.top = 0
        if ball.bottom > HEIGHT:
            ball.bottom = HEIGHT
        if ball.left < 0:
            ball.left = 0
        if ball.right > WIDTH:
            ball.right = WIDTH

        # Scoring
        if ball.left <= 0:
            opponent_score += 1
            # Reset ball with consistent speed
            offset_x = random.randint(-40, 40)
            offset_y = random.randint(-40, 40)
            ball.center = (WIDTH // 2 + offset_x, HEIGHT // 2 + offset_y)
            # Ball goes to player with consistent speed
            angle = random.uniform(-0.3, 0.3)
            ball_speed_x = -int(ball_speed * (1 - abs(angle)))
            ball_speed_y = int(ball_speed * angle)
            if abs(ball_speed_y) < 1:
                ball_speed_y = random.choice([-1, 1])
        if ball.right >= WIDTH:
            player_score += 1
            # Add bonus points for selected ball
            player_score += get_selected_ball_bonus()
            # Reset ball with consistent speed
            offset_x = random.randint(-40, 40)
            offset_y = random.randint(-40, 40)
            ball.center = (WIDTH // 2 + offset_x, HEIGHT // 2 + offset_y)
            # Ball goes to opponent with consistent speed
            angle = random.uniform(-0.3, 0.3)
            ball_speed_x = int(ball_speed * (1 - abs(angle)))
            ball_speed_y = int(ball_speed * angle)
            if abs(ball_speed_y) < 1:
                ball_speed_y = random.choice([-1, 1])

    # Drawing
    screen.fill(LIGHTBLUE)

    if is_survival_mode:
        # Draw survival paddles with gradient effect
        for paddle in survival_paddles:
            # Create a gradient effect based on paddle position
            if paddle["speed_x"] != 0:  # Horizontal paddles
                color_intensity = min(255, 150 + abs(paddle["rect"].x) // 2)
            else:  # Vertical paddles
                color_intensity = min(255, 150 + abs(paddle["rect"].y) // 2)
            paddle_color = (255, 100, 100) if color_intensity < 200 else (255, 150, 150)
            pygame.draw.rect(screen, paddle_color, paddle["rect"])
            # Add a subtle border
            pygame.draw.rect(screen, (200, 50, 50), paddle["rect"], 2)
    else:
        # Draw regular paddles
        pygame.draw.rect(screen, WHITE, player)
        pygame.draw.rect(screen, WHITE, opponent)

    # Draw sparkle trail if Sparkly ball is selected (works in all modes)
    if tuple(selected_ball_color) == SPARKLY_COLOR and len(sparkle_trail) > 1:
        for i, pos in enumerate(sparkle_trail):
            # Fade out older sparkles
            alpha = int(255 * (i + 1) / len(sparkle_trail))
            sparkle_surface = pygame.Surface((BALL_SIZE, BALL_SIZE), pygame.SRCALPHA)
            # Random offset for sparkle effect
            offset_x = random.randint(-6, 6)
            offset_y = random.randint(-6, 6)
            # Draw a small sparkle (circle)
            pygame.draw.circle(sparkle_surface, (255, 255, 180, alpha), (BALL_SIZE // 2, BALL_SIZE // 2), 4)
            # Optionally, add a second smaller sparkle for more effect
            pygame.draw.circle(sparkle_surface, (255, 255, 255, alpha), (BALL_SIZE // 2 + 2, BALL_SIZE // 2 - 2), 2)
            screen.blit(sparkle_surface, (pos[0] - BALL_SIZE // 2 + offset_x, pos[1] - BALL_SIZE // 2 + offset_y))

    # Draw grayish white outline for the ball
    outline_rect = ball.inflate(8, 8)
    pygame.draw.ellipse(screen, BALL_OUTLINE_COLOR, outline_rect)
    pygame.draw.ellipse(screen, selected_ball_color, ball)

    # Draw center line (only in regular modes)
    if not is_survival_mode:
        pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    # Current game scores
    if is_survival_mode:
        # Survival mode scoring - cleaner layout
        survival_text = font.render(f"Score: {survival_score}", True, WHITE)
        screen.blit(survival_text, (WIDTH // 2 - survival_text.get_width() // 2, 20))
        time_text = side_font.render(f"Time: {survival_time // 60}s", True, WHITE)
        screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 70))
        # Show coin conversion info
        coin_text = side_font.render(f"= {survival_score} coins", True, (255, 215, 0))  # Gold color
        screen.blit(coin_text, (WIDTH // 2 - coin_text.get_width() // 2, 100))
    else:
        # Regular mode scoring
        player_text = font.render(str(player_score), True, WHITE)
        screen.blit(player_text, (WIDTH // 4, 20))
        opponent_text = font.render(str(opponent_score), True, WHITE)
        screen.blit(opponent_text, (WIDTH * 3 // 4, 20))

    # Show AI mode indicator
    if is_ai_mode:
        # Color code the AI difficulty
        if ai_difficulty == "Easy":
            ai_color = (100, 255, 100)  # Green for easy
        elif ai_difficulty == "Medium":
            ai_color = (255, 255, 100)  # Yellow for medium
        else:  # Hard
            ai_color = (255, 100, 100)  # Red for hard

        ai_indicator = side_font.render(f"AI: {ai_difficulty}", True, ai_color)
        screen.blit(ai_indicator, (WIDTH - ai_indicator.get_width() - 20, 60))
        player_indicator = side_font.render("Player", True, (100, 255, 100))
        screen.blit(player_indicator, (20, 60))

    # Draw total points on the sides (only in regular modes)
    if not is_survival_mode:
        player_total_text = side_font.render(f"Total: {total_player_points}", True, (0, 0, 0))
        opponent_total_text = side_font.render(f"Total: {total_opponent_points}", True, (0, 0, 0))
        screen.blit(player_total_text, (20, HEIGHT - 50))
        screen.blit(opponent_total_text, (WIDTH - opponent_total_text.get_width() - 20, HEIGHT - 50))

    # Draw timer (only in regular modes)
    if not is_survival_mode:
        timer_text = timer_font.render(f"Time Left: {time_left}", True, (0, 0, 0))
        screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 20 + font.get_height()))

    # Draw restart and back to menu buttons if game over
    if game_over:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        # Draw game over message with drop shadow and border
        if is_survival_mode:
            msg_text = f"Game Over! Earned {survival_score} coins!"
        else:
            msg_text = "Time's up!"
        # Use a softer off-white color for the message
        msg = gameover_font.render(msg_text, True, (230, 230, 230))
        shadow = gameover_font.render(msg_text, True, (0, 0, 0))
        # Calculate box size and position based on text
        rect_width = msg.get_width() + 40
        rect_height = msg.get_height() + 30
        rect_x = WIDTH // 2 - rect_width // 2
        rect_y = HEIGHT // 2 - 120 - 10
        # Draw rounded rectangle box first
        pygame.draw.rect(screen, (255, 255, 255, 60), (rect_x, rect_y, rect_width, rect_height), border_radius=24)
        # Draw drop shadow
        shadow_x = WIDTH // 2 - shadow.get_width() // 2 + 4
        shadow_y = rect_y + (rect_height - shadow.get_height()) // 2 + 4
        screen.blit(shadow, (shadow_x, shadow_y))
        # Draw main text centered in the box
        msg_x = WIDTH // 2 - msg.get_width() // 2
        msg_y = rect_y + (rect_height - msg.get_height()) // 2
        screen.blit(msg, (msg_x, msg_y))

        # Add more spacing between message and buttons
        button_spacing = 30
        # Calculate total height for both buttons and spacing
        total_buttons_height = restart_button.height + back_button.height + button_spacing
        buttons_top = msg_y + msg.get_height() + 40  # 40px below the message

        # Center Restart button
        restart_button.x = WIDTH // 2 - restart_button.width // 2
        restart_button.y = buttons_top
        button_text = back_button_font.render("Restart", True, (255, 255, 255))
        pygame.draw.rect(screen, (0, 90, 255), restart_button, border_radius=12)
        screen.blit(button_text, (restart_button.x + (restart_button.width - button_text.get_width()) // 2,
                                  restart_button.y + (restart_button.height - button_text.get_height()) // 2))

        # Center Back to Menu button below Restart
        back_button.x = WIDTH // 2 - back_button.width // 2
        back_button.y = restart_button.y + restart_button.height + button_spacing
        pygame.draw.rect(screen, SOFT_BLUE, back_button, border_radius=18)
        pygame.draw.rect(screen, WHITE, back_button, 4, border_radius=18)
        screen.blit(back_button_text, (back_button.x + (back_button.width - back_button_text.get_width()) // 2,
                                       back_button.y + (back_button.height - back_button_text.get_height()) // 2))

    pygame.display.flip()
    clock.tick(90)
