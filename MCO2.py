# pip install pyswip

# for prolog use
from pyswip import Prolog
prolog = Prolog()
prolog.consult("kb.pl")

# game status
coinCount = 0
start = True

DIRECTIONS = [
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0)
]

# two maps, think like sokobot
map = [ ['.', '.', '.', '.', 'G', '.'],
        ['.', '.', 'P', '.', '.', '.'],
        ['.', 'H', '.', 'P', '.', 'G'],
        ['P', '.', '.', '.', 'G', '.'],
        ['.', '.', '.', '.', 'P', '.'],
        ['G', '.', 'G', '.', '.', '.']]

playerVision = [ ['.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.'],
                ['.', '.', '.', '.', '.', '.']]

# store those spots as pit or gold within the KB
def storeItems(map):
    for i in range(len(map)):
        for j in range(len(map[i])):
            cell = map[i][j]
            if cell == 'P':
                prolog.assertz(f"pit(({j}, {i}))")
            elif cell == 'G':
                prolog.assertz(f"gold(({j}, {i}))")

storeItems(map)

def findPlayerStart(map):
    for i in range(len(map)):
        for j in range(len(map[i])):
            if map[i][j] == 'H':
                return [j, i]

playerPosition = findPlayerStart(map)
# print(f"Starting Position: {playerPosition}")

# just used on the playerVision
def displayMap():
    print(f"Coins: {coinCount}")
    for row in playerVision:
        print(" ".join(row))
    print()

def movePlayer(playerPos, direction):
    x, y = playerPos

    # based on the given strings
    directionOptions = {
        "move up": DIRECTIONS[0],
        "move down": DIRECTIONS[1],
        "move left": DIRECTIONS[2],
        "move right": DIRECTIONS[3]
    }

    # don't change the direction
    if direction not in directionOptions:
        return playerPos, "Invalid"


    xChange, yChange = directionOptions[direction]
    newX, newY = x + xChange, y + yChange

    # Check if the new position is within bounds
    if 0 <= newX < len(map[0]) and 0 <= newY < len(map):
        print(f"New position: ({newX}, {newY})")
        return (newX, newY), "Moved"
    else:
        return playerPos, "Out of bounds"

# Not really necessary but since specs call them that
def grab(x, y):
    print("GRABBING")
    prolog.retract(f"gold(({x}, {y}))")

def leave(coinCount):
    if coinCount < 2:
        print(f"Mission failed! Only {coinCount} coins collected.")
    else:
        print(f"Mission accomplished! {coinCount} coins collected.")

#
def findPits(adjX, adjY):
    print("FINDING PIT")
    print("Current Pit Spots:", list(prolog.query("pit((X, Y))")))
    print("Current Breeze Spots:", list(prolog.query("breezeSpot((X, Y))")))
    
    findPit = bool(list(prolog.query(f"findPit(({adjX}, {adjY}))")))
    return findPit

def markSpots(playerPosition):
    print("MARKING SPOT")
    x, y = playerPosition

    # to add a new breeze to the KB
    isBreeze = bool(list(prolog.query(f"findBreeze(({x}, {y}))")))

    print("COORDINATE CHECK", x, y, playerVision[x][y])

    if isBreeze:
        if (playerVision[y][x] != "#"):
            print(f"Adding breezeSpot: ({x}, {y})")
            prolog.assertz(f"breezeSpot(({x}, {y}))")

    # Check all the adjacents of the destination
    for xChange, yChange in DIRECTIONS:
        adjX, adjY = x + xChange, y + yChange
        if 0 <= adjX < len(map[0]) and 0 <= adjY < len(map):
            if isBreeze and playerVision[y][x] != "#":
                isPit = findPits(adjX, adjY)
                if isPit:
                    if (playerVision[y][x] != "#" or playerVision[y][x] != "@"):
                        print(f"Pit found at ({adjX}, {adjY})")
                        playerVision[adjY][adjX] = "P"

                    # prolog.assertz(f"pitSpot(({adjX}, {adjY}))")
                    # print(f"Added pitSpot: ({adjX}, {adjY})")
                else:
                    # to not modify P
                    if playerVision[adjY][adjX] == ".":
                        playerVision[adjY][adjX] = "?"
            else:
                # to not modify @ or #
                if playerVision[adjY][adjX] == ".":
                    playerVision[adjY][adjX] = "S"

# Set the player's starting position in playerVision
playerVision[playerPosition[1]][playerPosition[0]] = "H"
# Mark spots as explored so they dont get checked for pits
# otherwise, explored spots with 3 or more breezes become pits
prolog.assertz(f"explored(({playerPosition[0]}, {playerPosition[1]}))")
markSpots(playerPosition)

while start:
    print("Player Vision:")
    displayMap()

    action = input("Enter movement (move up, move down, move left, move right): ")

    newPosition, message = movePlayer(playerPosition, action)

    if message == "Moved":
        x, y = newPosition
        markSpots((x, y))

        # Update playerVision for the previous position
        originalX, originalY = playerPosition
        if playerVision[originalY][originalX] == "@":
            playerVision[originalY][originalX] = "#"

        # To always maintain @
        if playerVision[y][x] == "." or playerVision[y][x] == "S" or playerVision[y][x] == "?" or playerVision[y][x] == "#":
            playerVision[y][x] = "@"
            if playerVision[y][x] != "#":
                prolog.assertz(f"explored(({x}, {y}))")


        # Gold check
        is_glitter = bool(list(prolog.query(f"glitter(({x}, {y}))")))
        if is_glitter:
            coinCount += 1
            grab(x, y)
        # die
        elif bool(list(prolog.query(f"fall(({x}, {y}))"))):
            print("Mission Failed!")
            start = False
        # Home
        elif map[y][x] == 'H':
            # the player CAN leave but not forced to
            if (coinCount >= 2):
                leave(coinCount)
                start = False

        # Update player position
        playerPosition = newPosition
    else:
        print(message)
