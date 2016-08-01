## Term Project 15-112
## SETTLERS OF PLANET CATAN (3D Catan)
## Adaption of an existing board game called Settlers of Catan
## Developed By Sean D Kim
## CMU Class of 2018

from structClass import Struct
from Tkinter import *
import eventBasedAnimation
import random
import contextlib
import urllib
import string
import copy
import math

#########################################
########## GLOBAL CONSTANTS #############
#########################################

cWidth = 600
cHeight = 600

barRatio = 7
cardMargin = 10

maxDepth = -100 #do not draw if smaller than this value

tiles = ["BRICK", "ORE", "SHEEP", "WHEAT", "WOOD", "SEA"]
resources = ["brick", "ore", "sheep", "wheat", "wood"]
specials = ["invention", "knight", "monopoly", "vp"]

houseResources = ["brick", "sheep", "wheat", "wood"]
cityResources = ["ore", "ore", "ore", "wheat", "wheat"]
specialResources = ["ore", "sheep", "wheat"]

#########################################
################ COLORS #################
#########################################

#from 15-112 course note
def rgb(red, green, blue): 
    return "#%02x%02x%02x" % (red, green, blue)

#frm http://www.rapidtables.com/web/color/RGB_Color.htm

DarkGreen=rgb(0, 100, 0) #wood
Silver=rgb(192, 192, 192) #ore
LawnGreen=rgb(124, 252, 0) #sheep
DarkOrange=rgb(255, 140, 0) #brick
Gold=rgb(255, 215, 0) #wheat
Navy=rgb(0, 0, 128) #sea

DarkSlateGray = rgb(47, 79, 79)

backgroundColor = DarkSlateGray
borderColor = "brown"
buttonColor = "gray"

#player can choose the following color
DarkCyan = rgb(0,139,139)
MediumPurple = rgb(139,0,139)
DeepPink = rgb(255,20,147)
Olive = rgb(128,128,0)
DarkKhaki = rgb(189,183,107)
playerColors = [DarkCyan, MediumPurple, DeepPink, Olive, DarkKhaki]

#next two are from soltaire assignment, 15-112
#helper function to draw cards

#assign color to each tile/cards
def loadColor(kind):
    #resources
    if kind == "wood": color=DarkGreen
    elif kind == "ore": color=Silver
    elif kind == "sheep": color=LawnGreen
    elif kind == "brick": color=DarkOrange
    elif kind == "wheat": color=Gold
    elif kind == "sea": color=Navy
    
    #special cards
    else: color="white"
    return color

#from solitarie
def loadImage(name):
    filename = "images/%s.gif" % (name)
    return PhotoImage(file=filename)



#########################################
########## HELPER FUNCTION ##############
#########################################

#next 2 fn from 15-112 course note. for printing 2d lists
def maxItemLength(a):
    maxLen = 0
    rows = len(a)
    cols = len(a[0])
    for row in xrange(rows):
        for col in xrange(cols):
            maxLen = max(maxLen, len(str(a[row][col])))
    return maxLen

def print2dList(a):
    if (a == []):
        # So we don't crash accessing a[0]
        print []
        return
    rows = len(a)
    cols = len(a[0])
    fieldWidth = maxItemLength(a)
    print "[ ",
    for row in xrange(rows):
        if (row > 0): print "\n  ",
        print "[ ",
        for col in xrange(cols):
            if (col > 0): print ",",
            # The next 2 lines print a[row][col] with the given fieldWidth
            format = "%" + str(fieldWidth) + "s"
            print format % str(a[row][col]),
        print "]",
    print "]"

#next 4 fn from <http://www.cs.cmu.edu/~dga/somefunc.py>. for getting obj file
def readFile(filename, mode="rt"):       # rt = "read text"
    with open(filename, mode) as fin:
        return fin.read()

def writeFile(filename, contents, mode="wt"):    # wt = "write text"
    with open(filename, mode) as fout:
        fout.write(contents)

def readWebPage(url):
    assert(url.startswith("http://"))
    with contextlib.closing(urllib.urlopen(url)) as fin:
        return fin.read()

def getData(url):  
    with contextlib.closing(urllib.urlopen(url)) as fin:
        with open("tetrahedron.obj", "wt") as fout:
            for line in fin:
                fout.write(line)

#first, save this link as icosahedron.obj file
urlHedron = "http://people.sc.fsu.edu/~jburkardt/data/obj/icosahedron.obj"


#helper fn for readobj. line is a list of strings
def replaceSpace(line):
    for i in xrange(len(line)):
        if line[i]==" ": 
            if line[i+1] == " ":
                line[i] = 42

#converts obj file to list of nodes and list of faces
#stretch = multiply all the vertices by constant (for board)
def readObj(filename, stretch=1, mode="rt"): 
    with open(filename, mode) as fin:
        nodes = []
        faces = []
        for line in fin.read().splitlines():
            if line.startswith("v "):
                new = line.split()[1:]
                for i in xrange(len(new)):
                    new[i] = int(stretch*float(new[i]))
                nodes.append(new)

            if line.startswith("f "):
                new = line.split()[1:]
                for i in xrange(len(new)):
                    new[i] = int(new[i])-1 #index should start at 0
                faces.append(new)

        return nodes, faces


def swap(a, i, j):
    (a[i], a[j]) = (a[j], a[i])

#sort faces according to lowest depth => back side doens't show
#modification of a bubble sort from 15-112 course note. 
def sortDepth(faces, nodes):
    n = len(faces)
    end = n
    swapped = True
    while (swapped == True):
        swapped = False
        for i in xrange(1, end):

            sumZs1, sumZs2 = 0, 0

            for pt in faces[i-1]:
                if type(pt)==int: 
                    sumZs1 += nodes[pt][2]

            for pt in faces[i]:
                if type(pt)==int: 
                    sumZs2 += nodes[pt][2]

            if sumZs1 > sumZs2:
                swap(faces, i-1, i)
                swapped = True

        end -= 1    


#next two are helper fn for checking if vertex is clicked
def distance(x0, y0, x1, y1):
    return ((x0-x1)**2+(y0-y1)**2)**0.5

def clicked(checkX, checkY, eventX, eventY):
    return distance(checkX, checkY, eventX, eventY) < 20 #constant

#helper fn for drawing circle around rolled number
def circle(canvas, cx, cy, r, color="white"):
    x0, y0 = cx-r, cy-r
    x1, y1 = cx+r, cy+r
    canvas.create_oval(x0, y0, x1, y1, fill=color)

#########################################
########### HELPER CLASSES ##############
#########################################

#image searched from google 
# <http://ruhumunmasali.blogspot.com/2013_10_25_archive.html>
class Space(object):
    def __init__(self):
        self.im = PhotoImage(file="Images/space.gif")

    def draw(self, canvas):
        # cropped = im.crop((0, 0, cWidth, cHeight))
        # tk_im = ImageTk.PhotoImage(im)
        #canvas.create_rectangle(0, 0, cWidth, cHeight, fill="black")
        canvas.create_image(cWidth/2, cHeight/2, image=self.im)

#image searched from google
# <http://wallpaperswa.com/Abstract/Textures/
# minimalistic_patterns_textures_classy_1920x1080_wallpaper_16295>
class Bar(object):
    def __init__(self):
        self.cWidth, self.cHeight = cWidth, cHeight

        self.width = cWidth
        self.height = cHeight/barRatio #constant

        self.im = PhotoImage(file="Images/tile.gif")

    def draw(self, canvas):
        canvas.create_image(0, self.cHeight-self.height, anchor=NW, image=self.im)

