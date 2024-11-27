# pip install pyswip

# for prolog use
from pyswip import Prolog
prolog = Prolog()
prolog.consult("kb.pl")

# for GUI
import tkinter as tk
from tkinter import messagebox

# Map Reader

import sys

# Check if the script has received the correct number of arguments
if len(sys.argv) != 2:
    print("Usage: python gui.py <map_file>")
    sys.exit(1)  # Exit the program if arguments are incorrect

# Read the file name from the command line argument
map_file = sys.argv[1]

def load_map(map_file):
    try:
        with open(map_file, 'r') as file:
            # Read map data from the file (just an example)
            map_data = file.readlines()
            print(f"Map data from {map_file}:")
            return map_data
    except FileNotFoundError:
        print(f"Error: The file {map_file} was not found.")
        sys.exit(1)

def parseMap(map_data):
    map = []
    for row in map_data:
        # Strip the row of any leading/trailing whitespace or newline characters
        row = row.strip()
        
        # Convert each row (string) into a list of characters
        map_row = list(row)
        
        # Append the row to the 2D map
        map.append(map_row)
    
    return map

# End of Map Reader

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
map = parseMap(load_map(sys.argv[1]))

playerVision = [['.'] * len(map) for i in range(len(map))]

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

def addBoundaries():
    rows = len(map)
    cols = len(map[0])

    for j in range(cols):
        prolog.assertz(f"breezeSpot(({j}, -1))")
        prolog.assertz(f"breezeSpot(({j}, {rows}))")

    for i in range(-1, rows + 1):
        prolog.assertz(f"breezeSpot((-1, {i}))")
        prolog.assertz(f"breezeSpot(({cols}, {i}))")

addBoundaries()
print("Current Boundaries:", list(prolog.query("breezeSpot((X, Y))")))

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

def updateMap(g = "", b = ""):
    displayMap()

    # Create the main window
    header_label = tk.Label(root, text="Gold Count: " + str(coinCount), font=("Arial", 16), width=20, height=2)
    header_label.grid(row=0, column=0, columnspan=len(map), pady=10)  # Columnspan makes the header span across all columns
    breeze_label = tk.Label(root, text=b, width=20)
    gold_label = tk.Label(root, text=g, width=20)

    # Create a 6x6 grid of labels (empty cells)
    grid = []
    for i in range(len(map)):
        row = []
        for j in range(len(map)):
            if (playerVision[i][j] == 'H' or playerVision[i][j] == 'S' or playerVision[i][j] == '#' or playerVision[i][j] == "H@" or playerVision[i][j] == "@"):
                label = tk.Label(root, text=playerVision[i][j], width=10, height=4, bg="green", relief="solid", anchor="center")
            elif (playerVision[i][j] == 'G' or playerVision[i][j] == "G@"):
                label = tk.Label(root, text=playerVision[i][j], width=10, height=4, bg="yellow", relief="solid", anchor="center")
            elif (playerVision[i][j] == 'P'):
                label = tk.Label(root, text=playerVision[i][j], width=10, height=4, bg="red", relief="solid", anchor="center")
            else:
                label = tk.Label(root, text=playerVision[i][j], width=10, height=4, relief="solid", anchor="center")
            if (playerVision[i][j] == '@' or playerVision[i][j] == 'H@' or playerVision[i][j] == 'G@'):
                label.config(font=("Arial", 9, "bold underline"))
            label.grid(row=i+1, column=j, padx=0, pady=0)  # Note the row is shifted by 1 to make space for the header
            row.append(label)

        grid.append(row)
    
    breeze_label.grid(row=26, column=0, columnspan=len(map), pady=10) 
    gold_label.grid(row=27, column=0, columnspan=len(map), pady=10) 
# Not really necessary but since specs call them that
def grab(x, y):
    global coinCount

    if (playerVision[y][x] == "G" or playerVision[y][x] == "G@"):
        print("GRABBING")
        coinCount += 1
        playerVision[y][x] = "@"

        messagebox.showinfo("Gold Grabbed", "You got a gold!")

        updateMap()

        prolog.retract(f"gold(({x}, {y}))")
    else:
        print("No Gold")
        messagebox.showinfo("Invalid Gold", "No Gold Here")

