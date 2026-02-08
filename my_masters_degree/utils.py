import textwrap
from typing import Tuple

import colorsys
import numpy as np
from scipy.stats import mode

def hls_to_hex(h: float, l: float, s: float, *, from_adobe_or_css: bool = False) -> str:
    """Convert HLS to hex."""
    if from_adobe_or_css:
        hls_arr = np.array([h, s, l]) / [360, 100, 100]
    else:
        hls_arr = np.array([h, l, s]) / [360, 100, 100]
    
    rgb_arr = np.array(colorsys.hls_to_rgb(*hls_arr)) * 255
    rgb_arr = rgb_arr.astype(int)
    # print(rgb_arr)
    return "#" + "".join([f"{c:02x}".upper() for c in rgb_arr])


def get_precise_hls(hex_color: str, *, from_adobe_or_css: bool = False) -> Tuple[float, float, float]:
    colors_hex = textwrap.wrap(hex_color[1:], 2)
    rgb_arr = np.array([int(c, 16) for c in colors_hex], dtype=int)
    hls_arr = np.array(colorsys.rgb_to_hls(*rgb_arr / 255))
    if from_adobe_or_css:
        aux = hls_arr[1]
        hls_arr[1] = hls_arr[2]
        hls_arr[2] = aux
    hls_normalized = hls_arr * [360, 100, 100]
    return tuple(hls_normalized)

def fix_missalignment_hls(hls_matrix: np.ndarray) -> np.ndarray:
    hls_matrix = hls_matrix.copy()
    hls_matrix = hls_matrix[hls_matrix[:, 0].argsort()]
    diff_arr = np.round(np.diff(hls_matrix[:, 0]), 4)
    mode_value, mode_count = mode(diff_arr)
    assert mode_count > 1
    diff_arr_fixed = diff_arr - mode_value
    hls_matrix[:-1, 0] += diff_arr_fixed
    return hls_matrix

if __name__ == "__main__":
    samples_hex = ["#42B356", "#42B3A2", "#42B37C", "#59B342", "#429EB3"]
    samples_hls = [(130, 46, 48), (170, 46, 48), (150, 46, 48), (107, 46, 48), (191, 46, 48)]
    
    result = []
    for s in samples_hex:
        t = get_precise_hls(s, from_adobe_or_css=True)
        result.append(t)
        # result.append(hls_to_hex(*t, from_adobe_or_css=True))
    
    result_matrix = fix_missalignment_hls(np.array(result))

    # result_matrix[:, 2] += 20

    # print(*map(lambda x: hls_to_hex(*x, from_adobe_or_css=True), result_matrix))

    print(result_matrix)

    samples_hex = ["#59B342", "#3A5C30"]
    samples_hls = np.array([get_precise_hls(s, from_adobe_or_css=True) for s in samples_hex])
    print("samples_hls", samples_hls)

    transform_array = np.diff(samples_hls, axis=0)[0]

    print("transform_array", transform_array)

    result_matrix = result_matrix + transform_array

    print(result_matrix)
    print(*map(lambda x: hls_to_hex(*x, from_adobe_or_css=True), result_matrix))