class Button(object):
    def __init__(self, name, x, y, width, height, color=buttonColor):
        self.name = name
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.selected = False
        self.color = color

    def clicked(self, event, selectNeeded=False):
        if self.x < event.x < self.x+self.width:
            if self.y < event.y < self.y+self.height:
                if selectNeeded == True:
                    if self.selected == False: self.selected = True
                    elif self.selected == True: self.selected = False
                return self.name
        return False

    def draw(self, canvas):
        canvas.create_rectangle(self.x, self.y, 
            self.x+self.width, self.y+self.height, fill=self.color, 
            outline=borderColor, width=2)
        
        #gray background turns to red if selected:
        if self.selected == True:
            canvas.create_rectangle(self.x, self.y, self.x+self.width, 
                self.y+self.height, outline="white", width=4)

        canvas.create_text(self.x+self.width/2, self.y+self.height/2, 
            text=self.name)

#########################################
############ EXTRA WINDOWS ##############
#########################################

#top left window for manuevering through game
class Navigation(object):
    def __init__(self, mode):
        self.mode = mode

        #for drawing
        self.nX = cardMargin*2
        self.nY = cardMargin*2
        self.nWidth = cWidth/4
        self.nHeight = cHeight/barRatio

        #for buttons
        self.bX = self.nX+cardMargin
        self.bY = self.nY+cardMargin
        self.bWidth = (self.nWidth-3*cardMargin)/2
        self.bHeight = (self.nHeight-3*cardMargin)/2
        
    def update(self):

        #tenth digit = button number, unit=0 is start, 1 is end
        (x10, y10) = (self.bX, self.nY+cardMargin)
        (x20, y20) = (self.bX, self.bY+self.bHeight+cardMargin)
        (x30, y30) = (self.bX+self.bWidth+cardMargin, self.bY)
        (x40, y40) = (self.bX+self.bWidth+cardMargin, 
            self.bY+self.bHeight+cardMargin)

        if GAME.mode == "Your Turn" or GAME.mode[-6:] == "Rolled":
            rl = Button("Roll", x10, y10, self.bWidth, self.bHeight)
            bd = Button("Build", x20, y20, self.bWidth, self.bHeight)
            td = Button("Trade", x30, y30, self.bWidth, self.bHeight)
            bk = Button("End", x40, y40, self.bWidth, self.bHeight)

            self.buttons = [rl, bd, td, bk]

        elif GAME.mode == "Build":
            hs = Button("House", x10, y10, self.bWidth, self.bHeight)
            ct = Button("City", x20, y20, self.bWidth, self.bHeight)
            dc = Button("Special", x30, y30, self.bWidth, self.bHeight)
            cc = Button("Cancel", x40, y40, self.bWidth, self.bHeight)

            self.buttons = [hs, ct, dc, cc]

    def draw(self, canvas):
        x,y = self.nX, self.nY
        width, height = self.nWidth, self.nHeight
        #display player's color on background
        color = GAME.turn.color
        canvas.create_rectangle(x, y, x+width, y+height, 
            fill=color, outline=borderColor, width=1)
        
        for button in self.buttons:
            button.draw(canvas)

#window that displays players' info
class Widget(object):
    def __init__(self):
        #for drawing
        self.wWidth = cWidth/3.7
        self.wHeight = cHeight/barRatio
        self.wX = cWidth-self.wWidth-cardMargin
        self.wY = cardMargin * 2

    def drawInfo(self, canvas, player, x, y):
        yGap = self.wHeight/6
        textColor = "white"
        canvas.create_text(x, y+yGap, text="%s" %player.name, 
            fill=textColor, anchor=W)
        canvas.create_text(x, y+yGap*2, text="Points: %d" %player.points, 
            fill=textColor, anchor=W)
        canvas.create_text(x, y+yGap*3, text="Cards: %d" %len(player.resources), 
            fill=textColor, anchor=W)
        canvas.create_text(x, y+yGap*4, 
            text="Specials: %d" %len(player.specials), fill=textColor, anchor=W)
        canvas.create_text(x, y+yGap*5, text="Knights: %d" %player.knightsUsed, 
            fill=textColor, anchor=W)

    def draw(self, canvas):
        width, height = self.wWidth/2, self.wHeight
        x0 ,y0 = self.wX, self.wY
        x1, y1 = x0+width, y0
        canvas.create_rectangle(x0, y0, x0+width, y0+height, 
            fill=GAME.player.color)
        canvas.create_rectangle(x1, y1, x1+width, y1+height, 
            fill=GAME.computer.color)

        #displaying players info: 
        #name, victory points, numCards, numSpecials, numKnights
        self.drawInfo(canvas, GAME.player, x0+cardMargin/2, y0)
        self.drawInfo(canvas, GAME.computer, x1+cardMargin/2, y1)

#for special execution, trading & monopoly, invention
class SubWindow(object):
    def __init__(self, mode):
        self.mode = mode

        #determine windowwidth&height
        self.sWidth = cWidth/1.8
        self.sHeight = cHeight/8

        self.cx = cWidth/2
        self.cy = cHeight/2
        #for coordinates of background rectangle
        self.x0 = self.cx - self.sWidth/2
        self.x1 = self.cx + self.sWidth/2
        self.y0 = self.cy - self.sHeight/2
        self.y1 = self.cy + self.sHeight/2

        self.generateButtons(mode)

    def generateButtons(self, mode):
        self.buttons = [] #resources
        self.mainButtons = [] #confirm/cancel

        #buttons = resources
        numButtons = len(resources)

        #height&width of a button
        bWidth = (self.sWidth-cardMargin*(numButtons+1))/numButtons
        bHeight = (self.sHeight-cardMargin*3.5)/2

        for i in xrange(numButtons):
            resource = resources[i]

            bx0 = self.x0+cardMargin+(cardMargin+bWidth)*i
            by0 = self.y0+cardMargin

            self.buttons.append(Button(resource, bx0, by0, bWidth, bHeight))

        mainButtons = ["Confirm", "Cancel"]
        for i in xrange(len(mainButtons)):
            button = mainButtons[-1-i]
            bx0 = self.x1 - (cardMargin+bWidth)*(i+1)
            by0 = self.y1 - cardMargin - bHeight

            self.mainButtons.append(Button(button, bx0, by0, bWidth, bHeight))

    def unselectAll(self):
        for button in self.buttons:
            button.selected = False

    #activate monopoly and invention
    def power(self, player, special, listSelected):
        if special == "monopoly":
            #take away computer's card
            #get those cards
            #get rid of monopoly card
            #get rid of subWindow
            selected = listSelected[0] #should be only 1

            if player == GAME.player: other = GAME.computer
            elif player == GAME.computer: other = GAME.player

            for card in GAME.computer.resources:
                if selected == card.kind:
                    other.use([selected])
                    player.get(Card(selected))
        
        elif special == "invention":
            for selected in listSelected:
                player.get(Card(selected))

        player.use([special], mode="specials")

    def draw(self, canvas):
        if self.mode == "trade": title = "Trade With Bank"
        elif self.mode == "invention": title = "Invention"
        elif self.mode == "monopoly": title = "Special: Monopoly"

        x0 = self.x0
        x1 = self.x1
        y0 = self.y0
        y1 = self.y1

        color = backgroundColor #dark slate gray
        canvas.create_rectangle(x0, y0, x1, y1, fill=color)

        #title
        tx0 = self.cx - self.sWidth/4
        tx1 = self.cx + self.sWidth/4
        ty0 = y0 - self.sWidth/10
        ty1 = y0 - cardMargin
        canvas.create_rectangle(tx0, ty0, tx1, ty1, fill=color)
        canvas.create_text((tx0+tx1)/2, (ty0+ty1)/2, 
            text=title, fill="white")

        #different buttons
        for button in self.buttons:
            button.draw(canvas)

        for button in self.mainButtons:
            button.draw(canvas)

