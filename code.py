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
        self.max_dist = 2.5
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
                    if self.current_map[map_y][map_x] == 2:
                        wall_hit = True
                        wall_type = 2
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

                type = self.current_map[map_y][map_x]

                # Add ray to list
                rays.append(
                    {
                        "x": hit_pos_x,
                        "y": hit_pos_y,
                        "distance": distance,
                        "wall": wall_type,
                        "type": type,
                    }
                )
            else:
                rays.append(None)

        return rays


def play_sound(sounds, index):

    # Play sound based on sounds array and index given
    sound = ugame.audio
    sound.stop()
    sound.mute(False)

    if sounds == "stop" or sounds == "end":

        # Case where sounds is keyword to end sound
        sound.stop()
    else:
        # Play sound
        sound.play(sounds[index], loop=True)


def game_over():
    # Re setup game
    game = stage.Stage(ugame.display, constants.FPS)
    game.layers = []

    # Create text
    text = []

    # Prompt victory, how to continue
    text_1 = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_1.move(0, 0)
    text_1.text("You lost!")
    text.append(text_1)

    text_2 = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_2.move(0, 10)
    text_2.text("Press Start to continue")
    text.append(text_2)

    game.layers = text

    game.render_block()

    while True:

        game.tick()

        keys = ugame.buttons.get_pressed()
        if keys & ugame.K_START:
            print("User lost! returning to menu")
            break


def check_win(current_level, p_data):
    px, py = p_data.x, p_data.y
    ex, ey = constants.LEVEL_END
    dist = math.sqrt((px - ex) ** 2 + (py - ey) ** 2)
    return dist < 0.7


def radians(deg):
    return deg * (math.pi / 180)


def victoryScene(lvl):

    # Play victory theme
    sounds = [
        open("Burglar.wav", "rb"),
        open("step_sound.wav", "rb"),
        open("Victory.wav", "rb"),
        open("MenuTheme.wav", "rb"),
    ]
    play_sound(sounds, 2)

    # Re setup game
    game = stage.Stage(ugame.display, constants.FPS)
    game.layers = []

    # Create text
    text = []

    # Prompt victory, how to continue
    text_1 = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_1.move(0, 0)
    text_1.text("You won level " + str(lvl) if lvl < 1 else "You won the whole game!")
    text.append(text_1)

    text_2 = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_2.move(0, 10)
    text_2.text("Press B to continue")
    text.append(text_2)

    game.layers = text

    game.render_block()

    while True:

        game.tick()

        keys = ugame.buttons.get_pressed()
        if keys & ugame.K_O:
            print("User ended tutorial! returning to menu")
            break


def printGame(p_data, current_level):
    x = p_data.x
    y = p_data.y
    lvl = constants.LEVELS[current_level][::]  # make a copy of the level

    # Loop through rows
    for row in range(len(lvl)):
        if y == row:
            to_print = list(lvl[row])
            to_print[x] = "p"
            print(to_print)
        else:
            print(lvl[row])
    print("\n\n\n")


