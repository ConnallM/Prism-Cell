#Connall Milberry - Prism Cell

import pygame, os, random, time
from pygame.locals import *
import math

# set up the window
WINDOWWIDTH = 1600
WINDOWHEIGHT = 900

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (130, 130, 130)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

#other constants
SPEED = 1
FRAMERATE = 60
LEVELS = 10

def terminate():
    """ This function is called when the user closes the window or presses ESC """
    pygame.quit()
    os._exit(1)

def drawText(text, font, surface, x, y, textcolour):
    """ Draws the text on the surface at the location specified """
    textobj = font.render(text, 1, textcolour)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def load_image(filename):
    """ Load an image from a file.  Return the image and corresponding rectangle """
    image = pygame.image.load(filename)
    #image = image.convert()        #For faster screen updating
    image = image.convert_alpha()   #Not as fast as .convert(), but works with transparent backgrounds
    return image

def LineCollision(x1, y1, x2, y2, x3, y3, x4, y4):
    """ This function takes in 4 points belonging to two lines, and determines whether they intersect or not """

    div = ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))

    #lmao this seems to work
    if div == 0:
        div = 1

    ##calculate the distance to intersection point
    uA = ((x4-x3) * (y1-y3) - (y4-y3) * (x1-x3)) / div
    uB = ((x2-x1) * (y1-y3) - (y2-y1) * (x1-x3)) / div

    ## if uA and uB are between 0-1, lines are colliding
    if uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1:
        return True
    else:
        return False

def CollisionPoint(Ax1, Ay1, Ax2, Ay2, Bx1, By1, Bx2, By2):
    """ This function takes in 8 points and determines the coordinates of where a line and a rect intersect """
    
    d = (By2 - By1) * (Ax2 - Ax1) - (Bx2 - Bx1) * (Ay2 - Ay1)
    if d:
        uA = ((Bx2 - Bx1) * (Ay1 - By1) - (By2 - By1) * (Ax1 - Bx1)) / d
        uB = ((Ax2 - Ax1) * (Ay1 - By1) - (Ay2 - Ay1) * (Ax1 - Bx1)) / d
    else:
        return
    if not(0 <= uA <= 1 and 0 <= uB <= 1):
        return
    x = Ax1 + uA * (Ax2 - Ax1)
    y = Ay1 + uA * (Ay2 - Ay1)
 
    return x, y

def RectLineCollision(rect, lx1, ly1, lx2, ly2):
    """ returns the point of collision """
    #define points of the rectangle
    topleftx, toplefty = rect.topleft
    bottomleftx, bottomlefty = rect.bottomleft
    toprightx, toprighty = rect.topright
    bottomrightx, bottomrighty = rect.bottomright
    
    #do line collision on all sides of the rectangle
    if LineCollision(lx1, ly1, lx2, ly2, toprightx, toprighty, topleftx, toplefty):
        return CollisionPoint(lx1, ly1, lx2, ly2, toprightx, toprighty, topleftx, toplefty)
    elif LineCollision(lx1, ly1, lx2, ly2, topleftx, toplefty, bottomleftx, bottomlefty):
        return CollisionPoint(lx1, ly1, lx2, ly2, topleftx, toplefty, bottomleftx, bottomlefty)
    elif LineCollision(lx1, ly1, lx2, ly2, toprightx, toprighty, bottomrightx, bottomrighty):
        return CollisionPoint(lx1, ly1, lx2, ly2, toprightx, toprighty, bottomrightx, bottomrighty)
    elif LineCollision(lx1, ly1, lx2, ly2, bottomleftx, bottomlefty, bottomrightx, bottomrighty):
        return CollisionPoint(lx1, ly1, lx2, ly2, bottomleftx, bottomlefty, bottomrightx, bottomrighty)
    else:
        return 0
    

# photon class, contains all information about a photon, which is an invisible point that we use to trace the path of the light and do reflections and other interactions
class Photon():
    def __init__(self, speed, start_angle, colour, start_position):
        self.speed = speed
        self.colour = colour
        self.start_position = start_position
        self.position = start_position
        self.start_angle = start_angle
        self.angle = start_angle
        self.Rect = pygame.Rect(start_position[0], start_position[1], 3, 3)
        self.nodes = [start_position]
        self.updating = True
        self.split = False

    def update(self):
        """ updates the position of the photon """
        self.position = (self.position[0] + (self.speed * math.cos(self.angle)), self.position[1] - (self.speed * math.sin(self.angle)))
        self.Rect = pygame.Rect(self.position[0], self.position[1], 3, 3)

