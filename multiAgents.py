# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and Pieter 
# Abbeel in Spring 2013.
# For more info, see http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html

from util import manhattanDistance
from game import Directions
import random, util
from util import *

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        #print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        ##print newScaredTimes
        ##print dir(newFood)
        ##print "\n\n"
        "*** YOUR CODE HERE ***"
        maxint = 1000000
        score = 0
        dis = 0
        directions = [(1,0), (-1,0), (0,1), (0,-1)]


        def getdistance(pos1,pos2):
            return abs(pos1[0]-pos2[0])+abs(pos1[1]-pos2[1])
            #return pow((pos1[0]-pos2[0]),2)+pow((pos1[1]-pos2[1]),2)

        def nearstFoodDis(pos):
            queue = util.Queue()
            queue.push((pos[0], pos[1], 0))
            closed = set()
            closed.add((pos[0], pos[1]))
            while not queue.isEmpty():
              x, y, dis = queue.pop()
              for dx, dy in directions:
                  newx = x + dx
                  newy = y + dy
                  if (newx, newy) not in closed and (newx>=0 and newy>=0 and newx<newFood.width and newy<newFood.height) and not successorGameState.hasWall(newx, newy):
                      if successorGameState.hasFood(newx, newy):
                          return dis+1
                      closed.add((newx, newy))
                      queue.push((newx, newy, dis+1))

        if successorGameState.isWin():
            return maxint

        ghostPositions = successorGameState.getGhostPositions()
        for i in range(len(ghostPositions)):
            ghostPosition = ghostPositions[i]
            ghostScaredTime = newScaredTimes[i]
            tmp = getdistance(newPos, ghostPosition)
            if ghostScaredTime>0:
                if tmp<1:
                    score = maxint
                    break
            else:
                if tmp<2:
                    score = -maxint
                    break
            #dis += tmp
            
        mindis = maxint
        for i in range(newFood.width):
            for j in range(newFood.height):
                ##print (i, j)
                if newFood[i][j]:
                   mindis = min(mindis, abs(newPos[0]-i)+abs(newPos[1]-j))
        if mindis == maxint:
            mindis = 0
        
        walls = successorGameState.getWalls()
        wallCount = 0
        for dx, dy in directions:
            if walls[newPos[0]+dx][newPos[1]+dy]:
                wallCount += 1

        score += successorGameState.getScore()-nearstFoodDis(newPos)*0.01; #mindis*0.5-wallCount*0.25
        return score

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        maxint = 1000000
        numAgents = gameState.getNumAgents()

        def min_value(state, agentIndex, d):
            #print "Minimizer: "+str(agentIndex)
            v = maxint
            actions = state.getLegalActions(agentIndex)
            #if Directions.STOP in actions:
            #    actions.remove(Directions.STOP)
            next_states = [state.generateSuccessor(agentIndex, action) for action in actions]
            for next_state in next_states:
                v = min(v, value(next_state, (agentIndex+1)%numAgents, d+1))
            #print "Agent: "+ str(agentIndex)+" Min: "+str(v)
            return v
        
        def max_value(state, agentIndex, d):
            #print "Maximizer: "+str(agentIndex)
            v = -maxint
            actions = state.getLegalActions(agentIndex)
            #if Directions.STOP in actions:
            #    actions.remove(Directions.STOP)
            next_states = [state.generateSuccessor(agentIndex, action) for action in actions]
            for next_state in next_states:
                v = max(v, value(next_state, (agentIndex+1)%numAgents, d+1))
            #print "Agent: "+ str(agentIndex)+" Max: "+str(v)
            return v
        
        def value(state, agentIndex, d):
            if state.isWin() or state.isLose() or d > self.depth*numAgents:
                return self.evaluationFunction(state)
            if agentIndex>0:
                return min_value(state, agentIndex, d)
            else:
                return max_value(state, agentIndex, d)

        bestVal = -maxint
        bestAct = None
        actions = gameState.getLegalActions()
        #if Directions.STOP in actions:
        #    actions.remove(Directions.STOP)
        for action in actions:
            next_state = gameState.generateSuccessor(0, action)
            #print "Doing Minimax Search for "+str(action)
            val = value(next_state, 1, 2)
            if val>bestVal:
                bestVal = val
                bestAct = action
        #print bestAct
        #print bestVal
        
        return bestAct

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        maxint = 1000000
        numAgents = gameState.getNumAgents()

        def min_value(state, alpha, beta, agentIndex, d):
            #print "Minimizer: "+str(agentIndex)
            v = maxint
            actions = state.getLegalActions(agentIndex)
            #if Directions.STOP in actions:
            #    actions.remove(Directions.STOP)
            next_states = [state.generateSuccessor(agentIndex, action) for action in actions]
            for next_state in next_states:
                v = min(v, value(next_state, alpha, beta, (agentIndex+1)%numAgents, d+1))
                if v<alpha: return v
                beta = min(beta, v)
            #print "Agent: "+ str(agentIndex)+" Min: "+str(v)
            return v
        
        def max_value(state, alpha, beta, agentIndex, d):
            #print "Maximizer: "+str(agentIndex)
            v = -maxint
            actions = state.getLegalActions(agentIndex)
            #if Directions.STOP in actions:
            #    actions.remove(Directions.STOP)
            next_states = [state.generateSuccessor(agentIndex, action) for action in actions]
            for next_state in next_states:
                v = max(v, value(next_state, alpha, beta, (agentIndex+1)%numAgents, d+1))
                if v>beta: return v
                alpha = max(alpha, v)
            #print "Agent: "+ str(agentIndex)+" Max: "+str(v)
            return v
        
        def value(state, alpha, beta, agentIndex, d):
            if state.isWin() or state.isLose() or d > self.depth*numAgents:
                return self.evaluationFunction(state)
            if agentIndex>0:
                return min_value(state, alpha, beta, agentIndex, d)
            else:
                return max_value(state, alpha, beta, agentIndex, d)

        alpha = -maxint
        beta = maxint
        bestVal = -maxint
        bestAct = None
        actions = gameState.getLegalActions()
        #if Directions.STOP in actions:
        #    actions.remove(Directions.STOP)
        for action in actions:
            next_state = gameState.generateSuccessor(0, action)
            #print "Doing Minimax Search for "+str(action)
            val = value(next_state, alpha, beta, 1, 2)
            alpha = max(alpha, val)
            if val>bestVal:
                bestVal = val
                bestAct = action
        #print bestAct
        #print bestVal
        
        return bestAct

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        maxint = 1000000
        numAgents = gameState.getNumAgents()

        def exp_value(state, agentIndex, d):
            v = 0.0
            actions = state.getLegalActions(agentIndex)
            next_states = [state.generateSuccessor(agentIndex, action) for action in actions]
            for next_state in next_states:
                v += value(next_state, (agentIndex+1)%numAgents, d+1)
            return v/len(next_states)
        
        def max_value(state, agentIndex, d):
            v = -maxint
            actions = state.getLegalActions(agentIndex)
            next_states = [state.generateSuccessor(agentIndex, action) for action in actions]
            for next_state in next_states:
                v = max(v, value(next_state, (agentIndex+1)%numAgents, d+1))
            return v
        
        def value(state, agentIndex, d):
            if state.isWin() or state.isLose() or d > self.depth*numAgents:
                return self.evaluationFunction(state)
            if agentIndex>0:
                return exp_value(state, agentIndex, d)
            else:
                return max_value(state, agentIndex, d)

        bestVal = -maxint
        bestAct = None
        actions = gameState.getLegalActions()
        for action in actions:
            next_state = gameState.generateSuccessor(0, action)
            val = value(next_state, 1, 2)
            if val>bestVal:
                bestVal = val
                bestAct = action
        
        return bestAct

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    score = 0.0
    maxint = 1000000


    gameScore = currentGameState.getScore()
    

    #successorGameState = currentGameState.generatePacmanSuccessor(action)
    pacmanPos = currentGameState.getPacmanPosition()
    capsules = currentGameState.getCapsules()
    food = currentGameState.getFood()
    ghostStates = currentGameState.getGhostStates()
    ghostScaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]
    ghostPositions = currentGameState.getGhostPositions()
    #print ghostScaredTimes

    foodLeft = currentGameState.getNumFood()
    capsulesLeft = len(capsules)
    
    dis = 0
    directions = [(1,0), (-1,0), (0,1), (0,-1)]
    scareTimeSum = sum(ghostScaredTimes)
    
    #print scareTimeSum
    #score += scareTimeSum*1000
    if currentGameState.isWin():
        #if capsulesLeft!=0:
            #print "hai mei chi wan ne"
            #return -maxint
        #else:
            return gameScore

    def getdistance(pos1,pos2):
        return abs(pos1[0]-pos2[0])+abs(pos1[1]-pos2[1])
        #return pow((pos1[0]-pos2[0]),2)+pow((pos1[1]-pos2[1]),2)


    def nearstFoodDis(pos):
        capDis = 0
        foodDis = 0
        ghostDis = 0
        queue = util.Queue()
        queue.push((pos[0], pos[1], 0))
        closed = set()
        closed.add((pos[0], pos[1]))
        while not queue.isEmpty():
            x, y, dis = queue.pop()
            for dx, dy in directions:
                newx = x + dx
                newy = y + dy
                newpos = (newx, newy)
                if (newx, newy) not in closed and (newx>=0 and newy>=0 and newx<food.width and newy<food.height) \
                and not currentGameState.hasWall(newx, newy):
                    if capDis==0 and newpos in capsules:
                        capDis = dis+1
                    if foodDis==0 and currentGameState.hasFood(newx, newy):
                        foodDis = dis+1
                    if ghostDis==0 and (newx, newy) in ghostPositions:
                        ghostDis = dis+1
                    if (len(capsules)==0 or capDis!=0) and (foodLeft==0 or foodDis!=0):
                        break
                    closed.add(newpos)
                    queue.push((newx, newy, dis+1))
        return capDis, foodDis, ghostDis

    # print pacmanPos
    # print food
    # a=raw_input("Press any key..")
    # #print capsules
    # #print food[pacmanPos[0]][pacmanPos[1]]
    # #print type(food[pacmanPos[0]][pacmanPos[1]])
    # if food[pacmanPos[0]][pacmanPos[1]]:
    #     print "Food!"
    #     score += 3

    # if pacmanPos in capsules: 
    #     print "Capsule!"
    #     score += 5
    
    capDis, foodDis, ghostDis = nearstFoodDis(pacmanPos)

    #foodDis = min(foodDis, capDis)
    
    for i in range(len(ghostPositions)):
        ghostPosition = ghostPositions[i]
        ghostScaredTime = ghostScaredTimes[i]
        tmp = getdistance(pacmanPos, ghostPosition)
        if ghostScaredTime>0:
            if tmp<1:
                score += 200
                break
        else:
            if tmp<1:
                #score = -maxint
                break
        #dis += tmp
        
    # mindis = maxint
    # for i in range(food.width):
    #     for j in range(food.height):
    #         ##print (i, j)
    #         if food[i][j]:
    #            mindis = min(mindis, abs(pacmanPos[0]-i)+abs(pacmanPos[1]-j))
    # if mindis == maxint:
    #     mindis = 0
    
    walls = currentGameState.getWalls()
    wallCount = 0
    for dx, dy in directions:
        if walls[pacmanPos[0]+dx][pacmanPos[1]+dy]:
            wallCount += 1

    if scareTimeSum==0:
        score += -capsulesLeft*50

    score += gameScore-foodDis-foodLeft/2 #-wallCount*0.001 #mindis*0.5-wallCount*0.25
    

    return score
    

