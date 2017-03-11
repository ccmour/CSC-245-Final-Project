# A class for world
# Author: Caleb
# Winter 2017

import json

import pygame

from main_game.tile import Tile
from main_game.door import Door
from constants import TILE_WIDTH


class World:

    def __init__(self, x, y, spritesheet):

        self.width = x
        self.height = y
        self.tile_width = TILE_WIDTH
        self.bg_sprites = pygame.sprite.Group()
        self.fg_sprites = pygame.sprite.Group()
        self.spritesheet = spritesheet

        self.foreground_tiles = []
        self.background_tiles = []
        for column in range(x):
            self.foreground_tiles += [[]]
            self.background_tiles += [[]]

            for row in range(y):
                newTile = Tile(self.spritesheet,
                               (0, 0),
                               (column, row))
                self.bg_sprites.add(newTile)
                self.foreground_tiles[column] += [None]
                self.background_tiles[column] += [newTile]
        self.border = pygame.Rect(0, 0, x * self.tile_width, y * self.tile_width)

        self.parties = []

    @classmethod
    def load(cls, name):
        data = json.load(open("../assets/worlds/" + name + ".json"))
        world = World(data["width = "], data["height = "], pygame.image.load(
            "../assets/images/TheSheet.png").convert_alpha())
        world.import_world("../assets/worlds/"+name+".json")
        return world

    def add_party(self, party):
        self.parties += [party]

    def remove_party(self, party):
        self.parties.remove(party)

    def simulate(self):
        door = None
        for party in self.parties:
            door_to_test = party.simulate(1)
            if isinstance(door_to_test, Door):
                door = door_to_test
        return door

    def draw(self, window):
        self.bg_sprites.draw(window)
        self.fg_sprites.draw(window)

        for party in self.parties:
            party.draw(window)

    # Returns a the result of drawing the world, but only actually draws the part that will appear in the
    # clip_rect.  This saves a lot of resources because the world may be much larger than the part that will
    # appear on the screen.
    def get_draw_buffer(self, clip_rect):

        # Makes an empty buffer of the size of the world.  The buffer is transparent, so they can be overlayed.
        buffer = pygame.Surface((self.border.w, self.border.h), pygame.SRCALPHA, 32)
        # Indicates the clipping rectangle.  Subsequent draws to this buffer will only draw if the result would
        # appear in the clipping rectangle.
        buffer.set_clip(clip_rect)
        buffer = buffer.convert_alpha()
        self.draw(buffer)

        return buffer

    def get_border(self):
        return self.border

    def get_bg_tile(self, x, y):
        return self.background_tiles[x][y]

    def get_fg_tile(self, x, y):
        return self.foreground_tiles[x][y]

    def add_foreground_tile(self, x, y, sprite_rect):
        tile = Tile(self.spritesheet, (33, 33), (x, y))
        tile.change_sprite(sprite_rect)
        self.fg_sprites.add(tile)
        self.foreground_tiles[x][y] = tile

    def replace_tile_with_door(self, x, y, fg, dest_world, dest_coords):
        if fg:
            tile = self.get_fg_tile(x, y)
            door = Door(tile.spritesheet,
                        tile.sprite_loc,
                        tile.world_loc,
                        dest_world,
                        dest_coords)
            self.foreground_tiles[x][y] = door
            self.fg_sprites.remove(tile)
            self.fg_sprites.add(door)
        else:
            tile = self.get_bg_tile(x, y)
            door = Door(tile.spritesheet,
                        tile.sprite_loc,
                        tile.world_loc,
                        dest_world,
                        dest_coords)
            door.swap_image()
            self.background_tiles[x][y] = door
            self.bg_sprites.remove(tile)
            self.bg_sprites.add(door)

    def replace_door_with_tile(self, x, y, fg):
        if fg:
            door = self.get_fg_tile(x, y)
            tile = Tile(door.spritesheet,
                        door.sprite_loc,
                        door.world_loc)
            self.foreground_tiles[x][y] = tile
            self.fg_sprites.remove(door)
            self.fg_sprites.add(tile)
        else:
            door = self.get_bg_tile(x, y)
            tile = Tile(door.spritesheet,
                        door.sprite_loc,
                        door.world_loc)
            self.background_tiles[x][y] = tile
            self.bg_sprites.remove(door)
            self.bg_sprites.add(tile)

    def collide_parties(self, collider):
        '''
        Get a list of parties colliding with the collider
        :param collider:
        :return:
        '''
        parties = []

        for party in self.parties:
            if party != collider and party.hitbox.colliderect(collider.hitbox):
                parties += [party]
        return parties

    def collide_tiles(self, collider):
        '''
        Get a list of tiles colliding with the collider
        :param collider:
        :return:
        '''

        tiles = []

        for column in self.foreground_tiles:
            for tile in column:
                if tile != None and tile.rect.colliderect(collider.hitbox):
                    tiles += [tile]
        for column in self.background_tiles:
            for tile in column:
                if tile.rect.colliderect(collider.hitbox):
                    tiles += [tile]
        return tiles

    def export_world(self, path):
        background_tiles = []
        foreground_tiles = []
        for x in range(0, self.width):
            background_column = []
            foreground_column = []
            for y in range(0, self.height):
                background_column += [self.background_tiles[x][y].to_json()]

                tile = self.foreground_tiles[x][y]
                if tile:
                    foreground_column += [tile.to_json()]
                else:
                    foreground_column += [None]
            background_tiles += [background_column]
            foreground_tiles += [foreground_column]

        write_object = {
            "width = ": self.width,
            "height = ": self.height,
            "background": background_tiles,
            "foreground": foreground_tiles
        }

        with open(path, 'w') as outfile:
            json.dump(write_object, outfile)

    def import_world(self, path):
        data = json.load(open(path))

        self.background_tiles = []
        self.foreground_tiles = []
        self.bg_sprites = pygame.sprite.Group()
        self.fg_sprites = pygame.sprite.Group()

        for column in range(self.width):
            self.background_tiles += [[]]
            self.foreground_tiles += [[]]

            for row in range(self.height):
                background_tile_data = data["background"][column][row]
                foreground_tile_data = data["foreground"][column][row]
                if "dest_world" in background_tile_data:
                    dest_x = int(background_tile_data["dest_x"])
                    dest_y = int(background_tile_data["dest_y"])
                    background_tile = Door(self.spritesheet,
                                           background_tile_data["sprite_loc"],
                                           (column, row),
                                           background_tile_data["dest_world"],
                                           (dest_x, dest_y))
                else:
                    background_tile = Tile(self.spritesheet,
                                           background_tile_data["sprite_loc"],
                                           (column, row))
                if not background_tile_data["passable"]:
                    background_tile.passable = False
                if background_tile_data["flipped"]:
                    background_tile.sprite_flipped = True
                    background_tile.image = pygame.transform.flip(background_tile.image, True, False)
                    background_tile.alt_img = pygame.transform.flip(background_tile.alt_img, True, False)

                self.bg_sprites.add(background_tile)
                self.background_tiles[column] += [background_tile]

                if foreground_tile_data:
                    if "dest_world" in foreground_tile_data:
                        dest_x = int(foreground_tile_data["dest_x"])
                        dest_y = int(foreground_tile_data["dest_y"])
                        foreground_tile = Door(self.spritesheet,
                                               foreground_tile_data["sprite_loc"],
                                               (column, row),
                                               foreground_tile_data["dest_world"],
                                               (dest_x, dest_y))
                    else:
                        foreground_tile = Tile(self.spritesheet,
                                               foreground_tile_data["sprite_loc"],
                                               (column, row))
                    if not foreground_tile_data["passable"]:
                        foreground_tile.passable = False
                    if foreground_tile_data["flipped"]:
                        foreground_tile.sprite_flipped = True
                        foreground_tile.image = pygame.transform.flip(foreground_tile.image, True, False)
                        foreground_tile.alt_img = pygame.transform.flip(foreground_tile.alt_img, True, False)

                    self.fg_sprites.add(foreground_tile)
                    self.foreground_tiles[column] += [foreground_tile]
                else:
                    self.foreground_tiles[column] += [None]
