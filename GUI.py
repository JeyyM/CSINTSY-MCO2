# pip install pyswip

# for prolog use
from pyswip import Prolog
prolog = Prolog()
prolog.consult("kb.pl")

# for GUI
import tkinter as tk
from tkinter import messagebox

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
                ['.', '.', '.', '.', '.', '.'] ]

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

def exportMap():
    return playerVision

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
    messagebox.showinfo("Gold Grabbed", "You got a gold!")
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

    if (playerVision[y][x] != "#"):
        if isBreeze:
            print(f"Adding breezeSpot: ({x}, {y})")
            prolog.assertz(f"breezeSpot(({x}, {y}))")

        # Check all the adjacents of the destination
        for xChange, yChange in DIRECTIONS:
            adjX, adjY = x + xChange, y + yChange
            if 0 <= adjX < len(map[0]) and 0 <= adjY < len(map):
                if isBreeze and playerVision[adjY][adjX] != "S":
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
                    if playerVision[adjY][adjX] == "." or playerVision[adjY][adjX] == "?":
                        playerVision[adjY][adjX] = "S"

# Set the player's starting position in playerVision
playerVision[playerPosition[1]][playerPosition[0]] = "H"
# Mark spots as explored so they dont get checked for pits
# otherwise, explored spots with 3 or more breezes become pits
prolog.assertz(f"explored(({playerPosition[0]}, {playerPosition[1]}))")
markSpots(playerPosition)

def playerMove(direction):
    global playerPosition
    global coinCount

    action = direction

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
            root.quit()
        # Home
        elif map[y][x] == 'H':
            # the player CAN leave but not forced to
            if (coinCount >= 2):
                leave(coinCount)
                root.quit()

        # Update player position
        playerPosition = newPosition
    else:
        print(message)

    print("Player Vision:")
    displayMap()

    header_label = tk.Label(root, text="Gold Count: " + str(coinCount), font=("Arial", 16), width=20, height=2)
    header_label.grid(row=0, column=0, columnspan=6, pady=10)  # Columnspan makes the header span across all columns

    # Create the main window
    header_label = tk.Label(root, text="Gold Count: " + str(coinCount), font=("Arial", 16), width=20, height=2)
    header_label.grid(row=0, column=0, columnspan=6, pady=10)  # Columnspan makes the header span across all columns

    # Create a 6x6 grid of labels (empty cells)
    grid = []
    for i in range(6):
        row = []
        for j in range(6):
            if (playerVision[i][j] == 'H' or playerVision[i][j] == 'S' or playerVision[i][j] == '#' or playerVision[i][j] == '@'):
                label = tk.Label(root, text=playerVision[i][j], width=10, height=4, bg="green", relief="solid", anchor="center")
            elif (playerVision[i][j] == 'P'):
                label = tk.Label(root, text=playerVision[i][j], width=10, height=4, bg="red", relief="solid", anchor="center")
            else:
                label = tk.Label(root, text=playerVision[i][j], width=10, height=4, relief="solid", anchor="center")
            label.grid(row=i+1, column=j, padx=0, pady=0)  # Note the row is shifted by 1 to make space for the header
            row.append(label)
        grid.append(row)

# TO DO MAYBE
# put a safeConfirm, on ? spots, add a safeSpot()


root = tk.Tk()
root.title("Adventure World")

# Set window size
root.geometry("456x700")

# Create the main window
header_label = tk.Label(root, text="Gold Count: " + str(coinCount), font=("Arial", 16), width=20, height=2)
header_label.grid(row=0, column=0, columnspan=6, pady=10)  # Columnspan makes the header span across all columns

# Create a 6x6 grid of labels (empty cells)
grid = []
for i in range(6):
    row = []
    for j in range(6):
        if (playerVision[i][j] == 'H' or playerVision[i][j] == 'S' or playerVision[i][j] == '#' or playerVision[i][j] == '@'):
            label = tk.Label(root, text=playerVision[i][j], width=10, height=4, bg="green", relief="solid", anchor="center")
        elif (playerVision[i][j] == 'P'):
            label = tk.Label(root, text=playerVision[i][j], width=10, height=4, bg="red", relief="solid", anchor="center")
        else:
            label = tk.Label(root, text=playerVision[i][j], width=10, height=4, relief="solid", anchor="center")
        label.grid(row=i+1, column=j, padx=0, pady=0)  # Note the row is shifted by 1 to make space for the header
        row.append(label)
    grid.append(row)

# Buttons for movement (remove the gap between buttons)
button_up = tk.Button(root, text="Up", command=lambda: playerMove("move up"))
button_up.grid(row=24, column=2, padx=0, pady=5)

button_down = tk.Button(root, text="Down", command=lambda: playerMove("move down"))
button_down.grid(row=28, column=2, padx=0, pady=5)

button_left = tk.Button(root, text="Left", command=lambda: playerMove("move left"))
button_left.grid(row=28, column=1, padx=0, pady=5)

button_right = tk.Button(root, text="Right", command=lambda: playerMove("move right"))
button_right.grid(row=28, column=3, padx=0, pady=5)

displayMap()

root.mainloop()

# End of GUI code
