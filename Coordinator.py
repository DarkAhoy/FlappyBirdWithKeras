from threading import Thread
import numpy as np
import time
from multiprocessing.pool import ThreadPool

# local imports
from Game import SCREEN_SIZE, Bird, Board
from Network.Model import Model
import GeneticUtils

BIRDS_COUNT = 10


class ModelWithScore():
    def __init__(self, model, score):
        self.model = model
        self.score = score

    def get_model(self):
        return self.model

    def get_score(self):
        return self.score

    def update_score(self, score):
        self.score = score

    def copy(self, other):
        self.model.copy(other.get_model())
        self.score = other.get_score()

    def __eq__(self, other):
        return self.score == other.score

    def __gt__(self, other):
        return self.score > other.score

    def __lt__(self, other):
        return self.score < other.score

    def __str__(self):
        return 'Model name: {} Score: {}'.format(self.model.name, self.score)

    def __repr__(self):
        return str(self)


def start_board(board, birds):
    t = Thread(target=board.start_board, args=(birds, True,))
    t.daemon = True
    t.start()


def get_input_from_bird(bird: Bird, pipes):
    x, y = bird.get_position()
    height = SCREEN_SIZE[1] - y
    distance_from_pipe = 0
    lower_pipe_height = 0
    higher_pipe_height = 0
    for pipe in pipes:
        pipe_position = pipe.get_position()
        if not pipe_position < x:
            distance_from_pipe = pipe_position - x
            lower_pipe_height = pipe.lowerSize
            higher_pipe_height = pipe.upperSize
            break
    return np.asarray([height, distance_from_pipe, lower_pipe_height, higher_pipe_height])


def play_one_game_simple_model(model_with_score, bird, board):
    while bird.get_status():
        pipes = board.get_pipes()
        while pipes is None:
            pipes = board.get_pipes()
        data = get_input_from_bird(bird, pipes)
        data = np.atleast_2d(data)
        prediction = model_with_score.get_model().predict(data)[0][0]
        if prediction >= 0.5:
            bird.key_pressed()
            bird.update_position()
        else:
            bird.update_position()
        time.sleep(0.02)
    model_with_score.update_score(bird.get_score())
    return model_with_score


def function_wrapper(arguments_dict):
    return play_one_game_simple_model(arguments_dict['model'], arguments_dict['bird'], arguments_dict['board'])


def create_arguments(models, birds, board):
    assert len(models) == len(birds)
    res = list()
    for index, model_with_score in enumerate(models):
        res.append({'model': model_with_score, 'bird': birds[index], 'board': board})
    return res


def best_two_from_four(previous_two_best, current_two_best):
    tmp = previous_two_best + current_two_best
    tmp.sort()
    return [tmp[-1], tmp[-2]]


def update_two_best(previous_two_best, current_models_with_scores):
    current_two_best = best_two_from_four(previous_two_best,
                                          [current_models_with_scores[-1], current_models_with_scores[-2]])
    current_models_with_scores[-2].copy(current_two_best[1])
    current_models_with_scores[-1].copy(current_two_best[0])
    return current_two_best, current_models_with_scores


def run_generation(models, pool, two_best):
    birds = [Bird() for _ in range(BIRDS_COUNT)]
    board = Board()
    arguments = create_arguments(models, birds, board)
    start_board(board, birds)
    models = pool.map(function_wrapper, arguments)
    models.sort()
    tmp_two_best, models = update_two_best(two_best, models)
    two_best[0].copy(tmp_two_best[0])
    two_best[1].copy(tmp_two_best[1])
    new_weights = GeneticUtils.crossover(models[-1].get_model().get_weights(), models[-2].get_model().get_weights())
    print(models)
    for index, model in enumerate(models):
        weights = new_weights[0]
        if index > ((len(models) / 2) - 1):
            weights = new_weights[1]
        model.get_model().push_new_weights(GeneticUtils.mutate(weights, None))
    return models, two_best


def duplicate(models):
    for i in range(BIRDS_COUNT):
        models.append(ModelWithScore(Model(str(i + len(models))), 0).copy(models[-1]))
    return models


def create_from_saved():
    two_best = list()
    two_best.append(ModelWithScore(Model.load_model('first_best'), int(open('Model_Data/first_best_score','r').read())))
    two_best.append(ModelWithScore(Model.load_model('second_best'), int(open('Model_Data/second_best_score', 'r').read())))
    models = []
    for i in range(BIRDS_COUNT):
        models.append(ModelWithScore(Model(str(i)), 0))
    training_loop(models, two_best)


def training_loop(models, two_best):
    generation = 0
    pool = ThreadPool(BIRDS_COUNT)
    while True:
        print('running {} generation'.format(generation))
        models, tmp_two_best = run_generation(models, pool, two_best)
        for model_with_score in tmp_two_best:
            model_with_score.get_model().save_model()
            Model.save_score(model_with_score.get_model().name + "_score", str(model_with_score.get_score()))
        generation += 1


def create_from_scratch():
    models = [ModelWithScore(Model(str(i)), 0) for i in range(BIRDS_COUNT)]
    two_best = [ModelWithScore(Model('first_best'), 0), ModelWithScore(Model('second_best'), 0)]
    training_loop(models, two_best)


def main():
    create_from_scratch()


if __name__ == "__main__":
    main()
