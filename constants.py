# Level data:
LEVELS = [
    [
        [1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 1],
        [1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1],
        [1, 1, 1, 1, 2, 1],
    ],
    [
        [1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1],
        [1, 0, 1, 1, 0, 1],
        [1, 0, 1, 1, 0, 1],
        [1, 1, 1, 1, 2, 1],
    ],
    [
        [1, 1, 1, 1, 1, 1],
        [1, 0, 1, 0, 0, 1],
        [1, 0, 1, 0, 1, 1],
        [1, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1],
        [1, 1, 1, 1, 2, 1],
    ],
]

FPS = 60

# X and Y coordinates for start and end position in levels.
LEVEL_START = [1, 4]
LEVEL_END = [4, 5]

# Delay for sounds to prevent stopping too early
STEP_SFX_DELAY = 0.5
MUSIC_DELAY = 27

# BMP files
BMP_FILENAMES = ["strp0.bmp", "strp1.bmp", "strp2.bmp", "strp3.bmp", "strp4.bmp"]

# Text color
"""
RED_PALETTE = (
    b"\xff\xff\x00\x22\xcey\x22\xff\xff\xff\xff\xff\xff\xff\xff\xff"
    b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
)
WHITE_PALETTE = b"\xff\xff\xff\xff" * 8
"""

RED_PALETTE = b"\x00\x00\x00\x00\xff\x00\x00\x00" + b"\x00" * 24
WHITE_PALETTE = b"\x00\x00\x00\x00\xff\xff\xff\x00" + b"\x00" * 24


# Round info
ROUND_LENGTH = 30
