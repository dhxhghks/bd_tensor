import pygame

from dlgo.goboard_fast import GameState, Move

from dlgo.agent import load_prediction_agent
from dlgo.gotypes import Point
from dlgo.agent.base import Agent
from dlgo.agent.helpers import is_point_an_eye

from dlgo import goboard
from dlgo import encoders

import tensorflow as tf
import numpy as np

import h5py

class Bot:
    def __init__(self, game_state):
        self.game_state = game_state

    def select_move(self):
        pass

class Human(Bot):
    def __init__(self, game, gui):
        self.game = game
        self.gui = gui
        
    async def select_move(self, game_state):
        point = None
        done = False
        # while True:
        for ev in pygame.event.get():

            if ev.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                print(f"pos ->{pos}")
                # print("pos ->" + repr(pos[1]) + "," + repr(20 - pos[0]))
                point = self.gui.board.getPoint(pos[0], pos[1])
                print(point)
                break
        if point is None:
            return None
        # transform coordinate x, y -> y, x
        # need to sync bd_board and game_state
        return Move.play(Point(20 - point[1], point[0]))
        
class DlBot(Bot):
    def __init__(self, game):
        self.game = game
        self._bot = load_prediction_agent(h5py.File("./agents/betago.hdf5", "r"))

    async def select_move(self, game_state):
        move = self._bot.select_move(game_state)
        # pos = self._bot.command_and_response("genmove {}\n".format(their_name))
        # if pos.lower() == 'resign':
        #     self.game_state = self.game_state.apply_move(Move.resign())
        # elif pos.lower() == 'pass':
        #     self.game_state = self.game_state.apply_move(Move.pass_turn())
        # else:
        #     move = gtp_position_to_coords(pos)
        #     self.game_state = self.game_state.apply_move(move)
        return move


class TensorBot(Bot):
    def __init__(self):
        self._bot = self.load_tensor_agent()

    async def select_move(self, game_state):
        move = self._bot.select_move(game_state)

        return move

    def load_tensor_agent(self):
        interpreter = tf.lite.Interpreter(model_path="agents/betago.tflite")
        interpreter.allocate_tensors()

        encoder = encoders.get_encoder_by_name("betago", (19, 19))

        return TensorAgent(interpreter, encoder)

class TensorAgent(Agent):
    def __init__(self, model, encoder):
        Agent.__init__(self)
        self.model = model
        self.input_details = self.model.get_input_details()
        self.output_details = self.model.get_output_details()
        self.input_shape = self.input_details[0]['shape']
        
        self.encoder = encoder

    def predict(self, game_state):
        encoded_state = self.encoder.encode(game_state)
        input_tensor = np.array([encoded_state])
        print(f'input_tensor.dtype -->{input_tensor.dtype}')
        
        self.model.set_tensor(self.input_details[0]['index'], input_tensor)
        self.model.invoke()

        return self.model.get_tensor(self.output_details[0]['index'])[0]

    def select_move(self, game_state):
        num_moves = self.encoder.board_width * self.encoder.board_height
        move_probs = self.predict(game_state)
        print(f'bot.py select_move move_probs.shape -->{move_probs.shape}')
        print(f'bot.py select_move move_probs.dtype -->{move_probs.dtype}')
        
        move_probs = move_probs ** 3  # <1>
        eps = 1e-6
        move_probs = np.clip(move_probs, eps, 1 - eps)  # <2>
        move_probs = move_probs / np.sum(move_probs)  # <3>

        candidates = np.arange(num_moves)  # <1>
        ranked_moves = np.random.choice(
            candidates, num_moves, replace=False, p=move_probs)  # <2>
        for point_idx in ranked_moves:
            point = self.encoder.decode_point_index(point_idx)
            if game_state.is_valid_move(goboard.Move.play(point)) and \
                    not is_point_an_eye(game_state.board, point, game_state.next_player):  # <3>
                return goboard.Move.play(point)
        return goboard.Move.pass_turn()  # <4>
