import pygame
import sys
import time  # If you want to use delays

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Set the width and height of the screen [width, height]
SIZE = (400, 400)

# Function to print the puzzle
def printPuzzle(state):
    print "Puzzle:"
    for i in range(0, len(state)):      
        print "\n"
        for j in range(0, len(state[0])):
            sys.stdout.write(" " + str(state[i][j]))   
            
# Function to show the puzzle graphic
def showPuzzle(state):
    
    # Define constants
    WIDTH, HEIGHT, MARGIN = SIZE[0]/9, SIZE[1]/9, 12
    BIG_WIDTH, BIG_HEIGHT = WIDTH * 3, HEIGHT * 3
    
    # Set graphics settings and initiate GUI
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Sudoku Solver")
    myfont = pygame.font.SysFont("monospace", 25)
    
    screen.fill(WHITE) 
    
    # Draw the small grid
    for row in range(9):
        for column in range(9):
            color = BLACK
            pygame.draw.rect(screen,
                             color,
                             [WIDTH * column,
                              HEIGHT * row,
                              WIDTH,
                              HEIGHT], 2)
            # Render text
            number = state[row][column] if state[row][column] != 0 else ""
            label = myfont.render(str(number), 1, BLACK)
            screen.blit(label, ((WIDTH) * column + MARGIN, (HEIGHT) * row + MARGIN))
    
    # Draw larger grid in green
    for row in range(3):
        for column in range(3):
            color = BLACK
            pygame.draw.rect(screen,
                             color,
                             [(BIG_WIDTH) * column,
                              (BIG_HEIGHT) * row,
                              BIG_WIDTH,
                              BIG_HEIGHT], 5)
    
    # Add changes to the screen        
    pygame.display.flip()
    