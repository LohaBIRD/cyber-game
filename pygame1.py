import pygame
import sys
import random
import os
from pygame.locals import *
import drone
import requests 
import threading 

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700

API_URL = "https://leaderboard-api-e1y7.onrender.com"

def submit_score(player, score):
    def send():
        try:
            print("Sending score to:", API_URL)

            res = requests.post(
                f"{API_URL}/submit_score",
                json={"user": player, "score": score},
                timeout=3
            )

            print("STATUS:", res.status_code)
            print("RESPONSE:", res.text)

        except Exception as e:
            print("FAILED REQUEST:", e)

    threading.Thread(target=send).start()


def get_leaderboard():
    try:
        response = requests.get(f"{API_URL}/leaderboard", timeout=3)
        if response.status_code == 200:
            return response.json()
        else:
            print("Leaderboard error:", response.text)
            return []
    except Exception as e:
        print("Failed to fetch leaderboard:", e)
        return []

def reset_scores_admin():
    try:
        response = requests.post(f"{API_URL}/admin/reset_scores", timeout=3)
        if response.status_code == 200:
            return True, "Scores reset!"
        return False, f"Reset failed: {response.status_code}"
    except Exception as e:
        return False, f"Reset error: {e}"
    
try:
    pygame.init()
    pygame.joystick.init()
except pygame.error as e:
    print(f"Failed to initialize Pygame: {e}")
    sys.exit(1)

# Initialize joystick
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    pass

# Set up the display (full screen)
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error as e:
    print(f"Failed to set display mode: {e}")
    sys.exit(1) 

pygame.display.set_caption("Cybersecurity Firewall Protection Game")

# Load background image
try:
    background = pygame.image.load('actualgame/background.jpg').convert()
    background = pygame.transform.smoothscale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except (pygame.error, FileNotFoundError) as e:
    print(f"Failed to load background image (using solid color): {e}")
    background = None

# Load character image
try:
    character_image = pygame.image.load('actualgame/trollface.jpg').convert_alpha()
    character_image = pygame.transform.scale(character_image, (30, 50))
except (pygame.error, FileNotFoundError) as e:
    print(f"Failed to load character image: {e}")
    character_image = None

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
PIPE_GREEN = (0, 128, 0)
BRICK_RED = (178, 34, 34)
GRAY = (128, 128, 128)
CYBER_DARK_BLUE = (0, 10, 30)
CYBER_GRID_GREEN = (0, 50, 40)

# Font
try:
    font = pygame.font.SysFont('Consolas', 28, bold=True)
    small_font = pygame.font.SysFont('Consolas', 22)
except pygame.error as e:
    print(f"Failed to load Consolas font: {e}")
    font = pygame.font.SysFont('Courier New', 24, bold=True)
    small_font = pygame.font.SysFont('Courier New', 18)

questions = [
    ("What is a 'Zero-Day Exploit'?", ["A vulnerability unknown to the software creator", "A bug found on the first day of release", "A virus that infects in zero seconds"]),
    ("What is a 'DDoS' attack?", ["Flooding a server with traffic to shut it down", "Deleting a server's data", "Stealing a server's identity"]),
    ("What is a 'Honeypot' in cybersecurity?", ["A decoy system to attract and trap attackers", "A database of stolen passwords", "A highly secure server"]),
    ("What is 'Social Engineering'?", ["Tricking people to gain access to data", "A type of network architecture", "A social media virus"]),
    ("What does 'Malware' stand for?", ["Malicious Software", "Multiple Advertisements", "Mainframe Hardware"]),
    ("What is the main purpose of a 'Firewall'?", ["Monitor and filter network traffic", "Protect a computer from heat", "To make websites load faster"]),
    ("What is 'Phishing'?", ["Using fake emails to steal information", "A method to cool down a CPU", "Searching for bugs in code"]),
    ("What is 'Two-Factor Authentication' (2FA)?", ["Using two different methods to verify identity", "Using two passwords for one account", "A login that takes two seconds"]),
    ("What is 'Ransomware'?", ["Software that encrypts files and demands payment", "A program that holds a user's mouse hostage", "A free anti-virus trial"]),
    ("Which of these is the STRONGEST password?", ["Tr0ub4d&r!_77", "Password12345", "MyDogSparky"]),
    ("What is a 'VPN' (Virtual Private Network)?", ["Encrypts your internet traffic and hides your IP", "A virus that attacks private networks", "A high-speed internet connection"]),
    ("What is 'Spyware'?", ["Software that secretly monitors your activity", "A program that helps you 'spy' bugs", "A camera security system"]),
    ("What does 'HTTPS' in a URL mean?", ["The connection is secure and encrypted", "The website is high-speed", "The website has high-definition pictures"]),
    ("What is a 'Botnet'?", ["A network of infected computers controlled by one person", "A 'net' to catch spam emails", "A friendly AI robot"]),
    ("What is 'Encryption'?", ["Scrambling data so it can't be read without a key", "Deleting data permanently", "Compressing a file to make it smaller"])
]

