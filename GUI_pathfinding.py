#gui A* Djikstra
import pygame
import math
from queue import PriorityQueue
from random import randint
pygame.init()

WIDTH = 600    # dimentions:    350 w 50 w 100,  50 w 50         w : width of the grid
WIN = pygame.display.set_mode((WIDTH*2 + 500, WIDTH + 100))
pygame.display.set_caption("GUI Path Finding Algorithms")

font = pygame.font.SysFont("arial", 50) # font of the random button text

RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (250, 250, 250)
BLACK = (0, 0, 0)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
GREYWHITE = (172, 172, 172)

class Spot:
	def __init__(self, row, col, width, total_rows, x, y):
		self.row = row
		self.col = col
		self.x = x
		self.y = y
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = YELLOW

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = [] #       this - 1 is because col and row are used as index so they are - 1 compared to total
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # if there is a spot, not barrier, DOWN self
			self.neighbors.append(grid[self.row + 1][self.col]) # append the spot in neighbors

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # if there is a spot, not barrier, UP self
			self.neighbors.append(grid[self.row - 1][self.col]) # append the spot in neighbors

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # if there is a spot, not barrier, RIGHT self
			self.neighbors.append(grid[self.row][self.col + 1]) # append the spot in neighbors

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # if there is a spot, not barrier, LEFT self
			self.neighbors.append(grid[self.row][self.col - 1]) # append the spot in neighbors


def h(p1, p2):
    '''inputs are (rows, cols) of spots to calculate the distance between the 2 spots'''
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()

def algorithm(draw, grid, start, alg, end = None):
    ''' A* use 3 functions, h + g = f where h is the shortest path from the current spot to the end spot and
        g is shortest path from the start spot to the current spot, A* use the f score to find the shortest path
        Djikstra is slower than A* but work without knowing where is the end, this is why end = None,
        it works like A* but without h (and f useless since f = g without h)
        so every neighbors are inspected until we found the end '''
    is_possible = None  # it will break the loop if it found a path (either way the algorithm will close every spot and won't stop)
    if is_possible == None:                
        count = 0
        open_set = PriorityQueue() # efficient way to get the minimum element from this queue
        open_set.put((0, count, start)) # put the start spot in the open set
        came_from = {}  #   to reconstruct the path

        g_score = {spot : float("inf") for col in grid for spot in col} # if no score yet, set score to infinity
        g_score[start] = 0  # from start to start the distance is 0
        if alg == "A*": # f score is only needed in A*
            f_score = {spot : float("inf") for col in grid for spot in col} # if no score yet, set score to infinity
            f_score[start] = h(start.get_pos(), end.get_pos())
        open_set_hash = {start} # to check what is inside the open_set

        while not open_set.empty() and is_possible == None: #   main loop of the algorithm
            for event in pygame.event.get(): # to quit while the algorithm is working
                if event.type == pygame.QUIT:
                    pygame.quit()

            current = open_set.get()[2] # = current spot object (0 being the f or g score and 1 the count of the spot) + remove it from queue
            open_set_hash.remove(current)

            if current.is_end(): # if current is end
                reconstruct_path(came_from, current, draw)
                start.make_start()
                current.make_end()      
                is_possible = True      # break the main loop

            for neighbor in current.neighbors:  # inspectation of every neighbor of current
                temp_g_score = g_score[current] + 1 # g score of actually inspected spot (neighbor)

                if temp_g_score < g_score[neighbor]: # if we found better path, remember the scores are set to inf by default
                    came_from[neighbor] = current # update the dictionary for the path
                    g_score[neighbor] = temp_g_score # update the best score found

                    if alg == "A*": # A* use f score but not Djikstra
                        f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                    if neighbor not in open_set_hash:   #   we use open_set_hash to verify this condition
                        count += 1
                        if alg == "A*": # add the spot and it's caracteristics to the open_set
                            open_set.put((f_score[neighbor], count, neighbor))  #   remember this queue put the minimum score first
                        elif alg == "Djikstra":
                            open_set.put((g_score[neighbor], count, neighbor))  #   remember this queue put the minimum score first

                        open_set_hash.add(neighbor)
                        if not neighbor.is_end():
                            neighbor.make_open()    #   the green spots represents the next spots that will be inspected

            draw()

            if current != start and not current.is_end(): # so the color of the start and end are never red
                current.make_closed()
        if is_possible != True:
            is_possible = False
    return is_possible

