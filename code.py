import math
import random

import time

import constants
import displayio
import stage
import ugame


class player:
    def __init__(self, resolution, refresh, speed, turn):
        # Core stats
        self._fg_bitmap = displayio.Bitmap(5, 5, 5)
        self.resolution = resolution
        self.refresh = refresh
        self.speed = speed
        self.turn = turn
        self.max_dist = 2
        self.fov = 70
        self.current_map = constants.LEVELS[0]

        # Player origin
        self.x = 0
        self.y = 0
        self.rotation = 90

    def scan(self, origin_x, origin_y, direction):
        rays = []
        for ray_index in range(self.resolution):
            # Calculate offset for each ray based on its angle relative to FOV
            ray_offset_deg = (ray_index - self.resolution / 2) * (
                self.fov / self.resolution
            )
            ray_angle = math.radians(direction + ray_offset_deg)

            # Direction vector of the ray
            ray_dir_x = math.cos(ray_angle)
            ray_dir_y = math.sin(ray_angle)

            # Initial position in the map grid
            map_x = int(origin_x)
            map_y = int(origin_y)

            # Distance from one side of a grid cell to the next
            delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float("inf")
            delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float("inf")

            # Setup step direction and initial distance to first side
            if ray_dir_x < 0:
                step_x = -1
                side_dist_x = (origin_x - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1.0 - origin_x) * delta_dist_x

            if ray_dir_y < 0:
                step_y = -1
                side_dist_y = (origin_y - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1.0 - origin_y) * delta_dist_y

            distance = 0
            wall_hit = False
            wall_type = ""
            side_hit = (
                0  # 0 = hit x-side (vertical wall), 1 = hit y-side (horizontal wall)
            )

            # Perform DDA (Digital Differential Analyzer) stepping
            while not wall_hit and distance < self.max_dist:
                # Step to next tile in grid based on which side is closer
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side_hit = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side_hit = 1

                # Bounds check before accessing the map
                if 0 <= map_x < len(self.current_map[0]) and 0 <= map_y < len(
                    self.current_map
                ):
                    if self.current_map[map_y][map_x] == 1:
                        wall_hit = True
                        wall_type = "vertical" if side_hit == 0 else "horizontal"
                else:
                    break  # Went out of bounds

            # Finalize distance once hit or max distance reached
            if wall_hit:
                if side_hit == 0:
                    distance = (map_x - origin_x + (1 - step_x) / 2) / ray_dir_x
                else:
                    distance = (map_y - origin_y + (1 - step_y) / 2) / ray_dir_y

                hit_pos_x = origin_x + ray_dir_x * distance
                hit_pos_y = origin_y + ray_dir_y * distance

                rays.append(
                    {
                        "x": hit_pos_x,
                        "y": hit_pos_y,
                        "distance": distance,
                        "wall": wall_type,
                    }
                )
            else:
                rays.append(None)

        return rays


def play_sound(s):
    music_sound = open("Burglar.wav", "rb")
    step_sound = open("step_sound.wav", "rb")

    sound = ugame.audio
    sound.stop()
    sound.mute(False)
    if s == "music":
        sound.play(music_sound, loop=True)
    if s == "stop" or s == "end":
        sound.stop()


def game_over():
    print("Game's over! You lose!")


def check_win(current_level, p_data):
    print("Nice! you win!")
    px, py, ex, ey = p_data.x, p_data.y, constants.LEVEL_END[0], constants.LEVEL_END[1]
    if abs(px - ex) < 1 and abs(py - ey) < 1:
        return True
    else:
        return False


def radians(deg):
    return deg * (math.pi / 180)


