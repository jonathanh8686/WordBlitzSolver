import time
import urllib.request as urllib2
import string
from PIL import Image
import pyautogui

pyautogui.FAILSAFE = True

CONST_X, CONST_Y = 586, 470
boardState = []

used_words = set()


# find if game is on screen
# find the letters on the board
    # [x] OCR - too hard xd
    # [*] indiv pictures of each and find with pyauto
# connecting words in graphs
    # path finding use dictionary
# drag mouse across words

def manualEnter():
    board = []
    t = ""
    for i in range(4):
        t = input().strip()
        board.append(list(t))
    return board

def getBoard(boardim, confidence=0.8):
    print("Getting Board State")
    board = [["", "", "", ""] for _ in range(4)]
    # returns the state of the board as a 2d array

    letterPos = findBoardLetters(boardim, confidence)
    print(letterPos)
    for i in range(len(board)):
        for j in range(len(board[i])):
            board[j][i] = letterPos[4 * i + j][1]

    print("\n\n\n")

    for i in range(len(board)):
        print(board[i])

    return board

def findBoardLetters(boardim, confidence):
    print("Finding Board Letters...")
    letterPos = []
    checkletters = "abdefgiklmnoprstvyxz"

    lf = 0
    for c in checkletters:
        print("Finding all " + c)
        letterim = Image.open("letters/{}.png".format(c))

        fn = lambda x : 255 if x > 200 else 0

        letterim = letterim.convert("L").point(fn, mode="1")

        boardim = boardim.convert("L").point(fn, mode='1')

        loc = list(pyautogui.locateAll(letterim, boardim, True, confidence=confidence))
        loc = filterLocations(loc)
        print(loc)

        for p in loc:
            letterPos.append((p, c))
        lf += len(loc)
    print("Found " + str(lf) + " characters!")
    if(lf != 16):
        raise Exception("Expected 16 characters, found {}".format(str(lf)))
    return sorted(letterPos)



def filterLocations(loclist):
    print("Filtering Similar Locations")
    uni = []
    for l in loclist:
        l = list(l)
        l[0] = l[0] // 100 * 100
        l[1] = l[1] // 100 * 100

        uni.append(tuple(l))

    return list(set(uni))

def inBound(x, y):
    if(x < 0 or x > 3):
        return False
    if(y < 0 or y > 3):
        return False
    return True

def getPathsFromChar(row, col, board, depth, mxdepth):
    paths = []
    if(depth >= mxdepth):
        return [[board[row][col], [(row, col)]]]

    dx, dy = [-1,-1,0,1,1,1,0,-1], [0,-1,-1,-1,0,1,1,1]
    for i in range(8):
        if(inBound(row + dx[i], col + dy[i])):
            if(visit[row + dx[i]][col + dy[i]] == False):
                visit[row][col] = True
                p = getPathsFromChar(row + dx[i], col + dy[i], board, depth + 1, mxdepth)
                visit[row][col] = False
                for j in p:
                    newPath = [board[row][col] + j[0], [(row, col)] + j[1]]
                    paths.append(newPath)

    return paths

def filterGarbageWords(words):
    mousePaths = []
    for w in words:
        if(str(w[0]) in eng_words):
            if(w[0] in used_words):
                continue
            used_words.add(w[0])
            mousePaths.append(w[1])
    return mousePaths

def executePath(p):
    pyautogui.moveTo(p[0][1] * 100 + 650, p[0][0] * 100 + 530)
    pyautogui.mouseDown()
    for pos in p:
        xpos = pos[1] * 100
        ypos = pos[0] * 100
        print(boardState[pos[0]][pos[1]])

        print("Moving to: {}, {}".format(650 + xpos, 530 + ypos))
        pyautogui.moveTo(650 + xpos, 530 + ypos)

    pyautogui.mouseUp()
    print("-------------------\n\n")

print("Started")
print("Getting Board...")

wordsurl="https://raw.githubusercontent.com/first20hours/google-10000-english/master/20k.txt"
#wordsurl="https://gist.githubusercontent.com/h3xx/1976236/raw/bbabb412261386673eff521dddbe1dc815373b1d/wiki-100k.txt"
eng_words = urllib2.urlopen(wordsurl).read()
eng_words = eng_words.decode().replace("\r", "").split("\n")
eng_words = set(eng_words)

print("ora" in eng_words)

visit = [[False for _ in range(4)] for _ in range(4)]
try:
    boardImage = pyautogui.screenshot(region = (CONST_X,CONST_Y,415,415))
    #boardImage.show()
    #boardImage = Image.open("game2.png")
    #boardState = getBoard(boardImage)
    boardState = manualEnter()

    for i in range(4):
        for j in range(4):
            for k in range(2, 7)[::-1]:
                words = getPathsFromChar(i, j, boardState, 0, k)
                paths = filterGarbageWords(words)
                for p in paths:
                    executePath(p)

    print(used_words)
except KeyboardInterrupt:
    print("Closed.")



