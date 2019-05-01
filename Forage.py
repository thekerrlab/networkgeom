import random
import math

class spriteLocation:
    pass

class Forage:

    def __init__(self, width, height, density):
        self.width = width
        self.height = height
        self.density = max(0, min(1, density)) # number from 0-1
        self.foodCollected = 0
        self.occupancyGrid = []
        self.spriteLocation = spriteLocation()
        self.createField()
        print("Forage object created of size " + str(width) + "x" + str(height)\
            + " of density " + str(density))

    # Design of (good enough) algorithm:
    # This algorithm is much worse than O(n), however since the field in
    # typical application is small, it is deemed good enough.
    # The task is to populate a field of 0's with 1's according to some density.
    # The (trivial) algorithm is implemented below, where if the density is
    # <= 0.5 we find random coordinates and insert 1s if we can until we have
    # inserted enough. This significantly degrades as we approach a density of
    # approximately 0.5. If the density is > 0.5, then we do the same except
    # populate a feild of 1's with 0's.
    def createField(self):
        fillNum = 0
        if self.density > 0.5:
            fillNum = 1
        enterNum = (fillNum + 1) % 2
        for i in range(self.height):
            self.occupancyGrid.append([fillNum] * self.width)
        # Add the food to the grid
        totalFood = round(self.height * self.width * self.density)
        allocatedFood = 0
        while allocatedFood < totalFood:
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            # Skip if already put number there
            if self.getOccupancyGridLoc(x, y) == enterNum:
                continue
            # Otherwise put the number in
            self.setOccupancyGridLoc(x, y, enterNum)
            allocatedFood += 1

        # Set the sprite location to be between x = 0 to width-1, y = 0 to height-1
        self.spriteLocation.x = random.randint(0,self.width-1)
        self.spriteLocation.y = random.randint(0,self.height-1)
        #self.occupancyGrid[self.spriteLocation.y][self.spriteLocation.x] = 2
        self.setOccupancyGridLoc(self.spriteLocation.x, self.spriteLocation.y, 2)

    # Wrap-around movement, where direction is a number:
    # 1 2 3         NW N NE
    # 4 5 6   =>     W C  E
    # 7 8 9         SW S SE
    # Note that coordinate system is top left is (0,0)
    # 5 does nothing
    # returns # of collected food (0 or 1)
    def movePlayer(self, direction):
        if direction == 5:
            return
        # Set occupancy grid current spot to 0
        self.setOccupancyGridLoc(self.spriteLocation.x, self.spriteLocation.y, 0)
        # Lateral movement
        if direction == 1 or direction == 4 or direction == 7:
            if self.spriteLocation.x == 0:
                self.spriteLocation.x = self.width-1
            else:
                self.spriteLocation.x -= 1
        elif direction % 3 == 0:
            if self.spriteLocation.x == self.width-1:
                self.spriteLocation.x = 0
            else:
                self.spriteLocation.x += 1
        # Vertical movement
        if direction <= 3:
            if self.spriteLocation.y == 0:
                self.spriteLocation.y = self.height-1
            else:
                self.spriteLocation.y -= 1
        elif direction >= 7:
            if self.spriteLocation.y == self.height-1:
                self.spriteLocation.y = 0
            else:
                self.spriteLocation.y += 1
        # Set next occupancy grid current spot to 2, and collect any food
        collected = 0 # flag for collected food
        if self.getOccupancyGridLoc(self.spriteLocation.x, self.spriteLocation.y) == 1:
            self.foodCollected += 1
            collected = 1
        self.setOccupancyGridLoc(self.spriteLocation.x, self.spriteLocation.y, 2)
        return collected # return 0 or 1 depending on if food was collected

    # Simple setter function for occupancy grid
    def setOccupancyGridLoc(self, x, y, value):
        self.occupancyGrid[y][x] = value

    # Simple getter function for occupancy grid
    def getOccupancyGridLoc(self, x, y):
        return self.occupancyGrid[y][x]

    # Get list of occupied spaces, centred on person. So if 0 is in the list,
    # this corresponds with the top-left of the grid centred on the sprite.
    # e.g.     1|2|0 or 0|1|2
    #          p|5|3    3|p|5
    #          7|8|6    6|7|8
    # for a 3x3 map and sprite at p.
    # e.g. for a 4x4, we take top left of middle 4, hence better to work with
    # odd size grids
    #          0| 1| 2| 3
    #          4| p| 6| 7
    #          8| 9|10|12
    #         12|13|14|15
    # e.g. for a 3x4
    #         11|8|9|10
    #          3|0|1|2
    #          7|4|p|6
    def getOccupiedGridList(self):
        # Pre-process some useful variables
        right_shift = self.spriteLocation.x - math.floor((self.width-1)/2)
        down_shift = self.spriteLocation.y - math.floor((self.height-1)/2)
        start_col = (right_shift + self.width) % self.width
        start_row = (down_shift + self.height) % self.height
        #print("rs = " + str(right_shift) + ", ds = " + str(down_shift))
        #print("sc = " + str(start_col) + ", sr = " + str(start_row))
        index = ((self.height - down_shift) % self.height)*self.width - right_shift
        if right_shift > 0:
            index += self.width
        list = []
        for row in range(self.height):
            if row == start_row and index >= self.width:
                index -= self.height*self.width
            for col in range(self.width):
                # Special case for not adjusting is if this is the first element
                if col == start_col and not (row == 0 and right_shift == 0):
                    index -= self.width
                #print(str(row) + "," + str(col) + "=" + str(index))
                if self.getOccupancyGridLoc(col, row) == 1:
                    list.append(index)
                index += 1
            index += self.width
        return list

    # Simple print function
    def printField(self):
        for row in range(self.height):
            for col in range(self.width):
                #print(str(self.occupancyGrid[row][col]), end="")
                print(str(self.getOccupancyGridLoc(col, row)), end="")
                if col < self.width - 1:
                    print("-",end="")
            print()
            if row < self.height - 1:
                for col in range(2*self.width):
                    if col < 2*self.width - 1:
                        if col % 2 == 0:
                            print("|",end="")
                        else:
                            print(" ",end="")
                print()