def game_start(player_data, current_level):

    player_data.current_map = constants.LEVELS[current_level]

    # Define image banks
    background_image = stage.Bank.from_bmp16("blank.bmp")
    image_bank_sprites = stage.Bank.from_bmp16("core_icons.bmp")
    palette_bank = stage.Bank.from_bmp16("palette.bmp")

    # Background and timer icon
    background = stage.Grid(background_image, 10, 8)
    timer_icon = stage.Sprite(image_bank_sprites, 4, 10, 10)

    # Timer text
    text_timer = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE
    )
    text_timer.move(25, 10)
    text_timer.text(str(constants.ROUND_LENGTH))

    # Create reusable wall sprites (2 per ray)
    wall_sprites = []
    for _ in range(player_data.resolution * 2):
        sprite = stage.Sprite(palette_bank, 0, 0, 0)  # default values
        wall_sprites.append(sprite)

    # Add to layers
    game = stage.Stage(ugame.display, constants.FPS)
    game.layers = wall_sprites + [text_timer] + [timer_icon, background]
    game.render_block()

    # Init player
    player_data.x = constants.LEVEL_START[0]
    player_data.y = constants.LEVEL_START[1]

    sounds = [
        open("Burglar.wav", "rb"),
        open("step_sound.wav", "rb"),
        open("Victory.wav", "rb"),
        open("MenuTheme.wav", "rb"),
    ]

    game_start_time = time.monotonic()
    last_rendered_walls = 0
    last_music_played = 0

    game_running = True
    game_won = True

    while game_running:
        game.tick()
        keys = ugame.buttons.get_pressed()

        # Rotation
        if keys & ugame.K_X:
            player_data.rotation -= player_data.turn
        if keys & ugame.K_O:
            player_data.rotation += player_data.turn

        # Movement with wall collisions
        rotation_rad = radians(player_data.rotation)
        level = constants.LEVELS[current_level]

        # Forward (Up)
        if keys & ugame.K_UP:
            next_x = player_data.x + math.cos(rotation_rad) / 50
            next_y = player_data.y + math.sin(rotation_rad) / 50
            if 0 <= int(next_y) < len(level) and 0 <= int(next_x) < len(level[0]):
                if level[int(next_y)][int(next_x)] != 1:
                    player_data.x = next_x
                    player_data.y = next_y

        # Backward (Down)
        if keys & ugame.K_DOWN:
            next_x = player_data.x - math.cos(rotation_rad) / 50
            next_y = player_data.y - math.sin(rotation_rad) / 50
            if 0 <= int(next_y) < len(level) and 0 <= int(next_x) < len(level[0]):
                if level[int(next_y)][int(next_x)] != 1:
                    player_data.x = next_x
                    player_data.y = next_y

        # Strafe Left
        strafe_rad_left = radians(player_data.rotation + 90)
        if keys & ugame.K_LEFT:
            next_x = player_data.x + math.cos(strafe_rad_left) / 50
            next_y = player_data.y + math.sin(strafe_rad_left) / 50
            if 0 <= int(next_y) < len(level) and 0 <= int(next_x) < len(level[0]):
                if level[int(next_y)][int(next_x)] != 1:
                    player_data.x = next_x
                    player_data.y = next_y

        # Strafe Right
        strafe_rad_right = radians(player_data.rotation - 90)
        if keys & ugame.K_RIGHT:
            next_x = player_data.x + math.cos(strafe_rad_right) / 50
            next_y = player_data.y + math.sin(strafe_rad_right) / 50
            if 0 <= int(next_y) < len(level) and 0 <= int(next_x) < len(level[0]):
                if level[int(next_y)][int(next_x)] != 1:
                    player_data.x = next_x
                    player_data.y = next_y

        # Music
        now = time.monotonic()
        if now - last_music_played > constants.MUSIC_DELAY:
            play_sound(sounds, 0)
            last_music_played = now

        if now - int(now) < 0.1:
            timer_icon.set_frame(rotation=random.randint(1, 7))
        else:
            timer_icon.set_frame(rotation=0)

        # Wall rendering
        if now - last_rendered_walls >= player_data.refresh:
            # Update timer
            text_timer.clear()
            t = str(int(constants.ROUND_LENGTH + (game_start_time - now)))
            text_timer.text(t)

            scan_data = player_data.scan(
                player_data.x, player_data.y, player_data.rotation
            )
            sprite_idx = 0

            for ray_n, ray in enumerate(scan_data):
                ray_offset_deg = (ray_n - player_data.resolution / 2) * (
                    player_data.fov / player_data.resolution
                )

                if ray:
                    corrected_dist = ray["distance"] * math.cos(
                        math.radians(ray_offset_deg)
                    )
                    corrected_dist = max(0.1, corrected_dist)
                    palette_index = 1
                    if corrected_dist > 2:
                        palette_index = 8 if ray["wall"] == "vertical" else 9
                    else:
                        palette_index = 1 if ray["wall"] == "vertical" else 5
                    if ray["type"] == 2:
                        palette_index = 3

                    xpos = 160 - (ray_n * 16)

                    # Render up to two sprites per ray
                    for i in range(2):
                        ypos = (
                            round(-1 / corrected_dist * 8 + 80)
                            if i == 0
                            else round(1 / corrected_dist * 8 + 80)
                        )
                        wall_sprites[sprite_idx].move(xpos, ypos)
                        wall_sprites[sprite_idx].set_frame(palette_index)
                        sprite_idx += 1
                else:
                    # Move off-screen if no hit
                    for i in range(2):
                        wall_sprites[sprite_idx].move(500, 500)
                        sprite_idx += 1
            last_rendered_walls = now

        text_timer.move(25, 10)

        game.render_sprites(wall_sprites + [timer_icon])

        # Game timer
        if now - game_start_time >= constants.ROUND_LENGTH:
            game_won = False
            game_running = False

        if check_win(current_level, player_data):
            game_won = True
            game_running = False

    # End of round
    # Stop sound
    play_sound("stop", 0)

    # If won, move onto next level, otherwise restart program
    if game_won:
        victoryScene(current_level)
        if current_level + 1 < len(constants.LEVELS) - 1:
            current_level += 1
            game_start(player_data, current_level)
        else:
            print("You won the whole game!")
            open_program()
    else:
        game_over()
        open_program()