def rand_map(grid1, grid2, rows):
    '''make a random map'''
    num_barriers = randint(rows*2, rows*rows*1//2) # random number of barriers
    
    for col in range(len(grid1)): # in order to reset every spot
        for spot in range(len(grid1[col])):
            grid1[col][spot].reset()
            grid2[col][spot].reset()

    for i in range(num_barriers): # for a number of barriers
        barrier_col = randint(0, rows - 1) # we store row and col of the spot we want to make a barrier
        barrier_row = randint(0, rows - 1)
        barrier = grid1[barrier_col][barrier_row]

        while barrier.is_barrier(): # if the spot is already a barrier 
            barrier_col = randint(0, rows - 1)
            barrier_row = randint(0, rows - 1)
            barrier = grid1[barrier_col][barrier_row] # we change of spot

        barrier1 = grid1[barrier_col][barrier_row]
        barrier2 = grid2[barrier_col][barrier_row]
        barrier1.make_barrier()
        barrier2.make_barrier()

    start_col = randint(0, rows - 1) 
    start_row = randint(0, rows - 1) # we need to store the values to use it twice
    end_col = randint(0, rows - 1)
    end_row = randint(0, rows - 1)

    start = grid1[start_col][start_row]
    start.make_start()
    start2 = grid2[start_col][start_row]
    start2.make_start()
    end = grid1[end_col][end_row]
    end.make_end()
    end2 = grid2[end_col][end_row]
    end2.make_end()

    return start, start2, end, end2

def draw_button(win, font):
    '''draw the random map button'''
    pygame.draw.rect(win,WHITE,(50,250,215,100))
    pygame.draw.rect(win,BLACK,(50,250,215,100),5)
    text = font.render("Random", True, BLACK)
    text2 = font.render("map", True, BLACK)
    win.blit(text, (62, 250))
    win.blit(text2, (101, 285))

def make_grid(rows, width, which_grid):
    '''make a grid without lines but place the spots as they should be placed'''
    grid = [] # 2d list to store every spot by columns (list of columns where columns are lists of spots)
    gap = width // rows # gap between each rows, in other terms the width of the Spots
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            if which_grid == 1: #(row, col, width, totalrows, x, y)
                spot = Spot(i, j, gap, rows, i * gap + 350, j * gap + 50)
            elif which_grid == 2:
                spot = Spot(i, j, gap, rows, i * gap + width + 400, j * gap + 50)
            grid[i].append(spot)
    return grid

def draw_grid(win, rows, width):
    '''draw the lines of the grid but don't place any spot'''
    gap = width // rows
    base_1x = 350
    base_2x = 400 + width
    base_y = 50

    for i in range(rows + 1):
        pygame.draw.line(win, GREY, (base_1x + gap * i, base_y), (base_1x + gap * i, base_y + width)) # vertical
        pygame.draw.line(win, GREY, (base_1x, base_y + gap * i), (base_1x + width, base_y + gap * i)) # horizontal

        pygame.draw.line(win, GREY, (base_2x + gap * i, base_y), (base_2x + gap * i, base_y + width)) # grid 2
        pygame.draw.line(win, GREY, (base_2x, base_y + gap * i), (base_2x + width, base_y + gap * i)) 

def draw(win, grid, rows, width, font):
    '''draw the screen'''
    win.fill(GREYWHITE)  
    police = pygame.font.SysFont("arial", 35) 
    text = police.render("A*", True, BLACK)
    text2 = police.render("DJIKSTRA", True, BLACK)
    win.blit(text, (570, 0))   #   350 w 50 w 100, 50
    win.blit(text2, (1200, 0)) #                   w = 600
    for col in range(len(grid[0])):#               50
        for spot in range(len(grid[0][col])):
            grid[0][col][spot].draw(win)
            grid[1][col][spot].draw(win)
    draw_grid(win, rows, width) 
    draw_button(win, font)
    pygame.display.update()

def get_clicked_pos(pos, rows, width, clicked_grid):
    '''return the row and col of the clicked spot'''
    gap = width // rows
    x, y = pos
    row = (y - 50) // gap
    if clicked_grid == 1: # if clicked in grid 1
        col = (x - 350) // gap # make the right calculus to get col
    else: # if clicked in grid 2
        col = (x - 400 - width) // gap # make the right calculus to get col
    return row, col

def main(win, width):
    ROWS = 50
    grid1 = make_grid(ROWS, width, 1) # the grid take a number as parameter (the interface is a square so the number of rows will be the same as the number of cols)
    grid2 = make_grid(ROWS, width, 2) # both grid are the same, only the position of he spots are different
    grids = [grid1, grid2]
    start = None
    start2 = None
    end = None
    end2 = None
    is_started = False

    run = True
    while run:
        draw(win, grids, ROWS, width, font)
        for event in pygame.event.get(): # to quit pygame
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:# left click
                if not is_started:
                    clicked_grid = None
                    button_clicked = False
                    POS = pygame.mouse.get_pos()    #   get the position so we can try to figure out what was clicked
                    
                    if POS[1] > 250 and POS[1] < 350:    #                                      (50,   250, 215,   100)        
                        if POS[0] > 50 and POS[0] < 265: # if clicked in the random button
                                button_clicked = True

                    if POS[1] > 50  and POS[1] < 50 + width: # if clicked in the y of grids
                        if POS[0] > 350 and POS[0] < 350 + width: # if clicked in grid 1
                            clicked_grid = 1
                        elif POS[0] > 400 + width and POS[0] < 400 + width*2: # if clicked in grid 2
                            clicked_grid = 2
                        
                    if clicked_grid != None:
                        row, col = get_clicked_pos(POS, ROWS, width, clicked_grid)  # the calculus isn't the same depending on the grid clicked
                        spot = grid1[col][row]  #   clicked spot, there is two because of the 2 grids (like with end and start)
                        spot2 = grid2[col][row]
                        if not start and spot != end: # if start is still None make it start
                            start = spot
                            start2 = spot2
                            start.make_start()
                            start2.make_start()

                        elif not end and spot != start: # if end is still None make it end
                            end = spot
                            end2 = spot2
                            end.make_end()
                            end2.make_end()

                        elif spot != start and spot != end: # if end and start != none then make it barrier
                            spot.make_barrier()
                            spot2.make_barrier()

                    if button_clicked:  # if the button has been clicked
                        start, start2, end, end2 = rand_map(grid1, grid2, ROWS)

            elif pygame.mouse.get_pressed()[2]: #   right click
                if not is_started:
                    POS = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(POS, ROWS, width, clicked_grid)
                    spot = grid1[col][row]
                    spot2 = grid2[col][row]
                    spot.reset() # reset the spot
                    spot2.reset()
                    if spot == start:   # reset start if it was start
                        spot = None
                        start = None
                        spot2 = None
                        start2 = None
                    elif spot == end:   # reset end if it was end
                        spot = None
                        end = None
                        spot2 = None
                        end2 = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:   #    run the algorithm
                    for col in range(len(grid1)):
                        for spot in range(len(grid1[col])):
                            grid1[col][spot].update_neighbors(grid1)
                            grid2[col][spot].update_neighbors(grid2)
                    possible = algorithm(lambda: draw(win, grids, ROWS, width, font), grid1, start, "A*", end) # lambda is like a call of function but we can take it as an argument
                    if possible:    # so we don't try 2 times to find a path that doesn't exist
                        algorithm(lambda: draw(win, grids, ROWS, width, font), grid2, start2, "Djikstra")
                    is_started = True
                elif event.key == pygame.K_c:   #   reset everything, clean the grids
                    start = None
                    start2 = None
                    end = None
                    end2 = None
                    is_started = False
                    grid1 = make_grid(ROWS, width, 1)
                    grid2 = make_grid(ROWS, width, 2)
                    grids = [grid1, grid2]

    pygame.quit()

main(WIN, WIDTH)