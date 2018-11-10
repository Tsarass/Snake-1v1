#MAKE THE GAME DPI AWARE
import ctypes
ctypes.windll.user32.SetProcessDPIAware()

import pygame, sys
from random import randint
from pygame.locals import *
import settings     #settings module for Save/Load operations

#DISPLAY PARAMETERS
h=26                #rows of playable terrain
w=30                #columns of playable terrain
size=30             #size of snake path in pixels
widthpx=w*size      #width of playable area in pixels
heightpx=h*size     #height of playable area in pixels
void=int(size*0.12) #void between tail pieces in pixels
panel=230           #width of panel in pixels
panx = 0            #pan all drawings in the x axis
pany = 0            #pan all drawings in the y axis
videomodes = list() #stores all supported video modes as tuples
vmodes_str = list() #stores all supported video modes as strings of WxH
activemode = [0, 0] #stores the active video mode
bitsize = 0         #stores the system color depth
aspectratio = 0     #stores the monitor preferred aspect ratio
screenset = False   #this is set to True after initializing display mode
####################

#GAME PARAMETERS
standard_fps=60     #standard frame updates per second
fps = standard_fps  #currently running fps
gups=10             #game state updates per second
checkedfps=fps      #fps the game was readjusted to
framesperstateupdate=fps/gups
boostertmin=17      #minimum booster respawn time
boostertmax=27      #maximum booster respawn time
boostertypes=6      #number of booster types 0=ULTRA BOOST 1=TRIPLE BOOST 2=REVERSE BOOST 3=WALL BOOST 4=SNAKE HUNTER BOOST 5=FREEZE BOOST
boosterchances=[30,20,10,15,12,13]      #booster chances % by type
boosterchances_ex=[10,18,17,15,20,20]   #extreme booster chances % by type (after half of MAXSCORE is reached)
boosterdurations=(15,10,10,12,10,10)    #booster durations by type in seconds
BOOSTERNAMES = ['Ultra Boost', 'Triple Boost', 'Reverse Boost', 'Wall Boost', 'Snake Hunter', 'Freeze Boost']
MAXSCORE=500        #victory score target
INVULNERABLEDUR=3   #invulnerability duration
LIFERESTORE=50      #life restoration timeout
SOUNDON=True        #game sounds state
MUSICON=True        #menu music state
BOOSTERSON=True     #game boosters state
PLAYERSCORE=[0,0]   #total score after all games played
SNAKECOLOR=[pygame.Color(50, 50, 255), pygame.Color(20, 180, 50)]   #snake default colors
maxnamelen = 8      #max number of characters on player names
shadeSur, shadevertSur = None, None #surfaces storing the static shadows

#functions to switch between speed option and actual fps
def Fps2SpeedOption(fps):
    temp = 4*(fps/standard_fps - 1)
    gamespeed = temp + 1
    return int(gamespeed)

def SpeedOption2Fps(SpeedOption):
    temp = SpeedOption - 1
    fps = (1+(temp*0.25))*standard_fps
    return int(fps)

#load settings file
settings_list = settings.Load()
mappedcolors=[0]*2
try:
    SOUNDON, MUSICON, BOOSTERSON, MAXSCORE, gamespeed, mappedcolors[0] ,mappedcolors[1], activemode[0], activemode[1] = settings_list
except:
    print('Settings file not found or corrupt. Using default game settings.')
else:
    fps = SpeedOption2Fps(gamespeed)
    perc = fps/standard_fps
    newgups = gups*perc
    framesperstateupdate=fps/newgups
    for i in range(2):
        b = mappedcolors[i]%256
        g = ((mappedcolors[i]-b) % (256*256))/256
        r = (mappedcolors[i]-b-256*g)/(256*256)
        SNAKECOLOR[i] = pygame.Color(int(r),int(g),int(b))
    print('Successfully loaded settings file.')

starttails=3        #number of starting tails
maxlives=4          #max number of lives
flashspeed=3        #number of flashes per second when invulnerable
boosteranimmax=fps*1.2      #max number of animation ticks for the booster (duration = boosteranimmax/fps)
eyesanimmax=fps*5           #max number of animation ticks for the snake eyes
tonganimmax=int(fps*0.3)    #max number of animation ticks for the snake tongue
floatanimmax=int(fps*1.5)   #max number of animation ticks for floating text

PLAYERNAMES = ['PLAYER 1', 'PLAYER 2']   #player name strings
gamever = 'v1.2'
####################

