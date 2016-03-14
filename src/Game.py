"""
File that holds the essential methods for solving a sudoku puzzle
"""
# Import the needed libraries
import Graphics, GameController, Utils
import random, sys, copy, time, math
from __builtin__ import True

# Create initial assignment
initialAssignment = [
[0, 8, 0, 0, 0, 0, 2, 0, 0],
[0, 0, 0, 0, 8, 4, 0, 9, 0],
[0, 0, 6, 3, 2, 0, 0, 1, 0],
[0, 9, 7, 0, 0, 0, 0, 8, 0],
[8, 0, 0, 9, 0, 3, 0, 0, 2],
[0, 1, 0, 0, 0, 0, 9, 5, 0],
[0, 7, 0, 0, 4, 5, 8, 0, 0],
[0, 3, 0, 7, 1, 0, 0, 0, 0],
[0, 0, 8, 0, 0, 0, 0, 4, 0]
]

# Dictionary to hold list of not set numbers (variables) and their respective domains
initialDomains = {}

# List of initial variables
initialVariables = []

# List to hold constants 
constants = []

def countConflicts(assignment, position, value):
    """
    Nearly identical to the isConsistant function; made separate so that isConsistant can return False early on.
    Counts how many constraints a potential addition would violate.
    """
    
    # Create count variable
    count = 0
    
    # Get the row and column of the variable
    row = position[0]
    column = position[1]

    # Check three-by-three squares
    nearRow = row - (row % 3)
    nearColumn = column - (column % 3)
    
    for i in range(0, 3):
        for j in range(0, 3):
            if value == assignment[nearRow + i][nearColumn + j]:
                count += 1
    
    # Returns 0 if no constraints were violated
    return count

def isConsistant(assignment, position, value):
    """
    Determines whether a state would be consistent with the addition of a number at a position
    """
    
    # Get the row and column of the variable
    row = position[0]
    column = position[1]
    
    # Check rows and columns
    for i in range(0, 9):
        if value == assignment[i][column] or value == assignment[row][i]:
            return False

    # Check three-by-three squares
    nearRow = row - (row % 3)
    nearColumn = column - (column % 3)
    
    for i in range(0, 3):
        for j in range(0, 3):
            if value == assignment[nearRow + i][nearColumn + j]:
                return False
    
    # Return True if no constraints were violated
    return True

def getArcs(domains, variable, isTail):
    """
    Returns all arcs related to a variable, and whether the variable should be the head or tail.
    Arcs returned in a list containing tuples of the form (tail, head).
    """
    
    # Initiate empty list for arcs and positions covered (needed to prevent overlap)
    arcs, added = [], []
    
    # Get the row and column of the variable
    row, column = variable
           
    # Add row and column arcs
    for i in range(0, 9):
        
        # Create temporary arc variable for readability
        arc = (row, i)
          
        # Add rows
        if arc in domains and arc != variable:
            arcs.append( (variable, arc) ) if isTail else arcs.append( (arc, variable) )
            added.append( arc )
        
        # Update temporary arc variable for readability
        arc = (i, column)
        
        # Add columns
        if arc in domains and arc != variable:
            arcs.append( (variable, arc) ) if isTail else arcs.append( (arc, variable) )
            added.append( arc )
            
    # Add 3x3 squares
    nearRow = row - (row % 3)
    nearColumn = column - (column % 3)
    
    for i in range(0, 3):
        for j in range(0, 3):
            
            # Create temporary variable to hold prospective position
            arc = (nearRow + i, nearColumn + j)
            
            # Only add variable if it is not a constant, it is not at the input position, and it is not in arcs already
            if arc in domains and arc != variable and not arc in added:
                arcs.append( (variable, arc) ) if isTail else arcs.append( (arc, variable) )
                added.append(arc)
    
    # Return the generated arcs
    return arcs

def backtrackingSearch(csp, conflicted):
    """
    Holder function to run the recursive search that takes a CSP of the form (assignment, domains)
    """
    return recursiveBacktracking(csp, conflicted)

