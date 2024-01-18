import sys
import asyncio

import pygame
from  pygame.locals import QUIT

from pgu import gui

import h5py

import board
import bd
from play_local import LocalGtpBot
from dlgo.agent.predict import load_prediction_agent
from dlgo.gtp.board import gtp_position_to_coords, coords_to_gtp_position

from dlgo.agent.termination import PassWhenOpponentPasses
from dlgo.goboard_fast import GameState, Move
from gameengine import LocalGameEngine

from bot import Human, DlBot, TensorBot

class DrawingArea(gui.Widget):
    def __init__(this, width, height):
        gui.Widget.__init__(this, width=width, height=height)
        this.imageBuffer = pygame.Surface((width, height))

    def paint(this, surf):
        surf.blit(this.imageBuffer, (0, 0))

class TestDialog(gui.Dialog):
    def __init__(this):
        title = gui.Label("Some Dialog Box")
        label = gui.Label("Close this window to resume.")
        gui.Dialog.__init__(this, title, label)

class MainGui(gui.Desktop):
    boardAreaHeight = board.WINDOWHEIGHT
    boardArea = None
    bottomArea = None
    rightArea = None
    engine = None

    def __init__(self, disp, game):
        gui.Desktop.__init__(self)
        
        self.disp = disp
        self.game = game
        self.selected_point = None

        # (maingui(<->gamectl) <- board(<->gamectl)) <-> gamectl
        # self.game.gui = self
        self.board = board.board(19, board.WINDOWWIDTH, board.WINDOWHEIGHT, g=self.game)
        self.board.init()
        self.board.rect.w, self.board.rect.h = self.board.resize()

        self.boardArea = DrawingArea(self.disp.get_width(), self.boardAreaHeight)
        self.bottomArea = gui.Container(height=self.disp.get_height() - self.boardAreaHeight)
        tbl = gui.Table(height=self.disp.get_height())
        tbl.tr()
        tbl.td(self.boardArea)
        tbl.tr()
        tbl.td(self.bottomArea)

        self.setup_bottom()

        # self.init(tbl, disp)
        self.init(tbl, self.disp)

    def setup_bottom(self):
        tbl = gui.Table()
        
        start_btn = gui.Button("<<")
        start_btn.connect(gui.CLICK, self.navi_action, 0)
        previous_btn = gui.Button("<")
        previous_btn.connect(gui.CLICK, self.navi_action, -1)
        next_btn = gui.Button(">")
        next_btn.connect(gui.CLICK, self.navi_action, 1)
        end_btn = gui.Button(">>")
        end_btn.connect(gui.CLICK, self.navi_action, None)

        back_btn = gui.Button("BS")
        back_btn.connect(gui.CLICK, self.back_space)

        self.seq_tf = gui.Input(value="0", size=3)
        self.seq_tf.connect(gui.CHANGE, self.seq_tf_activate)
        
        tbl.tr()
        tbl.td(start_btn)
        tbl.td(previous_btn)
        tbl.td(self.seq_tf)
        tbl.td(next_btn)
        tbl.td(end_btn)
        tbl.td(back_btn)

        self.bottomArea.add(tbl, 0, 0)

    def back_space(self):
        pass

    def navi_action(self):
        if arg is not None and (self.game.getLastSeq() < (int(self.seq_tf.value) + arg) or int(self.seq_tf.value) + arg < 0) : return

        if arg == 0:
            self.seq_tf.value = 0
        elif arg == None:
            self.seq_tf.value = self.game.getLastSeq()
        else:
            self.seq_tf.value = int(self.seq_tf.value) + arg

    def seq_tf_activate(self):
        self.game.setSeq(int(self.seq_tf.value))
        self.board.repaint()

    def get_render_area(self):
        return self.boardArea.get_abs_rect()

    def status_changed(self):
        # print('Entering status_changed...')
        # fire seq_tf_activate
        # print("seq ->" + repr(self.game.getSeq()))
        self.seq_tf.value = self.game.getSeq()
        # print('Leaving status_changed...')

    def event(self, e):
        for event in pygame.event.get(QUIT): # get all the QUIT events
            self.terminate() # terminate if any QUIT events are present

    def terminate(self):
        pygame.quit()
        sys.exit()
            
if __name__ == "__main__":
    # disp = pygame.display.set_mode((640, 800))
    disp = pygame.display.set_mode((922, 1152))
    
    g = bd.GameCtl()
    g.setBW('b')
    g.setSize(19)

    main_gui = MainGui(disp, game = g)

    # bot = load_prediction_agent(h5py.File("./agents/betago.hdf5", "r"))
    # localGtp = LocalGtpBot(go_bot=bot, termination=PassWhenOpponentPasses(), output_sgf='test', handicap=0, opponent='gnugo', )
    human = Human(g, main_gui)
    dlbot = DlBot(g)
    tensorbot = TensorBot()

    # g.setPlayer(human, dlbot)
    g.setPlayer(human, tensorbot)
    g.game_state = GameState.new_game(19)
    print(f'bd_gui.main -> {g.game_state.board._grid}')
    
    eng = LocalGameEngine(main_gui = main_gui)

    asyncio.run(eng.run())
    # eng.agent.sgf.write_sgf()

    # print("Estimated result: ")
    # print(compute_game_result(self.game_state))            