def tutorial():
    print("Tutorial, awaiting user input")
    game = stage.Stage(ugame.display, constants.FPS)

    game.layers = []

    # Create text
    text = []

    # Create title display
    text_1 = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_1.move(0, 0)
    text_1.text("Up, Right, Left, Down:")
    text.append(text_1)

    text_2 = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_2.move(0, 10)
    text_2.text("Move")
    text.append(text_2)

    text_3 = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_3.move(0, 40)
    text_3.text("A, B:")
    text.append(text_3)

    text_4 = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_4.move(0, 50)
    text_4.text("Turn")
    text.append(text_4)

    text_5 = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_5.move(0, 115)
    text_5.text("Press B to return")
    text.append(text_5)

    text_6 = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_6.move(0, 80)
    text_6.text("Your goal: Steal the")
    text.append(text_6)

    text_7 = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_7.move(0, 90)
    text_7.text("Golden Tuna fo money")
    text.append(text_7)

    game.layers = text

    game.render_block()

    while True:

        game.tick()

        keys = ugame.buttons.get_pressed()
        if keys & ugame.K_O:
            print("User ended tutorial! returning to menu")
            break


def open_program():

    # Define player data
    player_data = player(16, 0.25, 0.5, 1)

    # Ensure this function/class is defined elsewhere
    game = stage.Stage(ugame.display, constants.FPS)

    background_image = stage.Bank.from_bmp16("Blank.bmp")
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
    text_1.move(40, 10)
    text_1.text("Cat burglar")
    text.append(text_1)

    # Prompt Tutorial and start options
    text_tut = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_tut.move(0, 100)
    text_tut.text("Press A for tutorial")
    text.append(text_tut)

    text_srt = stage.Text(
        width=29, height=12, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_srt.move(0, 80)
    text_srt.text("Press Start to begin")
    text.append(text_srt)

    # Render new background

    new = []
    off_x = 17
    off_y = 40

    sounds = [
        open("Burglar.wav", "rb"),
        open("step_sound.wav", "rb"),
        open("Victory.wav", "rb"),
        open("MenuTheme.wav", "rb"),
    ]

    now = time.monotonic()
    last_played_menu = 0

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
                new.append(sprite)

    game.layers = text + new + [background]

    game.render_block()

    skip_game_start = False

    # Wait until user clicks select to begin the game
    while True:
        now = time.monotonic()
        game.tick()

        if now - last_played_menu > 7:
            play_sound(sounds, 3)
            last_played_menu = now

        keys = ugame.buttons.get_pressed()
        if keys & ugame.K_START:
            break

        if keys & ugame.K_X:
            tutorial()
            game.layers = text + new + [background]
            game.render_block()
            skip_game_start = True

    if not skip_game_start:

        # Call start function
        game_start(player_data, 0)


if __name__ == "__main__":
    open_program()