#allows trading options
class TradeWindow(SubWindow):
    #wanted=button pressed in subwindow; listSelected=from player's hand
    #wanted and listSelected is all list
    def trade(self, player, wanted, listSelected):
        player.use(listSelected)
        player.get(Card(wanted[0]))


class HelpWindow(SubWindow):
    def __init__(self):
        self.cx = cWidth/2
        self.cy = cHeight/2

        self.wWidth = cWidth/1.4
        self.wHeight = cHeight/1.7
        #for coordinates of background rectangle
        self.x0 = self.cx - self.wWidth/2
        self.x1 = self.cx + self.wWidth/2
        self.y0 = self.cy - self.wHeight/2
        self.y1 = self.cy + self.wHeight/2

        #exit button
        bWidth = self.wWidth/5
        bHeight = self.wHeight/10

        bx0 = self.x1 - cardMargin - bWidth
        by0 = self.y1 - cardMargin - bHeight

        self.exit = Button("Exit", bx0, by0, bWidth, bHeight)

    def draw(self, canvas):
        x0 = self.x0
        x1 = self.x1
        y0 = self.y0
        y1 = self.y1

        canvas.create_rectangle(x0, y0, x1, y1, fill=backgroundColor,
            outline=borderColor, width=2)

        self.exit.draw(canvas)

        helpText = """
<Help Text>
Objective: Get 10 Points before Computer

Resource Overview
- House (Triangle): Wood, Brick, Sheep, Wheat (1 Point)
- City (Square): Ore, Ore, Ore, Wheat, Wheat (2 Points)
- Special Cards: Ore, Sheep, Wheat (? Points)

All the rules are adapted from original Settlers of Catan 
EXCEPT...
- Less vertices on board => only two players at a game
- No Roads: house/city can be build anywhere
- Alien: When 7 is rolled, randomly blocks one tile; no stealing
- Knight: knight removes any alien on the board; no stealing
- No Trading Ports: All resources are traded 4:1 ratio with bank

To access the complete guide to the original Settlers of Catan,
go to <www.catan.com/service/game-rules>

"""
        canvas.create_text(x0+cardMargin, y0-cardMargin, anchor=NW, 
            text=helpText, fill="white")

#before game
class StartWindow(object):
    def __init__(self):
        self.cx = cWidth/2
        self.cy = cHeight/2

        self.wWidth = cWidth/1.5
        self.wHeight = cHeight/2.5

        #for drawing & placement of buttons
        self.x0 = self.cx - self.wWidth/2
        self.y0 = self.cy - self.wHeight/2
        self.x1 = self.cx + self.wWidth/2
        self.y1 = self.cy + self.wHeight/2
 
        self.generateButtons() #colors & start buttons

    #allow players to select colors
    def generateButtons(self):
        self.buttons = []

        #buttons = player colors defined at the top; copied below
        colors = playerColors
        colorNames = ["Cyan", "Purple", "Pink", "Olive", "Khaki"]
        numButtons = len(colors)

        #height&width of a button
        bWidth = (self.wWidth-cardMargin*(numButtons+1))/numButtons
        bHeight = cardMargin*2

        #generate start button
        bx0 = self.x1 - cardMargin - bWidth
        by0 = self.y1 - cardMargin - bHeight
        self.start = Button("Start", bx0, by0, bWidth, bHeight)

        for i in xrange(numButtons):
            name = colorNames[i]
            color = playerColors[i]

            bx0 = self.x0+cardMargin+(cardMargin+bWidth)*i
            by0 = self.cy+self.wHeight/5

            self.buttons.append(Button(name, bx0, by0, bWidth, bHeight, color))

    def draw(self, canvas):
        canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, 
            fill=backgroundColor, outline=borderColor)

        title="Settlers of Planet Catan"
        subtitle="-3D Catan-"
        subtext="Please select a color"
        canvas.create_text(self.cx, (self.y0+self.cy)/2, anchor=S, fill="white",
            text=title, font="Times 35 bold")
        canvas.create_text(self.cx, (self.y0+self.cy)/1.9, anchor=N, fill="white",
            text=subtitle, font="Times 25 bold")
        canvas.create_text(self.cx, self.cy+self.wHeight/11, fill="white", text=subtext, 
            font="Times 15")

        self.start.draw(canvas)

        for button in self.buttons:
            button.draw(canvas)

#after game
class EndWindow(object):
    def __init__(self, winner):
        self.cx = cWidth/2
        self.cy = cHeight/2

        self.wWidth = cWidth/2
        self.wHeight = cHeight/4

        self.winner = winner

    def draw(self, canvas):
        x0 = self.cx - self.wWidth/2
        x1 = self.cx + self.wWidth/2
        y0 = self.cy - self.wHeight/2
        y1 = self.cy + self.wHeight/2
        canvas.create_rectangle(x0, y0, x1, y1, fill=backgroundColor, 
            outline=borderColor, width=5)
        text1 = "= GAMEOVER ="
        text2 = "THE WINNER IS.." 
        text3 = self.winner.name + "!!!"

        textColor = rgb(220,220,220)

        canvas.create_text(self.cx, (self.cy+y0)/2, text=text1, 
            font="Arial 25 bold", fill=textColor)
        canvas.create_text(self.cx, self.cy, text=text2, 
            font="Arial 20 bold", fill=textColor)
        canvas.create_text(self.cx, (self.cy+y1)/2, text=text3, 
            font="Arial 35 bold", fill=textColor)


#########################################
############### ON BOARD ################
#########################################

