from os import path
import pygame


def load_graphics():
    """
    Loads the spritesheet and breaks it down into individual sprites.

    Returns:
        dict: A dictionary of sprite names to images.
    """
    def _get_image(x, y, width, height):
        image = pygame.Surface([width, height]).convert()
        image.blit(spritesheet, (0, 0), (x, y, width, height))
        return image

    dirname = path.dirname(__file__)
    resource_path = path.join(dirname, "..", "..", "resources")
    spritesheet_path = path.join(resource_path, "sprites.jpg")
    def_path = path.join(resource_path, "sprites.txt")
    if not path.exists(spritesheet_path) or not path.exists(def_path):
        raise Exception("sprite.jpg and sprite.txt required to be in resources.")

    try:
        spritesheet = pygame.image.load(spritesheet_path).convert()
        spritesheet.set_colorkey((0, 0, 0))
    except pygame.error as e:
        print(f"Unable to load spritesheet image.")
        raise SystemExit(e)

    sprites = {}
    rowheight = 0
    i = x = y = 0
    ssw, _ = spritesheet.get_rect().size

    spriteDefFile = open(def_path, 'r')
    for line in spriteDefFile:
        i += 1
        (name, _, _, w, h, _) = line.split()
        w = int(w) * 4
        h = int(h) * 2
        if x + w > ssw:
            x = 0
            y += rowheight + 10
            rowheight = 0

        sprites[name] = _get_image(x, y, w, h)
        x += w + 10
        if h > rowheight:
            rowheight = h

    return sprites
