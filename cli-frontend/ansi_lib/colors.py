reset = 0
fg_reset = 39

bg_reset = 49

bold = 1
italic = 3
underline = 4

# basic palette
black = 0
red = 1
green = 2
yellow = 3
blue = 4
magenta = 5
cyan = 6
white = 7


# bright color palette
def fg_bright(color):
    return 90 + color


def bg_bright(color):
    return 100 + color


def fg(color):
    return 30 + color


def bg(color):
    return 40 + color


# 256 color palette
def fg_256(color):
    return f"38;5;{color}"


def bg_256(color):
    return f"48;5;{color}"


def fg_rgb(r, g, b):
    return f"38;2;{r};{g};{b}"


def bg_rgb(r, g, b):
    return f"48;2;{r};{g};{b}"
