from keras import Sequential
from keras.layers import Dense
from keras.models import load_model
import tensorflow as tf
import os
import uuid

from Game import SCREEN_SIZE

MODEL_DIR = 'Model_Data'
MODEL_NAME = 'Model'


def checkDir(f):
    def checking(*args, **kwargs):
        if not os.path.isdir(MODEL_DIR):
            os.mkdir(MODEL_DIR)
        return f(*args, **kwargs)

    return checking


def simple_model():
    model = Sequential()
    model.add(Dense(4, input_shape=(4,), activation='relu'))
    model.add(Dense(7, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    return model


def with_session(f):
    def inner(*args, **kwargs):
        with args[0].graph.as_default():
            with args[0].thread_session.as_default():
                return f(*args, **kwargs)

    return inner


class Model(object):
    def __init__(self, name):
        self.name = name
        thread_graph = tf.Graph()
        with thread_graph.as_default():
            self.thread_session = tf.Session()
            with self.thread_session.as_default():
                self.model = simple_model()
                self._compile()
                self.graph = tf.get_default_graph()
                self.model._make_predict_function()

    def _compile(self):
        self.model.compile(optimizer='adam', loss='binary_crossentropy')
        return
        if not os.path.exists(MODEL_DIR):
            self.model.compile(optimizer='adam', loss='binary_crossentropy')
        else:
            try:
                self.load_model()
            except Exception as e:
                print("Failed to load one of the models: %s" % str(e))
                os._exit(1)

    @with_session
    def get_weights(self):
        return self.model.get_weights()

    def get_name(self):
        return self.name

    @staticmethod
    def save_score(name, score):
        open(os.path.join(MODEL_DIR, name), 'w').write(score)

    @staticmethod
    def load_model(name):
        model_path = os.path.join(MODEL_DIR, name)
        tmp_model = load_model(model_path)
        return_model = Model(name)
        return_model.push_new_weights(tmp_model.get_weights())
        return return_model

    @with_session
    def push_new_weights(self, weights):
        self.model.set_weights(weights)

    def copy(self, other):
        self.push_new_weights(other.get_weights())

    @checkDir
    @with_session
    def save_model(self):
        self.model.save(os.path.join(MODEL_DIR, self.name))

    @with_session
    def predict(self, input_data):
        return self.model.predict(input_data, steps=1)