def recursiveBacktracking(csp, conflicted):   
    """
    Recursive backtracking function that takes a CSP of the form (assignment, domains),
    and a list of not yet set variables (for efficiency)
    """ 

    # If every variable is assigned, return assignment (solution)
    if not conflicted:
        return csp[0]
    
    # Unpack the CSP
    assignment, domains = csp
    
    # Enforce arc consistency
    modifiedDomains = AC3(domains) if GameController.arcConsistency else domains
    
    # Return failure if any of the domains are empty
    for v in modifiedDomains:
        if domains[v] == []:
            return -1
    
    # Update the domains
    domains = modifiedDomains
    
    # Show the puzzle to the screen
    Graphics.showPuzzle(assignment)
    
    # Pop a variable (without any kind of order)
    variable = conflicted.pop()
    
    # Assign row and column for readability
    row, column = variable
    
    # Loop through all values in the variable's domain
    for value in domains[variable]:
       
        # Check if adding the value would break a constraint
        if isConsistant(assignment, variable, value):
            
            # Update the assignment
            assignment[row][column] = value   
            
            # Implement forward checking, using the getArcs() method (not elegant, but reuses function)
            pruned = []
            for arc in getArcs(domains, variable, False):
                
                # Make sure forward checking is turned on
                if not GameController.forwardChecking:
                    continue
                
                # Get the connected variable, and its components
                var = arc[0]
                tailRow, tailColumn = var
                
                # Prune its domain, if it contains the value, and is not yet assigned
                if value in domains[var] and assignment[tailRow][tailColumn] == 0:
                    domains[var].remove(value)
                    pruned.append(var)               
                    
            # Create CSP tuple for recursive call            
            csp = (assignment, domains) 
            
            # Add the recursive call
            result = recursiveBacktracking(csp, conflicted)
            
            # Only return result if it is not failure
            if result != -1:
                return result
            
            # Reset the assignment
            assignment[row][column] = 0
                       
            # Reset forward-checking
            for var in pruned:
                domains[var].append(value)           
    
    # Add back the variable that was popped off
    conflicted.append(variable)  
    
    # If it is a dead-end, return failure      
    return -1

def removeInconsistantValues(arc, domains):
    """
    Function that alters the domain to enforce arc consistency, and returns true if any deletions occur
    """
    
    # Create boolean to signal whether any deletions have occurred
    removed = False
    
    # Get the arc's components
    (tail, head) = arc
    
    # Loop through all values for the tail variable
    for v1 in domains[tail]:
        
        # Variable that changes when a possible value is found
        anyPossible = False
        
        # Loop through all values for the head variable
        for v2 in domains[head]:
            
            # If a consistent value is found, adjust the anyPossible variable
            if v1 != v2: anyPossible = True
        
        # If no variable choices exist, remove the value being tested from the tail's domain
        if not anyPossible:
            
            # Mark that a value was deleted
            removed = True
            
            # Because the dictionary was passed by "name" (reference), this deletion is sufficient
            domains[tail].remove(v1)  

    # Return the the removed boolean
    return removed

def AC3(d):
    """
    Enforces arc consistency over the entire graph, and returns the adjusted domains
    """
    
    # Deep-copy the domains
    domains = copy.deepcopy(d)
    
    # Initialize the queue and push all of the arcs
    arcs = Utils.Queue()
    
    # Push arcs (both directions) for all variables
    for variable in domains:
        for i in getArcs(domains, variable, True):
            arcs.push(i)
        for j in getArcs(domains, variable, False):
            arcs.push(j)
          
    # While there are still arcs in the queue, enforce consistency
    while not arcs.isEmpty():
        
        # Pop off the first arc in the queue, and assign tail and head values for readability
        arc = arcs.pop()
        (tail, head) = arc  # Tail included for readability; not used
        
        # If any deletions were performed (a value was removed from the tail's domain)
        if removeInconsistantValues(arc, domains):
            
            # Add the additional arcs that would be impacted by the deletion
            additionalArcs = getArcs(domains, head, False)
            for a in additionalArcs:
                arcs.push(a)

    # Return the modified domains
    return domains

def assessValue(assignment):
    """
    Count the total number of conflicts in an assignment

    """
    
    print assignment
    
    # List to holds lists of columns, rows, and squares
    related = []
    
    # Add rows and columns
    for i in range(0, 9):
        
        # Create list for the row
        row = []
        column = []
        
        # Add all items in the row
        for j in range(0,9):
            row.append(assignment[i][j])
            column.append(assignment[j][i])
            
        related.extend([row, column])
    
    # Add 3x3 squares 
    squareStarts = [(0,0), (0,2), (0,5), (2,0), (2,2), (2,5), (5,0), (5,2), (5,5)]
    
    for start in squareStarts:
        square = []
        for i in range(0, 3):
            for j in range(0, 3):
                square.append(assignment[start[0] + i][start[1] + j])
        related.append(square)
        
    # Initialize count variable
    count = 0
    
    # Find number of conflicts
    for group in related:
        count += ( len(group) - len(set(group)) )
    
    # Return the final count
    return count

