import pygame
import bd
import asyncio

from pgu import gui, timer
from dlgo.gtp.board import gtp_position_to_coords, coords_to_gtp_position
from dlgo.goboard_fast import Move
from dlgo.utils import print_board
from dlgo.gotypes import Point

class LocalGameEngine(object):
    def __init__(self, main_gui):
        # self.disp = disp
        # self.square = pygame.Surface((640, 640)).convert_alpha()
        # self.square.fill((255, 0, 0))

        self.disp = main_gui.disp

        # self.game = bd.GameCtl(gui=main_gui)

        # self.game.setBW('b')
        # self.game.setSize(19)
        self.game = main_gui.game
        
        # self.app = MainGui(self.disp, g=self.game)
        self.app = main_gui
        self.app.engine = self
        self.game.connect(gui.CHANGE, self.app.status_changed)
        
    def pause(self):
        self.clock.pause()

    def resume(self):
        self.clock.resume()

    def render(self, dest, rect):
        self.app.board.drawBoard()

        self.app.board.drawStoneLayer()
        self.app.board.drawStones()

        dest.blit(self.app.board.surface, (0, 0))
        dest.blit(self.app.board.stoneLayer, (0, 0))

        return(rect,)

    async def run(self):
        self.app.update()
        pygame.display.flip()

        self.font = pygame.font.SysFont("", 16)

        self.clock = timer.Clock()
        self.game._stopped = False
        done = False
        # while not done and not self.gnu_go._stopped:
        # while not done and not self.agent._stopped:
        while not done:

            # for ev in pygame.event.get():
            #     # print(f"{ev.type}") 
            #     if ev.type == pygame.QUIT:
            #         done = True
                # self.app.event(ev)
                # if (ev.type == pygame.QUIT or
                #     ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                #     done = True
                # if (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                #     self.game._stopped = not self.game._stopped
                    # self.game.sgf.write_sgf()

                # point = None
                # if ev.type == pygame.MOUSEBUTTONUP:
                #     pos = pygame.mouse.get_pos()
                #     print(f"pos ->{pos}")
                #     # print("pos ->" + repr(pos[1]) + "," + repr(20 - pos[0]))
                #     point = self.app.board.getPoint(pos[0], pos[1])
                #     print(point)
                #     self.app.selected_point = point

                # move = None
                # if self.game.bw == 'b':
                #     move = self.game.black_player.select_move(self.game.game_state)
                # else:
                #     move = self.game.white_player.select_move(self.game.game_state)
            task = None
            result = None
            if self.game.bw == 'b':
                task = asyncio.create_task(self.game.black_player.select_move(self.game.game_state))
            else:
                task = asyncio.create_task(self.game.white_player.select_move(self.game.game_state))

            await task
            move = task.result()
            # print(f'gameengine.py ->{move}')

            if move is not None:
                self.game.game_state = self.game.game_state.apply_move(move)
                print(f'gameengine.py ->{self.game.game_state.board._grid}')
                print_board(self.game.game_state.board)
                
                self.game.move(move.point)
                self.app.board.drawStones()
                self.app.selected_point = None
                
            self.update_ui()

    def update_ui(self):
        rect = self.app.get_render_area()
        updates = []
        self.disp.set_clip(rect)
        lst = self.render(self.disp, rect)
        if(lst):
            updates += lst
        self.disp.set_clip()
        
        self.clock.tick(30)

        lst = self.app.update()
        if(lst):
            updates += lst

        pygame.display.update(updates)
        pygame.time.wait(10)
            

