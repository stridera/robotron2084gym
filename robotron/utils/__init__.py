from typing import Tuple

import numpy as np

def crop(image: np.ndarray, rect) -> np.ndarray:
    """
    Crop an image
    
    Args:
        image (np.ndarray): The image we want to crop
        coords (Tuple[int, int, int, int]): The left, top, right, and 
            bottom crop coords

    Returns:
        np.ndarray: The cropped image
    """
    left, top, right, bottom = rect
    return image[left:right, top:bottom]
