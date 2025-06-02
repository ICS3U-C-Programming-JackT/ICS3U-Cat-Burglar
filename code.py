import time
import math
import random

import stage
import ugame
import displayio
import constants

timer = 60
moving = False

class Color(object):
    """Standard colors"""
    WHITE = 0xFFFFFF
    BLACK = 0x000000
    RED = 0xFF0000
    ORANGE = 0xFFA500
    YELLOW = 0xFFFF00
    GREEN = 0x00FF00
    BLUE = 0x0000FF
    PURPLE = 0x800080
    PINK = 0xFFC0CB

    colors = (BLACK, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, WHITE)

    def __init__(self):
        return self

class player():
    def __init__(self,resolution,refresh,speed,turn):
        # Core stats
        self._fg_bitmap = displayio.Bitmap(5,5,5)
        self.resolution = resolution
        self.refresh = refresh
        self.speed = speed
        self.turn = turn
        self.max_dist = 6
        self.fov = 70
        self.current_map = constants.LEVELS[0]

    def scan(self,origin_x,origin_y,direction):
        rays = []
        for ray_index in range(self.resolution):
            # Calculate offset for each ray based on its angle relative to FOV
            ray_offset_deg = (ray_index - self.resolution / 2) * (self.fov / self.resolution)
            ray_angle = math.radians(direction + ray_offset_deg)

            # Direction vector of the ray
            ray_dir_x = math.cos(ray_angle)
            ray_dir_y = math.sin(ray_angle)

            # Initial position in the map grid
            map_x = int(origin_x)
            map_y = int(origin_y)

            # Distance from one side of a grid cell to the next
            delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
            delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')

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
            side_hit = 0  # 0 = hit x-side (vertical wall), 1 = hit y-side (horizontal wall)

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
                if 0 <= map_x < len(self.current_map[0]) and 0 <= map_y < len(self.current_map):
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

                rays.append({
                    "x": hit_pos_x,
                    "y": hit_pos_y,
                    "distance": distance,
                    "wall": wall_type
                })

        return rays

def game_start(player_data):

    background_image = stage.Bank.from_bmp16("background.bmp")
    image_bank_sprites = stage.Bank.from_bmp16("core_icons.bmp")

    background = stage.Grid(background_image,10,8)
    timer_icon = stage.Sprite(image_bank_sprites,4,10,10)
    temp_icon = stage.Sprite(image_bank_sprites,13,15,15)

    game = stage.Stage(ugame.display, 60)
    
    # Finalize layers
    game.layers = [timer_icon, temp_icon, background]
    game.render_block()

    last_step_sound = time.monotonic()

    # Step sound
    step_sound = open("step_sound.wav","rb")
    sound = ugame.audio
    sound.stop()
    sound.mute(False)
    
    # Game loop
    while True:

        # Render sprites, tick
        game.render_sprites([timer_icon])
        game.render_sprites([temp_icon])
        game.tick()

        # Define Keys
        keys = ugame.buttons.get_pressed()

        # Get keys pressed for movement
        if keys & ugame.K_X:
            print("A")
        if keys & ugame.K_O:
            print("B")
        if keys & ugame.K_START:
            print("Start")
        if keys & ugame.K_SELECT:
            print("Select")
        if keys & ugame.K_RIGHT:
            temp_icon.move(temp_icon.x+1,temp_icon.y)
            if temp_icon.x>=constants.BORDER_RIGHT:
                temp_icon.move(temp_icon.x-1,temp_icon.y)
        if keys & ugame.K_LEFT:
            temp_icon.move(temp_icon.x-1,temp_icon.y)
            if temp_icon.x<=constants.BORDER_LEFT:
                temp_icon.move(temp_icon.x+1,temp_icon.y)
        if keys & ugame.K_UP:
            temp_icon.move(temp_icon.x,temp_icon.y-1)
            if temp_icon.y<=0:
                temp_icon.move(temp_icon.x,127)
        if keys & ugame.K_DOWN:
            temp_icon.move(temp_icon.x,temp_icon.y+1)
            if temp_icon.y>=128:
                temp_icon.move(temp_icon.x,0)
                
        #Check if player is moving
        if keys & (ugame.K_UP | ugame.K_DOWN | ugame.K_LEFT | ugame.K_RIGHT):
            moving = True
        else:
            moving = False

        # Step sfx
        if time.monotonic() - last_step_sound > constants.STEP_SFX_DELAY and moving == True:
            sound.play(step_sound)
            last_step_sound = time.monotonic()
        elif not moving:
            sound.stop()
        if time.monotonic()-int(time.monotonic())<.1:
            timer_icon.set_frame(rotation=random.randint(1,7))
        else:
            timer_icon.set_frame(rotation=0)
        


def open_program():
    player_data = player(16,5,1,90)
    
    while True:
        keys = ugame.buttons.get_pressed()
        if keys & ugame.K_SELECT:
            break
    game_start(player_data)


if __name__ == "__main__":
    open_program()