import pygame, sys
from random import randint
import itertools
import cv2

SCREEN_SIZE = (600, 600)


class Bird(object):
    images = ["assets/sprites/yellowbird-midflap.png", "assets/sprites/yellowbird-upflap.png",
              "assets/sprites/yellowbird-downflap.png"]

    START_SPEED = 1
    GRAVITY = 15
    UP = 30
    ROTATE_ANGLE = 10

    def __init__(self):
        self.x = int(SCREEN_SIZE[0] / 2)
        self.y =  randint(int(SCREEN_SIZE[1] / 10), int(SCREEN_SIZE[1]) - int(SCREEN_SIZE[1]/10)*3) #int(SCREEN_SIZE[1] / 2)  #
        self.speed = Bird.START_SPEED
        self.image = Bird.images[0]
        self.generator = None
        self.score = 0
        self.animation = 0
        self.status = True

    def update_score(self):
        self.score += 10

    def get_score(self):
        return self.score

    def update_position(self):
        self.x += self.speed * 0
        if self.animation and self.animation <= 3:
            self.y -= Bird.UP
        else:
            self.y += Bird.GRAVITY

    def get_position(self):
        return self.x, self.y

    def key_pressed(self):
        self.animation = 1

    def _image_generator(self):
        for image in itertools.cycle(Bird.images):
            yield image

    def get_image(self):
        if self.generator is None:
            self.generator = self._image_generator()
        if self.animation == 0:
            return pygame.image.load(next(self.generator))
        else:
            image = pygame.image.load(next(self.generator))
            return_image = None
            if self.animation == 1:
                return_image = pygame.transform.rotate(image.convert(), Bird.ROTATE_ANGLE)
            elif self.animation == 2:
                return_image = pygame.transform.rotate(image.convert(), 2 * Bird.ROTATE_ANGLE)
            elif self.animation == 3:
                return_image = pygame.transform.rotate(image.convert(), Bird.ROTATE_ANGLE)
            elif self.animation == 4:
                return_image = image
            elif self.animation == 5:
                return_image = pygame.transform.rotate(image.convert(), - Bird.ROTATE_ANGLE)
            elif self.animation == 6:
                return_image = pygame.transform.rotate(image.convert(), - 2 * Bird.ROTATE_ANGLE)
            elif self.animation == 7:
                return_image = pygame.transform.rotate(image.convert(), - Bird.ROTATE_ANGLE)
            self.animation += 1
            if self.animation == 8:
                self.animation = 0
            return return_image

    def lost(self):
        self.status = False

    def get_status(self):
        return self.status


class Pipe(object):
    speed = 10
    image = "assets/sprites/pipe-green.png"
    minSpaceBetweenPipes = 150
    minPipeSize = 20

    def __init__(self):
        self.leftUp = SCREEN_SIZE[0]
        self.image = pygame.image.load(Pipe.image)
        self.image = pygame.transform.scale(self.image, (self.image.get_rect().size[0], SCREEN_SIZE[1]))
        self.rotatedImage = pygame.transform.rotate(self.image, 180)
        self.width, self.height = self.image.get_rect().size
        self.lower, self.upper = self._calculate_images()

    def _calculate_images(self):
        self.lowerSize = randint(Pipe.minPipeSize, SCREEN_SIZE[1] - (Pipe.minPipeSize + Pipe.minSpaceBetweenPipes))
        self.upperSize = SCREEN_SIZE[1] - (self.lowerSize + Pipe.minSpaceBetweenPipes)

        lower = pygame.Surface((self.width, self.lowerSize), pygame.SRCALPHA, 32)  # two last args for transparency
        lower.blit(self.image, (0, 0), (0, 0, self.width, self.lowerSize))

        upper = pygame.Surface((self.width, self.upperSize), pygame.SRCALPHA, 32)  # two last args for transparency
        upper.blit(self.rotatedImage, (0, 0), (0, (self.height - self.upperSize), self.width, self.height))
        return lower, upper

    def get_image(self):
        return self.lower, self.upper

    def update_position(self):
        self.leftUp -= Pipe.speed

    def get_position(self):
        return self.leftUp

    def get_sizes(self):
        return self.lowerSize, self.upperSize


class Board(object):
    backgroundImage = "assets/sprites/background-day.png"
    marginBetweenPipes = 300

    def __init__(self):
        pygame.init()
        self.screen = None
        self.currentScreen = None
        self.pipes = None
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load(Board.backgroundImage)
        self.background = pygame.transform.scale(self.background, SCREEN_SIZE)

    def display_bird(self, bird: Bird):
        self.screen.blit(bird.get_image(), bird.get_position())

    def display_pipe(self, pipe: Pipe):
        lower, upper = pipe.get_image()
        position = pipe.get_position()
        lower_height = lower.get_rect().size[1]
        self.screen.blit(lower, (position, SCREEN_SIZE[1] - lower_height))
        self.screen.blit(upper, (position, 0))
        return position

    def game_logic(self, birds, pipes):
        for bird in birds:
            bird_position = bird.get_position()
            if bird_position[1] >= SCREEN_SIZE[1]:
                bird.lost()
                continue
            for pipe in pipes:
                pipe_position = pipe.get_position()
                pipe_width = pipe.width
                if (bird_position[0] <= pipe_position + pipe_width) and (bird_position[0] >= pipe_position):
                    lower_size, upper_size = pipe.get_sizes()
                    if (bird_position[1] <= upper_size) or (bird_position[1] >= (SCREEN_SIZE[1] - lower_size)):
                        bird.lost()
                        break

    def get_current_screen(self):
        if self.currentScreen is None:
            return None
        return cv2.cvtColor(cv2.transpose(self.currentScreen), cv2.COLOR_BGR2GRAY)

    def get_pipes(self):
        return self.pipes

    def start_board(self, birds, auto=False):
        self.screen = pygame.display.set_mode(self.background.get_rect().size)
        pygame.display.flip()
        self.pipes = [Pipe()]
        i = 0
        while True:
            self.screen.blit(self.background, (0, 0))

            # check game logic and update birds list
            self.game_logic(birds, self.pipes)
            birds = [bird for bird in birds if bird.get_status()]
            if len(birds) == 0:
                break

            # display all birds and update position for the next iteration
            for bird in birds:
                bird.update_score()
                self.display_bird(bird)

            # display all pipes and update position for the next iteration
            for pipe in self.pipes:
                self.display_pipe(pipe)
                pipe.update_position()

            # if the first pipe passed the left side we should delete it
            if self.pipes[0].get_position() + self.pipes[0].width <= 0:
                del self.pipes[0]

            # if the last pipe passed the margin between pipes we should add another pipe
            if SCREEN_SIZE[0] - (self.pipes[-1].get_position() + self.pipes[-1].width) >= Board.marginBetweenPipes:
                self.pipes.append(Pipe())

            if auto:
                pass
            else:
                update_flag = True
                for event in pygame.event.get():
                    if event == pygame.QUIT:
                        sys.exit(0)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            birds[0].key_pressed()
                            update_flag = False
                if update_flag:
                    birds[0].update_position()

            pygame.display.update()
            self.currentScreen = pygame.surfarray.array3d(self.screen)
            self.clock.tick(60)


def event_listener(listener):
    e = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP})
    while True:
        command = listener.readInput()
        if command == 'u':
            pygame.event.post(e)
        elif command == 'x':
            listener.kill()
            break


def main():
    b = Board()
    bird = Bird()
    b.start_board([bird])
    print(bird.get_status())


if __name__ == "__main__":
    main()
