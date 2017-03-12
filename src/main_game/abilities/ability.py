# Interface for abilities
# Author: Caleb
# "Winter" 2017

import pygame

class Ability(pygame.sprite.Sprite):
    pass

    def draw_icon(self, x, y, window):
        window.blit(self.icon, (x, y))

    @classmethod
    def apply_effects(cls, enemy):
        pass

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def __str__(self):
        return self.name

    @classmethod
    def apply_cost(cls, user):
        pass

    @classmethod
    def can_be_used_by(cls, user):
        return True

    @classmethod
    def can_be_used_on(cls, target):
        return True

    @classmethod
    def add_effect(cls, effects):
        pass
