""" Handle loading graphics and returning individual sprites by name."""

from os import path
from typing import Dict

import pygame


def load_graphics(resource_path: str = None) -> Dict[str, pygame.Surface]:
    """
    Loads the spritesheet and breaks it down into individual sprites.

    Args:
        resource_path: Optional path to resources directory. Defaults to ../../../resources

    Returns:
        A dictionary mapping sprite names to pygame.Surface images.

    Raises:
        FileNotFoundError: If spritesheet or definition file not found
        ValueError: If sprite definition file is malformed
        pygame.error: If spritesheet image cannot be loaded
    """
    def _get_image(x: int, y: int, width: int, height: int) -> pygame.Surface:
        """Extract a sprite from the spritesheet."""
        image = pygame.Surface([width, height]).convert()
        image.blit(spritesheet, (0, 0), (x, y, width, height))
        return image

    # Determine resource path
    if resource_path is None:
        dirname = path.dirname(__file__)
        resource_path = path.join(dirname, "..", "..", "resources")

    spritesheet_path = path.join(resource_path, "sprites.jpg")
    def_path = path.join(resource_path, "sprites.txt")

    # Validate files exist
    if not path.exists(spritesheet_path):
        raise FileNotFoundError(
            f"Spritesheet not found at: {spritesheet_path}\n"
            f"Expected location: {path.abspath(spritesheet_path)}"
        )
    if not path.exists(def_path):
        raise FileNotFoundError(
            f"Sprite definition file not found at: {def_path}\n"
            f"Expected location: {path.abspath(def_path)}"
        )

    # Load spritesheet
    try:
        spritesheet = pygame.image.load(spritesheet_path).convert()
        spritesheet.set_colorkey((0, 0, 0))
    except pygame.error as e:
        raise pygame.error(
            f"Unable to load spritesheet image from {spritesheet_path}: {e}"
        ) from e

    # Parse sprite definitions
    sprites = {}
    rowheight = 0
    x = y = 0
    ssw, _ = spritesheet.get_rect().size

    try:
        with open(def_path, 'r', encoding="utf-8") as sprite_definition_file:
            for line_num, line in enumerate(sprite_definition_file, 1):
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue

                parts = line.split()
                if len(parts) < 6:
                    raise ValueError(
                        f"Invalid sprite definition at line {line_num}: '{line}'\n"
                        f"Expected format: name x y width height frame"
                    )

                (name, _, _, w, h, _) = parts[:6]
                try:
                    w = int(w) * 4
                    h = int(h) * 2
                except ValueError as e:
                    raise ValueError(
                        f"Invalid dimensions at line {line_num}: width='{parts[3]}', height='{parts[4]}'"
                    ) from e

                if x + w > ssw:
                    x = 0
                    y += rowheight + 10
                    rowheight = 0

                sprites[name] = _get_image(x, y, w, h)
                x += w + 10
                if h > rowheight:
                    rowheight = h

    except IOError as e:
        raise IOError(f"Error reading sprite definition file {def_path}: {e}") from e

    if not sprites:
        raise ValueError(f"No sprites loaded from {def_path}")

    return sprites