class Board(object):
    def __init__(self, cx, cy, filename):
        self.cx, self.cy = cx, cy
        self.nodes, self.faces = readObj(filename, 10)

        self.generateTiles()
        self.assignTiles()
        self.assignNum()

        self.dtheta = 0
        self.dphi = 0
        self.t = 0.1

        sortDepth(self.faces, self.nodes)

        #image from <http://www.animatedimages.org/cat-ufo-34.htm>
        self.alienImage = PhotoImage(file="Images/alien.gif")

    def generateTiles(self):
        tiles = []
        for i in xrange(3):
            tiles.append("wood")
            tiles.append("wheat")
            tiles.append("ore")
            tiles.append("brick")
            tiles.append("sheep")
        for i in xrange(5):
            tiles.append("sea")
        random.shuffle(tiles)
        self.tiles = tiles

    #assign a tile to each face
    def assignTiles(self):
        for i in xrange(len(self.faces)):
            line = self.faces[i]
            line.append(self.tiles[i])

    def assignNum(self):
        nums = range(2, 13)
        nums += [5,6,8,9]
        random.shuffle(nums)

        for i in xrange(len(self.faces)):
            line = self.faces[i]
            if line[3] != "sea": 
                pop = nums.pop()
                line.append(str(pop))
            else: 
                line.append("None")

            line.append(False) #rolled truth value
            line.append(False) #alien truth value
 
    #increase x,y,z coordinates 
    def zoom(self, dratio):
        for nodeIndex in xrange(len(GAME.board.nodes)):
            node = GAME.board.nodes[nodeIndex]
            for i in xrange(len(node)):
                newCoordinate = node[i]*(1+dratio)
                GAME.board.nodes[nodeIndex][i] = newCoordinate


    #formula extracted from 
    #<http://www.petercollingridge.appspot.com/3D-tutorial/generating-objects>
    def rotateX(self, dtheta):
        for i in xrange(len(self.nodes)):
            node = self.nodes[i]
            x = node[0]
            z = node[2]
            self.nodes[i][0] = x*math.cos(dtheta) + z*math.sin(dtheta)
            self.nodes[i][2] = z*math.cos(dtheta) - x*math.sin(dtheta)

        sortDepth(self.faces, self.nodes)

    def rotateY(self, dphi):
        for i in xrange(len(self.nodes)):
            node = self.nodes[i]
            x = node[0]
            y = node[1]
            z = node[2]
            self.nodes[i][2] = z*math.cos(dphi) + y*math.sin(dphi)
            self.nodes[i][1] = y*math.cos(dphi) - z*math.sin(dphi)        

        sortDepth(self.faces, self.nodes)

    #for displaying number in the middle
    def midpt(self, v0, v1, v2):
        x0, y0, z0 = v0
        x1, y1, z1 = v1
        x2, y2, z2 = v2

        midx = (x0+x1)/2
        midy = (y0+y1)/2
        midz = (z0+z1)/2

        vx = x2 - midx
        vy = y2 - midy
        vz = z2 - midz

        MIDx = midx + vx/3
        MIDy = midy + vy/3
        MIDz = midz + vz/3

        return MIDx, MIDy, MIDz

    #return what node is clicked (its index)
    def checkNodes(self, event, cx, cy):
        for line in self.faces:
            nodeIndexes = line[0:3]
            for nodeIndex in nodeIndexes:
                coordinates = self.nodes[nodeIndex]
                x = coordinates[0]
                y = coordinates[1]
                z = coordinates[2]

                if z > maxDepth: 
                    if clicked(cx+x, cy+y, event.x, event.y):
                        return nodeIndex
        return None

    #for dice roll
    def checkNum(self, roll):
        for line in self.faces:
            if line[4] != "None" and roll == int(line[4]):
                line[5] = True

    def resetNum(self):
        for line in self.faces:
            line[5] = False

    def draw(self, canvas):
        cx, cy = self.cx, self.cy

        for line in self.faces:
            i0, i1, i2, tile, num, rolled, alien = line
            x0, y0, z0 = self.nodes[i0]
            x1, y1, z1 = self.nodes[i1]
            x2, y2, z2 = self.nodes[i2]

            canvas.create_polygon(cx+x0, cy+y0, cx+x1, cy+y1, 
                cx+x2, cy+y2, fill=loadColor(tile), outline="black")

            #displaying number and circle if rolled
            x, y, z = self.midpt(self.nodes[i0], self.nodes[i1], self.nodes[i2])

            #displaying roll number & circle if rolled
            if num != "None":
                if rolled == True: 
                    circle(canvas, cx+x, cy+y, 35)
                
                canvas.create_text(cx+x, cy+y, text=num, 
                    font="Arial 30", fill="black", anchor=S)

            #displaying tile type
            color="black"
            if tile == "sea": color="white"
            canvas.create_text(cx+x, cy+y, text=tile, 
                anchor=N, font="Arial 12 bold", fill=color)

            #drawing alien
            if alien == True:
                canvas.create_image(cx+x, cy+y, image=self.alienImage)


class Dice(object):
    def __init__(self, cx, cy):
        self.cx, self.cy = cx, cy
        self.r = 20
        self.result1 = "?"
        self.result2 = "?"

    #reset rolled in board, roll dice, then check land
    def roll(self):
        self.result1 = random.randint(1,6)
        self.result2 = random.randint(1,6)
        roll = self.result1 + self.result2
        return roll

    def draw(self, canvas): 
        x0, x1 = self.cx - self.r, self.cx + self.r
        y0, y1 = self.cy - self.r, self.cy + self.r

        canvas.create_rectangle(x0, y0, x1, y1, fill="red")
        canvas.create_text(self.cx, self.cy, 
            text=str(self.result1), fill="yellow")

        x0, x1 = self.cx + self.r, self.cx + self.r*3
        canvas.create_rectangle(x0, y0, x1, y1, fill="yellow")
        canvas.create_text(self.cx + self.r*2, self.cy, 
            text=str(self.result2), fill="red")


class House(object):
    def __init__(self, color, nodeIndex):
        self.index = nodeIndex
        self.r = 15
        self.color = color

    #represent house as a triangle
    #cx and cy are where houses are at
    def draw(self, canvas):
        node = GAME.board.nodes[self.index]

        cx = cWidth/2 + node[0]
        cy = cHeight/2 + node[1]
        cz = node[2]

        #TRIANGLE
        x0, y0 = cx, cy-self.r
        x1, y1 = cx + self.r*math.sqrt(3)/2, cy + self.r/2
        x2, y2 = cx - self.r*math.sqrt(3)/2, cy + self.r/2

        if cz > maxDepth: 
            canvas.create_polygon(x0, y0, x1, y1, x2, y2, fill=self.color)

class City(House):
    #for now, represent house as a triangle
    def draw(self, canvas):
        #canvas.create_rectangle(0, 0, 600, 600, fill="red")
        node = GAME.board.nodes[self.index]

        r = self.r*2/3
        cx = cWidth/2 + node[0]
        cy = cHeight/2 + node[1]
        cz = node[2]

        x0, y0 = cx-r, cy-r
        x1, y1 = cx+r, cy+r

        if cz > maxDepth: 
            canvas.create_rectangle(x0, y0, x1, y1, fill=self.color)

class Card(object):
    def __init__(self, kind):
        self.kind = kind
        self.color = loadColor(kind)

        self.height = cHeight/barRatio - 2*cardMargin
        self.width = self.height/1.7

        self.selected = False

    def __repr__(self): return self.kind

    def __eq__(self, other): 
        if type(other)==str: return str(self) == other
        else: return str(self) == str(other)

    def clickWithSelection(self, event, x, y):
        if x < event.x < x+self.width:
            if y < event.y < y+self.height:
                if self.selected == False: self.selected = True
                elif self.selected == True: self.selected = False
                return True
        return False

    def clicked(self, event, x, y):
        if x < event.x < x+self.width:
            if y < event.y < y+self.height:
                return True
        return False

    def draw(self, canvas, x, y):
        
        canvas.create_rectangle(x, y, 
            x+self.width, y+self.height, fill=self.color)

        if self.selected == True:
            canvas.create_rectangle(x, y, 
                x+self.width, y+self.height, outline="red", width=3)

        canvas.create_text(x+self.width/2, y+self.height/2, 
            text=self.kind, fill="black", font="Arial 9")

class Special(Card):
    def activate(self, player):
        if self.kind == "knight":
            for face in GAME.board.faces:
                face[6] = False
            player.knightsUsed += 1
        elif self.kind == "invention":
            pass #get two free resources
        elif self.kind == "monopoly":
            pass #steal resources


#########################################
############### PLAYERS #################
#########################################

