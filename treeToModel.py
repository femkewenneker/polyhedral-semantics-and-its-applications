'''
Input: a json file in the form as made by treezer.py.
Output: a json file that can be used as input for PolyLogicA

All of the code in this file is based on the code that was written by Gianluca Grilletti
and modified by Mieke Massink to convert mazes into models for PolyLogicA. 
That code has been modified here to convert trees into models, such that the
nodes are square-based pyramids and the branches connect a square to a triangle.

Femke Wenneker, June 20 2025.
'''

import json
import sys
import random


# Auxiliary function to the coordinates in the template to have given x,y,z as the middle point,
# with factors to scale acoording to their height in the tree.
def translateCoords(template, x, y, z, dist):
    z_factor = sum([0.75**i for i in range(z)])
    x_factor = x * z_factor/2
    y_factor = y * z_factor/2
    return [[c[0]/(z+1) + dist*x_factor, c[1]/(z+1) + dist*y_factor, c[2]/(z+1) + dist*z_factor] for c in template]


# Auxiliary function to translate the simplex indices.
def translateSimplexIndices( listOfSimplexIndices, shift ):
  result = [  [ x + shift for x in s ]  for s in listOfSimplexIndices  ]
  return result


# Function that returns the simplexes of a branch.
def simplexesOfBranch(branch):
    sAdd = branch['source'] * POINTS_IN_A_NODE 
    tAdd = branch['target'] * POINTS_IN_A_NODE 
    simplexesPrototype = [
        # [0,1], [1,2], [2,0], [3,4], [4,5], [5,6], [6,4], [3,5]
        [0,3], [1,4], [1,5], [2,6],           # edges (7)
        [0,4], [2,5], [0,6],
        [0,1,4], [1,4,5], [1,2,5], [2,5,6],   # triangles (7)
        [0,2,6], [0,3,6], [0,3,4]
    ]

    pointsMap = {}
    if branch["index_to_source"] % 4 == 2:
        pointsMap = {
            0: sAdd+1,
            1: sAdd+4,
            2: sAdd+0,
            3: tAdd+1,
            4: tAdd+2,
            5: tAdd+3,
            6: tAdd+0
        }
    elif branch["index_to_source"] % 4 == 1:
        pointsMap = {
            0: sAdd+1,
            1: sAdd+4,
            2: sAdd+2,
            3: tAdd+1,
            4: tAdd+0,
            5: tAdd+3,
            6: tAdd+2
        }
    elif branch["index_to_source"] % 4 == 0:
        pointsMap = {
            0: sAdd+2,
            1: sAdd+4,
            2: sAdd+3,
            3: tAdd+2,
            4: tAdd+1,
            5: tAdd+0,
            6: tAdd+3
        }
    elif branch["index_to_source"] % 4 == 3:
        pointsMap = {
            0: sAdd+3,
            1: sAdd+4,
            2: sAdd+0,
            3: tAdd+3,
            4: tAdd+2,
            5: tAdd+1,
            6: tAdd+0
        }
    else:
        print("PROBLEM! " + str(branch["target"]) + ", " + str(branch["source"]))
    
    def mapSimplex( vertices ):
        return [ pointsMap[v] for v in vertices ]

    return [ mapSimplex(simp) for simp in simplexesPrototype ]


# Auxiliary function to append lists of values to a string
def stringOfList(vals):
  if len(vals) == 0:
    return '[]'
  result = '['
  for val in vals[:-1]:
    result += str(val) + ','
  result += str(vals[-1])
  result += ']'
  return result

def stringOfNames(vals):
  if len(vals) == 0:
    return '[]'
  result = '['
  for val in vals[:-1]:
    result += '"' + val + '",'
  result += '"' + str(vals[-1]) + '"'
  result += ']'
  return result


