# Import required libraries
import os
import sys
import math
import tkinter as tk      # Used to create the game window and GUI
import random             # Used to generate random pipe positions


def resource_path(relative_path):
    """Get absolute path to resource, works for development and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# ---------------- GAME WINDOW SETTINGS ---------------- #

# Width and height of the game window
WIDTH = 500
HEIGHT = 600

# Create the main application window
window = tk.Tk()

# Set the window title
window.title("Mini Flappy Bird")

# Prevent the window from being resized
window.resizable(False, False)

# Create a drawing area where all game objects will appear
canvas = tk.Canvas(
    window,
    width=WIDTH,
    height=HEIGHT,
    highlightthickness=0
)
canvas.pack()

bird_image = tk.PhotoImage(file=resource_path("bird.png"))

# High score persistence file
HIGH_SCORE_FILE = "high_score.txt"


def load_high_score():
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0

    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as file:
            return int(file.read().strip() or 0)
    except (ValueError, OSError):
        return 0


def save_high_score(value):
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
            file.write(str(value))
    except OSError:
        pass


# ---------------- GAME VARIABLES ---------------- #

# Bird object (will be created later)
bird = None

# List that stores all pipe pairs
pipes = []

# Player score
score = 0

# Highest score across rounds
high_score = load_high_score()

# Ground scroll state
ground_sections = []
GROUND_SCROLL_SPEED = 5

# Pipe difficulty state
PIPE_BASE_SPEED = 4
PIPE_SPEED_MAX = 10
PIPE_SPEED_INCREMENT = 0.0007
GAP_BASE = 170
GAP_MIN = 120
GAP_VARIATION = 16

game_time = 0

# Screen shake state
screen_shake_time = 0
screen_shake_duration = 150
screen_shake_offset = (0, 0)

# Moving cloud state
game_clouds = []
game_far_clouds = []
welcome_clouds = []
welcome_far_clouds = []
welcome_mode = False
welcome_bird_osc = 0
welcome_bird_direction = 1
welcome_animation_id = None

touch_start_y = None
TOUCH_SWIPE_THRESHOLD = 30

# Pause menu state
game_paused = False
pause_buttons = []

# Theme state
current_theme = "Default"
THEME_OPTIONS = ["Default", "Evening", "Night"]

theme_styles = {
    "Default": {
        "background": ["#7FC9FF", "#8FD9FF", "#A1E3FF", "#B8EDFF", "#D5F7FF"],
        "pipe_fill": "#31A24C",
        "pipe_outline": "#196A26",
        "cloud_fill": "#FFFFFF",
        "cloud_outline": "",
        "ground_top": "#4E8A2B",
        "ground_bottom": "#7C5D3A",
        "grass1": "#2E7D32",
        "grass2": "#3E8E41",
        "grass3": "#225624",
        "sun_fill": "#FFF28D",
        "sun_outline": "#FFDC3E",
        "sun_highlight": "#FFFBDC",
        "title_fill": "#D32F2F",
        "title_outline": "#FFF176",
        "subtitle": "#FFF4A0",
        "hint": "#F5F5EE",
        "hint_sub": "#FFF6B5",
        "pause_panel": "#FFFFFF",
        "pause_panel_outline": "#1E7D23",
        "pause_text": "#242424",
        "pause_button_bg": "#4E8A2B",
        "pause_button_fg": "white",
        "pause_button_hover": "#6B9B41"
    },
    "Evening": {
        "background": ["#422B1B", "#7A4F2B", "#C7773E", "#F7A262", "#FFD19E"],
        "pipe_fill": "#C1591B",
        "pipe_outline": "#8B3F0E",
        "cloud_fill": "#FFF0D1",
        "cloud_outline": "#E0B57B",
        "ground_top": "#6B3F24",
        "ground_bottom": "#3D2215",
        "grass1": "#8E5B2F",
        "grass2": "#BB7C42",
        "grass3": "#6E4424",
        "sun_fill": "#FFD57A",
        "sun_outline": "#E0A23C",
        "sun_highlight": "#FFE9B9",
        "title_fill": "#FFF5E4",
        "title_outline": "#6B3B1B",
        "subtitle": "#FFE3C0",
        "hint": "#FFF6E0",
        "hint_sub": "#FFE9C1",
        "pause_panel": "#3B2B1F",
        "pause_panel_outline": "#FFD19E",
        "pause_text": "#FFF6E0",
        "pause_button_bg": "#C1591B",
        "pause_button_fg": "#2B1507",
        "pause_button_hover": "#D18B58"
    },
    "Night": {
        "background": ["#030614", "#0B1C3A", "#122C5A", "#1F457F", "#2E5E9B"],
        "pipe_fill": "#4B2E80",
        "pipe_outline": "#2F1F48",
        "cloud_fill": "#E8ECFF",
        "cloud_outline": "#B8C6FF",
        "ground_top": "#1F2D4E",
        "ground_bottom": "#101A31",
        "grass1": "#263655",
        "grass2": "#2E4A74",
        "grass3": "#1A2642",
        "sun_fill": "#F5F8FF",
        "sun_outline": "#B8C7E6",
        "sun_highlight": "#FFFFFF",
        "title_fill": "#FFF2A8",
        "title_outline": "#2A3C5F",
        "subtitle": "#DCE8FF",
        "hint": "#F0F6FF",
        "hint_sub": "#DCE6F7",
        "pause_panel": "#0B1C3A",
        "pause_panel_outline": "#5E7DBE",
        "pause_text": "#F0F6FF",
        "pause_button_bg": "#2A3C5F",
        "pause_button_fg": "#F0F6FF",
        "pause_button_hover": "#3C5A8E"
    }
}

# Sun animation state
sun_rays = []
sun_frame = 0
SUN_CENTER_X = 430
SUN_CENTER_Y = 70
SUN_RAY_COUNT = 16
SUN_INNER_RADIUS = 38
SUN_OUTER_RADIUS = 56

# Current vertical speed of the bird
bird_velocity = 0

# Theme control button
theme_button = None

# Controls whether the game is running
game_running = False


# ---------------- FUNCTIONS ---------------- #

# Create the bird and return its object ID
def create_bird():

    return canvas.create_image(
        95,
        265,
        image=bird_image
    )

def start_screen_shake():
    global screen_shake_time
    screen_shake_time = screen_shake_duration
    apply_screen_shake()


def apply_screen_shake():
    global screen_shake_time, screen_shake_offset
    if screen_shake_time <= 0:
        return

    new_offset = (random.randint(-4, 4), random.randint(-4, 4))
    dx = new_offset[0] - screen_shake_offset[0]
    dy = new_offset[1] - screen_shake_offset[1]
    canvas.move("all", dx, dy)
    screen_shake_offset = new_offset

    screen_shake_time -= 20
    if screen_shake_time <= 0:
        canvas.move("all", -screen_shake_offset[0], -screen_shake_offset[1])
        screen_shake_offset = (0, 0)
    else:
        window.after(20, apply_screen_shake)


def draw_gradient():

    # Top-to-bottom sky colours with finer stripes for a more natural sky.
    style = theme_styles[current_theme]
    colors = style["background"]

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb):
        return "#%02x%02x%02x" % tuple(int(max(0, min(255, v))) for v in rgb)

    def interpolate_color(color_a, color_b, t):
        return tuple(color_a[i] + (color_b[i] - color_a[i]) * t for i in range(3))

    rgb_colors = [hex_to_rgb(color) for color in colors]
    stripe_count = max(40, len(rgb_colors) * 16)
    stripe_height = HEIGHT / stripe_count

    for i in range(stripe_count):
        position = i / max(stripe_count - 1, 1)
        segment = min(int(position * (len(rgb_colors) - 1)), len(rgb_colors) - 2)
        segment_start = segment / max(len(rgb_colors) - 1, 1)
        segment_end = (segment + 1) / max(len(rgb_colors) - 1, 1)
        local_t = (position - segment_start) / max(segment_end - segment_start, 1e-6)
        color = rgb_to_hex(interpolate_color(rgb_colors[segment], rgb_colors[segment + 1], local_t))

        canvas.create_rectangle(
            0,
            i * stripe_height,
            WIDTH,
            (i + 1) * stripe_height,
            fill=color,
            outline=color
        )

    if current_theme == "Night":
        draw_stars()


def draw_stars():
    star_positions = [
        (50, 60),
        (120, 40),
        (180, 75),
        (260, 55),
        (330, 90),
        (390, 45),
        (440, 70),
        (90, 140),
        (220, 130)
    ]

    for x, y in star_positions:
        canvas.create_oval(
            x - 2,
            y - 2,
            x + 2,
            y + 2,
            fill="#EEF7FF",
            outline=""
        )
        canvas.create_line(
            x - 4,
            y,
            x + 4,
            y,
            fill="#EEF7FF",
            width=1
        )
        canvas.create_line(
            x,
            y - 4,
            x,
            y + 4,
            fill="#EEF7FF",
            width=1
        )


def create_cloud(x, y, scale=1, speed=0.18):
    style = theme_styles[current_theme]
    tag = f"welcome_cloud{len(welcome_clouds)}"
    cloud_fill = style.get("cloud_fill", "white")
    cloud_outline = style.get("cloud_outline", "")

    canvas.create_oval(
        x,
        y,
        x + 35 * scale,
        y + 25 * scale,
        fill=cloud_fill,
        outline=cloud_outline,
        tags=(tag, "welcome_cloud")
    )

    canvas.create_oval(
        x + 18 * scale,
        y - 12 * scale,
        x + 60 * scale,
        y + 25 * scale,
        fill=cloud_fill,
        outline=cloud_outline,
        tags=(tag, "welcome_cloud")
    )

    canvas.create_oval(
        x + 45 * scale,
        y,
        x + 80 * scale,
        y + 25 * scale,
        fill=cloud_fill,
        outline=cloud_outline,
        tags=(tag, "welcome_cloud")
    )

    welcome_clouds.append((tag, speed))


def create_far_cloud(x, y, scale=0.8, speed=0.14):
    style = theme_styles[current_theme]
    tag = f"welcome_far_cloud{len(welcome_far_clouds)}"
    cloud_fill = style.get("cloud_fill", "white")
    cloud_outline = style.get("cloud_outline", "")

    canvas.create_oval(
        x,
        y,
        x + 30 * scale,
        y + 20 * scale,
        fill=cloud_fill,
        outline=cloud_outline,
        tags=(tag, "welcome_far_cloud")
    )

    canvas.create_oval(
        x + 15 * scale,
        y - 10 * scale,
        x + 50 * scale,
        y + 20 * scale,
        fill=cloud_fill,
        outline=cloud_outline,
        tags=(tag, "welcome_far_cloud")
    )

    canvas.create_oval(
        x + 40 * scale,
        y,
        x + 70 * scale,
        y + 20 * scale,
        fill=cloud_fill,
        outline=cloud_outline,
        tags=(tag, "welcome_far_cloud")
    )

    welcome_far_clouds.append((tag, speed))


def create_game_cloud(x, y, scale=1, speed=0.45):
    style = theme_styles[current_theme]
    tag = f"game_cloud{len(game_clouds)}"
    cloud_fill = style.get("cloud_fill", "white")
    cloud_outline = style.get("cloud_outline", "")

    canvas.create_oval(
        x,
        y,
        x + 35 * scale,
        y + 25 * scale,
        fill=cloud_fill,
        outline=cloud_outline,
        tags=(tag, "game_cloud")
    )

    canvas.create_oval(
        x + 18 * scale,
        y - 12 * scale,
        x + 60 * scale,
        y + 25 * scale,
        fill=cloud_fill,
        outline=cloud_outline,
        tags=(tag, "game_cloud")
    )

    canvas.create_oval(
        x + 45 * scale,
        y,
        x + 80 * scale,
        y + 25 * scale,
        fill=cloud_fill,
        outline=cloud_outline,
        tags=(tag, "game_cloud")
    )

    game_clouds.append((tag, speed))


def create_far_game_cloud(x, y, scale=0.8, speed=0.18):
    style = theme_styles[current_theme]
    tag = f"game_far_cloud{len(game_far_clouds)}"
    cloud_fill = style.get("cloud_fill", "white")
    cloud_outline = style.get("cloud_outline", "")

    canvas.create_oval(
        x,
        y,
        x + 30 * scale,
        y + 20 * scale,
        fill=cloud_fill,
        outline=cloud_outline,
        tags=(tag, "game_far_cloud")
    )

    canvas.create_oval(
        x + 15 * scale,
        y - 10 * scale,
        x + 50 * scale,
        y + 20 * scale,
        fill=cloud_fill,
        outline=cloud_outline,
        tags=(tag, "game_far_cloud")
    )

    canvas.create_oval(
        x + 40 * scale,
        y,
        x + 70 * scale,
        y + 20 * scale,
        fill=cloud_fill,
        outline=cloud_outline,
        tags=(tag, "game_far_cloud")
    )

    game_far_clouds.append((tag, speed))


def draw_sun():

    global sun_rays
    sun_rays.clear()
    style = theme_styles[current_theme]

    if current_theme == "Night":
        canvas.create_oval(
            SUN_CENTER_X - 35,
            SUN_CENTER_Y - 35,
            SUN_CENTER_X + 35,
            SUN_CENTER_Y + 35,
            fill=style["sun_fill"],
            outline=style["sun_outline"],
            width=4,
            tags=("sun_core", "sun")
        )

        canvas.create_oval(
            SUN_CENTER_X + 10,
            SUN_CENTER_Y - 20,
            SUN_CENTER_X + 22,
            SUN_CENTER_Y - 8,
            fill=style["sun_highlight"],
            outline="",
            tags=("sun_highlight", "sun")
        )

        canvas.create_arc(
            SUN_CENTER_X - 22,
            SUN_CENTER_Y - 8,
            SUN_CENTER_X - 10,
            SUN_CENTER_Y + 6,
            start=0,
            extent=-180,
            style="arc",
            width=3,
            outline=style["sun_outline"],
            tags=("sun", "moon_eye")
        )
        canvas.create_arc(
            SUN_CENTER_X + 10,
            SUN_CENTER_Y - 8,
            SUN_CENTER_X + 22,
            SUN_CENTER_Y + 6,
            start=0,
            extent=-180,
            style="arc",
            width=3,
            outline=style["sun_outline"],
            tags=("sun", "moon_eye")
        )

        canvas.create_text(
            SUN_CENTER_X + 44,
            SUN_CENTER_Y - 28,
            text="Zzz",
            font=("Verdana", 14, "bold"),
            fill=style["sun_fill"],
            tags=("sun", "moon_sleep")
        )
        return

    for i in range(SUN_RAY_COUNT):
        angle = i * (360 / SUN_RAY_COUNT)
        x1 = SUN_CENTER_X + SUN_INNER_RADIUS * math.cos(math.radians(angle))
        y1 = SUN_CENTER_Y + SUN_INNER_RADIUS * math.sin(math.radians(angle))
        x2 = SUN_CENTER_X + SUN_OUTER_RADIUS * math.cos(math.radians(angle))
        y2 = SUN_CENTER_Y + SUN_OUTER_RADIUS * math.sin(math.radians(angle))

        ray_id = canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill=style["sun_fill"],
            width=3,
            capstyle="round",
            tags=("sun_ray", "sun")
        )
        sun_rays.append((ray_id, angle))

    canvas.create_oval(
        SUN_CENTER_X - 35,
        SUN_CENTER_Y - 35,
        SUN_CENTER_X + 35,
        SUN_CENTER_Y + 35,
        fill=style["sun_fill"],
        outline=style["sun_outline"],
        width=4,
        tags=("sun_core", "sun")
    )

    canvas.create_oval(
        SUN_CENTER_X + 10,
        SUN_CENTER_Y - 20,
        SUN_CENTER_X + 20,
        SUN_CENTER_Y - 10,
        fill=style["sun_highlight"],
        outline="",
        tags=("sun_highlight", "sun")
    )


def draw_ground():

    global ground_sections
    ground_sections.clear()
    style = theme_styles[current_theme]

    section_width = WIDTH
    for section_index in range(2):
        offset = section_index * section_width
        ground_tag = f"ground{section_index}"

        # Grass strip
        base_id = canvas.create_rectangle(
            offset,
            HEIGHT - 55,
            offset + section_width,
            HEIGHT - 40,
            fill=style["ground_top"],
            outline="",
            tags=("ground", ground_tag)
        )

        # Ground
        canvas.create_rectangle(
            offset,
            HEIGHT - 40,
            offset + section_width,
            HEIGHT,
            fill=style["ground_bottom"],
            outline="",
            tags=("ground", ground_tag)
        )

        # Grass blades
        for x in range(offset, offset + section_width, 12):
            canvas.create_line(
                x,
                HEIGHT - 40,
                x + 3,
                HEIGHT - 48,
                fill=style["grass1"],
                width=2,
                tags=("ground", ground_tag)
            )

            canvas.create_line(
                x + 6,
                HEIGHT - 40,
                x + 8,
                HEIGHT - 50,
                fill=style["grass2"],
                width=2,
                tags=("ground", ground_tag)
            )

            canvas.create_line(
                x + 10,
                HEIGHT - 40,
                x + 13,
                HEIGHT - 47,
                fill=style["grass3"],
                width=2,
                tags=("ground", ground_tag)
            )

        ground_sections.append((ground_tag, base_id))


def show_start_screen():

    global welcome_mode, welcome_clouds, welcome_far_clouds, welcome_bird_osc, welcome_bird_direction
    canvas.delete("all")
    welcome_clouds.clear()
    welcome_far_clouds.clear()
    welcome_bird_osc = 0
    welcome_bird_direction = 1

    # Background
    draw_gradient()

    style = theme_styles[current_theme]

    create_far_cloud(30, 90, 0.8, 0.14)
    create_far_cloud(220, 75, 0.9, 0.16)
    create_cloud(40, 70, 1.0, 0.22)
    create_cloud(200, 120, 0.9, 0.20)
    create_cloud(360, 55, 1.2, 0.24)

    draw_sun()
    draw_ground()

    # Title and subtitle
    outline_color = style["title_outline"]
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        canvas.create_text(
            WIDTH // 2 + dx,
            80 + dy,
            text="MINI FLAPPY BIRD",
            font=("Arial Black", 28, "bold"),
            fill=outline_color,
            width=420,
            justify="center"
        )

    canvas.create_text(
        WIDTH // 2,
        80,
        text="MINI FLAPPY BIRD",
        font=("Arial Black", 28, "bold"),
        fill=style["title_fill"],
        width=420,
        justify="center"
    )

    canvas.create_text(
        WIDTH // 2,
        115,
        text="Fly high, dodge the pipes",
        font=("Verdana", 14, "bold"),
        fill=style["subtitle"],
        width=420,
        justify="center"
    )

    # Bird animation
    canvas.create_image(
        WIDTH // 2,
        180,
        image=bird_image,
        tags=("welcome_bird",)
    )

    # Control hints
    canvas.create_text(
        WIDTH // 2,
        260,
        text="Use SPACE, ↑ or W to Fly",
        font=("Verdana", 18, "bold"),
        fill=style["hint"]
    )

    canvas.create_text(
        WIDTH // 2,
        295,
        text="Press ENTER or Click START",
        font=("Verdana", 16),
        fill=style["hint_sub"]
    )

    style = theme_styles[current_theme]

    # Best score badge
    badge_x = WIDTH // 2
    badge_y = 35
    badge_width = 160
    badge_height = 38
    canvas.create_rectangle(
        badge_x - badge_width // 2,
        badge_y - badge_height // 2,
        badge_x + badge_width // 2,
        badge_y + badge_height // 2,
        fill=style["sun_highlight"],
        outline=style["title_outline"],
        width=2,
        tags=("score_badge",)
    )
    canvas.create_text(
        badge_x,
        badge_y,
        text=f"Best Score: {high_score}",
        font=("Verdana", 12, "bold"),
        fill="#4D4D4D",
        tags=("score_badge",)
    )

    # Larger start button placement
    start_button.place(
        x=WIDTH // 2 - 140,
        y=360,
        width=280,
        height=75
    )
    theme_button.place(
        x=WIDTH - 150,
        y=15,
        width=130,
        height=32
    )

    welcome_mode = True
    animate_welcome_screen()


# Pause menu helpers
def clear_pause_menu():
    global pause_buttons
    for button in pause_buttons:
        try:
            button.destroy()
        except Exception:
            pass
    pause_buttons.clear()
    canvas.delete("pause_menu")


def pause_game():
    global game_paused
    if game_paused or not game_running:
        return

    game_paused = True
    style = theme_styles[current_theme]

    panel_width = 270
    panel_height = 240
    x0 = (WIDTH - panel_width) // 2
    y0 = (HEIGHT - panel_height) // 2
    x1 = x0 + panel_width
    y1 = y0 + panel_height

    canvas.create_rectangle(
        x0,
        y0,
        x1,
        y1,
        fill=style["pause_panel"],
        outline=style["pause_panel_outline"],
        width=3,
        tags=("pause_menu",)
    )

    canvas.create_text(
        WIDTH // 2,
        y0 + 40,
        text="PAUSED",
        font=("Arial Black", 22, "bold"),
        fill=style["pause_text"],
        tags=("pause_menu",)
    )

    button_data = [
        ("Resume", resume_game),
        ("Restart", restart_game),
        ("Quit", quit_to_welcome)
    ]

    for index, (text, command) in enumerate(button_data):
        btn = tk.Button(
            window,
            text=text,
            font=("Arial", 12, "bold"),
            bg=style["pause_button_bg"],
            fg=style["pause_button_fg"],
            activebackground=style["pause_button_hover"],
            activeforeground=style["pause_button_fg"],
            bd=0,
            relief="raised",
            cursor="hand2",
            command=command
        )
        canvas.create_window(
            WIDTH // 2,
            y0 + 95 + index * 55,
            window=btn,
            width=180,
            height=40,
            tags=("pause_menu",)
        )
        pause_buttons.append(btn)

    canvas.tag_raise("pause_menu")


def resume_game():
    global game_paused
    if not game_paused:
        return

    game_paused = False
    clear_pause_menu()
    game()


def restart_game():
    clear_pause_menu()
    start_game()


def quit_to_welcome():
    global game_paused, game_running
    clear_pause_menu()
    game_paused = False
    game_running = False
    show_start_screen()


# Create one pair of pipes
def create_pipe():

    style = theme_styles[current_theme]

    # Shrink gap slightly as the player scores more
    shrink_amount = min(GAP_BASE - GAP_MIN, score * 1.8)
    gap = int(max(GAP_MIN, GAP_BASE - shrink_amount + random.uniform(-GAP_VARIATION, GAP_VARIATION)))
    gap = max(GAP_MIN, min(GAP_BASE, gap))

    # Vary the vertical position of the gap up and down
    top = random.randint(60, HEIGHT - 40 - gap - 60)

    tag = f"pipe{len(pipes)}"

    # ---------- Upper Pipe ----------
    upper = canvas.create_rectangle(
        WIDTH, 0,
        WIDTH + 60, top,
        fill=style["pipe_fill"],
        outline=style["pipe_outline"],
        width=3,
        tags=tag
    )

    # Highlight
    canvas.create_rectangle(
        WIDTH + 5, 0,
        WIDTH + 12, top,
        fill="#A9F5BC",
        outline="",
        tags=tag
    )

    # Cap
    canvas.create_rectangle(
        WIDTH - 6,
        top - 12,
        WIDTH + 66,
        top,
        fill=style["pipe_fill"],
        outline=style["pipe_outline"],
        width=2,
        tags=tag
    )

    # ---------- Lower Pipe ----------
    lower = canvas.create_rectangle(
        WIDTH,
        top + gap,
        WIDTH + 60,
        HEIGHT - 40,
        fill=style["pipe_fill"],
        outline=style["pipe_outline"],
        width=3,
        tags=tag
    )

    # Highlight
    canvas.create_rectangle(
        WIDTH + 5,
        top + gap,
        WIDTH + 12,
        HEIGHT - 40,
        fill="#A9F5BC",
        outline="",
        tags=tag
    )

    # Cap
    canvas.create_rectangle(
        WIDTH - 6,
        top + gap,
        WIDTH + 66,
        top + gap + 12,
        fill=style["pipe_fill"],
        outline=style["pipe_outline"],
        width=2,
        tags=tag
    )

    pipes.append((upper, lower, tag))


def handle_input(event=None):

    global bird_velocity

    key = getattr(event, "keysym", None) if event is not None else None
    click = getattr(event, "num", None) == 1

    if event is not None and click and getattr(event, "widget", None) is not None:
        if event.widget is not canvas:
            return

    if key == "Escape" and game_running:
        if game_paused:
            resume_game()
        else:
            pause_game()
        return

    if click:
        if game_running and game_paused:
            resume_game()
            return
        if game_running and not game_paused:
            bird_velocity = -8
            return
        if not game_running:
            start_game()
            return

    if game_running and not game_paused:
        if key in ("space", "Up", "Return", "KP_Enter", "w", "W"):
            bird_velocity = -8
    elif not game_running:
        if key in ("Return", "KP_Enter", "space", "Up", "w", "W"):
            start_game()


# Connect common game keys for both laptop and desktop
window.bind("<space>", handle_input)
window.bind("<Up>", handle_input)
window.bind("<Return>", handle_input)
window.bind("<KP_Enter>", handle_input)
window.bind("<Escape>", handle_input)
window.bind("<Key-w>", handle_input)
window.bind("<Key-W>", handle_input)
# Only the game canvas should trigger gameplay clicks so the pause/start buttons work normally.
canvas.bind("<Button-1>", handle_input)


# Main game loop
def game():

    global bird_velocity, score, game_running

    # Stop updating if game has ended
    if not game_running:
        return

    # ---------------- Gravity ---------------- #

    if game_paused:
        return

    # Gravity increases downward speed
    bird_velocity += 0.5

    # Move bird vertically
    canvas.move(bird, 0, bird_velocity)

    coords = canvas.coords(bird)
    if len(coords) == 2:
        x, y = coords
    elif len(coords) == 4:
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
    else:
        return

    bird_width = 40
    bird_height = 40

    bx1 = x - bird_width / 2
    by1 = y - bird_height / 2
    bx2 = x + bird_width / 2
    by2 = y + bird_height / 2

    # ---------------- Border Collision ---------------- #

    # If bird touches top or bottom, game ends
    if by2 >= HEIGHT - 40 or by1 <= 0:
        start_screen_shake()
        game_over()
        return

    # ---------------- Pipe Movement ---------------- #

    # Update game speed slowly over time and with score
    global game_time
    game_time += 1
    pipe_speed = min(PIPE_SPEED_MAX, PIPE_BASE_SPEED + game_time * PIPE_SPEED_INCREMENT)

    # Loop through a copy of pipe list
    for pipe in pipes[:]:

        canvas.move(pipe[2], -pipe_speed, 0)

        # Get coordinates of upper pipe
        ux1, uy1, ux2, uy2 = canvas.coords(pipe[0])

        # Get coordinates of lower pipe
        lx1, ly1, lx2, ly2 = canvas.coords(pipe[1])

        # ---------------- Remove Old Pipes ---------------- #

        # If pipe leaves screen
        if ux2 < 0:

            # Delete both pipes
            canvas.delete(pipe[0])
            canvas.delete(pipe[1])

            # Remove from list
            pipes.remove(pipe)

            # Create a new pipe
            create_pipe()

            # Increase score
            score += 1

            # Update score display
            canvas.itemconfig(
                score_text,
                text=f"Score : {score}"
            )

        # ---------------- Collision Detection ---------------- #

        # Check if bird is inside pipe's horizontal range
        if bx2 > ux1 and bx1 < ux2:

            # If bird hits upper or lower pipe
            if by1 < uy2 or by2 > ly1:
                start_screen_shake()
                game_over()
                return

    # Move ground left during play
    canvas.move("ground", -GROUND_SCROLL_SPEED, 0)
    for ground_tag, base_id in ground_sections:
        coords = canvas.coords(base_id)
        if coords and coords[2] <= 0:
            canvas.move(ground_tag, WIDTH * 2, 0)

    # Move game clouds slowly
    for cloud_tag, speed in game_far_clouds:
        canvas.move(cloud_tag, -speed, 0)
        bbox = canvas.bbox(cloud_tag)
        if bbox and bbox[2] < -20:
            canvas.move(cloud_tag, WIDTH + 140, 0)

    for cloud_tag, speed in game_clouds:
        canvas.move(cloud_tag, -speed, 0)
        bbox = canvas.bbox(cloud_tag)
        if bbox and bbox[2] < -20:
            canvas.move(cloud_tag, WIDTH + 120, 0)

    # Animate the sun rays
    global sun_frame
    sun_frame += 1
    angle_offset = sun_frame * 0.8

    for ray_id, base_angle in sun_rays:
        angle = base_angle + angle_offset
        x1 = SUN_CENTER_X + SUN_INNER_RADIUS * math.cos(math.radians(angle))
        y1 = SUN_CENTER_Y + SUN_INNER_RADIUS * math.sin(math.radians(angle))
        x2 = SUN_CENTER_X + SUN_OUTER_RADIUS * math.cos(math.radians(angle))
        y2 = SUN_CENTER_Y + SUN_OUTER_RADIUS * math.sin(math.radians(angle))
        canvas.coords(ray_id, x1, y1, x2, y2)

    # Keep the score badge visible above pipes and clouds
    canvas.tag_raise("score_display")

    if game_paused:
        return

    # Repeat game loop after 20 milliseconds
    window.after(20, game)


def animate_welcome_screen():

    global welcome_bird_osc, welcome_bird_direction, sun_frame

    if not welcome_mode:
        return

    move_amount = 0.35 * welcome_bird_direction
    canvas.move("welcome_bird", 0, move_amount)
    welcome_bird_osc += move_amount

    if welcome_bird_osc > 10 or welcome_bird_osc < -10:
        welcome_bird_direction *= -1

    for cloud_tag, speed in welcome_far_clouds:
        canvas.move(cloud_tag, -speed, 0)
        bbox = canvas.bbox(cloud_tag)
        if bbox and bbox[2] < -20:
            canvas.move(cloud_tag, WIDTH + 140, 0)

    for cloud_tag, speed in welcome_clouds:
        canvas.move(cloud_tag, -speed, 0)
        bbox = canvas.bbox(cloud_tag)
        if bbox and bbox[2] < -20:
            canvas.move(cloud_tag, WIDTH + 120, 0)

    sun_frame += 1
    angle_offset = sun_frame * 0.8
    for ray_id, base_angle in sun_rays:
        angle = base_angle + angle_offset
        x1 = SUN_CENTER_X + SUN_INNER_RADIUS * math.cos(math.radians(angle))
        y1 = SUN_CENTER_Y + SUN_INNER_RADIUS * math.sin(math.radians(angle))
        x2 = SUN_CENTER_X + SUN_OUTER_RADIUS * math.cos(math.radians(angle))
        y2 = SUN_CENTER_Y + SUN_OUTER_RADIUS * math.sin(math.radians(angle))
        canvas.coords(ray_id, x1, y1, x2, y2)

    canvas.move("ground", -1.4, 0)
    for ground_tag, base_id in ground_sections:
        coords = canvas.coords(base_id)
        if coords and coords[2] <= 0:
            canvas.move(ground_tag, WIDTH * 2, 0)

    window.after(30, animate_welcome_screen)


# Start a new game
def start_game():

    global bird, bird_velocity, game_time, welcome_mode, screen_shake_offset, screen_shake_time, game_paused
    global score, game_running

    clear_pause_menu()
    game_paused = False
    # Remove everything from canvas
    canvas.delete("all")
    game_clouds.clear()
    game_far_clouds.clear()
    draw_gradient()

    create_far_game_cloud(20, 70, 0.8, 0.15)
    create_far_game_cloud(260, 100, 1.0, 0.18)
    create_game_cloud(40, 60, 1.0, 0.45)
    create_game_cloud(200, 120, 0.9, 0.4)
    create_game_cloud(340, 50, 1.2, 0.5)
    draw_sun()
    draw_ground()

    # Remove old pipes from memory
    pipes.clear()

    # Create a fresh bird
    bird = create_bird()

    # Reset bird speed
    bird_velocity = 0

    # Reset score and difficulty progress
    score = 0
    game_time = 0
    welcome_mode = False
    if screen_shake_offset != (0, 0):
        canvas.move("all", -screen_shake_offset[0], -screen_shake_offset[1])
        screen_shake_offset = (0, 0)
    screen_shake_time = 0

    # ---------------- Score Text ---------------- #

    global score_text

    canvas.create_rectangle(
        WIDTH // 2 - 78,
        18,
        WIDTH // 2 + 78,
        52,
        fill="#000000",
        outline="",
        stipple="gray50",
        tags=("score_display",)
    )
    score_text = canvas.create_text(
        WIDTH // 2,
        35,
        text="Score : 0",
        font=("Verdana", 18, "bold"),
        fill="white",
        tags=("score_display",)
    )

    # Create first pipe
    create_pipe()
    canvas.tag_raise("score_display")

    # Hide buttons while playing
    start_button.place_forget()
    theme_button.place_forget()
    welcome_mode = False

    # Start the game
    game_running = True

    # Start game loop
    game()


# Called when player loses
def game_over():

    global game_running, high_score

    # Stop the game loop
    game_running = False

    # Update the high score if needed
    if score > high_score:
        high_score = score
        save_high_score(high_score)

    overlay_tag = "game_over_overlay"
    canvas.delete(overlay_tag)

    panel_width = 380
    panel_height = 290
    x0 = (WIDTH - panel_width) // 2
    y0 = (HEIGHT - panel_height) // 2
    x1 = x0 + panel_width
    y1 = y0 + panel_height

    def interpolate_color(start, end, t):
        return tuple(int(start[i] + (end[i] - start[i]) * t) for i in range(3))

    def rgb_to_hex(rgb):
        return "#%02x%02x%02x" % rgb

    start_color = (255, 244, 179)
    end_color = (255, 183, 77)

    for i in range(panel_height):
        t = i / max(panel_height - 1, 1)
        color = rgb_to_hex(interpolate_color(start_color, end_color, t))
        canvas.create_rectangle(
            x0,
            y0 + i,
            x1,
            y0 + i + 1,
            width=0,
            fill=color,
            tags=overlay_tag
        )

    canvas.create_rectangle(
        x0 + 8,
        y0 + 8,
        x1 - 8,
        y1 - 8,
        outline="#ffffff",
        width=2,
        tags=overlay_tag
    )

    game_over_messages = [
        "GAME OVER",
        "Nice Try!",
        "Keep Going!",
        "Almost!",
        "Fantastic!",
        "One More Round!"
    ]
    title_text = random.choice(game_over_messages)

    canvas.create_text(
        WIDTH // 2,
        y0 + 50,
        text=title_text,
        font=("Comic Sans MS", 32, "bold"),
        fill="#212121",
        tags=overlay_tag
    )

    canvas.create_text(
        WIDTH // 2,
        y0 + 100,
        text=f"Score: {score}",
        font=("Verdana", 18, "bold"),
        fill="#212121",
        tags=overlay_tag
    )

    canvas.create_text(
        WIDTH // 2,
        y0 + 135,
        text=f"Highest Score: {high_score}",
        font=("Verdana", 14, "italic"),
        fill="#424242",
        tags=overlay_tag
    )

    canvas.create_text(
        WIDTH // 2,
        y0 + 180,
        text="Press ENTER or TRY AGAIN to play again.",
        font=("Verdana", 12),
        fill="#424242",
        width=320,
        justify="center",
        tags=overlay_tag
    )

    try_button = tk.Button(
        window,
        text="TRY AGAIN",
        font=("Arial", 14, "bold"),
        bg="#212121",
        fg="white",
        activebackground="#424242",
        activeforeground="white",
        padx=18,
        pady=8,
        command=lambda: [canvas.delete(overlay_tag), start_game()]
    )

    canvas.create_window(
        WIDTH // 2,
        y0 + 235,
        window=try_button,
        tags=overlay_tag
    )

    # A second button can be added below if needed


# ---------------- BUTTONS ---------------- #

def cycle_theme():
    global current_theme
    index = THEME_OPTIONS.index(current_theme)
    current_theme = THEME_OPTIONS[(index + 1) % len(THEME_OPTIONS)]
    theme_button.config(text=f"Theme: {current_theme}")
    if not game_running:
        show_start_screen()

# Start Game button
start_button = tk.Button(
    window,
    text="▶ START GAME",
    font=("Arial", 16, "bold"),
    bg="#1E7D23",
    fg="white",
    activebackground="#2FA84B",
    activeforeground="white",
    bd=0,
    relief="raised",
    cursor="hand2",
    command=start_game
)
start_button.bind("<Enter>", lambda event: start_button.config(bg="#2FA84B"))
start_button.bind("<Leave>", lambda event: start_button.config(bg="#1E7D23"))
start_button.place(
    x=WIDTH // 2 - 125,
    y=430,
    width=250,
    height=70
)

theme_button = tk.Button(
    window,
    text=f"Theme: {current_theme}",
    font=("Arial", 10, "bold"),
    bg="#F4B400",
    fg="#242424",
    activebackground="#FFD54F",
    activeforeground="#242424",
    bd=0,
    relief="raised",
    cursor="hand2",
    command=cycle_theme
)
theme_button.bind("<Enter>", lambda event: theme_button.config(bg="#FFD54F"))
theme_button.bind("<Leave>", lambda event: theme_button.config(bg="#F4B400"))

show_start_screen()

# Start the Tkinter event loop
window.mainloop()
