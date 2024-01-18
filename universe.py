import copy

import sys

class Stone:
    def __init__(self, point, bw):
        # self.seq = seq
        self.point = point
        self.bw = bw

    def getPoint(self):
        return self.point

    def getBW(self):
        return self.bw

    def __eq__(self, other):
        if self.point == other.point:
            return True
        else: return False

    def __repr__(self):
        stone = "({0}, {1})"
        return stone.format(self.point, self.bw)
        
class Array2d:
    def __init__(self, size=19):
        self.cnt = 0

        a = []
        a.extend([(0,y) for y in range(1,1+size)])
        a.extend([(x,0) for x in range(1,1+size)])
        a.extend([(1+size,y) for y in range(1,1+size)])
        a.extend([(x,1+size) for x in range(1,1+size)])

        # 0 : nothing, 1 : black, 2 : white, -1 : boundary
        # sparse 2d array with default value 0
        self.data = {aa : -1 for aa in a}
        self.seq = {}
        self.index = 0
        # self.seq.append(self.data)

        self.mark = {}

        self.black = set()
        self.white = set()
        self.black_captured = set()
        self.white_captured = set()

    def getIndex(self):
        return self.index

    def setIndex(self, i):
        if len(self.seq) < i: return
        self.index = i
        
    def getItem(self, x, y):
        return self.data[(x,y)]

    def addItem(self, p, color):
        self.cnt = self.cnt + 1
        if color == 'b':
            self.data[p] = 1
        else:
            self.data[p] = 2
        self.seq[self.cnt] = Stone(p, color)

    def deleteLast(self):
        # del self.data[self.seq.pop(self.cnt).getPoint()]
        self.seq.pop(self.cnt)
        self.cnt = self.cnt - 1        
        
    def delItem(self, p):
        self.data.pop(p)
            
    def getSeq(self):
        return self.seq

    # def getSeq(self, cnt):
    #     rr = {}
    #     for key in [key for key in self.seq.keys() if key <= cnt]:
    #         rr[key] = self.seq[key]

    #     return rr
    
    def getCnt(self):
        return self.cnt

    def __repr__(self):
        return repr(self.seq)