class Player(object):
    def __init__(self, name, color):
        self.name = name

        self.cWidth = cWidth
        self.cHeight = cHeight

        self.points=0
        self.resources=[]
        self.specials=[]
        self.color=color
        self.tradePorts=[]

        self.houses = []
        self.cities = []
        self.knightsUsed = 0

        self.cardW = 30 #constant
        self.cardH = 60 #constant

    def printResources(self): 
        a = []
        for card in self.resources:
            a.append(card.kind)
        print a

    def getHouse(self, house):
        self.houses.append(house)

    def getCity(self, city):
        self.cities.append(city)

    def checkLand(self):
        faces = GAME.board.faces
        for house in self.houses:
            i = house.index

            for face in faces:
                if i in face[0:3]:
                    if face[5]:
                        self.get(Card(face[3]))

        for city in self.cities:
            i = city.index

            for face in faces:
                if i in face[0:3]:
                    if face[5]:
                        self.get(Card(face[3]))
                        self.get(Card(face[3]))

    #when a house is upgraded to a city
    def removeHouse(self, deleteIndex):
        copyHouses = []
        for house in self.houses:
            copyHouses.append(house.index)

        index = copyHouses.index(deleteIndex)
        self.houses.pop(index)

    #modification of selection sort
    def sortCards(self, player):
        resources = player.resources
        n = len(resources)
        for startI in xrange(n):
            minI = startI
            for i in xrange(startI, n):
                if (resources[i].kind < resources[minI].kind):
                    minI = i
            swap(player.resources, startI, minI)

    #card is a class Card
    def get(self, card):
        if card.kind in resources:
            numCards = len(self.resources)
            self.resources.append(card)

        elif card.kind in specials:
            self.specials.append(card)

    def check(self, listOfCards):
        #convert list of Card class to string list
        copyHand = []
        for card in self.resources:
            copyHand.append(card.kind)

        for card in listOfCards:
            if card in copyHand:
                copyHand.remove(card)
            else: return False
        return True

    def use(self, listOfCard, mode="resources"):
        if mode == "resources":
            #convert list of Card class to string list
            copyHand = []
            for card in self.resources:
                copyHand.append(card.kind)

            for card in listOfCard:
                if card in copyHand:
                    copyHand.remove(card)
                else: return False

            #update player's hand
            self.resources = []
            for strCard in copyHand:
                self.get(Card(strCard))

        elif mode == "specials":
            #remove just one special if clicked
            for i in xrange(len(self.specials)):
                special =  self.specials[i]
                if special.kind == listOfCard[0]:
                    self.specials.remove(special)
                    return True

        return True

    #during trade, select the resources in the bar if clicked
    def selectResources(self, event, mode="resource"):
        if mode == "resource":
            for i in xrange(len(self.resources)):      
                card = self.resources[i]
                x = cardMargin + (cardMargin+card.width)*i
                y = (cHeight-cHeight/barRatio)+cardMargin

                card.clickWithSelection(event, x, y)


    #returns a card clicked, None if nothing is clicked
    def checkClicked(self, event, mode="resource"):
        if mode == "special":
            for i in xrange(len(self.specials)):
                special = self.specials[-i]
                x = cWidth - cardMargin - (special.width + cardMargin)*(i+1)
                y = (cHeight-cHeight/barRatio)+cardMargin
                
                if special.clicked(event, x, y):
                    return special


    def updatePoints(self, other):
        self.points = 0
        for house in self.houses:
            self.points += 1

        for city in self.cities:
            self.points += 2

        for special in self.specials:
            if special.kind == "vp": 
                self.points += 1

        #two points for having largest army
        if self.knightsUsed >= 3:
            if self.knightsUsed >= other.knightsUsed:
                self.points += 2


    def draw(self, canvas):
        for house in self.houses:
            house.draw(canvas)
        for city in self.cities:
            city.draw(canvas)

        #draw cards for non-computer player
        if self.name != "Computer":
            for i in xrange(len(self.resources)):      
                card = self.resources[i]
                x = cardMargin + (cardMargin+card.width)*i
                y = (cHeight-cHeight/barRatio)+cardMargin
                card.draw(canvas, x, y)

            for i in xrange(len(self.specials)):
                card = self.specials[-i]
                x = cWidth - cardMargin - (card.width + cardMargin)*(i+1)
                y = (cHeight-cHeight/barRatio)+cardMargin
                card.draw(canvas, x, y)

class Computer(Player):
    #returns a probability of a roll
    def prob(self, roll):
        if roll == None or roll == "None": return 0
        roll = int(roll)
        if roll == 2: return 0.03
        elif roll == 3: return 0.06
        elif roll == 4: return 0.08
        elif roll == 5: return 0.11
        elif roll == 6: return 0.14
        elif roll == 7: return 0.17
        elif roll == 8: return 0.14
        elif roll == 9: return 0.11
        elif roll == 10: return 0.08
        elif roll == 11: return 0.06
        elif roll == 12: return 0.03

    #returns the neighboring tile & roll
    def nodeInfo(self, nodeIndex):
        tiles = []
        rolls = []

        for face in GAME.board.faces: 
            if nodeIndex in face[0:3]:
                rolls.append(face[4]) 
                tiles.append(face[5])

        return tiles, rolls

    #returns highest rolls probability
    def nodeValue(self, nodeIndex):
        tiles, rolls = self.nodeInfo(nodeIndex)
        rollProb = 0
        for roll in rolls:
            rollProb += self.prob(roll)
        return rollProb

    #returns the expected value of neighboring rolls
    def bestHouseNode(self, neededTile=None):
        bestNodeIndex = 100
        maxProb = 0

        for i in xrange(len(GAME.board.nodes)):
            #make sure nothing is built
            prob = 0
            if GAME.nodesStatus[i][0] == False:
                # node = GAME.board.nodes[i]
                prob = self.nodeValue(i)

            if prob > maxProb:
                bestNodeIndex = i
                maxProb = prob

        return bestNodeIndex

    def bestCityNode(self):
        bestNodeIndex = 100
        maxProb = 0

        for i in xrange(len(GAME.board.nodes)):
            #make sure nothing is built
            prob = 0
            if GAME.nodesStatus[i] == ["house", "Computer"]:
                # node = GAME.board.nodes[i]
                prob = self.nodeValue(i)

            if prob > maxProb:
                bestNodeIndex = i
                maxProb = prob

        return bestNodeIndex

    def alienNearby(self):
        for house in self.houses:
            i = house.index
            for face in GAME.board.faces:
                #if a face contains a node
                if i in face[0:3]: 
                    #if alien if present ON LAND
                    if face[3] != "sea" and face[6] == True:
                        return True

        for city in self.cities:
            i = city.index
            for face in GAME.board.faces:
                #if a face contains a node
                if i in face[0:3]: 
                    #if alien if present ON LAND
                    if face[3] != "sea" and face[6] == True:
                        return True

    #check if computer has same four cards. Return list of 4 cards in str
    def canTrade(self):
        for resource in resources:
            count = 0 
            for card in self.resources:
                if resource == card.kind:
                    count += 1
            if count >= 4: 
                return [resource]*4
        return None

    def getNeededCard(self):
        for resource in resources:
            for card in self.resources:
                obtained = False
                if resources == card.kind:
                    obtained = True
            if obtained == False:
                self.get(Card(resource))
                return True
        return None

    #returns either house/city/specials
    def options(self): 
        options = []
        copyHand = []
        for card in self.resources:
            copyHand.append(card.kind)

        houseValid = True
        for resource in houseResources:
            if resource in copyHand: pass
            else: houseValid = False
                
        if houseValid: options.append("house")

        #if house is available for upgrade
        cityValid = (self.houses!=[])
        for resource in cityResources: 
            if resource in copyHand: pass
            else: cityValid = False
        
        if cityValid: options.append("city")

        specialValid = True
        for resource in specialResources:
            if resource in copyHand: pass
            else: specialValid = False
        if specialValid: options.append("special")

        return options

    #delay computer's movement (either short/medium/long)
    def delay(self, mode="medium"):
        if mode == "short": num = int(10**7.5)
        elif mode == "medium": num = 10**8
        elif mode == "long": num = int(10**8.2)
        for x in xrange(num): pass