def leave(x, y):
    global coinCount
    start = findPlayerStart(map)

    print(start)
    print("X: " + str(x) + " Y: " + str(y))

    if ((start[0] == x) and (start[1] == y)):
        if coinCount < 2:
            print(f"Mission failed! Only {coinCount} coins collected.")
            messagebox.showinfo("Loss", "Mission Failed! Only " + str(coinCount) + " coins collected.")
            root.quit()
        else:
            print(f"Mission accomplished! {coinCount} coins collected.")
            messagebox.showinfo("Win", "Mission accomplished! " + str(coinCount) + " coins collected.")
            root.quit()
    else:
        messagebox.showinfo("Invalid Action", "You can only leave when you are home.")

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

    if (playerVision[y][x] != "#" and playerVision[y][x] != "G"):
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
                    if playerVision[adjY][adjX] == "." or playerVision[adjY][adjX] == "?" or playerVision[adjY][adjX] == "P":
                        playerVision[adjY][adjX] = "S"
    if isBreeze:
        return "You feel a breeze..."
    else:
        return ""

# Set the player's starting position in playerVision
playerVision[playerPosition[1]][playerPosition[0]] = "H@"
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
        breeze_text = markSpots((x, y))
        gold_text = ""

        # Update playerVision for the previous position
        originalX, originalY = playerPosition
        if playerVision[originalY][originalX] == "@":
            playerVision[originalY][originalX] = "#"
        elif playerVision[originalY][originalX] == "H@":
            playerVision[originalY][originalX] = "H"
        elif playerVision[originalY][originalX] == "G@":
            playerVision[originalY][originalX] = "G"

        # To always maintain @
        if playerVision[y][x] == "." or playerVision[y][x] == "S" or playerVision[y][x] == "?" or playerVision[y][x] == "#" or playerVision[y][x] == "P":
            if playerVision[y][x] != "#":
                prolog.assertz(f"explored(({x}, {y}))")
            playerVision[y][x] = "@"
        elif playerVision[y][x] == "H":
            playerVision[y][x] = "H@"
        # Gold check
        is_glitter = bool(list(prolog.query(f"glitter(({x}, {y}))")))
        if is_glitter:
            playerVision[y][x] = "G@"
            gold_text = "You see a glitter..."
        # die
        elif bool(list(prolog.query(f"fall(({x}, {y}))"))):
            print("Mission Failed!")
            messagebox.showinfo("Loss", "Mission Failed! You fell down a pit.")
            root.quit()

        # Update player position
        playerPosition = newPosition
    else:
        print(message)

    print("Player Vision:")
    updateMap(g = gold_text, b = breeze_text)

# GUI Code

root = tk.Tk()
root.title("Adventure World")

# Set window size
root.geometry("456x700")

updateMap()

# Buttons for movement (remove the gap between buttons)
button_up = tk.Button(root, text="Up", command=lambda: playerMove("move up"))
button_up.grid(row=24, column=2, padx=0, pady=5)

button_down = tk.Button(root, text="Down", command=lambda: playerMove("move down"))
button_down.grid(row=25, column=2, padx=0, pady=5)

button_left = tk.Button(root, text="Left", command=lambda: playerMove("move left"))
button_left.grid(row=25, column=1, padx=0, pady=5)

button_right = tk.Button(root, text="Right", command=lambda: playerMove("move right"))
button_right.grid(row=25, column=3, padx=0, pady=5)

button_leave = tk.Button(root, text="Leave World", command=lambda: leave(playerPosition[0], playerPosition[1]))
button_leave.grid(row=24, column=3, padx=0, pady=5)

button_grab = tk.Button(root, text="Grab Gold", command=lambda: grab(playerPosition[0], playerPosition[1]))
button_grab.grid(row=24, column=1, padx=0, pady=5)

root.mainloop()

# End of GUI code