class Universe:

    # localid = [[],0] : localid[0] = location, localid[1] = seq
    # stones = [()]
    # universe = (localid, stones)
    def __init__(self, size = 19, localid=None, stones=None):
        if localid == None:
            self.localid = '00'
        else:
            self.localid += '0'

        self.status = Array2d(size)
        # self.data = {self.localid : status}
        # self.stones = self.data[self.localid]
        self.current_epoch = len(self.localid)
        # self.epochs = set()
        # self.epochs.add(self.localid)
        self.dead = set()
        self.checked = set()
        self.seq = 0
        
        self.seq_data = []
        self.seq_data.append(copy.deepcopy(self.status))
        self.lastSeq = len(self.seq_data)
        # sys.setrecursionlimit(100)

    def getSeq(self):
        return self.seq

    def setSeq(self, seq):
        self.seq = seq

    def getLastSeq(self):
        return len(self.seq_data[-1].getSeq())

    def getCurrentEpoch(self):
        return self.current_epoch
        
    def setCurrentEpoch(self, epoch):
        self.current_epoch = epoch

    def getStones(self, seq=None):
        # print('Entering Universe.getStones...')
        # print('seq : ' + repr(seq))
        # print('localid : ' + self.localid)

        if seq is None:
            status = self.seq_data[-1]
        else:
            status = self.seq_data[seq]

        keys = list(self.seq_data[self.getSeq()].seq.keys())
        # keys = list(status.seq.keys())
        keys.sort()
        # print(keys)
         
        stones = []
        for key in keys:
            st = status.seq[key]
            p = st.getPoint()
            if p not in status.data:
                stones.append(Stone(p, 'n'))
            else:
                stones.append(Stone(p, 'b' if status.data[p] == 1 else 'w'))
                
        # print('Leaving Universe.getStones')
        return stones

    def setStones(self, stones):
        pass

    # def getStonesByLocalId(self, localid):
    #     print('Entering Universe.getStonesByLocalId...')
    #     print('localid : ' + repr(localid))
    #     status = copy.deepcopy(self.data[localid])

    #     d = []
    #     for key in [key for key in status.mark.keys() if key <= self.getSeq()]:
    #         d.extend(status.mark[key])
    #     print('delete marked : ' + repr(d))

    #     dd = status.getSeq()
        
    #     for i in d:
    #         if i in dd:
    #             dd.remove(i)

    #     print('Leaving Universe.getStonesByLocalId...')
    #     return [Stone(p, 'b' if status.data[p] == 1 else 'w') for p in dd]

    # def getLocalIndex(self):
    #     return self.data[self.localid].getIndex()

    # def setLocalIndex(self, index):
    #     self.data[self.localid].setIndex(index)

    # def deleteByLocalId(self, localid):
    #     self.data.pop(localid)

    # TODO : stepForward when seq is not last one do fork
    def stepForward(self, p, bw):
        print('Entering Universe.stepForward-------')
        # print('localid : ' + self.localid)
        # print('data : ' + str(self.data))
        status = self.getStatus()
        if p in status.data: return
        self.setSeq(self.getSeq() + 1)
        new_status = copy.deepcopy(status)
        new_status.addItem(p, bw)
        self.seq_data.append(new_status)

        # print('localdata ' + repr(status))        
        print('--------Leaving Universe.stepForward')

    def stepBackward(self):
        # status = self.getStatus()
        # self.setSeq(self.getSeq() - 1)
        # self.status.deleteLast()
        self.seq_data.pop(self.seq)
        self.setSeq(self.getSeq() - 1)

    def getStatus(self, seq=None):
        # print('in universe.getStatus')
        # print('return localdata : ' + self.localid)
        # print(self.data[self.localid])
        if seq is not None:
            return self.seq_data[seq]            
        else:
            return self.seq_data[self.getSeq()]

    def setStatus(self, seq, status):
        self.seq_data = copy.deepcopy(self.seq_data[:seq+1])
        self.seq_data = status

        # return self.data[self.localid]
           
    def check_capture(self, x, y, bw):
        status = self.getStatus()
        data = status.data
        # print(data);
        a = (x+1,y)
        b = (x,y-1)
        c = (x-1,y)
        d = (x,y+1)
        # print(repr(a) + ', ' + repr(b) + ', ' + repr(c) + ', ' + repr(d))

        r_check = set()
        if a in data and bw != data[a] and data[a] != -1:
            if self.check(a, bw) != False:
                r_check.update(self.checked)
                self.checked = set()
        if b in data and bw != data[b] and data[b] != -1:
            if self.check(b, bw) != False:
                r_check.update(self.checked)
                self.checked = set()                
        if c in data and bw != data[c] and data[c] != -1:
            if self.check(c, bw) != False:
                r_check.update(self.checked)
                self.checked = set()                
        if d in data and bw != data[d] and data[d] != -1:
            if self.check(d, bw) != False:
                r_check.update(self.checked) 
                self.checked = set()               

        if len(r_check) != 0:
            status.mark[self.getSeq()] = copy.copy(r_check)
            for p in r_check:
                bw = status.getItem(p[0], p[1])
                if bw == 1: status.black_captured.add(p)
                else: status.white_captured.add(p)                
                status.delItem(p)
        
        self.checked = set()
        
    def check(self, p, bw):
        print('Entering check : ' + repr(p) + ':' + repr(bw))
        print('dead ->' + repr(self.checked))
        status = self.getStatus()
        data = status.data
        a = (p[0]+1, p[1])
        b = (p[0], p[1]-1)
        c = (p[0]-1, p[1])
        d = (p[0], p[1]+1)
        
        if a not in data or b not in data or c not in data or d not in data:
            self.checked = set()
            return False

        self.checked.add(p)
        
        # if self.isBlocked(p, data[p]):
        if data[a] != -1 and data[a] != bw and a not in self.checked:
            if self.check(a, bw) is False: return False
        if data[b] != -1 and data[b] != bw and b not in self.checked:
            if self.check(b, bw) is False: return False
        if data[c] != -1 and data[c] != bw and c not in self.checked:
            if self.check(c, bw) is False: return False
        if data[d] != -1 and data[d] != bw and d not in self.checked:
            if self.check(d, bw) is False: return False

        print('dead ->' + repr(self.checked))
        print('Leaving check --------')
        return True
            
    def isBlocked(self, p, bw):
        status = self.getStatus()
        data = status.data
        a = (p[0]+1, p[1])
        b = (p[0], p[1]-1)
        c = (p[0]-1, p[1])
        d = (p[0], p[1]+1) 
        
        if status.data[a] == -1 or data[a] != bw:
            if status.data[b] == -1 or data[b] != bw:
                if status.data[c] == -1 or data[c] != bw:
                    if status.data[d] == -1 or data[d] != bw: return True
        
        return False

if __name__ == '__main__':
    # u = Universe()
    # u.stepForward((6,6),'b')
    # u.stepForward((7,7),'w')
    # u.diverge('00')
    # print(u.getStonesByLocalId('00'))
    # print(u.getStonesByLocalId('000'))
    # u.stepForward((1,1),'b')
    # u.stepForward((1,2),'w')
    # print(u.getStonesByLocalId('00'))
    # print(u.getStonesByLocalId('000'))    
    # arr = Array2d(9)
    # print(arr.data)
    st1 = Stone((1,1),'w')
    st2 = Stone((1,2),'b')
    print(repr(st1==st2))
          