# Function that writes results of the model to treeModel.json.
def write_model():
    with open('treeModel.json', "w") as outputFileModel:
        # prepare output of treeModel.json
        print("Encoding of the model in the output string...")
        outputFileModel.write('{\n')
        outputFileModel.write('"numberOfPoints": ' + str( NUMBER_OF_NODES * POINTS_IN_A_NODE ) + ',\n')
        outputFileModel.write('"coordinatesOfPoints": [\n')
        print("Saving the coordinates of points.")
        for coords in coordinatesOfPoints[:-1]:
            outputFileModel.write('  ' + stringOfList(coords) + ',\n')
        outputFileModel.write('  ' + stringOfList(coordinatesOfPoints[-1]) + '\n')
        outputFileModel.write('],\n')
        print("Saving the atom names.")
        outputFileModel.write('"atomNames": ' + stringOfNames( atomNames + ["branch"] ) + ',\n')
        outputFileModel.write('"simplexes": [\n')
        print("Saving the simplexes:")
        for id, simplex in enumerate(listOfSimplexes[:-1]):
            # print("=> Saving simplex number " + str(id))
            outputFileModel.write('  {\n')
            outputFileModel.write('    "id": "s' + str(id) + '",\n')
            outputFileModel.write('    "points": ' + stringOfList(simplex) + ',\n')
            if id < INDEX_BRANCH_SIMPLEXES:
                outputFileModel.write('    "atoms": ' + stringOfNames( [atom for atom in atomNames if atomEval[atom][id//SIMPLEXES_IN_A_NODE] ] ) + '\n')
            else:
                outputFileModel.write('    "atoms": [ "branch" ]\n')
            outputFileModel.write('  },\n')
        id = len(listOfSimplexes)
        simplex = listOfSimplexes[-1]
        outputFileModel.write('  {\n')
        outputFileModel.write('    "id": "s' + str(id) + '",\n')
        outputFileModel.write('    "points": ' + stringOfList(simplex) + ',\n')
        if id < NUMBER_OF_NODES * SIMPLEXES_IN_A_NODE:
            outputFileModel.write('    "atoms": ' + stringOfNames( [atom for atom in atomNames if atomEval[atom][id//SIMPLEXES_IN_A_NODE] ] ) + '\n')
        else:
            outputFileModel.write('    "atoms": [ "branch" ]\n')
        outputFileModel.write('  }\n')

        outputFileModel.write(']\n')
        outputFileModel.write('}')
        print("Model encoded successfully!")    


# Function that writes the results of the atoms to treeAtoms.json.
def write_atoms():
    with open('treeAtoms.json', "w") as outputFileModel:
        outputFileModel.write('{\n')
        for atom in atomNames[:-1]:
            outputFileModel.write('  "' + atom + '": [\n')
            for val in atomEval[atom]:
                if val:
                    outputFileModel.write('    true,\n' * SIMPLEXES_IN_A_NODE)
                else:
                    outputFileModel.write('    false,\n' * SIMPLEXES_IN_A_NODE)
            outputFileModel.write('    false,\n' * (NUMBER_OF_BRANCHES * SIMPLEXES_IN_A_BRANCH -1) + 'false\n')
            outputFileModel.write('  ],\n')
        atom = atomNames[-1]
        outputFileModel.write('  "' + atom + '": [\n')
        for val in atomEval[atom]:
            if val:
                outputFileModel.write('    true,\n' * SIMPLEXES_IN_A_NODE)
            else:
                outputFileModel.write('    false,\n' * SIMPLEXES_IN_A_NODE)
        else:
            outputFileModel.write('    false,\n' * (NUMBER_OF_BRANCHES * SIMPLEXES_IN_A_BRANCH -1) + 'false\n')
        outputFileModel.write('  ],\n')

        # Added line for "branch" atom
        outputFileModel.write('  "' + "branch" + '": [\n')
        outputFileModel.write('    false,\n' * (NUMBER_OF_NODES * SIMPLEXES_IN_A_NODE))
        outputFileModel.write('    true,\n' * (NUMBER_OF_BRANCHES * SIMPLEXES_IN_A_BRANCH -1) + 'true\n')
        outputFileModel.write('  ]\n')
        outputFileModel.write('}')



if __name__ == "__main__":
    # load tree file
    with open(sys.argv[1]) as f:
        treeData = json.load(f)
        nodesData = treeData["nodes"]
        linksData = treeData["links"]


        ''' Gather standard numbers for nodes and branches: '''

        POINTS_IN_A_NODE        = 5          # 5 corners points of the node
        EDGES_IN_A_NODE         = 9          # 8 ribs and 1 diagonal
        TRIANGLES_IN_A_NODE     = 7          # 6 on the sides of the node and 1 inside
        TETHRAEDRONS_IN_A_NODE  = 2          # 2 tetrahedra inside the node
        SIMPLEXES_IN_A_NODE     = POINTS_IN_A_NODE + EDGES_IN_A_NODE + TRIANGLES_IN_A_NODE + TETHRAEDRONS_IN_A_NODE
        # Total nr of cells for one single node:   5 + 8 + 7 + 2 = 22

        TRANSLATE_DISTANCE_NODES  = 10

        NUMBER_OF_NODES = len(nodesData)
        NUMBER_OF_BRANCHES = len(linksData)

        POINTS_IN_A_BRANCH        = 0
        EDGES_IN_A_BRANCH         = 7   # 4 edges outside and 3 inside
        TRIANGLES_IN_A_BRANCH     = 7+0  # 7 on the sides of the branch and 0? inside
        TETHRAEDRONS_IN_A_BRANCH  = 0   # 0? tetrahedra inside the branch
        SIMPLEXES_IN_A_BRANCH     = POINTS_IN_A_BRANCH + EDGES_IN_A_BRANCH + TRIANGLES_IN_A_BRANCH + TETHRAEDRONS_IN_A_BRANCH

        INDEX_NODE_SIMPLEXES = 0
        INDEX_BRANCH_SIMPLEXES = NUMBER_OF_NODES * SIMPLEXES_IN_A_NODE



        ''' Make the template for the points and simplexes of the nodes: '''

        # generate grid of points of a default node
        nodePointCoords = [ #[0,0,0],    # Point in the middle of the node
            [-2,-2,-2], [-2,2,-2], [2,2,-2], [2,-2, -2], # bottom square
            [0, 0, 2]                                    # upper corner
        ]

        # generate the simplexes of a default node
        nodeZeroSimplexes   = [ [i] for i in range(len(nodePointCoords))] 

        nodeOneSimplexes = [
            [ 0, 1], [ 1, 2], [ 2, 3], [ 3, 0],             # bottom edges
            [ 0, 4], [ 1, 4], [ 2, 4], [ 3, 4],             # upper edges
            [ 0, 2]                                         # diagonal edges outside 
        ]

        nodeTwoSimplexes    = [ 
            [0,1,2],[0,2,3],
            [0,3,4],[0,1,4],
            [1,2,4],[2,3,4],
            [0,2,4]
        ]

        nodeThreeSimplexes  = [[0,1,2,4],[0,2,3,4]]


        ''' Get the information for treeModel.json: '''

        # Fill the coordinates of  points.
        coordinatesOfPoints = []
        for node in nodesData:
            resTranslation = translateCoords(nodePointCoords, node['coord']['x'], node['coord']['y'], node['coord']['z'], TRANSLATE_DISTANCE_NODES)
            coordinatesOfPoints.extend(resTranslation)

        # Fill the list of simplexes with the node and branch data
        listOfSimplexes = []
        # add simplexes of nodes
        for nodeIndex in range( NUMBER_OF_NODES ):
            listOfSimplexes.extend( translateSimplexIndices( nodeZeroSimplexes , nodeIndex * POINTS_IN_A_NODE ) )
            listOfSimplexes.extend( translateSimplexIndices( nodeOneSimplexes  , nodeIndex * POINTS_IN_A_NODE ) )
            listOfSimplexes.extend( translateSimplexIndices( nodeTwoSimplexes  , nodeIndex * POINTS_IN_A_NODE ) )
            listOfSimplexes.extend( translateSimplexIndices( nodeThreeSimplexes, nodeIndex * POINTS_IN_A_NODE ) )
        # add 1-simplexes of branches
        for branch in linksData:
            listOfSimplexes.extend( simplexesOfBranch(branch) )



        ''' Get the information for treeAtoms.json: '''

        # Collect names of atoms data
        atomNames = []
        for node in nodesData:
            for atom in node["atoms"]:
                if atom not in atomNames:
                    atomNames.append(atom)

        # Atoms assigned to the nodes
        atomEval = {}
        for atom in atomNames:
            atomEval[atom] = [False for _ in range(NUMBER_OF_NODES)]
        for node in nodesData:
            nodeIndex = node['index']
            for atom in node["atoms"]:
                atomEval[atom][nodeIndex] = True

        ''' Write all information in the correct formats to the files: '''
        write_model()
        write_atoms()

