from typing import Tuple

import numpy as np


def crop(image: np.ndarray, dims: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Crop an image

    Args:
        image (np.ndarray): The image we want to crop
        dims (Tuple[int, int, int, int]): The top, left, bottom, and
            right crop coords (matching pygame Rect ordering)

    Returns:
        np.ndarray: The cropped image
    """
    top, left, bottom, right = dims
    return image[top:bottom, left:right]
