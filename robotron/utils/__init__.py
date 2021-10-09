from typing import Tuple

import numpy as np

def crop(self, image: np.ndarray, left: int, top: int, right: int, bottom: int) -> np.ndarray:
    """
    Crop an image
    
    Args:
        image (np.ndarray): The image we want to crop
        coords (Tuple[int, int, int, int]): The left, top, right, and 
            bottom crop coords

    Returns:
        np.ndarray: The cropped image
    """
    return image[left:right, top:bottom]