def simulatedAnnealing(csp, variables, schedule):
    """
    Min-conflicts with a factor of randomness approach. Schedule is a mapping of time to temperature
    """
    # Unpack the CSP
    assignment, domains = csp
    
    # Create list of conflicted variables
    conflictedList = []
    
    # Iterate through list, randomly assign numbers, and add conflicted variables to array
    for var in variables:

        # Randomly assign number
        num = random.randint(1,9)
        
        # Check if random number violates constraints, and add it to list if it does
        if not isConsistant(assignment, var, num):
            conflictedList.append(var)
        
        # Update the stack to include the new number, whether it works or not
        assignment[var[0]][var[1]] = num
    
    # Duplicate the variable for readability    
    current = assignment
    
    # Initialize time variable
    t = 1
    
    # Slowly increment the time
    while t < 100**100:
        
        # Set the temperature based on the passed schedule
        temp = schedule[t]
        
        # Cannot divide by zero - return the current assignment
        if temp == 0 or assessValue(current) == 0:
            return assignment
        
        # Randomly assign number
        num = random.randint(1,9)
        
        # Randomly choose a variable from the list
        (row, column) = random.choice(variables) 
        
        # Get the random successor state, and duplicate assignment
        prospective = assignment
        prospective[row][column] = num
        
        # Find the change in E
        valueChange = assessValue(current) - assessValue(prospective)
        
        # If there is a positive energy change, then update the current state
        if valueChange > 0:
            current = prospective
        else: 
            
            # With some probability (depending on change in E and temperature), step backwards
            if random.randint(1, math.e**(valueChange/temp)) == 1:
                current = prospective  
        
        Graphics.showPuzzle(assignment)
        
        # Increment time
        t += 1
    
    # Return failure
    return -1

def minConflicts(csp, variables):
    """
    Min-conflicts approach to solving the Sudoku puzzle
    """
    
    assignment, domains = csp  # Domains not applicable for this problem, but included for readability
    
    # Iterate through list, and randomly assign numbers
    for var in variables:

        # Randomly assign number
        num = random.randint(1,9)
        
        # Update the stack to include the new number, whether it works or not
        assignment[var[0]][var[1]] = num
    
    
    # Loop while the problem is not solved
    while variables != []:
        
        Graphics.showPuzzle(assignment)
        
        print variables
        
        # Randomly choose a variable from the list
        var = random.choice(variables)
        
        # Create value for least-conflict value
        bestValue, leastConstraints = None, sys.maxsize
        
        # Loop over possible domain values, and update best value if applicable
        for value in range(1,10):
            conflicts = countConflicts(assignment, var, value)
            if conflicts < leastConstraints:
                bestValue, leastConstraints = value, conflicts
        
        # Update the state with the new value
        assignment[var[0]][var[1]] = bestValue
        
        # If the variable does not violate any constraints, remove it from conflicted
        if leastConstraints == 0:
            variables.remove(var) 
            
    print "Solution Found!"
    
    return assignment

def init():
    "Initialize all of the lists and dictionaries"
    
    # Load variables into list in the form (row, column)
    for i in range(0, len(initialAssignment)):
        for j in range(0, len(initialAssignment[0])):
            if initialAssignment[i][j] == 0:
                initialDomains[(i,j)] = list(xrange(1, 10))
                initialVariables.append((i,j))
            else:
                constants.append((i,j))
    
    # Delete constants from appropriate domains
    for const in constants:
        connectedArcs = getArcs(initialDomains, const, False)
        for arc in connectedArcs:
            value = initialAssignment[const[0]][const[1]]
            if value in initialDomains[arc[0]]:
                initialDomains[arc[0]].remove(value)

# Run initialization function 
init()

# Create CSP for readability
csp = (initialAssignment, initialDomains)

# Fill the schedule for simulated annealing
schedule = []
i = 0
while i < 100*100:
    schedule.append(i/100 + 1)
    i += 1
    
if GameController.simulatedAnnealing:
    solution = simulatedAnnealing(csp, initialVariables, schedule)
else:
    # Run the selected algorithm with the puzzle
    solution = backtrackingSearch(csp, initialVariables) if GameController.backtrackingSearch else minConflicts(csp, initialVariables)

# Show the answer on the screen
Graphics.showPuzzle(solution)

# Pause until the user exits
while True:
    time.sleep(1)



