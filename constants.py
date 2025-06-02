# Level layout: '1-9' = wall, '0' = empty, 's' = start, 'e' = end
# 1 = Default, 2 = Pillar, 3 = Window, 4 = Secondary Colour, 8 = Locked Door, 9 = Elevator
# Due to how I set up scan algorithm, map aspect ratio MUST BE 1:1
LEVELS = [
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 9, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 3],
        [3, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 3],
        [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 3],
        [1, 0, 2, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [3, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 1, 0, 2, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
        [3, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        [3, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
        [3, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 3],
        [1, 1, 0, 2, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
        [3, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
        [3, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 8, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1],
    ],
]

# X and Y coordinates for start and end position in levels.
LEVEL_START = [
    [15, 2],
]
LEVEL_END = [
    [2, 15],
]

BORDER_LEFT = 0
BORDER_RIGHT = 144

STEP_SFX_DELAY = 0.5
MUSIC_DELAY = 27

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 128

BMP_FILENAMES = [
    "strip_0.bmp",
    "strip_1.bmp",
    "strip_2.bmp",
    "strip_3.bmp",
    "strip_4.bmp",
]

STRIP_WIDTH_TILES = 1
STRIP_HEIGHT_TILES = 16

TOTAL_BACKGROUND_WIDTH_TILES = len(BMP_FILENAMES) * STRIP_WIDTH_TILES
TOTAL_BACKGROUND_HEIGHT_TILES = STRIP_HEIGHT_TILES