def game_start(player_data, current_level):
    # Define image banks
    background_image = stage.Bank.from_bmp16("blank.bmp")
    image_bank_sprites = stage.Bank.from_bmp16("core_icons.bmp")
    palette_bank = stage.Bank.from_bmp16("palette.bmp")

    # Background and timer icon
    background = stage.Grid(background_image, 10, 8)
    timer_icon = stage.Sprite(image_bank_sprites, 4, 10, 10)

    # Timer text
    text_timer = stage.Text(width=20, height=8, font=None, palette=constants.RED_PALETTE)
    text_timer.move(15, 10)
    text_timer.text = str(constants.ROUND_LENGTH)

    timer = [text_timer]

    # Create reusable wall sprites (2 per ray)
    wall_sprites = []
    for _ in range(player_data.resolution * 2):
        sprite = stage.Sprite(palette_bank, 0, 0, 0)  # default values
        wall_sprites.append(sprite)

    # Add to layers
    game = stage.Stage(ugame.display, constants.FPS)
    game.layers = wall_sprites + timer + [timer_icon, background]
    game.render_block()

    # Init player
    player_data.x = constants.LEVEL_START[0]
    player_data.y = constants.LEVEL_START[1]

    game_start_time = time.monotonic()
    last_rendered_walls = game_start_time
    last_music_played = game_start_time

    game_running = True
    game_won = True

    while game_running:
        game.tick()
        keys = ugame.buttons.get_pressed()

        # Rotation
        if keys & ugame.K_X:
            player_data.rotation -= 1
        if keys & ugame.K_O:
            player_data.rotation += 1

        # Movement
        rotation_rad = radians(player_data.rotation)
        if keys & ugame.K_UP:
            player_data.x += math.cos(rotation_rad) / 50
            player_data.y += math.sin(rotation_rad) / 50
        if keys & ugame.K_DOWN:
            player_data.x -= math.cos(rotation_rad) / 50
            player_data.y -= math.sin(rotation_rad) / 50
        if keys & ugame.K_LEFT:
            strafe_rad = radians(player_data.rotation + 90)
            player_data.x += math.cos(strafe_rad) / 50
            player_data.y += math.sin(strafe_rad) / 50
        if keys & ugame.K_RIGHT:
            strafe_rad = radians(player_data.rotation - 90)
            player_data.x += math.cos(strafe_rad) / 50
            player_data.y += math.sin(strafe_rad) / 50

        # Music
        now = time.monotonic()
        if now - last_music_played > constants.MUSIC_DELAY:
            play_sound("music")
            last_music_played = now

        if now - int(now) < 0.1:
            timer_icon.set_frame(rotation=random.randint(1, 7))
        else:
            timer_icon.set_frame(rotation=0)

        # Wall rendering
        if now - last_rendered_walls >= player_data.refresh:
            scan_data = player_data.scan(player_data.x, player_data.y, player_data.rotation)
            sprite_idx = 0

            for ray_n, ray in enumerate(scan_data):
                ray_offset_deg = (ray_n - player_data.resolution / 2) * (player_data.fov / player_data.resolution)

                if ray:
                    corrected_dist = ray["distance"] * math.cos(math.radians(ray_offset_deg))
                    corrected_dist = max(0.1, corrected_dist)
                    palette_index = 1 if ray["wall"] == "vertical" else 5

                    xpos = 160 - (ray_n * 16)

                    # Render up to two sprites per ray
                    for i in range(2):
                        ypos = round(-corrected_dist * 8 + 80) if i == 0 else round(corrected_dist * 8 + 80)
                        wall_sprites[sprite_idx].move(xpos, ypos)
                        wall_sprites[sprite_idx].set_frame(palette_index)
                        sprite_idx += 1
                else:
                    # Move off-screen if no hit
                    for i in range(2):
                        wall_sprites[sprite_idx].move(240, 240)
                        sprite_idx += 1

            text_timer.text = str(int(game_start_time - now + constants.ROUND_LENGTH))
            game.render_sprites(wall_sprites + [timer_icon])
            last_rendered_walls = now

        # Game timer
        if now - game_start_time >= constants.ROUND_LENGTH:
            game_won = False
            game_running = False

        if check_win(current_level, player_data):
            game_won = True
            game_running = False

    play_sound("stop")
    if game_won:
        if current_level + 1 < len(constants.LEVELS):
            game_start(player_data, current_level + 1)
        else:
            print("You won the whole game!")
            open_program()
    else:
        print("Game over!")
        open_program()



def tutorial():
    print("Tutorial, awaiting user input")
    game = stage.Stage(ugame.display, constants.FPS)

    while True:
        game.tick()

        keys = ugame.buttons.get_pressed()
        if keys & ugame.K_X:
            print("User ended tutorial! returning to menu")
            break


def open_program():
    # Define player data
    player_data = player(16, .25, 0.5, 90)

    # Ensure this function/class is defined elsewhere
    game = stage.Stage(ugame.display, constants.FPS)

    background_image = stage.Bank.from_bmp16("blank.bmp")
    background = stage.Grid(background_image, 10, 8)

    # Load all image banks for the title screen background
    image_banks = [
        stage.Bank.from_bmp16(filename) for filename in constants.BMP_FILENAMES
    ]

    game.layers = []
    
    # Create text
    text = []

    # Create title display
    text_1 = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_1.move(20, 1)
    text_1.text = "Cat burglar"
    text.append(text_1)

    # Prompt Tutorial and start options
    text_tut = stage.Text(
        width=20, height=8, font=None, palette=constants.RED_PALETTE, buffer=None
    )
    text_tut.move(20, 50)
    text_tut.text = "Press A for tutorial"
    text.append(text_tut)

    text_srt = stage.Text(
        width=20, height=8, font=None, palette=constants.RED_PALETTE, buffer=None
    )
    text_srt.move(20, 50)
    text_srt.text = "Press Select to begin"
    text.append(text_srt)
    

    # Render new background
    

    new = []
    off_x = 17
    off_y = 40

    # Render each background sprite
    for x in range(10):
        for y in range(8):
            time.sleep(0.0001)
            # Showing only a portion of the background to reduce glitchy effect
            if x < 8 and y < 5:
                sprite_index = y * 10 + x
                sprite = stage.Sprite(
                    image_banks[0], sprite_index, x * 16 + off_x, y * 16 + off_y
                )
                game.layers.append(sprite)
                new.append(sprite)

    game.layers = text + game.layers

    game.render_block()
    

    skip_game_start = False

    # Wait until user clicks select to begin the game
    while True:
        game.tick()

        keys = ugame.buttons.get_pressed()
        if keys & ugame.K_SELECT:
            break
        if keys & ugame.K_X:
            tutorial()
            skip_game_start = True

    if not skip_game_start:
        # Call start function
        game_start(player_data, 1)


if __name__ == "__main__":
    open_program()
