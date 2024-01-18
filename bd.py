import pickle
import enum

# import antlr4
# import sgf_py

import universe
from pygame.locals import *
# import SgfReader
from dlgo.goboard_fast import GameState, Move
from dlgo.agent.termination import PassWhenOpponentPasses, TerminationAgent
from dlgo.gtp.board import gtp_position_to_coords, coords_to_gtp_position
from dlgo.gotypes import Point

# import mongodao as dao
import os

from pgu import gui

import copy
        
class GameMode(enum.Enum):
    GAME = 1
    GIBO = 2
    EXERCISE = 3
   
class GameCtl(gui.Widget):
    def __init__(self, **params):
        gui.Widget.__init__(self, **params)
        self.gui = None
        for key, value in params.items():
            if key == 'gui':
                self.gui = value
            
        self.seq = 0
        self.stones = []
        # self.u = universe.Universe()
        self.u = {}
        self.u['0'] = None
        self.current_localid = '00'
        self.u[self.current_localid] = universe.Universe()   # Main Thread
        self.stones = self.u[self.current_localid].getStones()
        self.mode = GameMode.GIBO
        self.bw = None
        self.size = 19
        self._stopped = False
        self.game_state = None

    def getSize(self):
        return size

    def setSize(self, size):
        self.size = size

    def getChilds(self, localid):
        return {locals for locals in self.u.keys() if locals.startswith(localid) and (len(locals) == (len(localid) + 1))}

    def getParent(self, localid):
        print("getParent localid : " + repr(localid))
        if localid[0:len(localid)-1] in self.u.keys():
            return localid[0:len(localid)-1]
        else:
            p = self.getParent(localid[0:len(localid)-1])
        return p
    
    # '00' -> '000'    
    def diverge(self, localid, current_seq):
        print('Entering bd.diverge ---------------')
        print(localid)
        print(current_seq)
        self.u[localid].setSeq(current_seq)

        new_localid = ''
        c = self.getChilds(localid)
        if len(c) == 0:
            new_localid = localid + '0'
            self.current_epoch = len(new_localid)
        else:
            maxid = max(c)
            new_localid = str(int(maxid) + 1).zfill(len(maxid))

        print(self.u[localid].seq_data)
        print(self.u[localid].seq_data[:current_seq+1])

        self.u[new_localid] = copy.deepcopy(self.u[localid])
        self.u[new_localid].seq_data = copy.deepcopy(self.u[localid].seq_data[:current_seq+1])
        self.current_localid = new_localid
        
        self.stones = self.u[self.current_localid].getStones()
        print('------------ Leaving bd.diverge')

    # '00' -> '01'
    def fork(self, localid, current_seq):
        print('universe.fork : ' + localid)
        c = self.getChilds(self.getParent(localid))
        print(c)
        maxid = max(c)
        # print('max : ' + maxid)
        new_localid = str(int(maxid) + 1).zfill(len(maxid))
        # print('localid : ' + new_localid)
        # newStatus = self.u[localid].getStatus(self.getSeq())

        self.u[new_localid] = copy.deepcopy(self.u[localid])
        self.u[new_localid].seq_data = copy.deepcopy(self.u[localid].seq_data[:current_seq+1])
        # self.u[new_localid].setStatus(newStatus)

        self.current_localid = new_localid

        # self.stones = self.u.getStones()[:]
        self.stones = self.u[self.current_localid].getStones()
        
    def delete(self, n):
        self.current_localid = self.getParent(n)
        self.u.pop(n)
        self.setSeq(self.u[self.current_localid].getSeq())        
        self.stones = self.u[self.current_localid].getStones()

    def changeLocalid(self, localid):
        print("Entering changeLocalid...")
        print("localid : " + localid)
        # save current seq
        self.u[self.current_localid].setSeq(self.getSeq()) 

        self.current_localid = localid
        # self.u.setLocalid(localid)
        # self.stones = self.u.getStonesByLocalId(localid)
        self.setSeq(self.u[self.current_localid].getSeq())
        self.stones = self.u[self.current_localid].getStones()
        if self.getSeq() == 0 :
            self.setBW('b')
        else :
            bw = self.stones[-1].getBW()
            self.setBW('b' if bw == 'w' else 'w')
        
        print("Leaving changeLocalid...")
        self.send(gui.const.CHANGE)

    def getStonesByLocalid(self, localid):
        return self.u[localid].getStones()

    def getCurrentStones(self):
        return self.u[self.current_localid].getStones(self.getSeq())
        # return self.u.status.getStatus()
        # return self.u.status.getStatusBySeq(self.getSeq())
        # return self.stones

    def getStonesBySeq(self, seq):
        return self.stones[0:seq]

    # return localids except '0'
    def getLocalids(self):
        return [k for k in self.u if len(k) > 1]
    
    def setSeq(self, seq):
        print('bd.setSeq Entering...')
        print('seq : ' + str(seq))
        self.u[self.current_localid].setSeq(seq)
        self.seq = seq
        self.stones = self.u[self.current_localid].getStones(self.seq)
        print('Leaving bd.setSeq...')

    def getSeq(self):
        return self.u[self.current_localid].getSeq()

    def getLastSeq(self):
        return self.u[self.current_localid].getLastSeq()

    def setGameMode(self, mode):
        self.mode = mode

    def setBW(self, bw):
        self.bw = bw

    def getBW(self):
        return self.bw

    def back(self):
        self.u[self.current_localid].stepBackward()
        self.stones = self.u[self.current_localid].getStones()

        self.seq = self.u[self.current_localid].getSeq()        
        # self.seq = self.u.status.getCnt()

        if self.bw=='w':
            self.bw='b'
        elif self.bw=='b':
            self.bw='w'

        self.send(gui.const.CHANGE)

    def move_silently(self, point):
        print('----- Entering move_silently -----')
        print(self.bw + ' ' + repr(point))
        self.u[self.current_localid].stepForward(point, self.bw)
        self.check(point[0], point[1], self.bw)
        print('----- Leaving move_silently -----')        

    def move_silently_post(self):
        print('----- Entering move_silently_post -----')
        self.stones = self.u[self.current_localid].getStones()
        self.seq = self.u[self.current_localid].getSeq()
        if self.bw=='w':
            self.bw='b'
        elif self.bw=='b':
            self.bw='w'
        self.send(gui.const.CHANGE)
        print('----- Leaving move_silently_post -----')        
        
    def move(self, point):
        print('--> move')
        print('point : ' + repr(point))
        print(f'point : ({point.row}, {point.col})')
        point = Point(point.col, 20 - point.row)

        status = self.u[self.current_localid].getStatus()
        if point in status.data: return

        if self.getSeq() < self.getLastSeq():
            print('mid point fork')
            self.fork(self.current_localid, self.getSeq())
            self.gui.universeL.clear()
            localids = self.getLocalids()
            localids = sorted(localids)
            self.gui.universeL.add_list_items(localids)

        self.u[self.current_localid].stepForward(point, self.bw)
        self.stones = self.u[self.current_localid].getStones()

        # save stones as current localid
        # self.u.data[localid] = copy.copy(self.u.getStatus())

        self.seq = self.u[self.current_localid].getSeq()

        self.check(point[0], point[1], self.bw)

        # ss = self.u.getStatus()
        # print(ss.mark)        

        if self.bw=='w':
            self.bw='b'
        elif self.bw=='b':
            self.bw='w'

        self.send(gui.const.CHANGE)

    def check(self, x, y, bw):
        if bw == 'b': c = 1
        else: c = 2
        
        self.u[self.current_localid].check_capture(x, y, c)
        
    def new(self, localid='00'):
        self.stones = []
        self.setBW('b')

        self.u = {}
        self.current_localid = localid
        self.u[self.current_localid] = universe.Universe()   # Main Thread 
        self.setSeq(0)
        self.stones = self.u[self.current_localid].getStones()        

    # TODO : Newly created and then update kibo at the same id
    def save(self, file_path):
        print("save entering...")
        print(self.stones)
        a = ['','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s']

        d = dao.MongoDao()
        name = os.path.basename(file_path)
        f2 = open(file_path + '.seq', 'w')
        for k in self.getLocalids():
            seq=''
            for key, stone in self.u[k].getStatus().seq.items():
                p = stone.getPoint()
                seq += a[p[0]] + a[p[1]]
            d.save(seq, name, k, "")

            local = k + ':' + seq
            f2.write(local + '\n')
        f2.close()

        f = open(file_path, "wb")
        pickle.dump(self.u, f)
        f.close()

    def loadSeqFromMongo(self, arry):
        self.u = {}
        for line in arry:
            localid = line['localid']
            print(localid)
            seq = line['seq']
            
            self.current_localid = localid
            self.u[self.current_localid] = universe.Universe()

            self.bw = 'b'
            for i in range(int(len(seq)/2)):
                a = seq[i*2:(i+1)*2]
                p = (ord(a[0:1])-96, ord(a[1:2])-96)
                self.move_silently(p)
                self.setBW('w' if self.bw == 'b' else 'b')
                
        self.current_localid = '00'
        self.move_silently_post()
        
    def loadSeq(self, file_path):
        self.u = {}
        f = open(file_path, "r")
        lines = f.readlines()
        for line in lines:
            l = line.split(':')
            localid = l[0]
            seq = l[1]
            
            self.current_localid = localid
            self.u[self.current_localid] = universe.Universe()   # Main Thread
            
            self.bw = 'b'
            for i in range(int(len(seq)/2)):
                a = seq[i*2:(i+1)*2]
                p = (ord(a[0:1])-96, ord(a[1:2])-96)
                self.move_silently(p)
                self.setBW('w' if self.bw == 'b' else 'b')
                
        self.current_localid = '00'
        self.move_silently_post()

    def load(self, file_path):
        print('Entering load..')
        f = open(file_path, "rb")
        # self.space = pickle.load(f)
        self.u = pickle.load(f)
        self.current_localid = '00'
        self.stones = self.u[self.current_localid].getStatus()
        print(repr(self.stones))
        self.seq = self.u[self.current_localid].getSeq()
        print('seq : ' + repr(self.seq))
        # bw = self.stones[self.seq-1].bw
        # self.setBW('w' if bw == 'b' else 'b')
        print(self.u[self.current_localid].status)
        print('Leaving load..')

        f.close()

    def detect(self, file):
        detector = UniversalDetector()
        for filename in glob.glob('*.xml'):
            print(filename.ljust(60), end='')
            detector.reset()
            for line in open(filename, 'rb'):
                detector.feed(line)
                if detector.done: break
            detector.close()
            print(detector.result)
            
    def readSgf(self, file_path):
        # cp949
        f = antlr4.FileStream(file_path, encoding='utf-8')
        l = sgf_py.SgfLexer(f)
        t = antlr4.CommonTokenStream(l)
        p:sgf_py.SgfParser =  sgf_py.SgfParser(t)
        pt = p.collection()

        walker = antlr4.ParseTreeWalker()
        walker.walk(SgfReader.SgfReader(self), pt)

    def setPlayer(self, black_player, white_player):
        self.black_player = black_player
        self.white_player = white_player

    def play(self):
        pass

    def play_black(self):
        move = self.black_player.select_move(self.game_state)
        self.game_state.apply_move(move)
        self.move((p[1], 20 - p[0]))

    def play_white(self):
        move = self.white_player.select_move(self.game_state)
        self.game_state.apply_move(move)
        self.game.move((move.point[1], 20 - move.point[0]))

if __name__ == "__main__":
    g = GameCtl()
    # g.move((4,4),'b')
    # g.move((5,5),'w')
    # print(g.stones)
    # g.save("./test.txt")
    # print(g.stones)
    g.readSgf('./kibo/DangVsMi.sgf')

