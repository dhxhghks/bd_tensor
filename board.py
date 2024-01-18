import pygame, sys
from pygame.locals import *

from pgu import gui
# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

FPS = 30
WINDOWWIDTH = 922
WINDOWHEIGHT = 922

class board(gui.Widget):
    def __init__(self, size, width, height, **params):
        gui.Widget.__init__(self,**params)

        self.size = size
        self.BOARDSIZE = size
        self.width = width
        self.height = height

        self.WIDTHMARGIN = int(self.width / 37)
        self.HEIGHTMARGIN = int(self.height / 37)

        self.BOARDWIDTH = self.width - self.WIDTHMARGIN * 2
        self.BOARDHEIGHT = self.height - self.HEIGHTMARGIN * 2

        self.STONESIZE = (int(2*WINDOWWIDTH/37), int(2*WINDOWHEIGHT/37))

        for arg in params:
            if(arg == 'g'):
                self.game = params[arg]
        
        # self.game = bd.GameCtl(size)
        # self.game.setBW('b')

        # Initialize the game engine
        # pygame.init()

        # Set the height and width of the screen
        # self.screen = pygame.display.set_mode([WINDOWWIDTH, WINDOWHEIGHT])
        self.screen = None
        # self.stoneLayer = None

        self.rects = [] ## stoneLayer - each location of stone
        
        # pygame.display.set_caption("Baduk")

        #Loop until the user clicks the close button.
        # self.clock = pygame.time.Clock()

    def init(self):
        self.surface = pygame.Surface((self.width, self.height))
        
        self.stoneLayer = pygame.Surface((self.width, self.height))
        self.stoneLayer.set_colorkey(BLACK)
        self.drawBoard()
        self.drawStoneLayer()
        # self.drawStones()

    def paint(self, s):
        self.drawBoard()

        self.drawStoneLayer()
        self.drawStones()

        s.blit(self.surface, (0, 0))
        s.blit(self.stoneLayer, (0, 0))
    
    # def update(self, s):
    #     print("Pan.update entering...")
    #     return [pygame.Rect(0,0,self.rect.w,self.rect.h)]

    def event(self, e):
        pass

    def resize(self, width=None, height=None):
        return self.width, self.height

    def drawBoard(self):
        self.surface.fill(WHITE)
        # print("drawBoard ");
        left, top = self.getLocation(1, 1)
        # print("left : " + repr(left) + ", top : " + repr(top) + "\n")
        width = self.BOARDWIDTH
        height = self.BOARDHEIGHT
        # print("width : " + repr(width) + ", height : " + repr(height) + "\n")
        pygame.draw.rect(self.surface, BLACK, (left, top, width, height), 2)

        for i in range(1, self.BOARDSIZE-1):
            pygame.draw.line(self.surface, BLACK, self.getLocation(i+1, 1), self.getLocation(i+1, self.BOARDSIZE), 1)
        for i in range(1, self.BOARDSIZE-1):
            pygame.draw.line(self.surface, BLACK, self.getLocation(1, i+1), self.getLocation(self.BOARDSIZE, i+1), 1)

        pygame.draw.circle(self.surface, BLACK, self.getLocation(4,4), 4)
        pygame.draw.circle(self.surface, BLACK, self.getLocation(4,10), 4)
        pygame.draw.circle(self.surface, BLACK, self.getLocation(4,16), 4)
        pygame.draw.circle(self.surface, BLACK, self.getLocation(10,4), 4)
        pygame.draw.circle(self.surface, BLACK, self.getLocation(10,10), 4)
        pygame.draw.circle(self.surface, BLACK, self.getLocation(10,16), 4)
        pygame.draw.circle(self.surface, BLACK, self.getLocation(16,4), 4)
        pygame.draw.circle(self.surface, BLACK, self.getLocation(16,10), 4)
        pygame.draw.circle(self.surface, BLACK, self.getLocation(16,16), 4)

    def drawStoneLayer(self):
        # print("drawStoneLayer entering...")
        # print("STONESIZE : " + repr(self.STONESIZE))
        self.rects = []
        for i in range(1,1+self.BOARDSIZE):
            for j in range(1,1+self.BOARDSIZE):
                stoneLoc = self.getLocation(i, j)
                # print("(" + str(i) + ", " + str(j) + ") ->" + repr(stoneLoc))
                stoneLoc = (stoneLoc[0] - self.STONESIZE[0] / 2, stoneLoc[1] - self.STONESIZE[1] / 2)
                # print(repr(stoneLoc))
                rect = Rect(stoneLoc, self.STONESIZE)
                self.rects.append(rect)
                pygame.draw.rect(self.stoneLayer, BLACK, rect, 1)

    def drawStones(self):
        stones = self.game.getCurrentStones()
        # print(stones)
        for st in stones:
            self.drawStone(st.point[0], st.point[1], st.bw)
        
    def drawStone(self, x, y, bw):
        # print("drawStone entering...")
        # print("point : " + " (" + repr(x) + ", " + repr(y) + ")")
        # print(bw)
        rect = self.rects[(x-1)*19 + (y-1)]
        
        if bw == 'w':
            pygame.draw.ellipse(self.surface, WHITE, rect)
            pygame.draw.ellipse(self.surface, BLACK, rect, 1)
        elif bw == 'b':
            pygame.draw.ellipse(self.surface, BLACK, rect)
        else:
            pass
            
    def getLocation(self, x, y):
        # print("getLocation");
        # left -> x, top -> y
        left = (x-1) * self.BOARDWIDTH / (self.BOARDSIZE-1) + self.WIDTHMARGIN
        top = (y-1) * self.BOARDHEIGHT / (self.BOARDSIZE-1) + self.HEIGHTMARGIN
        # print("left : " + repr(left) + ", top : " + repr(top) + "\n")
        return (int(left), int(top))

    def getPoint(self, left, top):
        print("getPoint ->" + repr(left) + ":" + repr(top))
        cnt = 0
        for rect in self.rects:
            if rect.collidepoint(left, top):
                x = cnt / 19 + 1
                y = cnt % 19 + 1
                return (int(x), int(y))
            cnt = cnt + 1
            
    def checkForQuit(self):
        for event in pygame.event.get(QUIT): # get all the QUIT events
            self.terminate() # terminate if any QUIT events are present
        for event in pygame.event.get(KEYUP): # get all the KEYUP events
            if event.key == K_ESCAPE:
                self.terminate() # terminate if the KEYUP event was for the Esc key
            pygame.event.post(event) # put the other KEYUP event objects back

    def terminate(self):
        pygame.quit()
        sys.exit()

    def start(self):
        print('Game Started')
        while True:
            self.drawBoard()
            self.checkForQuit()
            # for event in pygame.event.get():
            #     if event.type == MOUSEBUTTONUP:
            #         pos = pygame.mouse.get_pos()
            #         point = self.getPoint(pos[0], pos[1])
            #         print("point : " + repr(point))
            #         self.game.move(point)
            #         print(repr(point))

            self.drawStoneLayer()
            self.drawStones()

            # self.screen.blit(self.stoneLayer, (0,0))
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    print(pygame.version.ver)
    p = board(19, 640, 640)
    pygame.init()
    p.screen = pygame.display.set_mode([WINDOWWIDTH, WINDOWHEIGHT])
    p.init()
    p.start()

