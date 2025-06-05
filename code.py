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
        self.max_dist = 6
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

    # Define core sprites
    background = stage.Grid(background_image, 10, 8)
    timer_icon = stage.Sprite(image_bank_sprites, 4, 10, 10)

    # Core game
    game = stage.Stage(ugame.display, 60)
    game_start_time = time.monotonic()
    game_running = True
    game_won = True

    # Finalize layers
    game.layers = [timer_icon, background]
    game.render_block()

    # Sound-related stuff:
    last_step_sound = 0
    last_music_played = 0

    # Render Delay
    last_rendered_walls = time.monotonic()

    # Timer text
    timer = []
    text_timer = stage.Text(
        width=20, height=8, font=None, palette=constants.WHITE_PALETTE, buffer=None
    )
    text_timer.move(15, 10)
    text_timer.text = str(constants.ROUND_LENGTH)
    timer.append(text_timer)

    player_data.x = constants.LEVEL_START[0]
    player_data.y = constants.LEVEL_START[1]

    # Game loop
    while game_running:

        # Render sprites, tick
        game.render_sprites([timer_icon])
        game.tick()

        # Define Keys
        keys = ugame.buttons.get_pressed()

        # Get keys pressed for movement
        if keys & ugame.K_X:
            player_data.rotation -= 1
        if keys & ugame.K_O:
            player_data.rotation += 1
        if keys & ugame.K_START:
            print("Start")
        if keys & ugame.K_SELECT:
            print("Select")

        if keys & ugame.K_RIGHT:
            rotation_radians = radians(player_data.rotation - 90)
            move_step_x = math.cos(rotation_radians) / 50
            move_step_y = math.sin(rotation_radians) / 50
            player_data.x += move_step_x
            player_data.y += move_step_y
        if keys & ugame.K_LEFT:
            rotation_radians = radians(player_data.rotation + 90)
            move_step_x = math.cos(rotation_radians) / 50
            move_step_y = math.sin(rotation_radians) / 50
            player_data.x += move_step_x
            player_data.y += move_step_y
        if keys & ugame.K_UP:
            rotation_radians = radians(player_data.rotation)
            move_step_x = math.cos(rotation_radians) / 50
            move_step_y = math.sin(rotation_radians) / 50
            player_data.x += move_step_x
            player_data.y += move_step_y
        if keys & ugame.K_DOWN:
            rotation_radians = radians(player_data.rotation + 180)
            move_step_x = math.cos(rotation_radians) / 50
            move_step_y = math.sin(rotation_radians) / 50
            player_data.x += move_step_x
            player_data.y += move_step_y

        # Check if player is moving
        if keys & (ugame.K_UP | ugame.K_DOWN | ugame.K_LEFT | ugame.K_RIGHT):
            moving = True
        else:
            moving = False

        # Music
        if time.monotonic() - last_music_played > constants.MUSIC_DELAY:
            play_sound("music")
            last_music_played = time.monotonic()

        if time.monotonic() - int(time.monotonic()) < 0.1:
            timer_icon.set_frame(rotation=random.randint(1, 7))
        else:
            timer_icon.set_frame(rotation=0)

        # Check if walls are ready to be updated
        if time.monotonic() - last_rendered_walls >= player_data.refresh:

            # Get wall sizes and positions
            scan_data = player.scan(
                player_data, player_data.x, player_data.y, player_data.rotation
            )

            # Create array to append to game layers
            new = []
            for ray_n in range(player_data.resolution):

                # Draw a wall sprite at the top
                ray = scan_data[ray_n]
                if ray != None:
                    ray_offset_deg = (ray_n - player_data.resolution / 2) * (
                        player_data.fov / player_data.resolution
                    )

                    # Remove fisheye lens
                    corrected_dist = ray["distance"] * math.cos(
                        math.radians(ray_offset_deg)
                    )

                    # Color of wall if vertical or not
                    palette_index = 1 if ray["wall"] == "vertical" else 5

                    if corrected_dist * 8 > 2:

                        # Triple wall height
                        for wall_num in range(1, 3):
                            ypos = 0
                            if wall_num == 1:
                                ypos = round(-corrected_dist * 8 + 80)
                            elif wall_num == 2:
                                ypos = 80
                            else:
                                ypos = round(corrected_dist * 8 + 80)

                            new.append(
                                stage.Sprite(
                                    palette_bank, palette_index, ray_n * 16, ypos
                                )
                            )
                    elif corrected_dist >= 1:

                        # Double wall height
                        for wall_num in range(1, 2):
                            ypos = (
                                round(-corrected_dist * 8 + 80)
                                if wall_num == 1
                                else round(corrected_dist * 8 + 80)
                            )
                            new.append(
                                stage.Sprite(
                                    palette_bank, palette_index, ray_n * 16, ypos
                                )
                            )
                    else:

                        # Single wall height
                        new.append(
                            stage.Sprite(
                                palette_bank,
                                palette_index,
                                ray_n * 16,
                                round(-corrected_dist * 8 + 80),
                            )
                        )
            # Reset game layers to prevent multiple renders overlapping
            game.layers = new + [timer_icon, background] + timer
            game.render_block()
            game.render_sprites([timer_icon])
            last_rendered_walls = time.monotonic()

        # Update timer text
        text_timer.text = str(
            game_start_time - time.monotonic() + constants.ROUND_LENGTH
        )

        if time.monotonic() - game_start_time >= constants.ROUND_LENGTH:
            game_won = False
            game_running = False

        if check_win(current_level, player_data) == True:
            game_won = True
            game_running = False

        if not game_running:
            break

    play_sound("stop")
    # Transition to next stage or quit logic
    if game_won:
        if current_level + 1 < 3:
            game_start(player_data, current_level + 1)
        else:
            print("You won the whole game!")
            open_program()
    else:
        print("Game over!")
        open_program()


def open_program():
    # Define player data
    player_data = player(16, 0.5, 0.5, 90)

    # Ensure this function/class is defined elsewhere
    game = stage.Stage(ugame.display, 60)

    # Load all image banks for the title screen background
    image_banks = [
        stage.Bank.from_bmp16(filename) for filename in constants.BMP_FILENAMES
    ]

    game.layers = []
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

    game.layers += text

    game.render_block()

    # Wait until user clicks select to begin the game
    while True:
        game.tick()

        keys = ugame.buttons.get_pressed()
        if keys & ugame.K_SELECT:
            break

    # Call start function
    game_start(player_data, 1)


if __name__ == "__main__":
    open_program()