# Abbreviation
better = betterEvaluationFunction

class ContestAgent(MultiAgentSearchAgent):
    """
      Your agent for the mini-contest
    """
    def __init__(self, evalFn = 'betterEvaluationFunction', depth = '4'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

    def getAction(self, gameState):
        """
          Returns an action.  You can use any method you want and search to any depth you want.
          Just remember that the mini-contest is timed, so you have to trade off speed and computation.

          Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
          just make a beeline straight towards Pacman (or away from him if they're scared!)
        """
        "*** YOUR CODE HERE ***"
        maxint = 1000000
        numAgents = gameState.getNumAgents()

        def min_value(state, alpha, beta, agentIndex, d):
            #print "Minimizer: "+str(agentIndex)
            v = maxint
            actions = state.getLegalActions(agentIndex)
            #if Directions.STOP in actions:
            #    actions.remove(Directions.STOP)
            next_states = [state.generateSuccessor(agentIndex, action) for action in actions]
            for next_state in next_states:
                v = min(v, value(next_state, alpha, beta, (agentIndex+1)%numAgents, d+1))
                if v<alpha: return v
                beta = min(beta, v)
            #print "Agent: "+ str(agentIndex)+" Min: "+str(v)
            return v
        
        def max_value(state, alpha, beta, agentIndex, d):
            #print "Maximizer: "+str(agentIndex)
            v = -maxint
            actions = state.getLegalActions(agentIndex)
            #if Directions.STOP in actions:
            #    actions.remove(Directions.STOP)
            next_states = [state.generateSuccessor(agentIndex, action) for action in actions]
            for next_state in next_states:
                v = max(v, value(next_state, alpha, beta, (agentIndex+1)%numAgents, d+1))
                if v>beta: return v
                alpha = max(alpha, v)
            #print "Agent: "+ str(agentIndex)+" Max: "+str(v)
            return v
        
        def value(state, alpha, beta, agentIndex, d):
            if state.isWin() or state.isLose() or d > self.depth*numAgents:
                return self.evaluationFunction(state)
            if agentIndex>0:
                return min_value(state, alpha, beta, agentIndex, d)
            else:
                return max_value(state, alpha, beta, agentIndex, d)

        alpha = -maxint
        beta = maxint
        bestVal = -maxint
        bestAct = None
        actions = gameState.getLegalActions()
        #if Directions.STOP in actions:
        #    actions.remove(Directions.STOP)
        for action in actions:
            next_state = gameState.generateSuccessor(0, action)
            #print "Doing Minimax Search for "+str(action)
            val = value(next_state, alpha, beta, 1, 2)
            alpha = max(alpha, val)
            if val>bestVal:
                bestVal = val
                bestAct = action
        #print bestAct
        #print bestVal
        
        return bestAct