# refractor class, contains information to make a sprite and to refract a white photon
class Refractor(pygame.sprite.Sprite):
    def __init__(self, position, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.position = position
        self.mask = pygame.mask.from_surface(image)
        self.mask_outline = pygame.mask.Mask.outline(self.mask)
        self.rect.center = position

        pygame.sprite.Sprite.__init__(self)
    
    def refract(self, photons):
        """ creates three new coloured photons from a single white one """
        red_photon = Photon(1, math.radians(30), 'RED', (self.position[0], self.position[1] + 10))
        green_photon = Photon(1, math.radians(270), 'GREEN', (self.position[0], self.position[1] + 10))
        blue_photon = Photon(1, math.radians(150), 'BLUE', (self.position[0], self.position[1] + 10))
        photons.append(red_photon)
        photons.append(green_photon)
        photons.append(blue_photon)

        return photons

# laser class, contains all information for laser sprite
class Laser(pygame.sprite.Sprite):
    def __init__(self, angle, colour, position, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.angle = angle
        self.colour = colour
        rotated_image = pygame.transform.rotate(image, math.degrees(angle) - 90)
        rotated_rect = rotated_image.get_rect()
        rotated_rect.center = self.rect.center
        self.image = rotated_image
        self.rect = rotated_rect

        pygame.sprite.Sprite.__init__(self)

# detector class, stores all information for detector sprite 
class Detector(pygame.sprite.Sprite):
    def __init__(self, colour, position, image_on, image_off):
        self.image = image_off
        self.image_on = image_on
        self.colour = colour
        self.position = position
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_outline = pygame.mask.Mask.outline(self.mask)
        self.rect = self.image_on.get_rect()
        self.rect.center = position
        self.on = False

        pygame.sprite.Sprite.__init__(self)

# splitter class, contains all information for splitter sprite and to split a photon into two of the same colour with slightly different angles
class Splitter(pygame.sprite.Sprite):
    def __init__(self, position, image):
        self.image = image
        self.position = position
        self.mask = pygame.mask.from_surface(image)
        self.mask_outline = pygame.mask.Mask.outline(self.mask)
        self.rect = self.image.get_rect()
        self.rect.center = position

        pygame.sprite.Sprite.__init__(self)

    def split(self, photons, photon):
        """ creates two photons of the same colour with slightly different angles from a single photon """
        photons.append(Photon(1, photon.angle + math.radians(30), photon.colour, (photon.Rect.centerx, photon.Rect.centery)))
        photons[len(photons) - 1].split = True
        photons.append(Photon(1, photon.angle - math.radians(30), photon.colour, (photon.Rect.centerx, photon.Rect.centery)))
        photons[len(photons) - 1].split = True
        photon.updating = False
        photon.split = True

        return photons

# wall class, contains dimensions and position of walls                                                                                         
class Wall():
    def __init__(self, position, width, length):
        self.position = position
        self.length = length
        self.width = width
        self.rect = (position[0], position[1], width, length)

# game class
class Game():
    """ This class represents an instance of the game. If we need to
        reset the game we'd just need to create a new instance of this
        class. """
     
    def __init__(self):
        """ Constructor. Create all our attributes and initialize
        the game."""
        self.first = False
        self.lines = []
        self.click = False
        self.reflect_sound = pygame.mixer.Sound('Music and Sounds/mixkit-sci-fi-positive-notification-266.wav')
        self.reflect_sound.set_volume(0.1)
        self.refract_sound = pygame.mixer.Sound('Music and Sounds/mixkit-sci-fi-interface-zoom-890.wav')
        self.refract_sound.set_volume(0.1)
        self.detect_sound = pygame.mixer.Sound('Music and Sounds/mixkit-sci-fi-click-900.wav')
        self.detect_sound.set_volume(0.25)
        self.split_sound = pygame.mixer.Sound('Music and Sounds/mixkit-futuristic-robotic-fast-sweep-171.wav')
        self.split_sound.set_volume(0.05)

        self.complete = False
        
        self.update = True

        self.walls = []
        self.refractors = []
        self.lasers = []
        self.detectors = []
        self.splitters = []
        self.photons = []
        self.initial_photons = []
        self.mirrors = None

        self.start = False

        self.musicplaying = True

        self.total_time = 0

        self.start_time = None

    def load_level(self, level):
        """ loads all the necessary elements from a text file into the game class """
        self.level = str(level)
        file = open(level, 'r')
        lines = file.readlines()
        self.walls = []
        self.refractors = []
        self.lasers = []
        self.detectors = []
        self.splitters = []

        #check all properties of each line and add class objects to their respective lists
        for line in lines:
            line = line.split()
            if line[0] == 'laser':
                image = pygame.image.load(line[5])
                position = (int(line[3]), int(line[4]))
                laser = Laser(math.radians(int(line[1])), line[2], position, image)
                self.lasers.append(laser)
                photon = Photon(SPEED, math.radians(int(line[1])), line[2], position)
                self.photons.append(photon)
                self.initial_photons.append(photon)
            elif line[0] == 'detector':
                image_on = pygame.image.load(line[4])
                image_off = pygame.image.load(line[5])
                position = (int(line[2]), int(line[3]))
                detector = Detector(line[1], position, image_on, image_off)
                self.detectors.append(detector)
            elif line[0] == 'wall':
                position = (int(line[1]), int(line[2]))
                wall = Wall(position, int(line[3]), int(line[4]))
                self.walls.append(wall)
            elif line[0] == 'splitter':
                image = pygame.image.load(line[3])
                position = (int(line[1]), int(line[2]))
                splitter = Splitter(position, image)
                self.splitters.append(splitter)
            elif line[0] == 'refractor':
                image = pygame.image.load(line[3])
                position = (int(line[1]), int(line[2]))
                refractor = Refractor(position, image)
                self.refractors.append(refractor)
            elif line[0] == 'mirrors':
                self.mirrors = line[1]
        self.all_sprites = pygame.sprite.Group()
        for laser in self.lasers:
            self.all_sprites.add(laser)
        for detector in self.detectors:
            self.all_sprites.add(detector)
        for splitter in self.splitters:
            self.all_sprites.add(splitter)
        for refractor in self.refractors:
            self.all_sprites.add(refractor)
        #print(self.initial_photons)

    def process_events(self, windowSurface, x):
        """ Process all of the keyboard and mouse events.  """
        
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:

                #undo latest mirror
                if event.key == ord('z') and len(self.lines) > 0 and x > 1:
                    self.photons = []
                    for photon in self.initial_photons:
                        self.photons.append(photon)
                    for photon in self.photons:
                        photon.position = photon.start_position
                        photon.Rect = pygame.Rect(photon.start_position[0], photon.start_position[1], 3, 3)
                        photon.angle = photon.start_angle
                        photon.nodes = [photon.start_position]
                        photon.split = False
                        photon.updating = True
                    self.lines.pop()
                    for detector in self.detectors:
                        detector.on = False
                        self.all_sprites.remove(detector)
                        detector = Detector(detector.colour, detector.position, detector.image_on, detector.image)
                        self.all_sprites.add(detector)
                #skip level and exit tutorial
                if event.key == pygame.K_RETURN:
                    if not self.start:
                        self.start_time = time.time()
                    self.start = True
                    self.complete = True

                #stop/start music
                if event.key == ord('m'):
                    if self.musicplaying:
                        self.musicplaying = False
                        pygame.mixer.music.stop()
                    else:
                        self.musicplaying = True
                        pygame.mixer.music.play()

                #reset lasers
                if event.key == ord('r'):
                    self.photons = []
                    for photon in self.initial_photons:
                        self.photons.append(photon)
                    for photon in self.photons:
                        photon.position = photon.start_position
                        photon.Rect = pygame.Rect(photon.start_position[0], photon.start_position[1], 3, 3)
                        photon.angle = photon.start_angle
                        photon.nodes = [photon.start_position]
                        photon.split = False
                        photon.updating = True

                    for detector in self.detectors:
                        detector.on = False
                        self.all_sprites.remove(detector)
                        detector = Detector(detector.colour, detector.position, detector.image_on, detector.image)
                        self.all_sprites.add(detector)
            #first part of drawing a mirror
            elif event.type == MOUSEBUTTONDOWN and x > 1 and len(self.lines) < int(self.mirrors):
                if not self.first:
                    self.start = event.pos
                    self.first = True
                    self.click = True
            #second part of drawing a mirror
            elif event.type == MOUSEBUTTONUP and x > 1 and len(self.lines) < int(self.mirrors):
                self.end = event.pos
                self.first = False
                self.lines.append((self.start, self.end))
                
                self.photons = []
                for photon in self.initial_photons:
                    self.photons.append(photon)
                for photon in self.photons:
                    photon.position = photon.start_position
                    photon.Rect = pygame.Rect(photon.start_position[0], photon.start_position[1], 3, 3)
                    photon.angle = photon.start_angle
                    photon.nodes = [photon.start_position]
                    photon.split = False
                    photon.updating = True
                self.click = False
                for detector in self.detectors:
                    detector.on = False
                    self.all_sprites.remove(detector)
                    detector = Detector(detector.colour, detector.position, detector.image_on, detector.image)
                    self.all_sprites.add(detector)
                        
        if self.click:
            self.temp = pygame.mouse.get_pos()
            temp_line = (self.start, self.temp)
            return temp_line


    def run_logic(self, windowSurface):
        """ This method is run each time through the frame. It
        updates positions and checks for collisions. This focusses on detecting collisions between photons and other objects """
        for photon in self.photons:
            if photon.updating:
                #wall logic
                for wall in self.walls:
                    if photon.Rect.colliderect(wall.rect):
                        photon.updating = False

                #detector logic
                for detector in self.detectors:
                    for pixel in detector.mask_outline:
                         if (pixel[0] + detector.rect.topleft[0] > photon.Rect.left) and (pixel[0] + detector.rect.topleft[0] < photon.Rect.right) and (pixel[1] + detector.rect.topleft[1] > photon.Rect.top) and (pixel[1] + detector.rect.topleft[1] < photon.Rect.bottom):
                             if photon.colour == detector.colour:
                                self.all_sprites.remove(detector)
                                detector.on = True
                                detector = Detector(detector.colour, detector.position, detector.image, detector.image_on)
                                self.all_sprites.add(detector)
                                self.detect_sound.play()
                             photon.updating = False
                             break
                #reflection logic
                for line in self.lines:
                    node = RectLineCollision(photon.Rect, line[0][0], line[0][1], line[1][0], line[1][1])
                    if node != 0 and node is not None:
                        if (line[1][0] - line[0][0]) != 0:
                            angle = math.atan(-(line[1][1] - line[0][1]) / (line[1][0] - line[0][0]))
                        else:
                            angle = math.radians(90)
                        photon.angle = -photon.angle + angle * 2
                        photon.nodes.append(node)
                        self.reflect_sound.play()
                        break

                #splitter logic
                for splitter in self.splitters:
                    if not photon.split:
                        for pixel in splitter.mask_outline:
                            if (pixel[0] + splitter.rect.topleft[0] > photon.Rect.left) and (pixel[0] + splitter.rect.topleft[0] < photon.Rect.right) and (pixel[1] + splitter.rect.topleft[1] > photon.Rect.top) and (pixel[1] + splitter.rect.topleft[1] < photon.Rect.bottom):
                                self.photons = splitter.split(self.photons, photon)
                                self.split_sound.play()
                         
                #refractor logic
                for refractor in self.refractors:
                    if photon.colour == 'WHITE':
                        for pixel in refractor.mask_outline:
                            if (pixel[0] + refractor.rect.topleft[0] > photon.Rect.left) and (pixel[0] + refractor.rect.topleft[0] < photon.Rect.right) and (pixel[1] + refractor.rect.topleft[1] > photon.Rect.top) and (pixel[1] + refractor.rect.topleft[1] < photon.Rect.bottom):
                                refractor.refract(self.photons)
                                self.refract_sound.play()
                                photon.updating = False
                                break
                        photon.update()
                    elif photon.colour != 'WHITE' and photon.updating:
                        photon.update()
                if photon.updating:
                    photon.update()

        #check if level is complete      
        for detector in self.detectors:
            if detector.on:
                self.complete = True
            else:
                self.complete = False
                break
        if self.complete and self.start_time is not None:
            self.total_time += round(time.time() - self.start_time, 3)
            self.start_time = time.time()
            
                
    def display_frame(self, windowSurface, temp_line, x):
        """ Display everything to the screen for the game. """
        windowSurface.fill(BLACK)

        for photon in self.photons:
            for i in range(len(photon.nodes) - 1):
                pygame.draw.aaline(windowSurface, photon.colour, photon.nodes[i], photon.nodes[i + 1], 5)
            
            pygame.draw.aaline(windowSurface, photon.colour, photon.nodes[len(photon.nodes) - 1], (photon.Rect.centerx, photon.Rect.centery), 5)
            #pygame.draw.circle(windowSurface, photon.colour, photon.Rect.center, 5, 0)

        self.all_sprites.draw(windowSurface)

        #display level
        if x >= 1:
            basicFont = pygame.font.Font('BrickshaperseXPx.ttf', 56)
            text = basicFont.render('Level: ' + str(x), True, WHITE)
            textRect = text.get_rect()
            textRect.center = (800, 50)
            windowSurface.blit(text, textRect)

        #display number of remaining mirrors
        if self.mirrors is not None:
            basicFont = pygame.font.Font('BrickshaperseXPx.ttf', 36)
            text = basicFont.render('Mirrors: ' + str(int(self.mirrors) - len(self.lines)), True, WHITE)
            textRect = text.get_rect()
            textRect.center = (800, 100)
            windowSurface.blit(text, textRect)

        #display time
        if x >= 1 and x is not None:
            basicFont = pygame.font.Font('BrickshaperseXPx.ttf', 36)
            text = basicFont.render(str(round(time.time() - start_time, 2)), True, WHITE)
            textRect = text.get_rect()
            textRect.center = (800, 150)
            windowSurface.blit(text, textRect)

        #display all walls
        for wall in self.walls:
            pygame.draw.rect(windowSurface, GRAY, wall.rect)
            
        #draws the mirrors
        if self.level[13] != '0':
            for line in self.lines:
                pygame.draw.aaline(windowSurface, GRAY, line[0], line[1], 5)

        # draw the temporary mirror
        if temp_line is not None:
            pygame.draw.aaline(windowSurface, GRAY, temp_line[0], temp_line[1], 5)
            pygame.display.update()
            temp_last = temp_line            

def main():
    """ Mainline for the program """

    #set up game
    pygame.init()
    mainClock = pygame.time.Clock()

    windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
    screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    
    pygame.display.set_caption("Game Project")
    game = Game()
    windowSurface.fill(BLACK)
    count = 0
    pygame.mixer.music.load('Music and Sounds/quads.mp3')
    pygame.mixer.music.set_volume(0.25)
    pygame.mixer.music.play(-1, 0.0)

    #load each of the levels
    for x in range(LEVELS + 2):
        game = Game()
        game.load_level('Levels/Level ' + str(x) + '.txt')
        game.complete = False

        #special case for initial screen
        if x == 0:
            while not game.start:
                game.run_logic(windowSurface)

                temp_line = game.process_events(windowSurface, x)

                game.display_frame(windowSurface, temp_line, x - 1)

                basicFont = pygame.font.Font('BrickshaperseXPx.ttf', 108)
                text = basicFont.render('Prism    Cell', True, WHITE)
                textrect = text.get_rect()
                textrect.topleft = (900, 400)
                windowSurface.blit(text, textrect)
                
                basicFont = pygame.font.Font('BrickshaperseXPx.ttf', 56)
                text = basicFont.render('Press Enter to Start', True, WHITE)
                textrect = text.get_rect()
                textrect.topleft = (100, 775)
                windowSurface.blit(text, textrect)
                
                if count == 3:
                    pygame.display.update()
                    count = 0
                count += 1
                game.complete = True
            game.start = False

        # special case for tutorial screen
        elif x == 1:
            while not game.start:
                game.run_logic(windowSurface)

                temp_line = game.process_events(windowSurface, x)

                game.display_frame(windowSurface, temp_line, x - 1)

                basicFont = pygame.font.Font('BrickshaperseXPx.ttf', 56)
                
                text = basicFont.render('Click and drag to draw mirrors', True, WHITE)
                textrect = text.get_rect()
                textrect.topleft = (200, 100)
                windowSurface.blit(text, textrect)

                text = basicFont.render('to reflect light into the detectors.', True, WHITE)
                textrect = text.get_rect()
                textrect.topleft = (200, 200)
                windowSurface.blit(text, textrect)

                text = basicFont.render('Colours MUST match.', True, WHITE)
                textrect = text.get_rect()
                textrect.topleft = (200, 300)
                windowSurface.blit(text, textrect)
                
                text = basicFont.render('Press Z to undo', True, WHITE)
                textrect = text.get_rect()
                textrect.topleft = (1000, 100)
                windowSurface.blit(text, textrect)

                text = basicFont.render('the last mirror that you drew.', True, WHITE)
                textrect = text.get_rect()
                textrect.topleft = (1000, 200)
                windowSurface.blit(text, textrect)

                text = basicFont.render('You have a limited number of mirrors.', True, WHITE)
                textrect = text.get_rect()
                textrect.topleft = (1000, 300)
                windowSurface.blit(text, textrect)

                text = basicFont.render('Press Enter to skip the current level, or exit this tutorial.', True, WHITE)
                textrect = text.get_rect()
                textrect.topleft = (500, 600)
                windowSurface.blit(text, textrect)

                text = basicFont.render('Press M to start/stop the music.', True, WHITE)
                textrect = text.get_rect()
                textrect.topleft = (500, 700)
                windowSurface.blit(text, textrect)

                text = basicFont.render('You may also choose to press R at any time to reset the lasers.', True, WHITE)
                textrect = text.get_rect()
                textrect.topleft = (500, 800)
                windowSurface.blit(text, textrect)
                
                pygame.display.update()

                game.complete = True
                global start_time
                start_time = time.time()
            game.start = False
        
        # game loop
        while not game.complete:
            game.run_logic(windowSurface)

            temp_line = game.process_events(windowSurface, x)
            if count == 3:
                game.display_frame(windowSurface, temp_line, x - 1)
                pygame.display.update()
                count = 0
            count += 1

            #mainClock.tick(FRAMERATE)
        game.display_frame(windowSurface, temp_line, x)
        pygame.display.update()
        time.sleep(0.5)

    #credits
    windowSurface.fill(BLACK)
    basicFont = pygame.font.Font('BrickshaperseXPx.ttf', 108)
    text = basicFont.render('Congratulations on completing Prism Cell!', True, WHITE)
    textrect = text.get_rect()
    textrect.topleft = (100, 100)
    windowSurface.blit(text, textrect)

    basicFont = pygame.font.Font('BrickshaperseXPx.ttf', 56)
    text = basicFont.render('You took ' + str(round(time.time() - start_time, 2)) + ' seconds to complete the game!', True, WHITE)
    textrect = text.get_rect()
    textrect.topleft = (100, 200)
    windowSurface.blit(text, textrect)

    basicFont = pygame.font.Font('BrickshaperseXPx.ttf', 56)
    text = basicFont.render('I hope you enjoyed it!', True, WHITE)
    textrect = text.get_rect()
    textrect.topleft = (100, 300)
    windowSurface.blit(text, textrect)

    text = basicFont.render('A short game created by Connall Milberry', True, WHITE)
    textrect = text.get_rect()
    textrect.topleft = (100, 400)
    windowSurface.blit(text, textrect)

    text = basicFont.render('With music by Callum Gillies (bonus marks for Callum)', True, WHITE)
    textrect = text.get_rect()
    textrect.topleft = (100, 500)
    windowSurface.blit(text, textrect)

    text = basicFont.render('Completed on June 20 2021', True, WHITE)
    textrect = text.get_rect()
    textrect.topleft = (100, 600)
    windowSurface.blit(text, textrect)

    pygame.display.update()
    
    while True:
        game.process_events(windowSurface, 0)
main()