#########################################
########### GRAND FUNCTION ##############
#########################################
class Catan(eventBasedAnimation.Animation):
    def onInit(self):
        self.windowTitle = "Settlers of Planet Catan (3D Catan)"
        self.aboutText = "15-112 Term Project \n\
        Settlers of Planet Catan \n\
        Based on a existing board game \n\
        Developed by Sean D. Kim \n\
        CMU Class of 2018"
        
        self.startWindow = StartWindow()
        self.playerColors = playerColors
        self.gameStatus = "Start" #Start/ Set-up / Playing / End

        #these are for displaying message on top
        self.exception = False #exception to not updating navigation
        self.sweepMessage = None #message that appears when mouse if over
        self.sweepAllow = True #allowing mouse-sweep message

        self.cx = self.width/2
        self.cy = self.height/2

        self.space = Space()
        self.playerColor = rgb(0, 139, 139)

        self.bar = Bar()
        self.dice = Dice(cardMargin*5, cHeight/4)
        self.roll = None
        self.specialDeck = []
        self.generateSpecialDeck()

    def startWindowOnMouse(self, event):
        #select one color; unselect if another color is selected
        for button in self.startWindow.buttons:
            clicked =  button.clicked(event)
            if clicked != False:
                for button in self.startWindow.buttons: 
                    button.selected=False
                    button.clicked(event, True)
        
        selectedColor = None
        for button in self.startWindow.buttons:
            if button.selected: selectedColor = button.color

        #if one color is selected & start is pressed, start the game
        if selectedColor != None and self.startWindow.start.clicked(event):

            self.gameStatus = "Set-up" #Start/ Set-up / Playing / End
            self.mode = "Build your first house"
            self.message = "\
     Click on a vertex to build \n Press arrow key to rotate board"
            self.subMessage = None #message that displays when subWindow is on
            self.board = Board(self.width/2, self.height/2, "icosahedron.obj")
            #display board slanted
            self.zoomed = 0 #for zooming in before start
            self.dtheta = 0.1
            self.dphi = 0.1

            #computer's color is randomly chosen from leftover colors
            colors = copy.copy(playerColors)
            self.playerColor = selectedColor
            index = colors.index(selectedColor)
            colors.pop(index)
            self.computerColor = random.choice(colors)

            self.player = Player("You", self.playerColor)
            self.computer = Computer("Computer", self.computerColor) 
            self.computerStep = 0
            self.players = [self.player, self.computer]
            self.turn = self.player

            #to avoid house building on same spot 
            #False => house/city ; None => player/computer
            self.nodesStatus = [[False, None]] * len(self.board.nodes)

            self.navigation = Navigation(self.mode)
            self.navigation.update()
            self.widget = Widget()

            self.startWindow = None
            self.subWindow = None
            self.tradeWindow = None
            self.helpWindow = None
            self.makeHelpButton()

            self.winner = None
            self.endWindow = None

    def makeHelpButton(self):
        bWidth = 50
        bHeight = 25
        x0 = cWidth - cardMargin - bWidth
        y0 = cHeight - self.bar.height - cardMargin - bHeight
        self.helpButton = Button("help", x0, y0, bWidth, bHeight)

    def generateSpecialDeck(self):
        self.specialDeck += ["knight"]*14
        self.specialDeck += ["vp"]*5
        self.specialDeck += ["invention"]*2
        self.specialDeck += ["monopoly"]*2
        random.shuffle(self.specialDeck)

    #allow key => obtain card. Press its first letter expect wheat = t
    def cheatKeyDemo(self, player):
        #resources
        if self.key == "w":
            self.message = "wood obtained"
            player.get(Card("wood"))

        elif self.key == "o":
            self.message = "ore obtained"
            player.get(Card("ore"))

        elif self.key == "b":
            self.message = "brick obtained"
            player.get(Card("brick"))

        elif self.key == "t":
            self.message = "wheat obtained"
            player.get(Card("wheat"))

        elif self.key == "s":
            self.message = "sheep obtained"
            player.get(Card("sheep"))

        #special cards
        elif self.key == "l":
            self.pickSpecial(player)

        elif self.key == "v":
            player.get(Special("vp"))

        elif self.key == "k":
            player.get(Special("knight"))

        elif self.key == "m":
            player.get(Special("monopoly"))

        elif self.key == "i":
            player.get(Special("invention"))

    def onKey(self, event):
        self.key = event.keysym
        if self.key == "Right":
            self.board.rotateX(self.dtheta)
        elif self.key == "Left":
            self.board.rotateX(-self.dtheta)
        elif self.key == "Up":
            self.board.rotateY(self.dphi)
        elif self.key == "Down":
            self.board.rotateY(-self.dphi)

        if self.gameStatus == "End":
            if self.key == "r":
                GAME.onInit()

        #for debugging
        if self.key =="p":
            print self.computer.resources

        #cheat key for demo/debugging
        if self.gameStatus == "Playing":
            self.cheatKeyDemo(self.player)
            #self.cheatKeyDemo(self.computer)

    def updateMessage(self):
        if self.gameStatus == "Set-up":
            if self.turn == self.player:
                self.message = "\
     Click on a vertex to build \n Press arrow key to rotate board"
            
            elif self.turn == self.computer:
                self.message = "Please Wait"

        elif self.gameStatus == "Playing":
            #computer's turn
            if self.turn == self.computer:
                self.message = "Wait for computer's turn"

            #player 1's turn
            else: 
                if self.mode == "Your Turn":
                    self.message = "Roll a dice"

                elif self.mode == "Rolled":
                    self.message = "Execute Your Turn"

                elif self.mode == "Build":
                    self.subMessage = "Choose what to buy"

                elif self.mode == "House Build": 
                    self.subMessage = "Click a vertex"
                elif self.mode == "City Build": 
                    self.subMessage = "Click a vertex"

        elif self.gameStatus == "Game Over":
            self.message = str(self.winner) + " Wins!"

    def executeRoll(self):
        #player has to roll FIRST
        self.board.resetNum()
        roll=self.dice.roll()
        self.roll = roll
        self.board.checkNum(roll)
        if self.turn == self.player:
            self.message = "Build/Trade; Press End to end turn"
        for player in self.players:
            player.checkLand() #gives out resources?

        if roll == 7: 
            for line in self.board.faces:
                line[6] = False
            i = random.randint(0, 19)
            
            tile = self.board.faces[i][3]
            num = self.board.faces[i][4]
            self.board.faces[i][6] = True
            self.message = "Alien arrived at %s (%s)" %(tile, num)
            self.exception = True

        self.mode = "%d is Rolled" % roll

    #build house & update nodeStatus
    def buildHouse(self, player, index):
        #built = False/house/city ; owner = None/player/computer
        built = self.nodesStatus[index][0]
        owner = self.nodesStatus[index][1]

        if built != False: #if already occupied
            self.exception = True
            self.subMessage = "Already Occupied"
            return False

        else: 
            #remove resources if built in the middle of game
            if self.gameStatus=="Playing":
                self.player.use(houseResources) 
            player.getHouse(House(player.color, index))
            self.nodesStatus[index] = ["house", player.name]
            
            #do not change the mode if gameStatus is set-up
            if self.gameStatus=="Playing":
                self.mode = str(self.roll) + " is Rolled"
            self.subMessage = None

    #build city & erase house & update nodeStatus
    def buildCity(self, player, index):
        #built = False/house/city ; owner = None/player/computer
        
        built = self.nodesStatus[index][0]
        owner = self.nodesStatus[index][1]

        #have to be built on your house => upgrade to city
        if built == "house" and owner == player.name:            
            #remove resources if built in the middle of game
            if self.gameStatus=="Playing":
                self.player.use(cityResources) 

            player.removeHouse(index) #remove original house
            player.getCity(City(player.color, index))
            self.nodesStatus[index] = ["city", player.name]

            #update mode
            if self.gameStatus == "Playing":
                self.mode = str(self.roll) + " is Rolled"
            self.subMessage = None

        else: #if city cannot be built
            self.subMessage = "Build on your house"
            self.exception = True
    
    def pickSpecial(self, player):
        #reshuffle if empty
        if self.specialDeck == []: 
            self.generateSpecialDeck()        
        player.use(specialResources) 
        special = self.specialDeck.pop()
        player.get(Special(special))

    def executeBuild(self, player, event, nodeIndex):
        valid = False
        if self.mode == "House Build" and nodeIndex != None:
            valid=self.buildHouse(player, nodeIndex)

        elif self.mode == "City Build" and nodeIndex != None:
            valid=self.buildCity(player, nodeIndex)

        #if house/city is built
        if valid == True: self.navigationClick(event)

    #execute when the button is clicked
    def navigationClick(self, event):
        atLeastOneClick = False
        for button in self.navigation.buttons:            
            if button.clicked(event) != False: #pass if a button is clicked
                atLeastOneClick = True

                #################
                ####MAIN MENU####
                #################
                if button.name == "Roll":
                    if self.mode == "Your Turn": 
                        self.executeRoll()
                    else: 
                        self.subMessage = "You can only roll once per turn"
                        self.exception = True

                #make sure player has rolled dice first
                if self.mode != "Your Turn":
                    if button.name == "Build":
                        self.mode = "Build"

                    elif button.name == "Trade": 
                        self.mode = "Trade"
                        self.subMessage = "Select 4 same resources \
from hand\n     Get 1 resource in return"
                        self.tradeWindow = TradeWindow("trade")

                    elif button.name == "End": 
                        #make sure player has rolled dice first
                        self.subMessage = None
                        self.turn = self.computer
                        self.mode = "Computer's Turn"
                        self.computerStep = 0 #for adding delay to computer
                else: 
                    self.message = "You must roll first"
                    self.exception = "True"

                #################
                ###BUILD MENU####
                #################

                if button.name == "House":
                    if self.player.check(houseResources):
                        self.mode = "House Build"
                    else: 
                        self.exception = True #do not update message
                        self.subMessage = "Not Enough Resources"

                elif button.name == "City":
                    if self.player.check(cityResources):
                        self.mode = "City Build"
                    else:
                        self.exception = True 
                        self.subMessage = "Not Enough Resources"

                elif button.name == "Special":
                    if self.player.check(specialResources):
                        self.pickSpecial(self.player)
                        self.mode = "Rolled"
                        self.exception = True
                        self.message = "Special Card Drawn"
                    else:
                        self.exception = True
                        self.subMessage = "Not Enough Resources"

                elif button.name == "Special":
                    self.mode = str(self.roll) + " is Rolled"
                    self.subMessage = None

                elif button.name == "Cancel":
                    self.mode = str(self.roll) + " is Rolled"
                    self.subMessage = None

        #if at least one button is clicked
        #don't allow mouse-sweep displaying message
        if atLeastOneClick == True:
            self.allowSweep = False

        #updates navigation menu
        self.navigation.update() 

    def setup(self, event):
        if self.helpWindow == None:
            if self.mode == "Build your first house":
                index = self.board.checkNodes(event, self.cx, self.cy)
                if index != None: 
                    self.buildHouse(self.player, index)
                    self.turn = self.computer
                    self.mode = "Computer's Turn to Build"
                    self.message = "Please Wait"

            elif self.mode == "Build your second house": 
                index = self.board.checkNodes(event, self.cx, self.cy)
                if index != None: 
                    #valid is false if occupied
                    valid = self.buildHouse(self.player, index)
                    if valid != False:
                        self.gameStatus = "Playing"
                        self.mode = "Your Turn"
                        self.navigation.update()

    def specialClicked(self, card):
        if card.kind == "vp": #card cannot be used
            self.message = "Victory Point cannot be used"
        elif card.kind == "knight": #card is upon clicked
            self.player.use([card], "specials")
            card.activate(self.player)
            self.message = "Knight removed the alien"
        elif card.kind == "monopoly": #card is used when confirmed
            self.subWindow = SubWindow("monopoly")
            self.subMessage = "Select one resource type"
        elif card.kind == "invention":
            self.subWindow = SubWindow("invention")
            self.subMessage = "Select two resources you want"

    def subWindowClick(self, event):  
        if self.subWindow.mode == "monopoly":
            #resources buttons on top
            for button in self.subWindow.buttons:
                button.clicked(event, True)

            #check which button is selected
            selected = []
            for button in self.subWindow.buttons:
                if button.selected == True:
                    selected.append(button.name)

            #main buttons
            for button in self.subWindow.mainButtons:
                clicked = button.clicked(event)
                if clicked == "Confirm":
                    #if nothing is selected yet
                    if len(selected) != 1: 
                        self.subMessage = "Select ONE resource"

                    #use the power of monopoly
                    #get rid of subWindow
                    else: 
                        self.subWindow.power(self.player, "monopoly", selected)
                        self.subWindow = None
                        self.subMessage = None

                if clicked == "Cancel":
                    self.subWindow = None
                    self.subMessage = None
            
        elif self.subWindow.mode == "invention":
            #resources buttons on top
            for button in self.subWindow.buttons:
                button.clicked(event, True)
                
            #check which button is selected
            selected = []
            for button in self.subWindow.buttons:
                if button.selected == True:
                    selected.append(button.name)

            #main buttons
            for button in self.subWindow.mainButtons:
                clicked = button.clicked(event)
                if clicked == "Confirm":
                    #if nothing is selected yet
                    if len(selected) != 2: 
                        self.subMessage = "Select TWO resources"
    
                    #use the power of invention
                    #get rid of subWindow
                    else: 
                        self.subWindow.power(self.player, "invention", selected)
                        self.subWindow = None
                        self.subMessage = None

                if clicked == "Cancel":
                    self.subWindow = None
                    self.subMessage = None
                
    def tradeWindowClick(self, event):
        #resources buttons on top
        for button in self.tradeWindow.buttons:
            button.clicked(event, True)

        #check if resource cards are clicked => select them
        self.player.selectResources(event)  

        #check which button is selected
        selectedButton = []
        for button in self.tradeWindow.buttons:
            if button.selected == True:
                selectedButton.append(button.name)

        #check which cards are selected
        selectedCards = []
        for card in self.player.resources:
            if card.selected == True:
                selectedCards.append(card)

        #main buttons
        for button in self.tradeWindow.mainButtons:
            clicked = button.clicked(event)
            if clicked == "Confirm":
                tradeRatio = 4
                #check only one button is selected
                if len(selectedButton) != 1: 
                    self.subMessage = "Select ONE resource"

                #check 4 cards are selected
                elif len(selectedCards) != tradeRatio:
                    self.subMessage = "Select FOUR cards from your hand"

                #check if 4 SAME resources were clicked
                #when appropriately press confirmed,
                #trade,  get rid of tradeWindow & reset selection
                else: 
                    #check 4 selected cards are same kind
                    sameKind = True
                    for i in xrange(1, tradeRatio): 
                        if selectedCards[0].kind != selectedCards[i].kind:
                            sameKind = False
                    if not sameKind: 
                        self.subMessage = "Select four cards of SAME kind"
                
                    else:
                        self.tradeWindow.trade(self.player, selectedButton, 
                            selectedCards)
                        self.tradeWindow = None
                        self.subMessage = None
                        self.mode = str(self.roll) + " is Rolled"
                        for resource in self.player.resources:
                            resource.selected = False

            #when cancel, get rid of tradeWindow & unselected all cards
            if clicked == "Cancel":
                self.tradeWindow = None
                self.subMessage = None
                self.mode = str(self.roll) + " is Rolled"
                for resource in self.player.resources:
                    resource.selected = False

    def executePlaying(self, event):
        if self.turn == self.player:
            #if navigation button is clicked, execute accordingly
            #build click is NOT executed here
            if (self.subWindow == None and self.tradeWindow == None 
                and self.helpWindow == None):
                self.navigationClick(event)

            #For building House/City (only if self.mode=House/City Build)
            nodeIndex = self.board.checkNodes(event, self.cx, self.cy)

            self.executeBuild(self.player, event, nodeIndex)

            #bar check (check if card special card clicked)
            special = self.player.checkClicked(event, mode="special")
            if special != None: self.specialClicked(special)

            #sub-window
            if self.subWindow != None:
                self.subWindowClick(event)

            if self.tradeWindow != None:
                self.tradeWindowClick(event)

    def onMouse(self, event): 
        #for start window
        if self.gameStatus == "Start": self.startWindowOnMouse(event)

        else:
            #keeps track of background click
            clicked = False
            self.exception = False

            self.sweepMessage = None
            self.allowSweep = False

            #regarding help
            if self.helpButton.clicked(event): self.helpWindow = HelpWindow()
            elif self.helpWindow != None:
                if self.helpWindow.exit.clicked(event): self.helpWindow = None

            #player
            if self.turn == self.player: 
                #SET-UP (Before game)
                if self.gameStatus == "Set-up":
                    self.setup(event)

                #after SET-UP
                elif self.gameStatus == "Playing":
                    self.executePlaying(event)

            #updates message if not exception. deactivate when subwindow is on
            if self.subWindow == None:
                if self.tradeWindow == None:
                    if self.exception == False:
                        self.updateMessage() 

            #sort cards for cleaner hand
            self.player.sortCards(self.player) 

            #update point & check winner
            self.player.updatePoints(self.computer)
            self.computer.updatePoints(self.player)
            for player in self.players:
                if player.points >= 10:
                    self.mode = "Victory"
                    self.message = "Press r to play again"
                    self.winner = player
                    self.gameStatus = "End"
                    self.endWindow = EndWindow(player)

    #for help message on what button does
    def onMouseMove(self, event):
        valid = False #to know when to update message
        if (self.gameStatus == "Playing" and self.turn==self.player and
            self.subWindow == None and self.tradeWindow == None and 
            self.allowSweep == True):
            for button in self.navigation.buttons:
                clicked = button.clicked(event)
                if clicked != False:
                    valid = True
                    #main menu
                    if clicked == "Roll": 
                        self.sweepMessage = "Click to roll dices"
                    elif clicked == "Build":
                        self.sweepMessage = "Build house/city or draw special cards"
                    elif clicked == "Trade":
                        self.sweepMessage = "Trade any one card for four same cards"
                    elif clicked == "End":
                        self.sweepMessage = "End your turn"

                    #build menu
                    elif clicked == "House": 
                        self.sweepMessage = "for wood, brick, sheep, wheat"
                    elif clicked == "City":
                        self.sweepMessage = "for ore, ore, ore, wheat, wheat"
                    elif clicked == "Special":
                        self.sweepMessage = "for ore, sheep, wheat"
                    elif clicked == "Cancel":
                        self.sweepMessage = "Go back"        

            for card in self.player.specials:
                special = self.player.checkClicked(event, mode="special")
                if special != None:
                    valid = True
                    if special.kind == "knight":
                        self.sweepMessage = "kills the alien on the board"
                    elif special.kind == "monopoly":
                        self.sweepMessage = "steal one type of resource \n\
from another player"
                    elif special.kind == "invention":
                        self.sweepMessage = "get two free resources of any kind"

        #if mouse is not over any button
        if valid == False: 
            self.allowSweep = True
            self.sweepMessage = None

    #AI
    def computerRun(self): 
        if self.gameStatus == "Set-up":
            step = self.computerStep

            self.computer.delay("short")
            #build two houses
            if step == 0: 
                nodeIndex = self.computer.bestHouseNode()
                self.buildHouse(self.computer, nodeIndex)
                self.computerStep += 1

            elif step == 1: 
                nodeIndex = self.computer.bestHouseNode()
                self.buildHouse(self.computer, nodeIndex)
                self.computerStep += 1

            elif step == 2:
                self.turn = self.player
                self.mode = "Build your second house"
                self.message = None

        elif self.gameStatus == "Playing": 
            step = self.computerStep
            
            if step == 0: 
                #use knight when alien is nearby land
                for special in self.computer.specials:
                    if special.kind == "knight":
                        if self.computer.alienNearby():
                            self.computer.use([special], "specials")
                            special.activate(self.computer)
                            self.message = "Computer uses a knight"
                            self.exception = True
                
                #trade when computer can
                exports = self.computer.canTrade()
                if exports != None: 
                    get = self.computer.getNeededCard()
                    if get != None:
                        self.computer.use(exports)

                self.computer.delay("medium")
                self.executeRoll()
                self.computerStep += 1

            elif step == 1: 
                self.computer.delay("medium")

                options = self.computer.options()
            
                #check city option first b/c city is more valuable
                if "city" in options: 
                    self.computer.delay("short")
                    nodeIndex = self.computer.bestCityNode()
                    self.buildCity(self.computer, nodeIndex)

                if "house" in options:
                    self.computer.delay("short")
                    nodeIndex = self.computer.bestHouseNode()
                    self.buildHouse(self.computer, nodeIndex)

                if "special" in options:
                    self.pickSpecial(self.computer)

                self.computerStep += 1

            elif step == 2: 
                self.turn = self.player
                self.mode = "Your Turn"
                self.message = "Roll a dice"

            #update point
            self.computer.updatePoints(self.player)

    def onStep(self):
        if self.gameStatus != "Start":
            #zoom until self.zoomed exceeds a threshold
            #magic number necesssary to fit the zoom & control speed of zoom
            if self.zoomed < 12: 
                self.board.zoom(0.29)
                self.board.rotateX(self.dtheta*2)
                self.board.rotateY(self.dphi*3)
                self.zoomed += 1
            #add delay for realness of computer
            if self.turn == self.computer:
                self.computer.delay("short")
                self.computerRun()

    def onDraw(self, canvas):
        self.space.draw(canvas)
        self.bar.draw(canvas)

        #when start/end of game
        if self.gameStatus == "Start":
            self.startWindow.draw(canvas)

        else:
            self.board.draw(canvas)

            #displaying mode
            modeText = self.turn.name + ": " + self.mode
            canvas.create_text(self.width/2, 30, text=modeText, fill="white")
            
            #displaying message
            if self.sweepMessage != None:
                message = self.sweepMessage
            elif self.subMessage != None:
                message = self.subMessage
            else:
                message = self.message
            canvas.create_text(self.width/2, 50, text=message, 
                fill="white", anchor=N)
            
            if self.gameStatus != "Set-up":
                self.navigation.draw(canvas)
                self.widget.draw(canvas)
                self.dice.draw(canvas)
            
            #draw cards
            for player in self.players:
                player.draw(canvas)

            for house in self.player.houses:
                house.draw(canvas)

            #subwindow for trade & monopoly/invention
            if self.subWindow != None:
                self.subWindow.draw(canvas)
            if self.tradeWindow != None:
                self.tradeWindow.draw(canvas)
            if self.helpWindow != None:
                self.helpWindow.draw(canvas)
            self.helpButton.draw(canvas)

            
            if self.gameStatus == "End": 
                self.endWindow.draw(canvas)

        
GAME = Catan(width=cWidth, height=cHeight, timerDelay=100)    
GAME.run()