#DISPLAY VARIABLES
MENUOPTIONTITLESIZE = int(size*2.3)
MENUOPTIONTITLEY = int(heightpx*0.15)
MENUOPTIONOPTIONSIZE = int(size*0.9)
MENUOPTIONY = int(heightpx*0.35)
MENUOPTIONYSTEP = int(size*1.35)
PLAYERSCORESIZE = int(size*0.95)
INSTRUCTIONTEXTSIZE = int(size//1.4)
BOOSTERBORDER = int(size//8)
RESETBUTTONHEIGHT = int(heightpx*0.15)
FLOATTEXTSIZE = int(size*0.75)
####################

def SetDisplayVariables():
    global MENUOPTIONTITLESIZE, MENUOPTIONTITLEY, MENUOPTIONOPTIONSIZE, MENUOPTIONY, MENUOPTIONYSTEP, PLAYERSCORESIZE, INSTRUCTIONTEXTSIZE, BOOSTERBORDER, FLOATTEXTSIZE
    MENUOPTIONTITLESIZE = int(size*2.3)
    MENUOPTIONTITLEY = int(heightpx*0.25)
    MENUOPTIONOPTIONSIZE = int(size*0.9)
    MENUOPTIONY = int(heightpx*0.45)
    MENUOPTIONYSTEP = int(size*1.35)
    PLAYERSCORESIZE = int(size*0.95)
    INSTRUCTIONTEXTSIZE = int(size//1.4)
    BOOSTERBORDER = int(size//8)
    RESETBUTTONHEIGHT = int(heightpx*0.15)
    FLOATTEXTSIZE = int(size*0.75)

#SET UP DISPLAY ACCORDING TO SUPPORTED SCREEN RESOLUTIONS
def SetDisplayMode(resw=0, resh=0):
    global size, widthpx, heightpx, panx, pany, panel, void, videomodes, bitsize, activemode, aspectratio, screenset

    if not screenset:
        screeninfo = pygame.display.Info()
        bitsize  = screeninfo.bitsize // 4
        videomodes = pygame.display.list_modes()
        print('Supported video modes: ' + str(videomodes))
        desktopw = screeninfo.current_w
        desktoph = screeninfo.current_h
        aspectratio = desktopw / desktoph
        screenset = True

    for mode in videomodes:
        #set new screen width, height
        if resw == 0 and resh == 0:
            screenw, screenh = mode
        else:
            screenw, screenh = resw, resh
        aspect = screenw / screenh
        if aspect >= 1:
            size = screenh // h
        else:
            size = screenw // w
        #set global pixel size of playable area and score panel
        widthpx = size * w
        heightpx = size * h
        panel = int(widthpx * 0.3)
        #make sure screen fits the playable area
        if screenw < widthpx + panel:
            size = (screenw - panel) // w
        if screenh < heightpx:
            size = screenh // h        
        #set pan values
        gamedisplayw = size * w + panel
        barw = screenw - gamedisplayw
        panx = barw // 2
        gamedisplayh = size * h
        barh = screenh - gamedisplayh
        pany = barh // 2
        void = int(size*0.12)
        #check if video mode ok and break the loop
        if pygame.display.mode_ok((screenw, screenh), 0, bitsize):
            break
        else:
            #revert to desktop resolution
            screenw, screenh = desktopw, desktoph

            
    #set the display mode
    print('Screen settings: Resolution: %ix%i, Playable area: %ix%i, Size: %i\nPlayable area (pixels): %ix%i, Total game area (pixels): %ix%i\nPanx:%i, Pany: %i' % (screenw, screenh, w, h, size, widthpx, heightpx, widthpx+panel, heightpx, panx, pany))
    DISPLAY = pygame.display.set_mode((screenw, screenh), pygame.DOUBLEBUF|pygame.FULLSCREEN|pygame.HWSURFACE)
    pygame.display.set_caption('Snake Hunter')
    activemode = [screenw, screenh]

    SetDisplayVariables()   #re-set all size-dependent display constants

    return DISPLAY
####################

#init pygame
pygame.init()

DISPLAY = SetDisplayMode(activemode[0],activemode[1])

#GENERIC FUNCTIONS
#=========================
#create custom shadow surface
def CreateShadowSurfaces():
    print('Creating static shadows...')
    shadowsize = int(size/8)
    shadowsur = pygame.Surface((size-void + shadowsize, shadowsize)).convert_alpha()
    shadowsur.fill((0,0,0,255))
    shadowvertsur = pygame.Surface((shadowsize, size-void+shadowsize)).convert_alpha()
    shadowvertsur.fill((0,0,0,255))

    MAXSHADE = 70
    ALPHA = 80

    pxs = pygame.PixelArray(shadowsur)

    #shadow under
    rect = shadowsur.get_rect()
    tot = rect.width
    for i in range(tot):
        for j in range(shadowsize):
            alpha = ALPHA
            shade = MAXSHADE+j*20
            if i < tot*0.35:
                minshade = 190+shade
                shade = shade + (minshade-shade) * ( 1 - i/(tot*0.35) )
            elif i > tot + j - shadowsize:
                alpha = 0
                shade = 255
            if shade > 255:
                shade = 255
            shade = int(shade)
            pxs[i, j] = (shade, shade, shade, alpha)
    del pxs

    pxs = pygame.PixelArray(shadowvertsur)
    #shadow right
    rect = shadowvertsur.get_rect()
    tot = rect.height
    for i in range(tot):
        for j in range(shadowsize):
            alpha = ALPHA
            shade = MAXSHADE+j*20
            if i < tot*0.35:
                minshade = 190+shade
                shade = shade + (minshade-shade) * ( 1 - i/(tot*0.35) )
            elif i > tot + j - shadowsize - 1:
                alpha = 0
                shade = 255
            if shade > 255:
                shade = 255
            shade = int(shade)
            pxs[j, i] = (shade, shade, shade, alpha)
    del pxs

    print('Finished creating static shadows.')
    return shadowsur, shadowvertsur

#CREATE BOOSTER CHANCES LIST (accumulative)
def BoosterChancesList(extreme=False):
    if not extreme:
        chanceslist = boosterchances
    else:
        chanceslist = boosterchances_ex
    result = [0]*len(chanceslist)
    accum=0
    for i in range(len(chanceslist)):
        accum += chanceslist[i]
        if accum > 100:
            accum = 100
            print('Warning: Booster chances sum not 100%.')
        result[i] = accum
    if result[i] < 100:
        result[i]=100
        print('Warning: Booster chances sum not 100%.')

    return result

def colorize(image, newColor):
    image = image.copy()

    # add in new RGB values
    image.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGB_MIN)

    return image

#CREATE VIDEO MODES STRING LIST
def CreateVideoModeStrings():
    global vmodes_str
    for mode in videomodes:
        modeaspect = mode[0]/mode[1]
        if mode[0] > 1024 and abs((modeaspect-aspectratio)) < 0.15:  #discard all resolutions that are <= 1024 width and not on the native aspect ratio
            vmode_str = str(mode[0]) + 'x' + str(mode[1])
            vmodes_str.append( vmode_str )
    vmodes_str = tuple(vmodes_str)

def RevDir(dir):
    #returns the opposite direction
    if dir==1:
        return 3
    elif dir==2:
        return 4
    elif dir==3:
        return 1
    elif dir==4:
        return 2
    else:
       return -1

def getFontBlit(font, fontsize, text, textcolor, xcoord, ycoord, center=False):
    #returns info to blit a text object
    #xcoord and ycoord represent the top left corner unless center=True
    textobj = pygame.font.Font(font, fontsize)
    textsurfaceobj = textobj.render(text, True, textcolor)
    textrectobj = textsurfaceobj.get_rect()
    if center:
        textrectobj.center = (xcoord, ycoord)
    else:
        textrectobj.left = xcoord
        textrectobj.top = ycoord
    return (textsurfaceobj, textrectobj)

def addRGB(basecolor, r, g, b):
    #adds the passed in rgb values to the basecolor
    endcolor = list(basecolor)
    endcolor = [endcolor[0]+r, endcolor[1]+g, endcolor[2]+b]
    for i in range(3):
        if endcolor[i] < 0:
            endcolor[i] = 0
        elif endcolor[i] > 255:
            endcolor[i] = 255
    return endcolor

def ResetPlayerScore():
    global PLAYERSCORE
    PLAYERSCORE = [0, 0]

def ResizeGfx():
    global lifeimg, gamebackimg, butoverlayimg, menubackimg, tonganimimg, appleimg, mouseimg, shadeSur, shadevertSur
    #test font blit just to get dimensions of text rect
    textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, PLAYERSCORESIZE, 'SAMPLE', FONTCOLOR, 0, 0)

    lifeimg, butoverlayimg, menubackimg, gamebackimg, tonganimimg, appleimg, mouseimg = LoadGfx()
    #try to smoothscale each of the images and resort to normal scaling if not possible
    try:
        lifeimg = pygame.transform.smoothscale(lifeimg, (textrectobj.height, textrectobj.height))
    except:
        lifeimg = pygame.transform.scale(lifeimg, (textrectobj.height, textrectobj.height))
    try:
        gamebackimg = pygame.transform.smoothscale(gamebackimg, (widthpx, heightpx))
    except:
        gamebackimg = pygame.transform.scale(gamebackimg, (widthpx, heightpx))
    try:
        tonganimimg = pygame.transform.smoothscale(tonganimimg, (int(size*0.9), int(size*0.5)))
    except:
        tonganimimg = pygame.transform.scale(tonganimimg, (int(size*0.9), int(size*0.5)))
    try:
        appleimg = pygame.transform.smoothscale(appleimg, (int(size*0.9),size))
    except:
        appleimg = pygame.transform.scale(appleimg, (int(size*0.9),size))
    try:
        mouseimg = pygame.transform.smoothscale(mouseimg, (size,size*2))
    except:
        mouseimg = pygame.transform.scale(mouseimg, (size,size*2))

    shadeSur, shadevertSur = CreateShadowSurfaces()
    if 'game' in globals():
        game.apples[0].Recolor()
        game.apples[1].Recolor()

def darken(col, amount):
    colout = col
    for i in range(3):
        if col[i] >= amount:
            colout[i] -= amount
        else:
            colout[i] = 0
    return colout

def CheckFps(rfps):
    global boosteranimmax,eyesanimmax,tonganimmax,floatanimmax,checkedfps,framesperstateupdate
    """checks if current fps is far from the desired one
    and readjusts some fps dependent animations to the real current fps"""
    if rfps < checkedfps*0.9 or rfps > checkedfps*1.1:
        boosteranimmax=rfps*1.2
        eyesanimmax=rfps*5
        tonganimmax=int(fps*0.3)
        floatanimmax=int(fps*1.5)
        perc = fps/standard_fps
        newgups = gups*perc
        framesperstateupdate=rfps/newgups
        checkedfps = rfps
        print('Readjusting game animations for %5.2f fps.' % rfps)

def QuitGame():
    mappedcolor1 = 256*256*SNAKECOLOR[0].r + 256*SNAKECOLOR[0].g + SNAKECOLOR[0].b
    mappedcolor2 = 256*256*SNAKECOLOR[1].r + 256*SNAKECOLOR[1].g + SNAKECOLOR[1].b
    sets = [SOUNDON, MUSICON, BOOSTERSON, MAXSCORE, Fps2SpeedOption(fps), mappedcolor1, mappedcolor2, activemode[0], activemode[1]]
    settings.Save(sets)
    pygame.quit()
    sys.exit()
    
#=========================

class Game:
    
    def __init__(self, DISPLAY):
        self.DISPLAY = DISPLAY
        self.DISPLAY.fill(BACKCOLOR)
        self.panelSur = pygame.Surface((panel, heightpx))

        self.snakes=[]
        self.apples=[]
        self.timers=[]
        self.mouse=Mouse(randint(1,w),randint(1,h),self)
        self.menus=[]
        self.booster=None
        self.boosteranim=0
        self.eyesanim=[randint(0,int(eyesanimmax)),randint(0,int(eyesanimmax))]
        self.floatanim=0
        self.floatxy=[0,0]
        self.floatsur = None
        self.playerwon=-1    #starts at -1, takes value of player index when he wins (0 or 1)
        self.paused = False
        self.showmenu = True
        self.playerscore=[0,0]
        self.ResetButton = pygame.Rect(panx + widthpx + int(size/2), pany + heightpx - RESETBUTTONHEIGHT - int(size/2), panel-size, RESETBUTTONHEIGHT)
        self.resetpressed = False
        self.scoreRects=[None]*6
        self.boosterex = False  # this is True when extreme booster chances are enabled
        self.bchances = BoosterChancesList()
        
        #create snakes
        self.snakes.append(Snake(randint(1,w),randint(1,h),0,SNAKECOLOR[0]))
        #next loop is just to make sure the 2nd snake doesn't appear in the same line as the 1st
        snake2y = randint(1,h)
        while snake2y == self.snakes[0].head.y:
            snake2y = randint(1,h)
        self.snakes.append(Snake(randint(1,w),snake2y,1,SNAKECOLOR[1]))
    
        #create apples
        self.apples.append(Apple(randint(1,w),randint(1,h),0,SNAKECOLOR[0]))
        apple2x, apple2y = self.findemptypos()
        self.apples.append(Apple(apple2x, apple2y, 1, SNAKECOLOR[1]))

        #create booster timer
        boostertimer = Timer(self.createbooster, randint(boostertmin,boostertmax), False)
        self.timers.append(boostertimer)

        self.UpdatePanelStandard()

    def createresetbutton(self):
        return pygame.Rect(panx + widthpx + int(size/2), pany + heightpx - RESETBUTTONHEIGHT - int(size/2), panel-size, RESETBUTTONHEIGHT)
    
    def createbooster(self):
        if not BOOSTERSON:
            return
        newx, newy = self.findemptypos()
        #randomize booster type
        rng=randint(1,100)
        for i in range(boostertypes):
            if rng <= self.bchances[i]:
                newtype=i
                break
        self.booster = Booster(newx, newy, newtype)
        self.boosteranim = 0

    def othersnake(self, snaketocheck):
        return self.snakes[not snaketocheck.index]

    def checkwincondition(self):
        #check score or lives
        for snake in self.snakes:
            if snake.points >= MAXSCORE * 0.5 and not self.boosterex:
                self.bchances = BoosterChancesList(extreme=True)
                self.boosterex = True
            if snake.points >= MAXSCORE or self.othersnake(snake).lives <= 0:
                self.forcewin(snake.index)
                
        #check for draw
        if (self.snakes[0].points >= MAXSCORE and self.snakes[1].points >= MAXSCORE) \
        or (self.snakes[0].lives <= 0 and self.snakes[1].lives <= 0):
            self.forcewin(3)    #3=draw
            
        #check if anyone won
        if self.playerwon >= 0:
            self.pause()

    def forcewin(self, player):
        self.playerwon = player     #player=0 -> player 1, player=1 -> player 2, player=3 -> draw
        if self.playerwon != 3:
            global PLAYERSCORE
            PLAYERSCORE[player] += 1
        #make all snakes visible
        self.snakes[0].visible = True
        self.snakes[1].visible = True
        
    def pause(self):
        if self.playerwon == -1:    #-1 means game is still going on
            textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, size*2, 'PAUSED', FONTCOLOR, widthpx//2 + panx, heightpx//2 + pany, center=True)
            self.DISPLAY.blit(textsurfaceobj, textrectobj)
        self.paused = True
        
    def unpause(self):
        self.paused = False

    def findemptypos(self):
        found=False
        while found==False: #loop until a position out of the snakes is found
            newx=randint(1,w)
            newy=randint(1,h)
            found=True
            for snake in self.snakes:
                for tail in snake.tails:
                    if newx==tail.x and newy==tail.y:
                        found=False
            for apple in self.apples:
                if newx==apple.x and newy==apple.y:
                    found=False
            if self.booster != None:
                if newx==self.booster.x and newy==self.booster.y:
                    found=False
        return (newx, newy)

    def getactivemenu(self):
        if len(self.menus) > 0:
            return self.menus[-1]
        else:
            return None

    def pausetimers(self):
        real_fps = clock.get_fps()
        if real_fps ==0:
            real_fps = fps
        for timer in self.timers:
            timer.addpausedtime(1/real_fps)

    def NextFrame(self):
        #check timers
        for timer in self.timers:
            if timer.check() == 1:      #timer ended
                self.timers.remove(timer)

        #check win condition
        self.checkwincondition()
        
        #game events
        invulnerabilities=[self.snakes[0].invulnerable, self.snakes[1].invulnerable]
        for snake in self.snakes:
            snake.Move(self)
        for snake in self.snakes:
            if invulnerabilities[snake.index]==False and not (self.othersnake(snake).boosted==True and self.othersnake(snake).boostertype==5):   #only check snake position if vulnerable and not frozen
                snake.CheckPos(self)
        for apple in self.apples:
            apple.CheckApple(self)

    def draweyes(self, direction, head, lids=False, frozen=False):
        #find eyes spot according to head direction
        if direction == 1:
            x1 = x2 = head.right - int(head.width*0.28)
            y1 = head.centery - int(head.height*0.22)
            y2 = head.centery + int(head.height*0.22)
        elif direction == 2:
            y1 = y2 = head.top + int(head.height*0.28)
            x1 = head.centerx - int(head.width*0.22)
            x2 = head.centerx + int(head.width*0.22)
        elif direction == 3:
            x1 = x2 = head.left + int(head.width*0.28)
            y1 = head.centery - int(head.height*0.22)
            y2 = head.centery + int(head.height*0.22)
        elif direction == 4:
            y1 = y2 = head.bottom - int(head.height*0.28)
            x1 = head.centerx - int(head.width*0.22)
            x2 = head.centerx + int(head.width*0.22)

        #frozen X eyes
        if frozen:
            Xsize = int(size*0.15)
            Xwidth = int(size*0.08)
            rect1 = pygame.Rect(0,0,Xsize,Xsize)
            rect1.center = (x1,y1)
            pygame.draw.line(self.DISPLAY, FONTCOLOR, (rect1.left, rect1.top), (rect1.right, rect1.bottom), Xwidth)
            pygame.draw.line(self.DISPLAY, FONTCOLOR, (rect1.left, rect1.bottom), (rect1.right, rect1.top), Xwidth)
            rect2 = pygame.Rect(0,0,Xsize,Xsize)
            rect2.center = (x2,y2)
            pygame.draw.line(self.DISPLAY, FONTCOLOR, (rect2.left, rect2.top), (rect2.right, rect2.bottom), Xwidth)
            pygame.draw.line(self.DISPLAY, FONTCOLOR, (rect2.left, rect2.bottom), (rect2.right, rect2.top), Xwidth)
            return

        if lids == False:
            pygame.draw.circle(self.DISPLAY, BACKCOLOR, (x1,y1), int(size*0.1))
            pygame.draw.circle(self.DISPLAY, BACKCOLOR, (x2,y2), int(size*0.1))
        else:
            lidw = int(size*0.08)
            lidh = int(size*0.15)
            if direction == 1 or direction == 3:
                lid1 = lid2 = pygame.Rect(0,0,lidw,lidh)
            else:
                lid1 = lid2 = pygame.Rect(0,0,lidh,lidw)
            lid1.center = (x1,y1)
            pygame.draw.rect(self.DISPLAY, FONTCOLOR, lid1)
            lid2.center = (x2,y2)
            pygame.draw.rect(self.DISPLAY, FONTCOLOR, lid2)
    
    def drawsquare(self, x, y, a, color):
        square = pygame.Rect(0, 0, a, a)
        square.center = (x,y)
        clip = square.clip((panx, pany, widthpx, heightpx))
        sup = None
        if square.right > widthpx + panx:
            sup = pygame.Rect(square.x-widthpx+clip.width, square.y,  square.width-clip.width, a)
        elif square.left < panx:
            sup = pygame.Rect(square.x+widthpx-clip.width, square.y, square.width-clip.width, a)
        elif square.top < pany:
            sup = pygame.Rect(square.x, square.y+heightpx-clip.height, square.height-clip.height, a)
        elif square.bottom > heightpx + pany:
            sup = pygame.Rect(square.x, square.y-heightpx+clip.height,  square.height-clip.height, a)

        pygame.draw.rect(self.DISPLAY, color, clip)
        if sup != None:
            pygame.draw.rect(self.DISPLAY, color, sup)
            return sup
        return clip

    def drawsquarebord(self, x, y, a, color):
        square = pygame.Rect(0, 0, a, a)
        square.center = (x,y)
        pygame.draw.rect(self.DISPLAY, color, square, BOOSTERBORDER)

    def drawdiamond(self, x, y, a, color):
        pygame.draw.polygon(self.DISPLAY, color, ((x,y-a),(x+a,y),(x,y+a),(x-a,y)))

    def drawdiamondbord(self, x, y, a, color):
        pygame.draw.lines(self.DISPLAY, color, True, ((x,y-a),(x+a,y), (x,y+a), (x-a,y)), BOOSTERBORDER)

    def drawresetbutton(self):
        self.ResetButton = self.createresetbutton()
        colormain = (200, 200, 70)
        colorlight = (255, 255, 200)
        colordark = (150, 150, 50)
        if self.resetpressed:
            colorup = colordark
            colordown = colorlight
            fontcolor = pygame.Color('red')
        else:
            colorup = colorlight
            colordown = colordark
            fontcolor = FONTCOLOR
        pygame.draw.rect(self.DISPLAY, colormain, self.ResetButton)
        pygame.draw.lines(self.DISPLAY, colorup, False, ((self.ResetButton.left, self.ResetButton.bottom),(self.ResetButton.left, self.ResetButton.top),(self.ResetButton.right, self.ResetButton.top)), 5)
        pygame.draw.lines(self.DISPLAY, colordown, False, ((self.ResetButton.left, self.ResetButton.bottom),(self.ResetButton.right, self.ResetButton.bottom),(self.ResetButton.right, self.ResetButton.top)), 5)
        #paint overlay
        overlay = pygame.transform.scale(butoverlayimg, (self.ResetButton.width, self.ResetButton.height))
        self.DISPLAY.blit(overlay, self.ResetButton, None, BLEND_RGB_ADD)
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, PLAYERSCORESIZE, 'RESET SCORES', fontcolor, self.ResetButton.centerx, self.ResetButton.centery, center = True)
        if self.resetpressed:
            #pan text a little to bottom right
            pan = (RESETBUTTONHEIGHT*0.05)
            textrectobj.centerx += pan
            textrectobj.centery += pan
        self.DISPLAY.blit(textsurfaceobj, textrectobj)
        
    def drawborders(self):
        #border of playable area
        border=pygame.Rect(panx, pany, widthpx, heightpx)
        pygame.draw.rect(self.DISPLAY, BORDERCOLOR, border, 1)
        #border of score panel
        pan=pygame.Rect(widthpx+panx, pany, panel, heightpx)
        pygame.draw.rect(self.DISPLAY, BORDERCOLOR, pan, 1)

    def drawwallboost(self, snake):
        #border for wall boost
        border=pygame.Rect(panx, pany, widthpx, heightpx)
        pygame.draw.rect(self.DISPLAY, BOOSTERCOLOR[snake.boostertype], border, 10)

    def UpdatePanelStandard(self):
        self.panelSur.fill(BACKCOLOR)

        drawx = int(panel*0.10)
                
        #player 1 score
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, PLAYERSCORESIZE, '%s - %i' % (PLAYERNAMES[0],PLAYERSCORE[0]), self.snakes[0].color, drawx, 20)
        self.panelSur.blit(textsurfaceobj, textrectobj)
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, PLAYERSCORESIZE, '000000', self.snakes[0].color, drawx, textrectobj.bottom)
        self.scoreRects[0]=textrectobj
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, PLAYERSCORESIZE, 'BOOST 000', FONTCOLOR, drawx, textrectobj.bottom)
        self.scoreRects[4]=textrectobj

        #create life objects rect 1
        move = 0
        for i in range(self.snakes[0].lives):
            move += int(lifeimg.get_width() * 1.25)
        self.scoreRects[2]=pygame.Rect(textrectobj.left, textrectobj.bottom, move, lifeimg.get_height())

        #player 2 score
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, PLAYERSCORESIZE, '%s - %i' % (PLAYERNAMES[1],PLAYERSCORE[1]), self.snakes[1].color, drawx, textrectobj.bottom + size*3)
        self.panelSur.blit(textsurfaceobj, textrectobj)
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, PLAYERSCORESIZE, '000000', self.snakes[1].color, drawx, textrectobj.bottom)
        self.scoreRects[1]=textrectobj
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, PLAYERSCORESIZE, 'BOOST 000', FONTCOLOR, drawx, textrectobj.bottom)
        self.scoreRects[5]=textrectobj

        #create life objects rect 2
        move = 0
        for i in range(self.snakes[1].lives):
            move += int(lifeimg.get_width() * 1.25)
        self.scoreRects[3]=pygame.Rect(textrectobj.left, textrectobj.bottom, move, lifeimg.get_height())
        self.drawlifeobjects()

        #game version text
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, int(PLAYERSCORESIZE/2), gamever, FONTCOLOR, 0, 0)
        textrectobj.bottom = heightpx
        textrectobj.right = panel
        self.panelSur.blit(textsurfaceobj, textrectobj)

    def drawlifeobjects(self):
        #clear object areas
        self.panelSur.fill(BACKCOLOR, self.scoreRects[2])
        self.panelSur.fill(BACKCOLOR, self.scoreRects[3])

        #draw life objects
        move = 0
        for i in range(self.snakes[0].lives):
            self.panelSur.blit(lifeimg, (self.scoreRects[2].left + move, self.scoreRects[2].top))
            move += int(lifeimg.get_width() * 1.25)

        move = 0
        for i in range(self.snakes[1].lives):
            self.panelSur.blit(lifeimg, (self.scoreRects[3].left + move, self.scoreRects[3].top))
            move += int(lifeimg.get_width() * 1.25)

    def UpdateScores(self):
        #find booster cooldown timer
        boostertimer = -1
        for i in range(len(self.timers)):
            if self.timers[i].isbooster == True:
                boostertimer=i

        #find boosted player
        boostercdstr1 = "-"
        boostercdstr2 = "-"
        boostercolor1 = FONTCOLOR
        boostercolor2 = FONTCOLOR
        if self.snakes[0].boosted == True:
            boostercdstr1 = str(self.timers[boostertimer].remaining())
            boostercolor1 = BOOSTERCOLOR[self.snakes[0].boostertype]
        elif self.snakes[1].boosted == True:
            boostercdstr2 = str(self.timers[boostertimer].remaining())
            boostercolor2 = BOOSTERCOLOR[self.snakes[1].boostertype]

        drawx = int(panel*0.10)
                
        #player 1 score
        self.panelSur.fill(BACKCOLOR, self.scoreRects[0])
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, PLAYERSCORESIZE, str(self.snakes[0].points), self.snakes[0].color, self.scoreRects[0].left, self.scoreRects[0].top)
        self.panelSur.blit(textsurfaceobj, textrectobj)
        self.panelSur.fill(BACKCOLOR, self.scoreRects[4])
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, PLAYERSCORESIZE, 'BOOST %s' % boostercdstr1, boostercolor1, drawx, textrectobj.bottom)
        self.panelSur.blit(textsurfaceobj, textrectobj)

        #player 2 score
        self.panelSur.fill(BACKCOLOR, self.scoreRects[1])
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, PLAYERSCORESIZE, str(self.snakes[1].points), self.snakes[1].color, self.scoreRects[1].left, self.scoreRects[1].top)
        self.panelSur.blit(textsurfaceobj, textrectobj)
        self.panelSur.fill(BACKCOLOR, self.scoreRects[5])
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, PLAYERSCORESIZE, 'BOOST %s' % boostercdstr2, boostercolor2, drawx, textrectobj.bottom)
        self.panelSur.blit(textsurfaceobj, textrectobj)

    def drawwintext(self):
        if self.playerwon == 3:
            text = "DRAW"
            textcolor = FONTCOLOR
        else:
            text = PLAYERNAMES[self.playerwon] + " WINS"
            textcolor = SNAKECOLOR[self.playerwon]
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, size*2, text, textcolor, widthpx//2 + panx, heightpx//2 + pany, center=True)
        self.DISPLAY.blit(textsurfaceobj, textrectobj)
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, MENUOPTIONOPTIONSIZE, 'Press SPACE to restart game', FONTCOLOR, widthpx//2 + panx, textrectobj.bottom, center=True)
        textrectobj.bottom += textrectobj.height/2
        self.DISPLAY.blit(textsurfaceobj, textrectobj)

    def drawtongue(self,snake,head):
        if snake.tonganim == -1:
            return
        tong = tonganimimg.copy()
        tongrect = tong.get_rect()
        #animate tongue by cropping
        if snake.tonganim < tonganimmax*0.4:
            perccrop = tongrect.width*snake.tonganim/(tonganimmax*0.4)
        else:
            perccrop = tongrect.width*(tonganimmax-snake.tonganim)/(tonganimmax*0.6)
        cropped = pygame.Surface((perccrop,tongrect.height)).convert_alpha()
        cropped.fill((0,0,0,0))
        cropped.blit(tong, (0,0), (tongrect.width-perccrop, 0, perccrop, tongrect.height))
        #rotate tongue according to head direction
        if snake.head.direct in (2,4):
            cropped = pygame.transform.rotate(cropped, (snake.head.direct*90+270))
        elif snake.head.direct == 3:
            cropped = pygame.transform.flip(cropped, True, False)
        tongrect = cropped.get_rect()
        #find head tip
        if snake.head.direct == 1:
            x = head.right
            y = head.top + head.height//2 - tongrect.height*0.6
        elif snake.head.direct == 2:
            x = head.left + head.width//2 - tongrect.width*0.6
            y = head.top - tongrect.height
        elif snake.head.direct == 3:
            x = head.left - tongrect.width
            y = head.top + head.height//2 - tongrect.height*0.6
        elif snake.head.direct == 4:
            x = head.left + head.width//2 - tongrect.width*0.6
            y = head.bottom
        self.DISPLAY.blit(cropped, (x, y))

    def blitshadow(self, x, y, size):
        #x,y are coordinates of the center of the rect
        rect = pygame.Rect(0, 0, size, size)
        rect.center = (x,y)
        self.DISPLAY.blit(shadeSur, (rect.left, rect.bottom), None, BLEND_RGBA_MULT)
        self.DISPLAY.blit(shadevertSur, (rect.right, rect.top), None, BLEND_RGBA_MULT)

    def drawfloattext(self):
        percanim = self.floatanim / floatanimmax
        if percanim < 0.4:
            alpha = 255
        else:
            alpha = 255 * (1 - (percanim-0.4)/0.6 )
        maxy = int(size*2.5)

        rect = self.floatsur.get_rect()
        x = self.floatxy[0]
        if x + rect.width > panx + widthpx:
            x = panx + widthpx - rect.width
        y = self.floatxy[1]-maxy*percanim
        if y < pany:
            y = 0
            
        trans = pygame.Surface((rect.width, rect.height)).convert_alpha()
        trans.fill((255,255,255,alpha))
        trans.blit(self.floatsur, (0,0),special_flags=pygame.BLEND_RGBA_MULT)
        self.DISPLAY.blit(trans, (x,y))

    def DrawAll(self, interp):
        if interp >= 1:
            interp = 0
        self.DISPLAY.blit(gamebackimg, (panx, pany))
        #draw score panel
        self.DISPLAY.blit(self.panelSur, (panx+widthpx, pany))
        #draw border around playable area and score panel
        self.drawborders()
        #draw snakes and their tails
        for snake in self.snakes:
            snake.CheckVisibility()
            other = self.othersnake(snake)
            if snake.visible:
                snakecolor = snake.color
                total = len(snake.tails)
                for i, tail in enumerate(snake.tails):
                    velx, vely = tail.GetTailVelocity()
                    xpos = tail.x + interp*velx*snake.vel
                    ypos = tail.y + interp*vely*snake.vel
                    drawx = xpos*size-size//2 + panx
                    drawy = ypos*size-size//2 + pany
                    if i==0: #head
                        #frozen trembling effect
                        if other.boosted == True and other.boostertype == 5:
                            magnitude = int(size*0.12)
                            if snake.head.direct in (1,3):
                                drawy += randint(-magnitude, magnitude)
                            else:
                                drawx += randint(-magnitude, magnitude)
                    #draw shadows
                    self.blitshadow(drawx, drawy, size-void)
                    #snake color effect
                    if i < total*0.4 or i > total*0.8:
                        snakecolor = addRGB(snakecolor, -4, -4, -4)
                    else:
                        snakecolor = addRGB(snakecolor, 4, 4, 4)
                    rect = self.drawsquare(drawx, drawy, size-void, snakecolor)
                    if i ==0:
                        head = rect
                        #draw tongue and animate it
                        if snake.tonganim > -1:
                            snake.updatetonganim()
                            self.drawtongue(snake, head) #draw tongue
                    if snake.boosted == True and snake.boostertype not in (2,5):
                        self.drawsquarebord(drawx, drawy, size-void, BOOSTERCOLOR[snake.boostertype])
                    elif other.boosted == True and other.boostertype in (2,5):
                        self.drawsquarebord(drawx, drawy, size-void, BOOSTERCOLOR[other.boostertype])
                #draw snake eyes and animate them
                self.updateeyesanim()
                froz = False
                if other.boosted == True and other.boostertype ==5:
                    froz = True
                if self.eyesanim[snake.index] <= eyesanimmax*0.9:
                    self.draweyes(snake.head.direct,head,lids=False, frozen=froz)
                else:
                    self.draweyes(snake.head.direct,head,lids=True, frozen=froz)
                
        #draw apples
        for apple in self.apples:
            self.DISPLAY.blit(apple.image, (apple.x*size-size + panx, apple.y*size-size + pany))
        #draw booster with it's animation
        if self.booster != None:
            self.updateboosteranim()
            maxsize_ = size*1.2/2
            minsize_ = size*0.8/2
            if self.boosteranim > boosteranimmax*0.80:
                size_ = minsize_ + (maxsize_-minsize_)*(self.boosteranim - boosteranimmax*0.85)/(boosteranimmax*0.15)
            else:
                size_ = maxsize_ - (maxsize_-minsize_)*(self.boosteranim)/(boosteranimmax*0.85)
            drawsize = int(round(size_,0))
            self.drawdiamond(self.booster.x*size-size//2 + panx, self.booster.y*size-size//2 + pany, drawsize, self.booster.color)
            self.drawdiamondbord(self.booster.x*size-size//2 + panx, self.booster.y*size-size//2 + pany, drawsize, FONTCOLOR)
        #draw wall boost border
        for snake in self.snakes:
            if snake.boosted==True and snake.boostertype==3:
                self.drawwallboost(snake)
        #draw reset button
        self.drawresetbutton()
        #draw floating text animations
        if self.floatanim > 0:
            self.drawfloattext()
            self.updatefloatanim()
        #draw win text
        if self.playerwon >= 0 and not self.showmenu:
            self.drawwintext()
        #draw mouse
##        drawx = self.mouse.x*size-size//2 + panx
##        drawy = self.mouse.y*size-size//2 + pany
##        self.DISPLAY.blit(self.mouse.image, (drawx,drawy))

    def updateboosteranim(self):
        if self.boosteranim < boosteranimmax:
            self.boosteranim += 1
        else:
            self.boosteranim = 0

    def updateeyesanim(self):
        for i in range(2):
            if self.eyesanim[i] < eyesanimmax:
                self.eyesanim[i] += 1
            else:
                self.eyesanim[i] = 0

    def startfloatanim(self, xy, text, color):
        self.floatxy = xy
        self.floatanim = 1
        textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, FLOATTEXTSIZE, text, color, 0, 0)
        self.floatsur = textsurfaceobj

    def updatefloatanim(self):
        if self.floatanim < floatanimmax:
            self.floatanim += 1
        else:
            self.floatanim = 0
            self.floatxy = [0,0]
            self.floatsur = None
               
class Snake:
    vel=1   #snake velocity: 0 or 1
    
    def __init__(self, x, y, index, color):
        self.color=color
        self.tails=[]
        self.head=None
        self.turnspending=[]
        self.points=0
        self.tonganim=-1   #tongue animation, -1 means it is static
        self.index=index
        self.boosted=False
        self.boostertype=-1
        self.lives=maxlives
        self.invulnerable=False
        self.visible=True
        self.maxflashticks=2*fps//flashspeed    #flash according to flashspeed constant
        self.flashtick=0

        for i in range(starttails + 1): #create initial tails and head
            newtail=Tailpiece(x, y, 1)
            self.tails.append(newtail)
            x -= 1
        self.head = self.tails[0]

    def __str__(self):
        return str(self.index)

    def updatetonganim(self):
        if self.tonganim < tonganimmax:
            self.tonganim += 1
        else:
            self.tonganim = -1

    def makeinvulnerable(self):
        self.invulnerable = True

    def makevulnerable(self):
        self.invulnerable = False
        self.maxflashticks=int(2*checkedfps/flashspeed)
    
    def Move(self,terrain):
        #check for freeze boost
        other=terrain.othersnake(self)
        if other.boosted==True and other.boostertype==5:
            self.vel=0
            #leave only the last turnspending instance to prevent flushing turns when unfrozen
            if len(self.turnspending) > 0:
                lastinst=self.turnspending[-1]
                self.turnspending=[]
                self.turnspending.append(lastinst)
        else:
            self.vel=1
        #move tails
        for tail in self.tails:
            velx, vely = tail.GetTailVelocity()
            tail.x += velx*self.vel
            tail.y += vely*self.vel
        #check for wall
        for i, tail in enumerate(self.tails):
            if i == 0:  #head
                walled=True
            if tail.x==w+1 and tail.direct==1: #hit right wall
                tail.x=1
            elif tail.x==0 and tail.direct==3: #hit left wall
                tail.x=w
            elif tail.y==0 and tail.direct==2: #hit top wall
                tail.y=h
            elif tail.y==h+1 and tail.direct==4: #hit bottom wall
                tail.y=1
            else:
                if i == 0:
                    walled=False
        #update tails directions
        if self.vel >0:
            for i in range(len(self.tails)-1,-1,-1):
                if i>0:
                    self.tails[i].direct = self.tails[i-1].direct
        #implement one turn at each movement tick
        if len(self.turnspending)>0:
            newdir=self.turnspending.pop(0)
            if RevDir(self.head.direct)!= newdir:
                self.head.direct=newdir
        #if walled, check for wall booster
        other=terrain.othersnake(self)
        if walled and self.invulnerable==False \
           and other.boosted==True and other.boostertype==3:
            self.loselife()
            self.makeinvulnerable()
            terrain.timers.append(Timer(self.makevulnerable, INVULNERABLEDUR))
            terrain.timers.append(Timer(self.addlife, LIFERESTORE))
    
    def CheckPos(self,terrain):
        #print('Check pos: snake %d (x:%d y:%d inv:%d)' % (self.index, self.head.x, self.head.y, self.invulnerable))
        #check if apple is hit by head
        for apple in terrain.apples:
            if self.head.x==apple.x and self.head.y==apple.y:
                self.EatApple(apple)
        #check if booster is hit by head
        if terrain.booster != None:
            if self.head.x==terrain.booster.x and self.head.y==terrain.booster.y:
                self.EatBooster(terrain)

        #check if tail hit
        hit=False
        face2face=False
        other=terrain.othersnake(self)
        #own snake's tails
        for i, tail in enumerate(self.tails):
            if i == 0:  #exclude head
                continue
            if self.head.x==tail.x and self.head.y==tail.y:
                hit=True
        #other snake's head / the smallest snake is hit otherwise they are both hit
        if self.head.x==other.head.x and self.head.y==other.head.y:
            print('smashed, snake%d tails: %d, snake%d tails: %d' % (self.index, len(self.tails), other.index, len(other.tails)))
            face2face = True
        if self.head.x==other.tails[1].x and self.head.y==other.tails[1].y and self.head.direct==RevDir(other.head.direct):
            print('smashed WEIRD, snake%d tails: %d, snake%d tails: %d' % (self.index, len(self.tails), other.index, len(other.tails)))
            face2face = True
        if face2face:
            #check for snake hunter boost
            if self.boosted==True and self.boostertype==4:
                terrain.forcewin(self.index)
                if SOUNDON: eatsound.play()
            elif len(self.tails) <= len(other.tails):
                hit=True
            
        #other snake's tails
        if not face2face:
            for i, tail in enumerate(other.tails):
                if i == 0:
                    continue
                if self.head.x==tail.x and self.head.y==tail.y and other.invulnerable==False:
                    print('snake%d smashed on snake%d tail%d' % (self.index, other.index, i))
                    #check for snake hunter boost
                    if self.boosted==True and self.boostertype==4:
                        other.removetail()
                        self.addtail()
                        self.tonganim = 0   #start the tongue animation
                        self.points += 10
                        other.points -= 10
                        if SOUNDON: eatsound.play()
                    else:
                        hit=True
                    
        #if snake hit something, start invulnerability and add back the life lost after LIFERESTORE seconds
        if hit:
            print('snake%d HIT' % self.index)
            self.loselife()
            self.makeinvulnerable()
            terrain.timers.append(Timer(self.makevulnerable, INVULNERABLEDUR))
            terrain.timers.append(Timer(self.addlife, LIFERESTORE))

    def CheckVisibility(self):
        #if snake invulnerable, increment flashticks and check with maxflashticks
        if self.invulnerable and game.playerwon < 0:
            if self.flashtick >= self.maxflashticks:
                self.flashtick = 0
                #slowly make flashing faster
                if self.maxflashticks > 2:
                    self.maxflashticks -= self.maxflashticks*0.1
            self.flashtick += 1
        else:
            self.flashtick = 0
            self.maxflashticks=int(2*checkedfps/flashspeed)

        #from 0 to 0.65*maxflashticks -> visible, from 0.65*maxflashticks to maxflashticks -> invisible
        if self.flashtick < 0.65*self.maxflashticks:
            self.visible=True
        else:
            self.visible=False
                        
    def EatApple(self,apple):
        apple.eaten=True
        self.tonganim = 0   #start the tongue animation
        if self.index==apple.index or (self.boosted and self.boostertype==0):
            self.addtail()
            if self.boosted and self.boostertype==1:
                self.points += 30
            else:
                self.points += 10
            if SOUNDON: applegood[randint(0,3)].play()
        else:
            self.removetail()
            if self.boosted and self.boostertype==1:
                self.points -= 30
            else:
                self.points -= 10
            if self.points < 0:
                self.points = 0
            if SOUNDON: applebad.play()
            
    def EatBooster(self,terrain):
        #boost snake
        self.boosted = True
        self.boostertype = terrain.booster.type_
        endtimer = Timer(self.endboost, boosterdurations[self.boostertype], isbooster=True)
        terrain.timers.append(endtimer)
        if SOUNDON: boostsounds[self.boostertype].play()
        #remove booster instance and create timer for next booster
        terrain.booster=None
        newtimer = Timer(terrain.createbooster, randint(boostertmin,boostertmax), False)
        terrain.timers.append(newtimer)
        #start animations
        self.tonganim = 0   #start the tongue animation
        terrain.startfloatanim((self.head.x*size-size//2+panx, self.head.y*size-size+pany), \
                               '%s!' % BOOSTERNAMES[self.boostertype], BOOSTERCOLOR[self.boostertype])
        #start playback of booster specific sounds
        if self.boostertype == 5:   #freeze boost
            chattersound.play(-1)
            stopsoundtimer = Timer(self.stopchatter, boosterdurations[5], False)
            terrain.timers.append(stopsoundtimer)

    def stopchatter(self):
        chattersound.stop()

    def loselife(self):
        self.lives -= 1
        game.drawlifeobjects()
        if SOUNDON: endsound.play()

    def addlife(self):
        if self.lives < maxlives:
            self.lives += 1
            game.drawlifeobjects()

    def endboost(self):
        self.boosted = False

    def moveright(self):
        self.turnspending.append(1)

    def moveup(self):
        self.turnspending.append(2)

    def moveleft(self):
        self.turnspending.append(3)

    def movedown(self):
        self.turnspending.append(4)

    def addtail(self):
        lasttail = self.tails[-1]
        if lasttail.direct==1:
            x = lasttail.x - 1
            y = lasttail.y
        elif lasttail.direct==2:
            x = lasttail.x
            y = lasttail.y + 1
        elif lasttail.direct==3:
            x = lasttail.x + 1
            y = lasttail.y
        elif lasttail.direct==4:
            x = lasttail.x
            y = lasttail.y - 1
        newtail=Tailpiece(x, y, lasttail.direct)
        self.tails.append(newtail)

    def removetail(self):
        if len(self.tails) > starttails + 1:
            self.tails.pop()

class Tailpiece:
    def __init__(self,x,y,direct):
        self.x=x
        self.y=y
        self.newx=0
        self.newy=0
        self.direct=direct

    def GetTailVelocity(self):
        velx = vely = 0
        if self.direct == 1:
            velx = 1
        elif self.direct == 2:
            vely = -1
        elif self.direct == 3:
            velx = -1
        elif self.direct == 4:
            vely = 1
        return velx, vely

class Mouse:
    def __init__(self,x,y,gameinst):
        self.gameinst = gameinst
        self.x=x
        self.y=y
        self.direct=1
        self.image=mouseimg
        self.canchange=True
        self.changedir(2)

    def update(self):
        self.move()
        self.changedir()

    def move(self):
        if self.direct == 1:
            self.x += 1
        elif self.direct == 2:
            self.y -= 1
        elif self.direct == 3:
            self.x -= 1
        elif self.direct == 4:
            self.y += 1

        if self.x > w - 1:
            self.changedir(4)
        elif self.x < 0:
            self.changedir(2)
        elif self.y < 1:
            self.changedir(1)
        elif self.y > h - 1:
            self.changedir(3)

    def changeon(self):
        self.canchange = True
            
    def changedir(self,force=0):
        if self.canchange == False and force == 0:
            return
        rng = randint(20,100)
        if rng < 10:
            while True:
                newdir = randint(1,4)
                if RevDir(newdir) != newdir:
                    self.direct = newdir
                    break
        if force:
            self.direct = force
        self.image = pygame.transform.rotate(mouseimg, self.direct*90+180)
        self.canchange = False
        self.gameinst.timers.append(Timer(self.changeon, 3))
            
class Apple:
    def __init__(self,x,y,index,color):
        self.x=x
        self.y=y
        self.eaten=False
        self.color=color
        self.index=index
        self.image=colorize(appleimg,color)

    def CheckApple(self,terrain):
        if self.eaten==True:
            newx, newy = terrain.findemptypos()
            self.Recreate(newx,newy)

    def Recreate(self,x,y):
        self.x=x
        self.y=y
        self.eaten=False

    def Recolor(self,color=None):
        if color != None:
            self.color = color
        self.image = colorize(appleimg,self.color)

class Booster:
    def __init__(self, x, y, type_):
        self.x = x
        self.y = y
        self.type_ = type_
        self.color = BOOSTERCOLOR[type_]

class Timer:
    def __init__(self, func, delay, isbooster=False):
        self.start = pygame.time.get_ticks()
        self.func = func
        self.delay = delay*1000
        self.isbooster=isbooster    #if a timer represents a booster cooldown, this is True

    def check(self):
        #checks if timer expired and fires the function
        now = pygame.time.get_ticks()
        if now > self.start+self.delay:
            if self.func != None: self.func()
            return 1
        return 0

    def addpausedtime(self, time):
        self.delay += time * 1000
    
    def remaining(self):
        #returns remaining timer time in seconds
        now = pygame.time.get_ticks()
        return str(int(self.delay-(now-self.start))//1000)

class Menu:
    def __init__(self, gameinst, title, *options):
        self.gameinst = gameinst                        #menus need a pointer to the game instance
        self.title = title
        self.options = []
        self.optionfireids = []
        self.selectedoptionid = 0                       #index of selected option
        self.optionhaschildren = [0]*len(options)       #list of bool values determining if an option has children
        self.optionchild = [None]*len(options)          #list of lists containing the possible children values
        self.optionchildindex = [0]*len(options)        #list of selected indexes of children values for each option
        for option, optionfireid in options:
            self.options.append(option)
            self.optionfireids.append(optionfireid)
        self.surface = pygame.Surface((widthpx, heightpx))
        self.acceptskeys = False                        #controls if a menu contains keyboard input fields / default to false and change only explicitly
        self.keyboardinputon = False                    #this is True if a keyboard input field is enabled
        self.keyboardinput = ['']*len(options)          #this stores the total keyboard input for all input options

    def AddChildren(self, *childtuples):
        #children should contain tuples: (option id, child value1, child value2, ..., child valuen, selected option id)
        if childtuples != None:
            for childtuple in childtuples:
                index = childtuple[0]
                self.optionhaschildren[index] = True
                childlist = []
                for i in range(1, len(childtuple) - 1):
                    childlist.append(childtuple[i])
                self.optionchild[index] = childlist
                self.optionchildindex[index] = childtuple[-1]
                
    def Show(self, display):
        self.gameinst.DISPLAY.fill(BACKCOLOR)
        self.surface.fill(BACKCOLOR)
        try:
            imgtodraw = pygame.transform.smoothscale(menubackimg, (widthpx, heightpx))
        except:
            imgtodraw = pygame.transform.scale(menubackimg, (widthpx, heightpx))
        self.surface.blit(imgtodraw, (0, 0))

        #check if instructions menu
        if self.title == 'Instructions':
            self.InstructionMenu()
            return

        #show title
        textsurfaceobj, textrectobj = getFontBlit(MENUTITLEFONT, MENUOPTIONTITLESIZE, self.title, FONTCOLOR, widthpx//2, MENUOPTIONTITLEY, center=True)
        self.surface.blit(textsurfaceobj, textrectobj)

        #show options
        y = MENUOPTIONY
        for idx, option in enumerate(self.options):
            if self.selectedoptionid == idx:
                fontcolor = pygame.Color('red')
            else:
                fontcolor = FONTCOLOR
            if self.optionhaschildren[idx]:
                if self.optionchild[idx][0] == 'COLOR_RECT':    #this string means the option has a colored rectangle
                    #draw rectangle
                    text = option + '     '
                    textsurfaceobj, textrectobj = getFontBlit(MENUOPTIONFONT, MENUOPTIONOPTIONSIZE, text, fontcolor, widthpx//2, y, center=True) #just sampling text height
                    rect = pygame.Rect(0, 0, size*3, textrectobj.height)
                    rect.left, rect.top = textrectobj.right, textrectobj.top
                    color = COLORSELECTIONLIST[self.optionchildindex[idx]]
                    pygame.draw.rect(self.surface, color, rect)
                    pygame.draw.rect(self.surface, (0, 0, 0), rect, BOOSTERBORDER)
                else:
                    text = option + '     ' + self.optionchild[idx][self.optionchildindex[idx]]
            else:
                text = option
            textsurfaceobj, textrectobj = getFontBlit(MENUOPTIONFONT, MENUOPTIONOPTIONSIZE, text, fontcolor, widthpx//2, y, center=True)
            self.surface.blit(textsurfaceobj, textrectobj)
            y += MENUOPTIONYSTEP
            
        self.gameinst.DISPLAY.blit(self.surface, (panx, pany))
        self.gameinst.UpdateScores()
        self.gameinst.drawborders()

    def ChangeOption(self, key):
        if key != None and self.title != 'Instructions':
            if key == K_UP:
                if SOUNDON: menuselectsound.play()
                self.optionup()
            elif key == K_DOWN:
                if SOUNDON: menuselectsound.play()
                self.optiondown()
            elif key == K_RIGHT and not self.acceptskeys:
                if SOUNDON and self.optionhaschildren[self.selectedoptionid]: menuselectsound.play()
                self.optionright()
            elif key == K_LEFT and not self.acceptskeys:
                if SOUNDON and self.optionhaschildren[self.selectedoptionid]: menuselectsound.play()
                self.optionleft()
            elif key == 13:     #ENTER
                if self.optionfireids:
                    self.MenuFireOption(self.optionfireids[self.selectedoptionid])
            elif key in ACCEPTEDKEYS:
                if self.keyboardinputon:
                    sound2play = menukeysound
                    if key == K_BACKSPACE:
                        self.optionchild[self.selectedoptionid][1] = self.optionchild[self.selectedoptionid][1][:-1]
                    else:
                        if len(self.optionchild[self.selectedoptionid][1]) < maxnamelen:
                            self.optionchild[self.selectedoptionid][1] += chr(key).upper()
                        else:
                            sound2play = menuerrorsound
                    if SOUNDON: sound2play.play()
                        
        if key != None:
            if key == K_ESCAPE:
                if SOUNDON: menubacksound.play()
                self.MenuFireOption(0)
    
    def optionup(self):
        #reset selection for the previous item
        self.ResetOptionDefaultValues()
        #change selection
        self.selectedoptionid -= 1
        if self.selectedoptionid < 0:
            self.selectedoptionid = len(self.options) - 1
                
    def optiondown(self):
        #reset selection for the previous item
        self.ResetOptionDefaultValues()
        #change selection
        self.selectedoptionid += 1
        if self.selectedoptionid > len(self.options) - 1:
            self.selectedoptionid = 0

    def optionright(self):
        if self.optionhaschildren[self.selectedoptionid]:
            self.optionchildindex[self.selectedoptionid] += 1
            if self.optionchildindex[self.selectedoptionid] > len(self.optionchild[self.selectedoptionid]) - 1:
                self.optionchildindex[self.selectedoptionid] = 0

    def optionleft(self):
        if self.optionhaschildren[self.selectedoptionid]:
            self.optionchildindex[self.selectedoptionid] -= 1
            if self.optionchildindex[self.selectedoptionid] < 0:
                self.optionchildindex[self.selectedoptionid] = len(self.optionchild[self.selectedoptionid]) - 1

    def MenuFireOption(self, option):
        global fps, MAXSCORE, SOUNDON, MUSICON, BOOSTERSON, SNAKECOLOR, activemode, backchannel, framesperstateupdate
        #fires the current option menu
        #events have a distinct integer id
        if option == 0:     #start game
            if len(self.gameinst.menus) <= 1:
                self.gameinst.unpause()
                self.gameinst.showmenu = False
                
                if SOUNDON: menuvalidatesound.play()
                if MUSICON == 1:
                    pygame.mixer.music.fadeout(1500)
                    if backchannel == None:
                        backchannel = gamemusic.play(-1)
                    pygame.mixer.unpause()
                if len(self.options) < 5:
                    self.options[0]='Resume Game'
                    self.options.insert(1, 'Restart Game')
                    self.optionfireids.insert(1, 4)
                    self.optionhaschildren.append(0)
            else:
                #if it is an overlay menu, remove it
                self.gameinst.menus.remove(self)
                if SOUNDON: menubacksound.play()
        elif option == 1:   #show options menu
            if SOUNDON: menuvalidatesound.play()
            optionsmenu = Menu(self.gameinst, 'Options', ('Display Settings' , 7), ('Player Names', 6), ('Sounds', 8), ('Music', 9), ('Max Score', 10), ('Game Speed', 11), ('Boosters', 12), ('Back',0))
            score, speed = self.GetOptionDefaultValues(option)
            optionsmenu.AddChildren((2, 'OFF', 'ON', SOUNDON), (3, 'OFF', 'ON', MUSICON), (4, '300', '400', '500', '750', '1000', score), (5, 'I', 'I I', 'I I I', speed), (6, 'OFF', 'ON', BOOSTERSON))
            self.gameinst.menus.append(optionsmenu)
        elif option == 2: #show instructions screen
            if SOUNDON: menuvalidatesound.play()
            self.gameinst.menus.append(Menu(self.gameinst, 'Instructions'))
        elif option == 3:   #quit game
            QuitGame()
        elif option == 4:   #restart game
            if SOUNDON: menuvalidatesound.play()
            if backchannel != None and MUSICON == 1:
                backchannel.play(gamemusic, -1)
            game = RestartGame(self.gameinst.DISPLAY)
            if MUSICON == 1: pygame.mixer.music.fadeout(1500)
        elif option == 6:   #player names menu
            if SOUNDON: menuvalidatesound.play()
            namesmenu = Menu(self.gameinst, 'Player Names', ('Player 1 Name', 16), ('Player 2 Name', 16), ('Back', 0))
            namesmenu.acceptskeys = True
            namesmenu.AddChildren((0, PLAYERNAMES[0], '', 0), (1, PLAYERNAMES[1], '', 0))
            self.gameinst.menus.append(namesmenu)
        elif option == 7:   #display options menu
            if SOUNDON: menuvalidatesound.play()
            colourmenu = Menu(self.gameinst, 'Snake Colours', ('Screen Resolution', 15), ('Player 1 Snake', 13), ('Player 2 Snake', 14), ('Back', 0))
            resolutions, functuple = self.GetOptionDefaultValues(option)
            colourmenu.AddChildren(resolutions, functuple[0], functuple[1])
            self.gameinst.menus.append(colourmenu)
        elif option == 8:   #sound on option
            if SOUNDON: menuvalidatesound.play()
            value = self.optionchildindex[self.selectedoptionid]
            SOUNDON = value
            print("Setting sound on to:" + str(SOUNDON))
        elif option == 9:   #music option
            if SOUNDON: menuvalidatesound.play()
            value = self.optionchildindex[self.selectedoptionid]
            if value == 0:
                pygame.mixer.music.fadeout(1500)
            elif value == 1 and not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
            elif value == 2 and not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
            MUSICON = value
            print("Setting music to:" + str(MUSICON))
        elif option == 10:   #max score option
            if SOUNDON: menuvalidatesound.play()
            value = self.optionchildindex[self.selectedoptionid]
            MAXSCORE = 300 + 100*value
            if value == 3:
                MAXSCORE = 750
            elif value == 4:
                MAXSCORE = 1000
            print("Setting max score to:" + str(MAXSCORE))
        elif option == 11:   #game speed option
            if SOUNDON: menuvalidatesound.play()
            value = self.optionchildindex[self.selectedoptionid]
            fps = SpeedOption2Fps(value)
            perc = fps/standard_fps
            newgups = gups*perc
            framesperstateupdate=fps/newgups
            print("Setting fps to: %d, Game updates per second: %.2f" % (fps, newgups))
        elif option == 12:   #boosters on option
            if SOUNDON: menuvalidatesound.play()
            value = self.optionchildindex[self.selectedoptionid]
            BOOSTERSON = value
            if BOOSTERSON:
                #create a booster timer
                boostertimer = Timer(self.gameinst.createbooster, randint(boostertmin,boostertmax), False)
                self.gameinst.timers.append(boostertimer)
            else:
                self.gameinst.booster = None
            print("Setting boosters on to:" + str(BOOSTERSON))
        elif option == 13:   #snake 1 colour option
            if SOUNDON: menuvalidatesound.play()
            value = self.optionchildindex[self.selectedoptionid]
            COLOR = COLORSELECTIONLIST[value]
            self.gameinst.snakes[0].color = COLOR
            self.gameinst.apples[0].Recolor(COLOR)
            SNAKECOLOR[0] = COLOR
            self.gameinst.UpdatePanelStandard()
            print("Setting player 1 colour to:" + str(COLOR))
        elif option == 14:   #snake 2 colour option
            if SOUNDON: menuvalidatesound.play()
            value = self.optionchildindex[self.selectedoptionid]
            COLOR = COLORSELECTIONLIST[value]
            self.gameinst.snakes[1].color = COLOR
            self.gameinst.apples[1].Recolor(COLOR)
            SNAKECOLOR[1] = COLOR
            self.gameinst.UpdatePanelStandard()
            print("Setting player 2 colour to:" + str(COLOR))
        elif option == 15:   #screen resolution option
            value = self.optionchildindex[self.selectedoptionid]
            vmode_str = vmodes_str[value]
            videomodetoapply = vmode_str.split('x')
            videomodetoapply[0], videomodetoapply[1] = int(videomodetoapply[0]), int(videomodetoapply[1])
            if pygame.display.mode_ok((videomodetoapply[0], videomodetoapply[1]), 0, bitsize):
                if SOUNDON: menuvalidatesound.play()
                print("Setting screen resolution to:" + vmode_str)
                self.gameinst.DISPLAY = SetDisplayMode(videomodetoapply[0], videomodetoapply[1])
                self.gameinst.DISPLAY.fill(BACKCOLOR)
                activemode = [videomodetoapply[0], videomodetoapply[1]]
                ResizeGfx()
                for menu in self.gameinst.menus:
                    menu.ResizeSurface()
                #redraw panel standard
                self.gameinst.UpdatePanelStandard()
            else:
                if SOUNDON: menuerrorsound.play()
                print("Video mode " + vmode_str + ' is unsupported.')
        elif option == 16:   #player names option
            index = self.optionchildindex[self.selectedoptionid]    #index 0 stores the text and 1 stores the empty string
            if index == 0:                                          #if the 1st position string is selected,
                if SOUNDON: menukeysound.play()
                self.optionchildindex[self.selectedoptionid] = 1    #select the empty string in the 2nd position of children strings (1)
                self.keyboardinputon = True
            else:
                if SOUNDON: menuvalidatesound.play()
                self.optionchildindex[self.selectedoptionid] = 0
                if self.optionchild[self.selectedoptionid][1] != '':
                    PLAYERNAMES[self.selectedoptionid] = self.optionchild[self.selectedoptionid][1]
                    self.optionchild[self.selectedoptionid][0] = self.optionchild[self.selectedoptionid][1]
                    self.optionchild[self.selectedoptionid][1] = ''
                    self.keyboardinputon = False
                self.gameinst.UpdatePanelStandard()
                
    def GetOptionDefaultValues(self, option):
        global fps, MAXSCORE, vmodes_str, activemode
        #takes the option fire id as an parameter and returns the list of default values for this option
        if option == 1:   #options menu
            #determine speed value
            speed = Fps2SpeedOption(fps)
            #determine MAXSCORE value
            if MAXSCORE == 300:
                score = 0
            elif MAXSCORE == 400:
                score = 1
            elif MAXSCORE == 500:
                score = 2
            elif MAXSCORE == 750:
                score = 3
            elif MAXSCORE == 1000:
                score = 4
            else:
                score = 2
            return (score, speed)
        elif option == 7:   #display options menu
            #create resolutions tuple
            resolutions = list(vmodes_str)
            #find active resolution
            for idx, mode in enumerate(resolutions):
                modestring = str(activemode[0]) + 'x' + str(activemode[1])
                if modestring == mode:
                    selectedid = idx
                    break
            resolutions.insert(0, 0)
            resolutions.append( selectedid )
            #create a children argument tuple of the following form(child id, 'COLOR_RECT' n times, selected option id)
            functuple = [0, 0]
            for j in range(2):
                functuple[j] = [j+1]
                for i in range(len(COLORSELECTIONLIST)):
                    functuple[j].insert(1, 'COLOR_RECT')
            #set up selections by finding the snake colors and matching with the color selection list
            for i, snake in enumerate(self.gameinst.snakes):
                for j, COLOR in enumerate(COLORSELECTIONLIST):
                    if snake.color == COLOR:
                        functuple[i].insert(len(functuple[i]), j)
            return (resolutions, functuple)
        elif option == 8:   #sound on option
            return SOUNDON
        elif option == 9:   #music option
            return MUSICON
        elif option == 10:   #max score option
            #just rerun this function passing the argument option = 1 and getting score value
            pass
        elif option == 11:   #game speed option
            #just rerun this function passing the argument option = 1 and getting speed value
            pass
        elif option == 12:   #boosters on option
            return BOOSTERSON
        elif option == 13:   #snake 1 colour option
            #just rerun this function passing the argument option = 7 and getting functuple[0][end] value
            pass
        elif option == 14:   #snake 2 colour option
            #just rerun this function passing the argument option = 7 and getting functuple[1][end] valu
            pass
        elif option == 15:   #screen resolution option
            #just rerun this function passing the argument option = 7 and getting resolutions[end] value
            pass

    def ResetOptionDefaultValues(self):
        #this function resets an option's selection to the one that is currently active after losing focus
        #first get option's fireid
        option = self.optionfireids[self.selectedoptionid]
        #here is a list of options that have a unique return value from GetOptionDefaultValues()
        uniquevalueoptions = (8, 9, 12)
        if option in uniquevalueoptions:
            self.optionchildindex[self.selectedoptionid] = self.GetOptionDefaultValues(option)
        elif option == 10:
            self.optionchildindex[self.selectedoptionid] = self.GetOptionDefaultValues(1)[0]
        elif option == 11:
            self.optionchildindex[self.selectedoptionid] = self.GetOptionDefaultValues(1)[1]
        elif option == 13:
            resolutions, functuple = self.GetOptionDefaultValues(7)
            value = functuple[0][-1]
            self.optionchildindex[self.selectedoptionid] = value
        elif option == 14:
            resolutions, functuple = self.GetOptionDefaultValues(7)
            value = functuple[1][-1]
            self.optionchildindex[self.selectedoptionid] = value
        elif option == 15:
            resolutions, functuple = self.GetOptionDefaultValues(7)
            value = resolutions[-1]
            self.optionchildindex[self.selectedoptionid] = value

    def ResizeSurface(self):
        self.surface = pygame.Surface((widthpx, heightpx))

    def InstructionMenu(self):
        #show title
        textsurfaceobj, textrectobj = getFontBlit(MENUTITLEFONT, MENUOPTIONTITLESIZE, self.title, INSTRUCTIONFONTCOLOR, widthpx//2, 100, center=True)
        self.surface.blit(textsurfaceobj, textrectobj)
        
        #show instructions text
        y = textrectobj.bottom + textrectobj.height//2
        text = "Controls: Snake 1 -> Arrow keys, Snake 2 -> WASD keys, P -> Pause game"
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 50, y, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "Each snake's goal is to reach " + str(MAXSCORE) + " points first. Snakes start with " + str(maxlives) + \
        " lives and lose one every"
        y = textrectobj.bottom + textrectobj.height
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 50, y, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "time they crash on the enemy or themselves. Lives are restored after " + str(LIFERESTORE) + \
        " seconds."
        y = textrectobj.bottom
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 50, y + pany, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "After crashing a snake becomes invulnerable and starts flashing for " + str(INVULNERABLEDUR) + " seconds."
        y = textrectobj.bottom + textrectobj.height
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 50, y, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "Points are gained by eating apples of the snake's own colour:"
        y = textrectobj.bottom + textrectobj.height
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 50, y, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "Good apple: +10 points"
        y = textrectobj.bottom
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 50, y, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "Bad apple: -10 points"
        y = textrectobj.bottom
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 50, y + pany, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "After a random amount of time a booster will appear:"
        y = textrectobj.bottom + textrectobj.height
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 50, y, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "Ultra boost: snakes can eat any apple"
        boostery = textrectobj.bottom + textrectobj.height
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 100, boostery, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "Triple boost: snakes get 3x the points for each apple"
        y = textrectobj.bottom + textrectobj.height
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 100, y + pany, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "Reverse boost: the controls for the enemy snake are reversed"
        y = textrectobj.bottom + textrectobj.height
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 100, y, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "Wall boost: walls are closed for the enemy snake"
        y = textrectobj.bottom + textrectobj.height
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 100, y, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "Snake Hunter boost: eats and claims enemy tails instead of crashing"
        y = textrectobj.bottom + textrectobj.height
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 100, y, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        text = "Freeze boost: completely freezes the enemy snake"
        y = textrectobj.bottom + textrectobj.height
        textsurfaceobj, textrectobj = getFontBlit(INSTRUCTIONFONT, INSTRUCTIONTEXTSIZE, text, INSTRUCTIONFONTCOLOR, 100, y, center=False)
        self.surface.blit(textsurfaceobj, textrectobj)
        
        self.gameinst.DISPLAY.blit(self.surface, (panx, pany))

        height = textrectobj.height
        y = boostery + height//2
        for i in range(boostertypes):
            self.gameinst.drawdiamond(75 + panx, y + pany, int(height*1.15//2), BOOSTERCOLOR[i])
            y += textrectobj.height*2
        
def StartGame():
    #set up Game instance
    DISPLAY.fill(BARCOLOR)
    game = Game(DISPLAY)
    pygame.event.post(pygame.event.Event(ACTIVEEVENT,{'gain': 1,'musicit': 1}))  #hack to start the music
    #set up Intro Menu
    game.drawborders()
    game.UpdateScores()
    game.menus.append(Menu(game, 'SNAKE HUNTER', ('Start Game', 0), ('Options', 1), ('Instructions', 2), ('Quit', 3)))
    game.pause()
    return game

def RestartGame(DISPLAY):
    #re-initialize game instance
    game.__init__(game.DISPLAY)
    #set up Resume Menu
    game.drawborders()
    game.UpdateScores()
    game.menus.append(Menu(game, 'SNAKE HUNTER', ('Resume Game', 0), ('Restart Game', 4), ('Options', 1), ('Instructions', 2), ('Quit', 3)))
    game.showmenu = False
    return game

#INITIALIZE RESOURCES
#init sounds
applegood = [pygame.mixer.Sound(r'sound\apple_eat1.wav'),
             pygame.mixer.Sound(r'sound\apple_eat2.wav'),
             pygame.mixer.Sound(r'sound\apple_eat3.wav'),
             pygame.mixer.Sound(r'sound\apple_eat4.wav')]
applebad = pygame.mixer.Sound(r'sound\applebad.wav')
endsound = pygame.mixer.Sound(r'sound\gameover.wav')
endsound.set_volume(0.3)
eatsound = pygame.mixer.Sound(r'sound\eat.wav')
menubacksound = pygame.mixer.Sound(r'sound\menu_back.wav')
menuselectsound = pygame.mixer.Sound(r'sound\menu_select.wav')
menuvalidatesound = pygame.mixer.Sound(r'sound\menu_validate.wav')
menuerrorsound = pygame.mixer.Sound(r'sound\menu_error.wav')
menuerrorsound.set_volume(0.3)
menukeysound = pygame.mixer.Sound(r'sound\menu_key.wav')
chattersound = pygame.mixer.Sound(r'sound\chatter.wav')
chattersound.set_volume(0.5)
boostsounds=[]
boostsounds.append( pygame.mixer.Sound(r'sound\ultraboost.wav') )
boostsounds.append( pygame.mixer.Sound(r'sound\tripleboost.wav') )
boostsounds.append( pygame.mixer.Sound(r'sound\reverseboost.wav') )
boostsounds.append( pygame.mixer.Sound(r'sound\wallboost.wav') )
boostsounds.append( pygame.mixer.Sound(r'sound\snakehunter.wav') )
boostsounds.append( pygame.mixer.Sound(r'sound\freezeboost.wav') )
#init music
try:
    pygame.mixer.music.load('sound\music.ogg')
    if MUSICON > 0:
        pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.4)
except pygame.error:
    print('Background music file music.ogg not found.')
gamemusic = pygame.mixer.Sound(r'sound\despacito.ogg')
gamemusic.set_volume(0.1)
backchannel = None

#set colors
BARCOLOR = pygame.Color(0, 0, 0 ,0)             #black bars
BACKCOLOR = pygame.Color(255, 255 ,255, 255)    #white background
BORDERCOLOR = pygame.Color(0, 0, 0 ,0)          #black border
FONTCOLOR = pygame.Color(20, 20, 50)               #black font
INSTRUCTIONFONTCOLOR = pygame.Color(0, 0, 0)
BOOSTERCOLOR=[]                                 #list of booster colors
BOOSTERCOLOR.append( pygame.Color(255, 30, 30) )    #ULTRA BOOST
BOOSTERCOLOR.append( pygame.Color(30, 130, 130) )   #TRIPLE BOOST
BOOSTERCOLOR.append( pygame.Color(255, 210, 50) )   #REVERSE BOOST
BOOSTERCOLOR.append( pygame.Color(200, 70, 165) )   #WALL BOOST
BOOSTERCOLOR.append( pygame.Color(128, 128, 64) )   #SNAKE HUNTER BOOST
BOOSTERCOLOR.append( pygame.Color(128, 255, 255) )  #FREEZE BOOST
COLORSELECTIONLIST=list()                       #list of colors for option selections
COLORSELECTIONLIST.append( pygame.Color(50, 50, 255) )
COLORSELECTIONLIST.append( pygame.Color(20, 180, 50) )
COLORSELECTIONLIST.append( pygame.Color(128, 0, 128) )
COLORSELECTIONLIST.append( pygame.Color(255, 80, 255) )
COLORSELECTIONLIST.append( pygame.Color(255, 128, 0) )
COLORSELECTIONLIST.append( pygame.Color(0, 180, 128) )
COLORSELECTIONLIST = tuple(COLORSELECTIONLIST)

def LoadGfx():
    #load images
    lifeimg = pygame.image.load(r'gfx\life.png').convert_alpha()
    butoverlayimg = pygame.image.load(r'gfx\buttonoverlay.png').convert_alpha()
    menubackimg = pygame.image.load(r'gfx\menuback.jpg').convert()
    menubackimg.set_alpha(210)
    gamebackimg = pygame.image.load(r'gfx\gameback.jpg').convert()
    tonganimimg = pygame.image.load(r'gfx\tong.png').convert_alpha()
    appleimg = pygame.image.load(r'gfx\apple.png').convert_alpha()
    mouseimg = pygame.image.load(r'gfx\mouse.png').convert_alpha()

    return lifeimg, butoverlayimg, menubackimg, gamebackimg, tonganimimg, appleimg, mouseimg

lifeimg, butoverlayimg, menubackimg, gamebackimg, tonganimimg, appleimg, mouseimg = LoadGfx()

#fonts
MENUTITLEFONT = r'font\SAMAN.TTF'
MENUOPTIONFONT = r'font\BROADW.TTF'
INSTRUCTIONFONT = r'font\Jura-Bold.ttf'
GAMEFONT = r'font\BROADW.TTF'

#video mode strings for options screen
CreateVideoModeStrings()

#menu keyboard input
ACCEPTEDKEYS = (K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_a, K_b, K_c, K_d, K_e, K_f, K_g, K_h, K_i, K_j, \
                K_k, K_l, K_m, K_n, K_o, K_p, K_q, K_r, K_s, K_t, K_u, K_v, K_w, K_x, K_y, K_z, K_UNDERSCORE, K_BACKSPACE)
#####################

ResizeGfx()
game = StartGame()

#set timer
clock = pygame.time.Clock()

desync = 0
menuframe = framesperstateupdate

#profiling
import cProfile
#cProfile.run('game.DISPLAY.fill(BACKCOLOR,(0,0,panx,activemode[1]))')

#game loop
while True:

    #handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            QuitGame()
        elif event.type == ACTIVEEVENT:
            if event.gain == 0:
                pygame.mixer.pause()
                pygame.mixer.music.pause()
            elif event.gain == 1 or event.musicit==1:
                if game.showmenu:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.unpause()
        #check if the reset button is clicked
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = pygame.mouse.get_pos()
            if game.ResetButton.collidepoint(x, y):
                game.resetpressed= True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            x, y = pygame.mouse.get_pos()
            if game.ResetButton.collidepoint(x, y):
                ResetPlayerScore()
            game.resetpressed= False
        #keyboard events
        elif event.type == KEYUP:
            #if currently showing menu, change active menu option
            if game.showmenu:
                game.getactivemenu().ChangeOption(event.key)
                continue
            #direction keys for actual game
            if event.key == K_LEFT and game.paused==False:
                if game.snakes[1].boosted and game.snakes[1].boostertype==2:
                    game.snakes[0].moveright()
                else:
                    game.snakes[0].moveleft()
            elif event.key == K_UP and game.paused==False:
                if game.snakes[1].boosted and game.snakes[1].boostertype==2:
                    game.snakes[0].movedown()
                else:
                    game.snakes[0].moveup()
            elif event.key == K_RIGHT and game.paused==False:
                if game.snakes[1].boosted and game.snakes[1].boostertype==2:
                    game.snakes[0].moveleft()
                else:
                    game.snakes[0].moveright()
            elif event.key == K_DOWN and game.paused==False:
                if game.snakes[1].boosted and game.snakes[1].boostertype==2:
                    game.snakes[0].moveup()
                else:
                    game.snakes[0].movedown()
            elif event.key == K_w and game.paused==False:
                if game.snakes[0].boosted and game.snakes[0].boostertype==2:
                    game.snakes[1].movedown()
                else:
                    game.snakes[1].moveup()
            elif event.key == K_d and game.paused==False:
                if game.snakes[0].boosted and game.snakes[0].boostertype==2:
                    game.snakes[1].moveleft()
                else:
                    game.snakes[1].moveright()
            elif event.key == K_a and game.paused==False:
                if game.snakes[0].boosted and game.snakes[0].boostertype==2:
                    game.snakes[1].moveright()
                else:
                    game.snakes[1].moveleft()
            elif event.key == K_s and game.paused==False:
                if game.snakes[0].boosted and game.snakes[0].boostertype==2:
                    game.snakes[1].moveup()
                else:
                    game.snakes[1].movedown()
            elif event.key == K_p and game.playerwon < 0:
                if game.paused:
                    game.unpause()
                else:
                    game.pause()
            elif event.key == K_ESCAPE:
                game.pause()
                game.showmenu = True
                menuframe = framesperstateupdate
                if MUSICON == 1:
                    pygame.mixer.music.play(-1)
                    pygame.mixer.pause()
            elif event.key == K_SPACE:
                if game.paused and game.playerwon >= 0:
                    if backchannel != None and MUSICON == 1:
                        backchannel.play(gamemusic, -1)
                    game = RestartGame(game.DISPLAY)

                    
    if game.paused != True:     #update game state only if game not paused
        #clear edges
        game.DISPLAY.fill(BACKCOLOR,(0,0,panx,activemode[1]))
        game.DISPLAY.fill(BACKCOLOR,(panx,0,widthpx,pany))
        game.DISPLAY.fill(BACKCOLOR,(panx,heightpx+pany,widthpx,pany))

        #this makes sure the game state updates and render updates are decoupled
        desync += 1
        interp = desync/framesperstateupdate
        
        if desync >= framesperstateupdate:
            #update game state only here
            #game.mouse.update()
            game.NextFrame()
            game.UpdateScores()
            desync = 0

        game.DrawAll(interp)
    elif game.showmenu == True:
        menuframe += 1
        if menuframe >= framesperstateupdate:
            #display any menus that exist
            game.getactivemenu().Show(game.DISPLAY)
            menuframe = 0
        game.pausetimers()
    else:
        game.pausetimers()

    #test current fps to game's standard
    real_fps = clock.get_fps()
    textsurfaceobj, textrectobj = getFontBlit(GAMEFONT, int(PLAYERSCORESIZE/2), '%8.2f fps ' % real_fps, FONTCOLOR, panx, pany)
    game.DISPLAY.blit(textsurfaceobj, textrectobj)
    if real_fps > 0:
        CheckFps(real_fps)
    
    #update display
    pygame.display.flip()
    
    #wait for next frame
    clock.tick(fps)
