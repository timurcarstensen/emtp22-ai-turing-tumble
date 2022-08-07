"""
Auxiliary function: uploads auxiliary TT matrix to Jesse Crossen simulator.
"""

# standard library imports
import base64
import webbrowser
from io import BytesIO
from typing import List

# 3rd party imports
from PIL import Image
import numpy as np

parts = {
    "NotValid": -100,
    "Valid": 0,
    "GreenLeft": 1,
    "GreenRight": 2,
    "Orange": 3,
    "Red": 4,
    "BlueLeft": 5,
    "Black": 6,
    "BlueWheelLeft": 7,
    "BlueWheelRight": 8,
    "BlueRight": 9,
    "LightGrey": -99,
    "DarkGrey": -98
}
colors = {
    "notValid": [32, 32, 32, 254],
    "red": [255, 0, 0, 255],
    "greenRight": [0, 255, 0, 255],
    "greenLeft": [0, 189, 0, 255],
    "orange": [255, 128, 0, 255],
    "blueLeft": [0, 255, 255, 255],
    "blueWheelLeft": [128, 0, 255, 255],
    "black": [0, 0, 0, 255],
    "white": [255, 255, 255, 255],
    "blueWheelRight": [96, 0, 189, 255],
    "blueRight": [0, 189, 189, 255],
    "lightGrey": [128, 128, 128, 254],
    "darkGrey": [96, 96, 96, 254]
}


def translate_value_to_color(val: int) -> List:
    """
    Auxiliary function to assign RGBA values to TT board pieces;
    needed to generate picture for upload to Jesse Crossen TT simulator.

    :param val: integer representing TT piece
    :return: colors: list of RGBA values
    """
    if val == parts["NotValid"]:
        return colors["notValid"]

    if val == parts["GreenLeft"]:
        return colors["greenLeft"]

    if val == parts["Black"]:
        return colors["black"]

    if val == parts["BlueLeft"]:
        return colors["blueLeft"]

    if val == parts["BlueRight"]:
        return colors["blueRight"]

    if val == parts["BlueWheelLeft"]:
        return colors["blueWheelLeft"]

    if val == parts["BlueWheelRight"]:
        return colors["blueWheelRight"]

    if val == parts["DarkGrey"]:
        return colors["darkGrey"]

    if val == parts["GreenRight"]:
        return colors["greenRight"]

    if val == parts["LightGrey"]:
        return colors["lightGrey"]

    if val == parts["Orange"]:
        return colors["orange"]

    if val == parts["Red"]:
        return colors["red"]

    return colors["white"]


def translate_matrix_to_board(mat: np.ndarray) -> str:
    """
    Takes matrix indicating placement of TT pieces and returns link for Jesse Crossen TT simulator.

    :param mat: auxiliary matrix indicating position of TT pieces on board.
    :return: formatted_str: image for upload to Jesse Crossen TT simulator in base 64.
    """
    mat = np.array(mat)
    img = Image.open('assets/long_board.png')
    pixel_map = img.load()

    rows = len(mat)
    cols = len(mat[0])
    z = int((cols - 1) / 2)
    for i in range(z):
        for j in range(z - i):
            mat[i, j] = parts["NotValid"]
            mat[i, cols - j - 1] = parts["NotValid"]
    z2 = int((cols - 3) / 2)
    for j in range(z2):
        mat[rows - 1, j] = parts["LightGrey"]
        mat[rows - 1, cols - j - 1] = parts["DarkGrey"]
    # testing:
    mat[rows - 2, 0] = parts["LightGrey"]
    mat[rows - 2, cols - 1] = parts["DarkGrey"]
    print(mat)

    for i in range(1, rows + 1):
        for j in range(2, cols + 2):
            # translates the value from the matrix into an rgba value (r, g, b, a)
            color = tuple(translate_value_to_color(mat[i - 1][j - 2]))
            pixel_map[j - 1, i + 1] = color

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    print(img_str)
    formatted_str = f"data:image/png;base64,{str(img_str)[2:-1]}"
    return formatted_str


def open_new_board(mat: np.ndarray):
    """
    Opens base-64 representation of TT board in browser.

    :param mat: numpy array indicating positioning of TT pieces on board
    :return: (nothing): displays TT board in browser.
    """
    ttsim_link = "https://jessecrossen.github.io/ttsim/#s=17,33&z=32&cc=8&cr=16&t=2&sp=1&sc=0&b="
    board = translate_matrix_to_board(mat)
    webbrowser.open(ttsim_link + board, new=2)