def draw_text(text, font, color, x, y):
    try:
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))
    except pygame.error as e:
        pass

def draw_cyber_background(surface):
    top_color = (75, 0, 130)  
    bottom_color = (138, 43, 226)  
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

def draw_hearts(hearts, x, y):
    for i in range(3):
        heart_x = x + i * 30
        if i < hearts:
            pygame.draw.circle(screen, RED, (heart_x + 5, y - 5), 5)
            pygame.draw.circle(screen, RED, (heart_x + 15, y - 5), 5)
            pygame.draw.polygon(screen, RED, [(heart_x, y), (heart_x + 10, y - 10), (heart_x + 20, y)])
        else:
            pygame.draw.circle(screen, BLACK, (heart_x + 5, y - 5), 5, 1)
            pygame.draw.circle(screen, BLACK, (heart_x + 15, y - 5), 5, 1)
            pygame.draw.polygon(screen, BLACK, [(heart_x, y), (heart_x + 10, y - 10), (heart_x + 20, y)], 1)

# Initialize drone BEFORE the game starts running
drone_connected = False

try:
    drone.init_drone()
    drone_connected = True
    print("Drone connected 🚁")
except Exception as e:
    print("Drone NOT connected, continuing without it:", e)

def main():
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 30)
    leaderboard = []
    last_fetch_time = 0
    running = True    
    state = 'start' 
    score_sent = False
    admin_sequence = ""
    admin_panel_visible = False
    admin_message = ""
    admin_message_timer = 0
    
    player_number = ""
    player_name = ""

    current_question_text = ""
    current_options = []
    current_correct_answer = ""

    score = 0
    hearts = 3
    feedback = ''
    feedback_timer = 0
    character_x = 100
    character_speed = 5
    ground = SCREEN_HEIGHT - 100
    character_y = ground - 50
    character_vy = 0
    gravity = 0.5
    jump_power = -15
    on_ground = True
    can_double_jump = True
    want_to_fall = False
    camera_x = 0
    platform_speed = 0
    invincible_timer = 0
    fallen_into_hole = False

    platforms = []
    lethal_blocks = []
    holes = []
    question_circles = [] 
    character_width = 20

    section_length = 800
    def generate_section(start_x):
        section_platforms = []
        section_lethal = []
        section_holes = []
        section_question_circles = [] 
        all_blocks = [] 

        x = start_x
        while x < start_x + section_length:
            choice = random.choices(
                ['hole', 'platform', 'moving', 'brick', 'box', 'car', 'branch', 'pipe', 'goomba', 'question_circle', 'empty'],
                weights=[0.05, 0.2, 0.1, 0.08, 0.08, 0.05, 0.05, 0.05, 0.05, 0.04, 0.25], 
                k=1
            )[0]

            if start_x == 0 and x < start_x + 200 and choice in ['hole', 'platform', 'brick', 'box', 'car', 'branch', 'pipe', 'goomba', 'moving', 'question_circle']:
                choice = 'empty'

            if choice == 'hole':
                hole_width = random.randint(80, 160)
                new_rect = pygame.Rect(x, ground - 20, hole_width, 20)
                overlap = any(new_rect.colliderect(pygame.Rect(b[0], b[1], b[2], b[3])) for b in all_blocks)
                if not overlap:
                    section_holes.append((x, hole_width))
                    all_blocks.append([x, ground - 20, hole_width, 20])
                    x += hole_width + random.randint(30, 80)
                else:
                    x += random.randint(30, 80)
            elif choice in ['platform', 'brick', 'box', 'car', 'branch']:
                platform_width = random.choice([80, 100, 120, 150])
                platform_height = 20
                platform_y = random.choice([ground - 50, ground - 100, ground - 150, ground - 200])
                new_rect = pygame.Rect(x, platform_y, platform_width, platform_height)
                overlap = any(new_rect.colliderect(pygame.Rect(b[0], b[1], b[2], b[3])) for b in all_blocks)
                hole_overlap = any(hole_x <= x < hole_x + hole_width or x <= hole_x < x + platform_width for hole_x, hole_width in section_holes)
                if not overlap and not hole_overlap:
                    section_platforms.append([x, platform_y, platform_width, platform_height, choice, 0])
                    all_blocks.append([x, platform_y, platform_width, platform_height])
                    x += platform_width + random.randint(20, 50)
                else:
                    x += random.randint(30, 80)
            elif choice == 'moving':
                platform_width = random.choice([80, 100, 120])
                platform_height = 20
                platform_y = random.choice([ground - 100, ground - 150, ground - 200])
                speed = random.choice([1, -1]) * random.randint(1, 2)
                left_limit = x - random.randint(50, 100)
                right_limit = x + platform_width + random.randint(50, 100)
                new_rect = pygame.Rect(x, platform_y, platform_width, platform_height)
                overlap = any(new_rect.colliderect(pygame.Rect(b[0], b[1], b[2], b[3])) for b in all_blocks)
                if not overlap:
                    section_platforms.append([x, platform_y, platform_width, platform_height, 'moving', speed, left_limit, right_limit])
                    all_blocks.append([x, platform_y, platform_width, platform_height])
                    x += platform_width + random.randint(20, 50)
                else:
                    x += random.randint(30, 80)
            elif choice == 'pipe':
                pipe_width = 40
                pipe_height = random.choice([100, 150, 200])
                pipe_y = ground - pipe_height
                new_rect = pygame.Rect(x, pipe_y, pipe_width, pipe_height)
                overlap = any(new_rect.colliderect(pygame.Rect(b[0], b[1], b[2], b[3])) for b in all_blocks)
                if not overlap:
                    section_platforms.append([x, pipe_y, pipe_width, pipe_height, 'pipe', 0])
                    all_blocks.append([x, pipe_y, pipe_width, pipe_height])
                    x += pipe_width + random.randint(20, 50)
                else:
                    x += random.randint(30, 80)
            elif choice == 'goomba':
                goomba_width = 20
                goomba_height = 20
                goomba_y = ground - goomba_height
                speed = random.choice([1, -1]) * 1
                left_limit = x - random.randint(50, 100)
                right_limit = x + goomba_width + random.randint(50, 100)
                new_rect = pygame.Rect(x, goomba_y, goomba_width, goomba_height)
                overlap = any(new_rect.colliderect(pygame.Rect(b[0], b[1], b[2], b[3])) for b in all_blocks)
                if not overlap:
                    section_lethal.append([x, goomba_y, goomba_width, goomba_height, 'goomba', speed, left_limit, right_limit])
                    all_blocks.append([x, goomba_y, goomba_width, goomba_height])
                    x += goomba_width + random.randint(20, 50)
                else:
                    x += random.randint(30, 80)
            elif choice == 'question_circle':
                radius = 15
                qc_x_center = x + radius
                qc_y_center = ground - radius
                new_rect = pygame.Rect(x, qc_y_center - radius, radius * 2, radius * 2)
                overlap = any(new_rect.colliderect(pygame.Rect(b[0], b[1], b[2], b[3])) for b in all_blocks)
                if not overlap:
                    section_question_circles.append((qc_x_center, qc_y_center))
                    all_blocks.append([x, qc_y_center - radius, radius * 2, radius * 2])
                    x += (radius * 2) + random.randint(20, 50)
                else:
                    x += random.randint(30, 80)
            else:
                x += random.randint(30, 80)
        
        return section_platforms, section_lethal, section_holes, section_question_circles

    def level_reset():
        nonlocal character_x, character_y, character_vy, on_ground, camera_x, platforms, lethal_blocks, holes, question_circles, current_max_x, invincible_timer, fallen_into_hole
        character_x = 100
        character_y = ground - 50
        character_vy = 0
        on_ground = True
        camera_x = 0
        platforms, lethal_blocks, holes, question_circles = generate_section(0)
        current_max_x = section_length
        invincible_timer = 600
        fallen_into_hole = False

    platforms, lethal_blocks, holes, question_circles = generate_section(0)
    current_max_x = section_length

    def is_character_over_hole():
        character_left = character_x
        character_right = character_x + character_width
        for hole_x, hole_width in holes:
            hole_right = hole_x + hole_width
            if character_right > hole_x and character_left < hole_right:
                return True
        return False
    
    while running:
        

    

    # 🔥 YOUR EXISTING CODE CONTINUES
        if state == 'game_over' and not score_sent:
            print("🔥 Sending score:", score)
            submit_score("player" + player_number, score)
            score_sent = True

        delta_time = clock.get_time()
        keys = pygame.key.get_pressed()
        
        if state == 'question' or state == 'popup_question' or state == 'feedback':
            screen.fill((0, 100, 200))  # blue color
        else:
            screen.fill(BLACK) 

        if state == 'question' or state == 'popup_question' or state == 'feedback':
            current_x = 0
            sorted_holes = sorted(holes, key=lambda h: h[0])
            for h in sorted_holes:
                hole_x, hole_width = h
                screen_hole_x = hole_x - camera_x
                screen_hole_end = screen_hole_x + hole_width
                if screen_hole_x > current_x:
                    pygame.draw.rect(screen, GRASS_GREEN, (current_x, ground, screen_hole_x - current_x, 20))
                current_x = max(current_x, screen_hole_end)
            if current_x < SCREEN_WIDTH:
                pygame.draw.rect(screen, GRASS_GREEN, (current_x, ground, SCREEN_WIDTH - current_x, 20))

       
        for event in pygame.event.get():

    # ALWAYS HANDLE QUIT
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                is_equals_press = (
                    event.key in (pygame.K_EQUALS, pygame.K_KP_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS)
                    or event.unicode in ("=", "+")
                )

                if is_equals_press:
                    admin_sequence = (admin_sequence + "=")[-3:]
                    if admin_sequence == "===":
                        admin_panel_visible = not admin_panel_visible
                        admin_sequence = ""
                        admin_message = "Admin panel opened" if admin_panel_visible else "Admin panel closed"
                        admin_message_timer = 180
                else:
                    admin_sequence = ""

                if admin_panel_visible:
                    if event.key == pygame.K_h:
                        admin_panel_visible = False
                        admin_message = "Admin panel closed"
                        admin_message_timer = 180
                    elif event.key == pygame.K_r:
                        ok, msg = reset_scores_admin()
                        admin_message = msg
                        admin_message_timer = 240
                        if ok:
                            leaderboard = get_leaderboard()
                            score = 0
                    elif event.key == pygame.K_l:
                        leaderboard = get_leaderboard()
                        admin_message = "Leaderboard refreshed"
                        admin_message_timer = 180
                    continue

            # =========================
            # START SCREEN INPUT
            # =========================
            if state == "start":
                if event.type == pygame.KEYDOWN:

                    if event.unicode.isdigit() and len(player_number) < 4:
                        player_number += event.unicode

                    elif event.key == pygame.K_BACKSPACE:
                        player_number = player_number[:-1]

                    elif event.key == pygame.K_RETURN and player_number != "":
                        state = "question"

                continue  # STOP everything else


            # =========================
            # GAME INPUT
            # =========================
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                if state == "question":

                    if event.key == pygame.K_SPACE and on_ground:
                        character_vy = jump_power
                        on_ground = False
                        want_to_fall = False

                    elif event.key == pygame.K_SPACE and can_double_jump and not on_ground:
                        character_vy = jump_power
                        can_double_jump = False

                    elif event.key == pygame.K_DOWN and on_ground:
                        want_to_fall = True
                        on_ground = False

                elif state == "popup_question":

                    selected = -1

                    if event.key == pygame.K_1:
                        selected = 0
                    elif event.key == pygame.K_2:
                        selected = 1
                    elif event.key == pygame.K_3:
                        selected = 2

                    if selected != -1:
                        selected_answer_text = current_options[selected]

                        if selected_answer_text == current_correct_answer:
                            feedback = "Correct!"
                            score += 1
                        else:
                            feedback = f"Incorrect. Correct was: {current_correct_answer}"
                            drone.trigger_flight()

                        state = "feedback"
                        feedback_timer = 4000

                elif state == "life_lost":
                    if event.key == pygame.K_r:
                        level_reset()
                        state = "question"

                elif state == "game_over":
                    if event.key == pygame.K_r:
                        state = "question"
                        score = 0
                        hearts = 3
                        level_reset()
                    elif event.key == pygame.K_q:
                        running = False
                        
                        if state == "start":
                            screen.fill((10, 10, 30))

                            font = pygame.font.Font(None, 80)
                            small_font = pygame.font.Font(None, 40)

                            title = font.render("DRONE ATTACK", True, (255, 255, 255))
                            input_text = font.render(player_number, True, (0, 255, 0))
                            hint = small_font.render("Enter ID - Press ENTER", True, (200, 200, 200))

                            screen.blit(title, (SCREEN_WIDTH//2 - 250, 150))
                            screen.blit(input_text, (SCREEN_WIDTH//2 - 50, 300))
                            screen.blit(hint, (SCREEN_WIDTH//2 - 250, 400))

                            pygame.display.flip()
                            continue

        if state == 'question':
            died_this_frame = False
            if invincible_timer > 0:
                invincible_timer -= 1

            new_x = character_x
            if (keys[pygame.K_LEFT] or (joystick and joystick.get_axis(0) < -0.5)) and character_x > 0:
                new_x -= character_speed
            if keys[pygame.K_RIGHT] or (joystick and joystick.get_axis(0) > 0.5):
                new_x += character_speed

            can_move = True
            character_rect = pygame.Rect(new_x - camera_x, character_y, 20, 50)
            for block in lethal_blocks + platforms:
                block_rect = pygame.Rect(block[0] - camera_x, block[1], block[2], block[3])
                if character_rect.colliderect(block_rect):
                    can_move = False
                    break

            if can_move:
                character_x = new_x

            if character_x > SCREEN_WIDTH // 2:
                camera_x = character_x - SCREEN_WIDTH // 2
            elif character_x < camera_x + SCREEN_WIDTH // 2 and camera_x > 0:
                camera_x = character_x - SCREEN_WIDTH // 2
                if camera_x < 0:
                    camera_x = 0

            if camera_x + SCREEN_WIDTH > current_max_x - 500:
                new_p, new_l, new_h, new_qc = generate_section(current_max_x)
                platforms.extend(new_p)
                lethal_blocks.extend(new_l)
                holes.extend(new_h)
                question_circles.extend(new_qc)
                current_max_x += section_length

            if camera_x > 1000:
                platforms = [p for p in platforms if p[0] > camera_x - 1000]
                lethal_blocks = [l for l in lethal_blocks if l[0] > camera_x - 1000]
                holes = [h for h in holes if h[0] > camera_x - 1000]
                question_circles = [qc for qc in question_circles if qc[0] > camera_x - 1000]

            on_ground = False
            platform_speed = 0
            for p in platforms:
                if len(p) > 5 and p[4] == 'moving':
                    p[0] += p[5]
                    if len(p) > 7:
                        if p[0] <= p[6] or p[0] + p[2] >= p[7]:
                            p[5] = -p[5]
            for l in lethal_blocks:
                if len(l) > 5 and l[4] == 'goomba':
                    next_x = l[0] + l[5]
                    goomba_rect_next = pygame.Rect(next_x, l[1], l[2], l[3])
                    will_fall = False
                    for h in holes:
                        hole_x, hole_width = h
                        hole_rect = pygame.Rect(hole_x, ground, hole_width, 20)
                        if goomba_rect_next.colliderect(hole_rect):
                            will_fall = True
                            break
                    if will_fall:
                        l[5] = -l[5] 
                    else:
                        safe_to_move = True
                        for h in holes:
                            hole_x, hole_width = h
                            if (l[0] + l[2] > hole_x and l[0] < hole_x + hole_width):
                                safe_to_move = False
                                break
                        if safe_to_move:
                            l[0] += l[5]
                        else:
                            l[5] = -l[5]  
                        if len(l) > 7:
                            if l[0] <= l[6]:
                                l[0] = l[6]
                                l[5] = -l[5]
                            elif l[0] + l[2] >= l[7]:
                                l[0] = l[7] - l[2]
                                l[5] = -l[5]
            if not on_ground:
                all_blocks = platforms
                for p in all_blocks:
                    p_rect = pygame.Rect(p[0], p[1], p[2], p[3])
                    temp_y = character_y + character_vy
                    temp_rect = pygame.Rect(character_x, temp_y, 20, 50)
                    if temp_rect.colliderect(p_rect) and character_vy > 0:
                        character_y = p[1] - 50
                        character_vy = 0
                        on_ground = True
                        can_double_jump = True
                        if len(p) > 5:
                            platform_speed = p[5]
                        break
                for p in all_blocks:
                    p_rect = pygame.Rect(p[0], p[1], p[2], p[3])
                    temp_y = character_y + character_vy
                    temp_rect = pygame.Rect(character_x, temp_y, 20, 50)
                    if temp_rect.colliderect(p_rect) and character_vy < 0:
                        character_y = p[1] + p[3]
                        character_vy = 0
                        break
                character_vy += gravity
                character_y += character_vy
                over_ground = not is_character_over_hole()
                if over_ground and character_y + 50 >= ground:
                    character_y = ground - 50
                    character_vy = 0
                    on_ground = True
            if on_ground:
                standing_on_something = False
                all_blocks = platforms + lethal_blocks
                for p in all_blocks:
                    p_rect = pygame.Rect(p[0], p[1], p[2], p[3])
                    c_rect = pygame.Rect(character_x, character_y, 20, 50)
                    if c_rect.colliderect(p_rect) and character_y + 50 >= p[1] and character_y + 50 <= p[1] + 10:
                        standing_on_something = True
                        character_y = p[1] - 50
                        break
                if not standing_on_something:
                    over_ground = not is_character_over_hole()
                    if over_ground and character_y + 50 >= ground and character_y + 50 <= ground + 10:
                        standing_on_something = True
                        character_y = ground - 50
                if not standing_on_something:
                    on_ground = False
            character_x += platform_speed

            if not died_this_frame:
                for block in lethal_blocks:
                    block_rect = pygame.Rect(block[0] - camera_x, block[1], block[2], block[3])
                    character_rect = pygame.Rect(character_x - camera_x, character_y, 20, 50)
                    if character_rect.colliderect(block_rect) and invincible_timer <= 0:
                        if len(block) > 4 and block[4] == 'goomba':
                            if character_vy > 0 and (character_y - character_vy + 50) <= block[1]:
                                lethal_blocks.remove(block)
                                character_vy = jump_power * 0.75  
                                can_double_jump = True
                                break  
                            else:
                                died_this_frame = True
                                drone.trigger_flight() # Drone trigger on Goomba Death
                                hearts -= 1
                                if hearts > 0:
                                    state = 'life_lost'
                                else:
                                    state = 'game_over'
                                    score_sent = False
                                break
                        else:
                            died_this_frame = True
                            drone.trigger_flight() # Drone trigger on Pipe Death
                            hearts -= 1
                            if hearts > 0:
                                state = 'life_lost'
                            else:
                                state = 'game_over'
                                score_sent = False
                            break

            if (not on_ground) and is_character_over_hole() and (character_y + 50 >= ground):
                fallen_into_hole = True

            if character_y > ground and fallen_into_hole and not died_this_frame and invincible_timer <= 0:
                died_this_frame = True
                drone.trigger_flight() # Drone trigger on falling into a hole
                hearts -= 1
                if hearts > 0:
                    state = 'life_lost'
                else:
                    state = 'game_over'
            
            if not died_this_frame:
                player_rect_world = pygame.Rect(character_x, character_y, 20, 50) 
                for i, qc in enumerate(question_circles):
                    qc_x_center, qc_y_center = qc
                    radius = 15
                    circle_rect_world = pygame.Rect(qc_x_center - radius, qc_y_center - radius, radius * 2, radius * 2)

                    if player_rect_world.colliderect(circle_rect_world):
                        state = 'popup_question'
                        question_circles.pop(i) 
                        
                        q_tuple = questions[random.randint(0, len(questions) - 1)]
                        current_question_text = q_tuple[0]
                        current_options = list(q_tuple[1]) 
                        current_correct_answer = q_tuple[1][0] 
                        random.shuffle(current_options) 
                        break
        if state == "start":
            screen.fill((10, 10, 30))

            title = font.render("DRONE ATTACK", True, (255, 255, 255))
            input_text = font.render("Player" + player_number, True, (0, 255, 0))
            hint = small_font.render("Enter up to 4 numbers - Press ENTER", True, (200, 200, 200))

            screen.blit(title, (SCREEN_WIDTH//2 - 250, 150))
            screen.blit(input_text, (SCREEN_WIDTH//2 - 150, 300))
            screen.blit(hint, (SCREEN_WIDTH//2 - 250, 400))

            pygame.display.flip()
            continue
        draw_text(f"SCORE: {score}", small_font, YELLOW, 10, 10)
        draw_hearts(hearts, SCREEN_WIDTH - 100, 10)

        if state == 'question' or state == 'popup_question' or state == 'feedback':
            for block in platforms:
                x, y, w, h, typ = block[0], block[1], block[2], block[3], block[4]
                x = x - camera_x
                if typ == 'brick':
                    pygame.draw.rect(screen, BROWN, (x, y, w, h))
                    pygame.draw.line(screen, BLACK, (x, y + h//2), (x + w, y + h//2), 1)
                    pygame.draw.line(screen, BLACK, (x + w//2, y), (x + w//2, y + h), 1)
                elif typ == 'box':
                    pygame.draw.rect(screen, BLUE, (x, y, w, h))
                elif typ == 'car':
                    pygame.draw.rect(screen, BLACK, (x, y, w, h))
                    pygame.draw.circle(screen, BLACK, (x + 10, y + h), 5)
                    pygame.draw.circle(screen, BLACK, (x + w - 10, y + h), 5)
                elif typ == 'branch':
                    pygame.draw.rect(screen, BROWN, (x, y, w, h))
                elif typ == 'moving':
                    pygame.draw.rect(screen, CYAN, (x, y, w, h))
                    pygame.draw.line(screen, BLACK, (x, y + h//2), (x + w, y + h//2), 1)
                    pygame.draw.line(screen, BLACK, (x + w//2, y), (x + w//2, y + h), 1)
                elif typ == 'pipe':
                    pygame.draw.rect(screen, PIPE_GREEN, (x, y, w, h))
                    pygame.draw.rect(screen, PIPE_GREEN, (x - 10, y, w + 20, 20))
                elif typ == 'platform':
                    pygame.draw.rect(screen, GRAY, (x, y, w, h))
            
            for qc in question_circles:
                qc_x_center, qc_y_center = qc
                screen_x = int(qc_x_center - camera_x)
                if 0 < screen_x < SCREEN_WIDTH:
                    pygame.draw.circle(screen, GREEN, (screen_x, int(qc_y_center)), 15)
                    draw_text("?", font, WHITE, screen_x - 5, int(qc_y_center) - 10)

            for block in lethal_blocks:
                x, y, w, h = block[0] - camera_x, block[1], block[2], block[3]
                typ = block[4] if len(block) > 4 else 'lethal'
                if typ == 'goomba':
                    pygame.draw.rect(screen, BROWN, (x, y, w, h))
                    pygame.draw.circle(screen, BLACK, (x + 5, y + 5), 2)
                    pygame.draw.circle(screen, BLACK, (x + 15, y + 5), 2)
                elif typ == 'pipe':
                    pygame.draw.rect(screen, PIPE_GREEN, (x, y, w, h))
                    pygame.draw.rect(screen, PIPE_GREEN, (x - 10, y, w + 20, 20))
                else:
                    pygame.draw.rect(screen, RED, (x, y, w, h))
            
            if state == 'question':
                if character_image:
                    screen.blit(character_image, (character_x - camera_x, character_y))
                else:
                    pygame.draw.rect(screen, BROWN, (character_x - camera_x, character_y, 20, 20))
                    pygame.draw.circle(screen, WHITE, (character_x - camera_x + 10, character_y - 10), 8)
                    pygame.draw.line(screen, BLACK, (character_x - camera_x + 10, character_y - 2), (character_x - camera_x + 10, character_y - 10), 2)
                    pygame.draw.line(screen, BLACK, (character_x - camera_x + 2, character_y + 20), (character_x - camera_x + 2, character_y + 50), 2)
                    pygame.draw.line(screen, BLACK, (character_x - camera_x + 8, character_y + 20), (character_x - camera_x + 8, character_y + 50), 2)
                    pygame.draw.line(screen, BLACK, (character_x - camera_x + 12, character_y + 20), (character_x - camera_x + 12, character_y + 50), 2)
                    pygame.draw.line(screen, BLACK, (character_x - camera_x + 18, character_y + 20), (character_x - camera_x + 18, character_y + 50), 2)
                    pygame.draw.line(screen, BLACK, (character_x - camera_x + 5, character_y - 15), (character_x - camera_x + 5, character_y - 5), 2)
                    pygame.draw.line(screen, BLACK, (character_x - camera_x + 15, character_y - 15), (character_x - camera_x + 15, character_y - 5), 2)
                    pygame.draw.line(screen, BLACK, (character_x - camera_x, character_y + 10), (character_x - camera_x - 5, character_y + 15), 2)
        
        if state == 'popup_question':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)) 
            screen.blit(overlay, (0, 0))

            box_width = SCREEN_WIDTH * 0.7
            box_height = SCREEN_HEIGHT * 0.6
            box_x = (SCREEN_WIDTH - box_width) / 2
            box_y = (SCREEN_HEIGHT - box_height) / 2
            pygame.draw.rect(screen, BLUE, (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 5)

            q = current_question_text
            opts = current_options
            
            draw_text(f"QUESTION:", font, YELLOW, box_x + 20, box_y + 20)
            words = q.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if font.size(test_line)[0] < box_width - 40:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line) 
            
            line_y = box_y + 60
            for line in lines:
                draw_text(line, font, WHITE, box_x + 20, line_y)
                line_y += 30

            opt_y = line_y + 40
            for i, opt in enumerate(opts):
                full_option_text = f"{i+1}) {opt}"
                
                words = full_option_text.split()
                lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    if font.size(test_line)[0] < box_width - 80:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = "  " + word + " "
                lines.append(current_line)
                
                for line in lines:
                    if opt_y < (box_y + box_height - 90): 
                        draw_text(line, font, WHITE, box_x + 40, opt_y)
                    opt_y += 30 
                
                opt_y += 10 
            
            footer_y = box_y + box_height - 90
            pygame.draw.rect(screen, BLACK, (box_x, footer_y, box_width, 90))
            pygame.draw.rect(screen, WHITE, (box_x, footer_y, box_width, 90), 2) 

            draw_text("Press 1, 2, or 3 to Answer", font, YELLOW, box_x + 20, footer_y + 40)
            if joystick:
                draw_text("Think Carefully!", font, CYAN, box_x + 20, footer_y + 10)

        elif state == 'feedback':
            feedback_timer -= delta_time
            if feedback_timer <= 0:
                state = 'question' 
            
            feedback_color = RED if "Incorrect" in feedback else GREEN
            
            box_width = SCREEN_WIDTH * 0.8
            box_x = (SCREEN_WIDTH - box_width) / 2
            box_y = 250
            
            words = feedback.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if font.size(test_line)[0] < box_width - 40:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line) 

            text_height = len(lines) * 30
            box_height = text_height + 40 
            box_y = (SCREEN_HEIGHT - box_height - 80) // 2 
            
            pygame.draw.rect(screen, BLACK, (box_x - 10, box_y - 10, box_width + 20, box_height + 20))
            pygame.draw.rect(screen, feedback_color, (box_x - 10, box_y - 10, box_width + 20, box_height + 20), 2)
            
            line_y = box_y + 20
            for line in lines:
                line_surface = font.render(line, True, feedback_color)
                line_width = line_surface.get_size()[0]
                line_x = (SCREEN_WIDTH - line_width) // 2 
                draw_text(line, font, feedback_color, line_x, line_y)
                line_y += 30
            
            timer_bar_y = box_y + box_height + 30
            timer_bar_width = (feedback_timer / 4000) * (SCREEN_WIDTH * 0.5) 
            timer_bar_x = (SCREEN_WIDTH * 0.25)
            pygame.draw.rect(screen, WHITE, (timer_bar_x - 2, timer_bar_y - 2, (SCREEN_WIDTH * 0.5) + 4, 24))
            pygame.draw.rect(screen, BLACK, (timer_bar_x, timer_bar_y, SCREEN_WIDTH * 0.5, 20))
            pygame.draw.rect(screen, YELLOW, (timer_bar_x, timer_bar_y, timer_bar_width, 20))

        elif state == 'life_lost':
            life_lost_surface = font.render("LIFE LOST!", True, RED)
            life_lost_width = life_lost_surface.get_size()[0]
            draw_text("LIFE LOST!", font, RED, (SCREEN_WIDTH - life_lost_width) // 2, 200)
            restart_surface = small_font.render("PRESS R TO RESTART LEVEL", True, WHITE)
            restart_width = restart_surface.get_size()[0]
            draw_text("PRESS R TO RESTART LEVEL", small_font, WHITE, (SCREEN_WIDTH - restart_width) // 2, 250)
        
        elif state == 'game_over':
            game_over_surface = font.render("GAME OVER!", True, RED)
            game_over_width = game_over_surface.get_size()[0]
            draw_text("GAME OVER!", font, RED, (SCREEN_WIDTH - game_over_width) // 2, 200)
            restart_quit_surface = small_font.render("PRESS R TO RESTART OR Q TO QUIT", True, WHITE)
            restart_quit_width = restart_quit_surface.get_size()[0]
            draw_text("PRESS R TO RESTART OR Q TO QUIT", small_font, WHITE, (SCREEN_WIDTH - restart_quit_width) // 2, 250)

        if admin_panel_visible:
            overlay_width = min(700, SCREEN_WIDTH - 80)
            overlay_height = 220
            overlay_x = (SCREEN_WIDTH - overlay_width) // 2
            overlay_y = 60

            pygame.draw.rect(screen, (0, 0, 0), (overlay_x, overlay_y, overlay_width, overlay_height))
            pygame.draw.rect(screen, CYAN, (overlay_x, overlay_y, overlay_width, overlay_height), 3)

            draw_text("ADMIN PANEL", font, CYAN, overlay_x + 20, overlay_y + 20)
            draw_text("R = Reset Scores", small_font, WHITE, overlay_x + 20, overlay_y + 80)
            draw_text("L = Reload Leaderboard", small_font, WHITE, overlay_x + 20, overlay_y + 115)
            draw_text("H = Hide Panel", small_font, WHITE, overlay_x + 20, overlay_y + 150)

        if admin_message_timer > 0:
            admin_message_timer -= 1
            draw_text(admin_message, small_font, YELLOW, 20, 20)

        pygame.display.flip()
        clock.tick(60)
        
    drone.disconnect_drone()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
