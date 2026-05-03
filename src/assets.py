import pygame


class Assets:
    _images = {}
    _sounds = {}

    @classmethod
    def image(cls, path):
        if path not in cls._images:
            cls._images[path] = pygame.image.load(path).convert_alpha()
        return cls._images[path]

    @classmethod
    def sound(cls, path):
        if path not in cls._sounds:
            cls._sounds[path] = pygame.mixer.Sound(path)
        return cls._sounds[path]

# how is this caching you may ask?
# it is caaching becuse we add everything into _images, and _sounds and everything is read only once
# then we check if an item is in _images or _sounds, so we never have to read a file twice