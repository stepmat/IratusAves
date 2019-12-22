from random import randint
from random import uniform
from random import shuffle
from math import sqrt, ceil, atan, atan2, cos, sin, pi, degrees, radians, tan
from copy import deepcopy
import itertools


#-------------------------------------------------------------------------------
# Simple parameters
#-------------------------------------------------------------------------------

# Number of levels to generate
number_levels = 10

# Minimum and Maximum number of pigs
# Number of pigs in a level is selected uniformly at random between these two values
# Value will be reduced automatically if there is not enough space in the level
minimum_number_pigs = 4
maximum_number_pigs = 8

# Weight multiplier on the number of birds in the level
# Increasing or decreasing the value for "number_birds_weight" will affect the levels difficulty
# E.g. increasing this value to 2.0 will give the player twice as many birds as normal (easier level)
number_birds_weight = 1.0

# Weight multiplier on the type of birds in the level
# Increasing the value for a certain bird type increases its likelihood of being given to the player
# E.g. increasing the value for number_blue_birds_weight to 2.0 will give the player twice as many blue birds as normal
# These weights are all considered relative to each other, so increasing all values to 2.0 will make no difference.
number_red_birds_weight = 1.0
number_blue_birds_weight = 1.0
number_yellow_birds_weight = 1.0
number_black_birds_weight = 1.0
number_white_birds_weight = 1.0

# Probability of selecting each block type when generating structures
# Giving higher probabilities to larger blocks will reduce the average number of blocks in a structure, and vice versa.
# The values for these probabilities are all considered relative to each other, so doubling all probabilities will make no difference.
# See Figure 2 of the paper found at the following link, for information about which numbers correspond to which blocks
# https://github.com/stepmat/IratusAves/blob/master/research_papers/(V0.5)%20(CIG16)%20Procedural%20Generation%20of%20Complex%20Stable%20Structures%20for%20Angry%20Birds%20Levels.pdf
probability_table_blocks = {'1':0.11870840863728756, '2':0.1114263927034903, '3':0.037753878358891865, '4':0.050210142536973326,
                            '5':0.06667300685830699, '6':0.07107219573486978, '7':0.07413694113148758, '8':0.11716619240567361,
                            '9':0.048982179880264536, '10':0.11503886132727455, '11':0.015224307126955784,
                            '12':0.15079620524923362, '13':0.02281128804929053}

# Probability of selecting each material when selecting the material for a block
# 1 = wood, 2 = ice, 3 = stone
# The values for these probabilities are all considered relative to each other, so doubling all probabilities will make no difference.
probability_table_materials = {'1':0.4, '2':0.3, '3':0.3}

# Defines local stability requirements (0 = nothing, 1 = edges or middle, 2 = edges only, 3 = edges and middle)
# 0 and 1 may not result in a stable level, 2 guarantees a stable level, 3 gives VERY robust structures
robustness = 2              

# Maximum number of peaks a structure can have
# Number of peaks for a structure is selected uniformly at random between one and this value
# The value for this cannot go higher than 5
max_peaks = 5               

# Minimum and Maximum number of ground structures
# Number of ground structures in a level is selected uniformly at random between these two values
# Value will be reduced automatically if there is not enough space in the level
minimum_number_ground_structures = 1
maximum_number_ground_structures = 3

# Minimum and Maximum number of platform structures
# Number of platform structures in a level is selected uniformly at random between these two values
# Value will be reduced automatically if there is not enough space in the level
minimum_number_platform_structures = 0
maximum_number_platform_structures = 2         

# If additional non-rectangular blocks (i.e. circular and triangular blocks) should be placed on top of structures after they are generated
additional_nonrectangular_blocks = True

# Minimum and Maximum number of TNT boxes
# Number of TNTs in a level is selected uniformly at random between these two values
# Value will be reduced automatically if not enough valid locations are found
minimum_number_TNT = 0
maximum_number_TNT = 3

# If slopes can be added to the generated level
# Not all levels will necessarily contain slopes
add_slopes = True


#-------------------------------------------------------------------------------
# Constants (don't change these values unless you know what you are doing)
#-------------------------------------------------------------------------------

# blocks number and size
blocks = {'1':[0.84,0.84], '2':[0.85,0.43], '3':[0.43,0.85], '4':[0.43,0.43],
          '5':[0.22,0.22], '6':[0.43,0.22], '7':[0.22,0.43], '8':[0.85,0.22],
          '9':[0.22,0.85], '10':[1.68,0.22], '11':[0.22,1.68],
          '12':[2.06,0.22], '13':[0.22,2.06]}

# blocks number and name
# (blocks 3, 7, 9, 11 and 13) are their respective block names rotated 90 degrees clockwise
block_names = {'1':"SquareHole", '2':"RectFat", '3':"RectFat", '4':"SquareSmall",
               '5':"SquareTiny", '6':"RectTiny", '7':"RectTiny", '8':"RectSmall",
               '9':"RectSmall",'10':"RectMedium",'11':"RectMedium",
               '12':"RectBig",'13':"RectBig"}

# additional objects number and name
additional_objects = {'1':"TriangleHole", '2':"Triangle", '3':"Circle", '4':"CircleSmall"}

# additional objects number and size
additional_object_sizes = {'1':[0.82,0.82],'2':[0.82,0.82],'3':[0.8,0.8],'4':[0.45,0.45]}

# materials number and name
materials = {'1':"wood", '2':"ice", '3':"stone"}

# Bird types number and name
bird_types_index = {'0':"BirdYellow", '1':"BirdBlue", '2':"BirdBlack", '3':"BirdRed", '4':"BirdWhite"}

pig_size = [0.5,0.45]    # size of pigs
tnt_size = [0.55,0.55]    # size of TNT
platform_size = [0.62,0.62]     # size of platform sections
absolute_ground = -3.5          # the position of ground within level


#-------------------------------------------------------------------------------
# Complex parameters
#-------------------------------------------------------------------------------

# material number and probability of being selected, when used for trajectory based material selection
probability_table_materials_trajectory = {'1':0.5, '2':0.5, '3':0.0}

vul_robustness = 1          # defines the local stability requirements for vulnerability analysis

edge_buffer = 0.11      # buffer used to push edge blocks further into the structure center (increases stability)
check_buffer = 0.05    # buffer used when checking if edges supported

min_peak_split = 10     # minimum distance between two peak blocks of structure
max_peak_split = 50     # maximum distance between two peak blocks of structure

minimum_height_gap = 3.5        # y distance min between platforms
platform_distance_buffer = 0.4  # x_distance min between platforms / y_distance min between platforms and ground structures

pig_precision = 0.01                # how precise to check for possible pig positions on ground

# Identify which additional blocks are allowed within the structure
trihole_allowed = True
tri_allowed = True
cir_allowed = True
cirsmall_allowed = True

# defines the levels area (ie. space within which structures/platforms can be placed)
level_width_min = -3.0
level_width_max = 9.0
level_height_min = -2.0         # only used by platforms, ground structures use absolute_ground to determine their lowest point
level_height_max = 6.0

min_ground_width = 2.5                      # minimum amount of space allocated to ground structure
ground_structure_height_limit = ((level_height_max - minimum_height_gap) - absolute_ground)/1.5    # desired height limit of ground structures

max_attempts = 100                          # number of times to attempt to place a platform, structure, row or pig before abandoning it

# factors that influence pig choice
factor1_weight = 3.0
factor2_weight = 0.002
factor3_distance = 0.8
factor3_bonus = 1.0

# used for trajectory estimation and identifying reachable blocks
trajectory_accuracy = 0.5
number_shots = 50
slingshot_x = -7.7
slingshot_y = -1.0
MAX_X = 20
launchAngle =   [0.13,  0.215, 0.296, 0.381, 0.476, 0.567, 0.657, 0.741, 0.832, 0.924, 1.014, 1.106, 1.197]
changeAngle =   [0.052, 0.057, 0.063, 0.066, 0.056, 0.054, 0.050, 0.053, 0.042, 0.038, 0.034, 0.029, 0.025]
launchVelocity = [2.9,   2.88,  2.866, 2.838, 2.810, 2.800, 2.790, 2.773, 2.763, 2.745, 2.74, 2.735, 2.73]
scale = 1.0
scaleFactor = 1.65

# used for protecting vulnerable blocks
vulnerable_score_threshold = 15     # threshold for determining which blocks are vulnerable (+1 for each affected block, +10 for each affected pig)
buffer_min = 0.1                    # minimum distance that protection stack can be from vulnerable block
buffer_max = 0.5                    # maximum distance that protection stack can be from vulnerable block
height_bonus = 1.0                  # this plus vulnerable block height gives maximum protection stack height
max_number_attempts = 10            # number of attempts to find new block for protection stack
far_left = False                    # uses the structures leftmost point for distance calculations rather than the vulnerable block itself

# used for swapping blocks within structures
prob_swap = 0.5

TNT_placement_threshold = 0.0   # threshold score needed to place TNT

# used when adding hills/slopes
max_slope_angle = 30.
max_slope_height = 1.5
max_slope_increase = 1.0

# used for swapping blocks within structures
block_swapping = True

# used for protecting vulnerable blocks
vulnerability_analysis = True
protection_method1 = True
protection_method2 = True
protection_method3 = True

# used when selecting materials for blocks
small_threshold = 10        # maximum number of blocks for a structure to have all the same material
random_chance = 0.3         # likelihood of material being random
cluster_chance = 0.5        # likelihood of material being in clusters
cluster_swap_prob = 0.2     # likelihood of material changing when forming clusters 
trajectory_chance = 0.8     # likelihood of material being chosen by trajectory analysis
                            # otherwise make material random for each row
                            
#-------------------------------------------------------------------------------






# generates a list of all possible subsets for structure bottom

def generate_subsets(current_tree_bottom):     
    current_distances = []
    subsets = []
    current_point = 0
    while current_point < len(current_tree_bottom)-1:
        current_distances.append(current_tree_bottom[current_point+1][1] - current_tree_bottom[current_point][1])
        current_point = current_point + 1

    # remove similar splits causesd by floating point imprecision
    for i in range(len(current_distances)):
        current_distances[i] = round(current_distances[i],10)

    split_points = list(set(current_distances))         # all possible x-distances between bottom blocks

    for i in split_points:      # subsets based on differences between x-distances
        current_subset = []
        start_point = 0
        end_point = 1
        for j in current_distances:
            if j >= i:
                current_subset.append(current_tree_bottom[start_point:end_point])
                start_point = end_point
            end_point = end_point + 1

        current_subset.append(current_tree_bottom[start_point:end_point])

        subsets.append(current_subset)

    subsets.append([current_tree_bottom])

    return subsets




# finds the center positions of the given subset

def find_subset_center(subset):
    if len(subset)%2 == 1:
        return subset[(len(subset)-1)//2][1]
    else:
        return (subset[len(subset)//2][1] - subset[(len(subset)//2)-1][1])/2.0 + subset[(len(subset)//2)-1][1]




# finds the edge positions of the given subset

def find_subset_edges(subset):
    edge1 = subset[0][1] - (blocks[str(subset[0][0])][0])/2.0 + edge_buffer
    edge2 = subset[-1][1] + (blocks[str(subset[-1][0])][0])/2.0 - edge_buffer
    return[edge1,edge2]




# finds the inner positions of the given subset

def find_subset_inners(subset):
    inner1 = subset[0][1] - (blocks[str(subset[0][0])][0])/4.0
    inner2 = subset[-1][1] + (blocks[str(subset[-1][0])][0])/4.0
    return[inner1,inner2]




# checks that positions for new block dont overlap and support the above blocks

def check_valid(grouping,choosen_item,current_tree_bottom,new_positions):

    # check no overlap
    i = 0
    while i < len(new_positions)-1:
        if (new_positions[i] + (blocks[str(choosen_item)][0])/2) > (new_positions[i+1] - (blocks[str(choosen_item)][0])/2):
            return False
        i = i + 1

    # check if each structural bottom block supported by new blocks
    for item in current_tree_bottom:
        center = item[1]
        edge1 = item[1] - (blocks[str(item[0])][0])/2 + check_buffer
        edge2 = item[1] + (blocks[str(item[0])][0])/2 - check_buffer
        center_supported = False
        edge1_supported = False
        edge2_supported = False
        for new in new_positions:
            if ((new - (blocks[str(choosen_item)][0])/2) <= center and (new + (blocks[str(choosen_item)][0])/2) >= center):
                center_supported = True
            if ((new - (blocks[str(choosen_item)][0])/2) <= edge1 and (new + (blocks[str(choosen_item)][0])/2) >= edge1):
                edge1_supported = True
            if ((new - (blocks[str(choosen_item)][0])/2) <= edge2 and (new + (blocks[str(choosen_item)][0])/2) >= edge2):
                edge2_supported = True
        if robustness == 1:
            if center_supported == False and (edge1_supported == False or edge2_supported == False):
                return False
        if robustness == 2:
            if edge1_supported == False or edge2_supported == False:
                return False
        if robustness == 3:
            if center_supported == False or edge1_supported == False or edge2_supported == False:
                return False
    return True




# check if new block can be placed under center of bottom row blocks validly

def check_center(grouping,choosen_item,current_tree_bottom):
    new_positions = []
    for subset in grouping:
        new_positions.append(find_subset_center(subset))
    return check_valid(grouping,choosen_item,current_tree_bottom,new_positions)




# check if new block can be placed under edges of bottom row blocks validly

def check_edge(grouping,choosen_item,current_tree_bottom):
    new_positions = []
    for subset in grouping:
        new_positions.append(find_subset_edges(subset)[0])
        new_positions.append(find_subset_edges(subset)[1])
    return check_valid(grouping,choosen_item,current_tree_bottom,new_positions)




# check if new block can be placed under both center and edges of bottom row blocks validly

def check_both(grouping,choosen_item,current_tree_bottom):
    new_positions = []
    for subset in grouping:
        new_positions.append(find_subset_edges(subset)[0])
        new_positions.append(find_subset_center(subset))
        new_positions.append(find_subset_edges(subset)[1])
    return check_valid(grouping,choosen_item,current_tree_bottom,new_positions)




# check if new block can be placed under inners of bottom row blocks validly

def check_inner(grouping,choosen_item,current_tree_bottom):
    new_positions = []
    for subset in grouping:
        new_positions.append(find_subset_inners(subset)[0])
        new_positions.append(find_subset_inners(subset)[1])
    return check_valid(grouping,choosen_item,current_tree_bottom,new_positions)




# check if new block can be placed under both center and inners of bottom row blocks validly

def check_inner_center(grouping,choosen_item,current_tree_bottom):
    new_positions = []
    for subset in grouping:
        new_positions.append(find_subset_inners(subset)[0])
        new_positions.append(find_subset_center(subset))
        new_positions.append(find_subset_inners(subset)[1])
    return check_valid(grouping,choosen_item,current_tree_bottom,new_positions)




# check if new block can be placed under both edges and inners of bottom row blocks validly

def check_inner_edge(grouping,choosen_item,current_tree_bottom):
    new_positions = []
    for subset in grouping:
        new_positions.append(find_subset_edges(subset)[0])
        new_positions.append(find_subset_inners(subset)[0])
        new_positions.append(find_subset_inners(subset)[1])
        new_positions.append(find_subset_edges(subset)[1])
    return check_valid(grouping,choosen_item,current_tree_bottom,new_positions)




# check if new block can be placed under both center, edges and inners of bottom row blocks validly

def check_inner_both(grouping,choosen_item,current_tree_bottom):
    new_positions = []
    for subset in grouping:
        new_positions.append(find_subset_edges(subset)[0])
        new_positions.append(find_subset_inners(subset)[0])
        new_positions.append(find_subset_center(subset))
        new_positions.append(find_subset_inners(subset)[1])
        new_positions.append(find_subset_edges(subset)[1])
    return check_valid(grouping,choosen_item,current_tree_bottom,new_positions)




# choose a random item/block from the blocks dictionary based on probability table

def choose_item(probability_table):
    ran_num = uniform(0.0,1.0)
    selected_num = 0
    while ran_num > 0:
        selected_num = selected_num + 1
        ran_num = ran_num - probability_table[str(selected_num)]
    return selected_num
    
    
    
    
# normalise the values in the specified dictionary to sum to one

def normalise_dictionary(d):
    factor=1.0/sum(d.values())
    for k in d:
        d[k] = d[k]*factor
    return d




# finds the width of the given structure

def find_structure_width(structure):
    min_x = 999999.9
    max_x = -999999.9
    for block in structure:
        if round((block[1]-(blocks[str(block[0])][0]/2)),10) < min_x:
            min_x = round((block[1]-(blocks[str(block[0])][0]/2)),10)
        if round((block[1]+(blocks[str(block[0])][0]/2)),10) > max_x:
            max_x = round((block[1]+(blocks[str(block[0])][0]/2)),10)
    return (round(max_x - min_x,10))



   
# finds the height of the given structure

def find_structure_height(structure):
    min_y = 999999.9
    max_y = -999999.9
    for block in structure:
        if round((block[2]-(blocks[str(block[0])][1]/2)),10) < min_y:
            min_y = round((block[2]-(blocks[str(block[0])][1]/2)),10)
        if round((block[2]+(blocks[str(block[0])][1]/2)),10) > max_y:
            max_y = round((block[2]+(blocks[str(block[0])][1]/2)),10)
    return (round(max_y - min_y,10))




# adds a new row of blocks to the bottom of the structure

def add_new_row(current_tree_bottom, total_tree, new_row_attempts):

    groupings = generate_subsets(current_tree_bottom)   # generate possible groupings of bottom row objects
    choosen_item = choose_item(probability_table_blocks)# choosen block for new row
    center_groupings = []                               # collection of viable groupings with new block at center
    edge_groupings = []                                 # collection of viable groupings with new block at edges
    both_groupings = []                                 # collection of viable groupings with new block at both center and edges
    inner_groupings = []                                # collection of viable groupings with new block at inners
    inner_center_groupings = []                         # collection of viable groupings with new block at both center and inners
    inner_edge_groupings = []                           # collection of viable groupings with new block at both inners and edges
    inner_both_groupings = []                           # collection of viable groupings with new block at center, inners and edges
    
    # check if new block is viable for each grouping in each position
    for grouping in groupings:
        if check_center(grouping,choosen_item,current_tree_bottom):             # check if center viable
            center_groupings.append(grouping)
        if check_edge(grouping,choosen_item,current_tree_bottom):               # check if edges viable
            edge_groupings.append(grouping)
        if check_both(grouping,choosen_item,current_tree_bottom):               # check if both center and edges viable
            both_groupings.append(grouping)
        if check_inner(grouping,choosen_item,current_tree_bottom):              # check if inners viable
            inner_groupings.append(grouping)
        if check_inner_center(grouping,choosen_item,current_tree_bottom):       # check if both center and inners viable
            inner_center_groupings.append(grouping)
        if check_inner_edge(grouping,choosen_item,current_tree_bottom):         # check if both inners and edges viable
            inner_edge_groupings.append(grouping)
        if check_inner_both(grouping,choosen_item,current_tree_bottom):         # check if center, inners and edges are all viable
            inner_both_groupings.append(grouping)

    # randomly choose a configuration (grouping/placement) from the viable options
    total_options = len(center_groupings) + len(edge_groupings) + len(both_groupings) + len(inner_groupings) + len(inner_center_groupings) + len(inner_edge_groupings) + len(inner_both_groupings)   #total number of options
    if total_options > 0:
        option = randint(1,total_options)
        if option > len(center_groupings) + len(edge_groupings) + len(both_groupings) + len(inner_groupings) + len(inner_center_groupings) + len(inner_edge_groupings):
            selected_grouping = inner_both_groupings[option- (len(center_groupings) + len(edge_groupings) + len(both_groupings) + len(inner_groupings) + len(inner_center_groupings) + len(inner_edge_groupings) + 1)]
            placement_method = 6
        elif option > len(center_groupings) + len(edge_groupings) + len(both_groupings) + len(inner_groupings) + len(inner_center_groupings):
            selected_grouping = inner_edge_groupings[option- (len(center_groupings) + len(edge_groupings) + len(both_groupings) + len(inner_groupings) + len(inner_center_groupings) + 1)]
            placement_method = 5
        elif option > len(center_groupings) + len(edge_groupings) + len(both_groupings) + len(inner_groupings):
            selected_grouping = inner_center_groupings[option- (len(center_groupings) + len(edge_groupings) + len(both_groupings) + len(inner_groupings) + 1)]
            placement_method = 4
        elif option > len(center_groupings) + len(edge_groupings) + len(both_groupings):
            selected_grouping = inner_groupings[option- (len(center_groupings) + len(edge_groupings) + len(both_groupings) + 1)]
            placement_method = 3
        elif option > len(center_groupings) + len(edge_groupings):
            selected_grouping = both_groupings[option- (len(center_groupings) + len(edge_groupings) + 1)]
            placement_method = 2
        elif option > len(center_groupings):
            selected_grouping = edge_groupings[option- (len(center_groupings) + 1)]
            placement_method = 1
        else:
            selected_grouping = center_groupings[option-1]
            placement_method = 0

        # construct the new bottom row for structure using selected block/configuration
        new_bottom = []
        for subset in selected_grouping:
            if placement_method == 0:
                new_bottom.append([choosen_item, find_subset_center(subset)])
            if placement_method == 1:
                new_bottom.append([choosen_item, find_subset_edges(subset)[0]])
                new_bottom.append([choosen_item, find_subset_edges(subset)[1]])
            if placement_method == 2:
                new_bottom.append([choosen_item, find_subset_edges(subset)[0]])
                new_bottom.append([choosen_item, find_subset_center(subset)])
                new_bottom.append([choosen_item, find_subset_edges(subset)[1]])
            if placement_method == 3:
                new_bottom.append([choosen_item, find_subset_inners(subset)[0]])
                new_bottom.append([choosen_item, find_subset_inners(subset)[1]])
            if placement_method == 4:
                new_bottom.append([choosen_item, find_subset_inners(subset)[0]])
                new_bottom.append([choosen_item, find_subset_center(subset)])
                new_bottom.append([choosen_item, find_subset_inners(subset)[1]])
            if placement_method == 5:
                new_bottom.append([choosen_item, find_subset_edges(subset)[0]])
                new_bottom.append([choosen_item, find_subset_inners(subset)[0]])
                new_bottom.append([choosen_item, find_subset_inners(subset)[1]])
                new_bottom.append([choosen_item, find_subset_edges(subset)[1]])
            if placement_method == 6:
                new_bottom.append([choosen_item, find_subset_edges(subset)[0]])
                new_bottom.append([choosen_item, find_subset_inners(subset)[0]])
                new_bottom.append([choosen_item, find_subset_center(subset)])
                new_bottom.append([choosen_item, find_subset_inners(subset)[1]])
                new_bottom.append([choosen_item, find_subset_edges(subset)[1]])

        for i in new_bottom:
            i[1] = round(i[1], 10)      # round all values to prevent floating point inaccuracy from causing errors

        current_tree_bottom = new_bottom
        total_tree.append(current_tree_bottom)      # add new bottom row to the structure
        return total_tree, current_tree_bottom, True      # return the new structure
    elif(new_row_attempts > max_attempts):
        return total_tree, current_tree_bottom, False      # return the new structure
    else:
        return add_new_row(current_tree_bottom, total_tree, new_row_attempts+1) # choose a new block and try again if no options available




# creates the peaks (first row) of the structure

def make_peaks(center_point):

    current_tree_bottom = []        # bottom blocks of structure
    number_peaks = randint(1,max_peaks)     # this is the number of peaks the structure will have
    top_item = choose_item(probability_table_blocks)    # this is the item at top of structure

    if number_peaks == 1:
        current_tree_bottom.append([top_item,center_point])     

    if number_peaks == 2:
        distance_apart_extra = round(randint(min_peak_split,max_peak_split)/100.0,10)
        current_tree_bottom.append([top_item,round(center_point - (blocks[str(top_item)][0]*0.5) - distance_apart_extra,10)] )
        current_tree_bottom.append([top_item,round(center_point + (blocks[str(top_item)][0]*0.5) + distance_apart_extra,10)] )

    if number_peaks == 3:
        distance_apart_extra = round(randint(min_peak_split,max_peak_split)/100.0,10)
        current_tree_bottom.append([top_item,round(center_point - (blocks[str(top_item)][0]) - distance_apart_extra,10)] )
        current_tree_bottom.append([top_item,round(center_point,10)])
        current_tree_bottom.append([top_item,round(center_point + (blocks[str(top_item)][0]) + distance_apart_extra,10)] )

    if number_peaks == 4:
        distance_apart_extra = round(randint(min_peak_split,max_peak_split)/100.0,10)
        current_tree_bottom.append([top_item,round(center_point - (blocks[str(top_item)][0]*1.5) - (distance_apart_extra*2),10)] )
        current_tree_bottom.append([top_item,round(center_point - (blocks[str(top_item)][0]*0.5) - distance_apart_extra,10)] )
        current_tree_bottom.append([top_item,round(center_point + (blocks[str(top_item)][0]*0.5) + distance_apart_extra,10)] )
        current_tree_bottom.append([top_item,round(center_point + (blocks[str(top_item)][0]*1.5) + (distance_apart_extra*2),10)] )

    if number_peaks == 5:
        distance_apart_extra = round(randint(min_peak_split,max_peak_split)/100.0,10)
        current_tree_bottom.append([top_item,round(center_point - (blocks[str(top_item)][0]*2.0) - (distance_apart_extra*2),10)] )
        current_tree_bottom.append([top_item,round(center_point - (blocks[str(top_item)][0]) - distance_apart_extra,10)] )
        current_tree_bottom.append([top_item,round(center_point,10)])
        current_tree_bottom.append([top_item,round(center_point + (blocks[str(top_item)][0]) + distance_apart_extra,10)] )
        current_tree_bottom.append([top_item,round(center_point + (blocks[str(top_item)][0]*2.0) + (distance_apart_extra*2),10)] )
    return current_tree_bottom




# recursively adds rows to base of strucutre until max_width or max_height is passed
# once this happens the last row added is removed and the structure is returned

def make_structure(absolute_ground, center_point, max_width, max_height):
    
    total_tree = []                 # all blocks of structure (so far)
    new_row_attempts = 0

    # creates the first row (peaks) for the structure, ensuring that max_width restriction is satisfied
    current_tree_bottom = make_peaks(center_point)
    if max_width > 0.0:
        while find_structure_width(current_tree_bottom) > max_width:
            current_tree_bottom = make_peaks(center_point)

    total_tree.append(current_tree_bottom)


    # recursively add more rows of blocks to the level structure
    structure_width = find_structure_width(current_tree_bottom)
    structure_height = (blocks[str(current_tree_bottom[0][0])][1])/2
    if max_height > 0.0 or max_width > 0.0:
        pre_total_tree = [current_tree_bottom]
        row_add_successful = True
        while structure_height < max_height and structure_width < max_width and row_add_successful:
            total_tree, current_tree_bottom, row_add_successful = add_new_row(current_tree_bottom, total_tree, new_row_attempts)
            complete_locations = []
            ground = absolute_ground
            for row in reversed(total_tree):
                for item in row:
                    complete_locations.append([item[0],item[1],round((((blocks[str(item[0])][1])/2)+ground),10)])
                ground = ground + (blocks[str(item[0])][1])
            structure_height = find_structure_height(complete_locations)
            structure_width = find_structure_width(complete_locations)
            if structure_height > max_height or structure_width > max_width:
                total_tree = deepcopy(pre_total_tree)
            else:
                pre_total_tree = deepcopy(total_tree)


    # make structure vertically correct (add y position to blocks)
    complete_locations = []
    ground = absolute_ground
    for row in reversed(total_tree):
        for item in row:
            complete_locations.append([item[0],item[1],round((((blocks[str(item[0])][1])/2)+ground),10)])
        ground = ground + (blocks[str(item[0])][1])


    # identify all possible pig positions on top of blocks (maximum 2 pigs per block, checks center before sides)
    possible_pig_positions = []
    for block in complete_locations:
        block_width = round(blocks[str(block[0])][0],10)
        block_height = round(blocks[str(block[0])][1],10)
        pig_width = pig_size[0]
        pig_height = pig_size[1]

        if blocks[str(block[0])][0] < pig_width:      # dont place block on edge if block too thin
            test_positions = [[round(block[1],10),round(block[2] + (pig_height/2) + (block_height/2),10)]]
        else:
            test_positions = [ [round(block[1],10),round(block[2] + (pig_height/2) + (block_height/2),10)],
                               [round(block[1] + (block_width/3),10),round(block[2] + (pig_height/2) + (block_height/2),10)],
                               [round(block[1] - (block_width/3),10),round(block[2] + (pig_height/2) + (block_height/2),10)]]     #check above centre of block
        for test_position in test_positions:
            valid_pig = True
            for i in complete_locations:
                if ( round((test_position[0] - pig_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                     round((test_position[0] + pig_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                     round((test_position[1] + pig_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                     round((test_position[1] - pig_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                    valid_pig = False
            if valid_pig == True:
                possible_pig_positions.append(test_position)


    #identify all possible pig positions on ground within structure
    left_bottom = total_tree[-1][0]
    right_bottom = total_tree[-1][-1]
    test_positions = []
    x_pos = left_bottom[1]

    while x_pos < right_bottom[1]:
        test_positions.append([round(x_pos,10),round(absolute_ground + (pig_height/2),10)])
        x_pos = x_pos + pig_precision

    for test_position in test_positions:
        valid_pig = True
        for i in complete_locations:
            if ( round((test_position[0] - pig_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                 round((test_position[0] + pig_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                 round((test_position[1] + pig_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                 round((test_position[1] - pig_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                valid_pig = False
        if valid_pig == True:
            possible_pig_positions.append(test_position)


    pig_protect_values = []
    for pig in possible_pig_positions:
        left = []
        right = []
        above = []
        for block in complete_locations:
            if block[1] < pig[0]:
                if ((block[2] - (blocks[str(block[0])][1]/2.0)) < pig[1]) and ((block[2] + (blocks[str(block[0])][1]/2.0)) > pig[1]) :
                    left.append(block)
                    
            if block[1] > pig[0]:
                if ((block[2] - (blocks[str(block[0])][1]/2.0)) < pig[1]) and ((block[2] + (blocks[str(block[0])][1]/2.0)) > pig[1]) :
                    right.append(block)
                
            if block[2] > pig[1]:
                if ((block[1] - (blocks[str(block[0])][0]/2.0)) < pig[0]) and ((block[1] + (blocks[str(block[0])][0]/2.0)) > pig[0]) :
                    above.append(block)

        if len(left) < len(right):
            if len(above) < len(left):
                pig_protect_values.append(len(above))
            else:
                pig_protect_values.append(len(left))
        else:
            if len(above) < len(right):
                pig_protect_values.append(len(above))
            else:
                pig_protect_values.append(len(right))

    return complete_locations, possible_pig_positions, pig_protect_values




# divide the available ground space between the chosen number of ground structures

def create_ground_structures(number_ground_structures):
    valid = False
    current_attempt = 0
    while valid == False:
        ground_divides = []
        if number_ground_structures > 0:
            ground_divides = [level_width_min, level_width_max]
        for i in range(number_ground_structures-1):
            ground_divides.insert(i+1,uniform(level_width_min, level_width_max))
        valid = True
        for j in range(len(ground_divides)-1):
            if (ground_divides[j+1] - ground_divides[j]) < min_ground_width:
                valid = False
        current_attempt = current_attempt + 1
        if (current_attempt > max_attempts):
            current_attempt = 0
            number_ground_structures = number_ground_structures - 1

    # determine the area available to each ground structure
    ground_positions = []
    ground_widths = []
    for j in range(len(ground_divides)-1):
        ground_positions.append(ground_divides[j]+((ground_divides[j+1] - ground_divides[j])/2))
        ground_widths.append(ground_divides[j+1] - ground_divides[j])

    print("number ground structures:", len(ground_positions))

    # creates a ground structure for each defined area 
    complete_locations = []
    final_pig_positions = []
    pig_protect_values = []
    for i in range(len(ground_positions)):
        max_width = ground_widths[i]
        max_height = ground_structure_height_limit
        center_point = ground_positions[i]
        complete_locations2, final_pig_positions2, pig_protect_values2 = make_structure(absolute_ground, center_point, max_width, max_height)
        complete_locations.append(complete_locations2)
        final_pig_positions.append(final_pig_positions2)
        pig_protect_values = pig_protect_values + pig_protect_values2

    return len(ground_positions), complete_locations, final_pig_positions, pig_protect_values, ground_divides




# creates a set number of platforms within the level
# automatically reduced if space not found after set number of attempts

def create_platforms(number_platforms, complete_locations, possible_pig_positions):

    platform_centers = []
    attempts = 0            # number of attempts so far to find space for platform
    final_platforms = []
    while len(final_platforms) < number_platforms:
        platform_width = randint(4,7)
        platform_position = [uniform(level_width_min+((platform_width*platform_size[0])/2.0), level_width_max-((platform_width*platform_size[0])/2.0)),
                             uniform(level_height_min, (level_height_max - minimum_height_gap))]
        temp_platform = []

        if platform_width == 1:
            temp_platform.append(platform_position)     

        if platform_width == 2:
            temp_platform.append([platform_position[0] - (platform_size[0]*0.5),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*0.5),platform_position[1]])

        if platform_width == 3:
            temp_platform.append([platform_position[0] - (platform_size[0]),platform_position[1]])
            temp_platform.append(platform_position) 
            temp_platform.append([platform_position[0] + (platform_size[0]),platform_position[1]])

        if platform_width == 4:
            temp_platform.append([platform_position[0] - (platform_size[0]*1.5),platform_position[1]])
            temp_platform.append([platform_position[0] - (platform_size[0]*0.5),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*0.5),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*1.5),platform_position[1]])

        if platform_width == 5:
            temp_platform.append([platform_position[0] - (platform_size[0]*2.0),platform_position[1]])
            temp_platform.append([platform_position[0] - (platform_size[0]),platform_position[1]])
            temp_platform.append(platform_position) 
            temp_platform.append([platform_position[0] + (platform_size[0]),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*2.0),platform_position[1]])

        if platform_width == 6:
            temp_platform.append([platform_position[0] - (platform_size[0]*2.5),platform_position[1]])
            temp_platform.append([platform_position[0] - (platform_size[0]*1.5),platform_position[1]])
            temp_platform.append([platform_position[0] - (platform_size[0]*0.5),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*0.5),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*1.5),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*2.5),platform_position[1]])

        if platform_width == 7:
            temp_platform.append([platform_position[0] - (platform_size[0]*3.0),platform_position[1]])
            temp_platform.append([platform_position[0] - (platform_size[0]*2.0),platform_position[1]])
            temp_platform.append([platform_position[0] - (platform_size[0]),platform_position[1]])
            temp_platform.append(platform_position) 
            temp_platform.append([platform_position[0] + (platform_size[0]),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*2.0),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*3.0),platform_position[1]])
            
        overlap = False
        for platform in temp_platform:

            if (((platform[0]-(platform_size[0]/2)) < level_width_min) or ((platform[0]+(platform_size[0])/2) > level_width_max)):
                overlap = True

            for structure in complete_locations:
                for block in structure:
                    if ( round((platform[0] - platform_distance_buffer - platform_size[0]/2),10) <= round((block[1] + blocks[str(block[0])][0]/2),10) and
                         round((platform[0] + platform_distance_buffer + platform_size[0]/2),10) >= round((block[1] - blocks[str(block[0])][0]/2),10) and
                         round((platform[1] + platform_distance_buffer + platform_size[1]/2),10) >= round((block[2] - blocks[str(block[0])][1]/2),10) and
                         round((platform[1] - platform_distance_buffer - platform_size[1]/2),10) <= round((block[2] + blocks[str(block[0])][1]/2),10)):
                        overlap = True

            for platform_set in final_platforms:
                for platform2 in platform_set:
                    if ( round((platform[0] - platform_distance_buffer - platform_size[0]/2),10) <= round((platform2[0] + platform_size[0]/2),10) and
                         round((platform[0] + platform_distance_buffer + platform_size[0]/2),10) >= round((platform2[0] - platform_size[0]/2),10) and
                         round((platform[1] + platform_distance_buffer + platform_size[1]/2),10) >= round((platform2[1] - platform_size[1]/2),10) and
                         round((platform[1] - platform_distance_buffer - platform_size[1]/2),10) <= round((platform2[1] + platform_size[1]/2),10)):
                        overlap = True

            for pig in possible_pig_positions:
                if ( round((platform[0] - platform_distance_buffer - platform_size[0]/2),10) <= round((pig[0] + pig_size[0]/2),10) and
                     round((platform[0] + platform_distance_buffer + platform_size[0]/2),10) >= round((pig[0] - pig_size[0]/2),10) and
                     round((platform[1] + platform_distance_buffer + platform_size[1]/2),10) >= round((pig[1] - pig_size[1]/2),10) and
                     round((platform[1] - platform_distance_buffer - platform_size[1]/2),10) <= round((pig[1] + pig_size[1]/2),10)):
                    overlap = True

            for platform_set2 in final_platforms:
                for i in platform_set2:
                    if i[0]+platform_size[0] > platform[0] and i[0]-platform_size[0] < platform[0]:
                        if i[1]+minimum_height_gap > platform[1] and i[1]-minimum_height_gap < platform[1]:
                            overlap = True
                            
        if overlap == False:
            final_platforms.append(temp_platform)
            platform_centers.append(platform_position)

        attempts = attempts + 1
        if attempts > max_attempts:
            attempts = 0
            number_platforms = number_platforms - 1
       
    print("number platforms:", number_platforms)

    return number_platforms, final_platforms, platform_centers




# create sutiable structures for each platform

def create_platform_structures(final_platforms, platform_centers, complete_locations, final_pig_positions, pig_protect_values):
    current_platform = 0
    for platform_set in final_platforms:
        platform_set_width = len(platform_set)*platform_size[0]

        above_blocks = []
        for platform_set2 in final_platforms:
            if platform_set2 != platform_set:
                for i in platform_set2:
                    if i[0]+platform_size[0] > platform_set[0][0] and i[0]-platform_size[0] < platform_set[-1][0] and i[1] > platform_set[0][1]:
                        above_blocks.append(i)

        min_above = level_height_max
        for j in above_blocks:
            if j[1] < min_above:
                min_above = j[1]

        center_point = platform_centers[current_platform][0]
        absolute_ground = platform_centers[current_platform][1] + (platform_size[1]/2)

        max_width = platform_set_width
        max_height = (min_above - absolute_ground)- pig_size[1] - platform_size[1]
        
        complete_locations2, final_pig_positions2, pig_protect_values2 = make_structure(absolute_ground, center_point, max_width, max_height)
        complete_locations.append(complete_locations2)
        final_pig_positions = final_pig_positions + final_pig_positions2
        pig_protect_values = pig_protect_values + pig_protect_values2

        current_platform = current_platform + 1

    return complete_locations, final_pig_positions, pig_protect_values




# choose the number of birds based on the number of pigs and structures present within level

def choose_number_birds(final_pig_positions,number_ground_structures,number_platforms):
    number_birds = len(final_pig_positions)/3.0
    if (number_ground_structures + number_platforms) >= number_birds:
        number_birds = number_birds + 1.0
    number_birds = int(ceil(number_birds*number_birds_weight))
    print("Number of birds: " + str(number_birds))
    return number_birds




# identify all possible triangleHole positions on top of blocks

def find_trihole_positions(complete_locations):
    possible_trihole_positions = []
    for structure in complete_locations:
        for block in structure:
            block_width = round(blocks[str(block[0])][0],10)
            block_height = round(blocks[str(block[0])][1],10)
            trihole_width = additional_object_sizes['1'][0]
            trihole_height = additional_object_sizes['1'][1]

            # don't place block on edge if block too thin
            if blocks[str(block[0])][0] < trihole_width:
                test_positions = [ [round(block[1],10),round(block[2] + (trihole_height/2) + (block_height/2),10)]]
            else:
                test_positions = [ [round(block[1],10),round(block[2] + (trihole_height/2) + (block_height/2),10)],
                                   [round(block[1] + (block_width/3),10),round(block[2] + (trihole_height/2) + (block_height/2),10)],
                                   [round(block[1] - (block_width/3),10),round(block[2] + (trihole_height/2) + (block_height/2),10)] ]
            
            for test_position in test_positions:
                valid_position = True
                for structure in complete_locations:
                    for i in structure:
                        if ( round((test_position[0] - trihole_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                             round((test_position[0] + trihole_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                             round((test_position[1] + trihole_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                             round((test_position[1] - trihole_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                            valid_position = False
                for j in final_pig_positions:
                    if ( round((test_position[0] - trihole_width/2),10) < round((j[0] + (pig_size[0]/2)),10) and
                         round((test_position[0] + trihole_width/2),10) > round((j[0] - (pig_size[0]/2)),10) and
                         round((test_position[1] + trihole_height/2),10) > round((j[1] - (pig_size[1]/2)),10) and
                         round((test_position[1] - trihole_height/2),10) < round((j[1] + (pig_size[1]/2)),10)):
                        valid_position = False
                for i in final_platforms:
                    for j in i:
                        if ( round((test_position[0] - trihole_width/2),10) < round((j[0] + (platform_size[0]/2)),10) and
                             round((test_position[0] + trihole_width/2),10) > round((j[0] - (platform_size[0]/2)),10) and
                             round((test_position[1] + platform_distance_buffer + trihole_height/2),10) > round((j[1] - (platform_size[1]/2)),10) and
                             round((test_position[1] - platform_distance_buffer - trihole_height/2),10) < round((j[1] + (platform_size[1]/2)),10)):
                            valid_position = False
                if valid_position == True:
                    possible_trihole_positions.append(test_position)
                        
    return possible_trihole_positions




# identify all possible triangle positions on top of blocks

def find_tri_positions(complete_locations):
    possible_tri_positions = []
    for structure in complete_locations:
        for block in structure:
            block_width = round(blocks[str(block[0])][0],10)
            block_height = round(blocks[str(block[0])][1],10)
            tri_width = additional_object_sizes['2'][0]
            tri_height = additional_object_sizes['2'][1]
            
            # don't place block on edge if block too thin
            if blocks[str(block[0])][0] < tri_width:
                test_positions = [ [round(block[1],10),round(block[2] + (tri_height/2) + (block_height/2),10)]]
            else:
                test_positions = [ [round(block[1],10),round(block[2] + (tri_height/2) + (block_height/2),10)],
                                   [round(block[1] + (block_width/3),10),round(block[2] + (tri_height/2) + (block_height/2),10)],
                                   [round(block[1] - (block_width/3),10),round(block[2] + (tri_height/2) + (block_height/2),10)] ]
            
            for test_position in test_positions:
                valid_position = True
                for structure in complete_locations:
                    for i in structure:
                        if ( round((test_position[0] - tri_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                             round((test_position[0] + tri_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                             round((test_position[1] + tri_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                             round((test_position[1] - tri_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                            valid_position = False
                for j in final_pig_positions:
                    if ( round((test_position[0] - tri_width/2),10) < round((j[0] + (pig_size[0]/2)),10) and
                         round((test_position[0] + tri_width/2),10) > round((j[0] - (pig_size[0]/2)),10) and
                         round((test_position[1] + tri_height/2),10) > round((j[1] - (pig_size[1]/2)),10) and
                         round((test_position[1] - tri_height/2),10) < round((j[1] + (pig_size[1]/2)),10)):
                        valid_position = False
                for i in final_platforms:
                    for j in i:
                        if ( round((test_position[0] - tri_width/2),10) < round((j[0] + (platform_size[0]/2)),10) and
                             round((test_position[0] + tri_width/2),10) > round((j[0] - (platform_size[0]/2)),10) and
                             round((test_position[1] + platform_distance_buffer + tri_height/2),10) > round((j[1] - (platform_size[1]/2)),10) and
                             round((test_position[1] - platform_distance_buffer - tri_height/2),10) < round((j[1] + (platform_size[1]/2)),10)):
                            valid_position = False
                if blocks[str(block[0])][0] < tri_width:      # as block not symmetrical need to check for support
                    valid_position = False
                if valid_position == True:
                    possible_tri_positions.append(test_position)

    return possible_tri_positions




# identify all possible circle positions on top of blocks (can only be placed in middle of block)

def find_cir_positions(complete_locations):
    possible_cir_positions = []
    for structure in complete_locations:
        for block in structure:
            block_width = round(blocks[str(block[0])][0],10)
            block_height = round(blocks[str(block[0])][1],10)
            cir_width = additional_object_sizes['3'][0]
            cir_height = additional_object_sizes['3'][1]

            # only checks above block's center
            test_positions = [ [round(block[1],10),round(block[2] + (cir_height/2) + (block_height/2),10)]]
            
            for test_position in test_positions:
                valid_position = True
                for structure in complete_locations:
                    for i in structure:
                        if ( round((test_position[0] - cir_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                             round((test_position[0] + cir_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                             round((test_position[1] + cir_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                             round((test_position[1] - cir_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                            valid_position = False
                for j in final_pig_positions:
                    if ( round((test_position[0] - cir_width/2),10) < round((j[0] + (pig_size[0]/2)),10) and
                         round((test_position[0] + cir_width/2),10) > round((j[0] - (pig_size[0]/2)),10) and
                         round((test_position[1] + cir_height/2),10) > round((j[1] - (pig_size[1]/2)),10) and
                         round((test_position[1] - cir_height/2),10) < round((j[1] + (pig_size[1]/2)),10)):
                        valid_position = False
                for i in final_platforms:
                    for j in i:
                        if ( round((test_position[0] - cir_width/2),10) < round((j[0] + (platform_size[0]/2)),10) and
                             round((test_position[0] + cir_width/2),10) > round((j[0] - (platform_size[0]/2)),10) and
                             round((test_position[1] + platform_distance_buffer + cir_height/2),10) > round((j[1] - (platform_size[1]/2)),10) and
                             round((test_position[1] - platform_distance_buffer - cir_height/2),10) < round((j[1] + (platform_size[1]/2)),10)):
                            valid_position = False
                if valid_position == True:
                    possible_cir_positions.append(test_position)

    return possible_cir_positions




# identify all possible circleSmall positions on top of blocks

def find_cirsmall_positions(complete_locations):
    possible_cirsmall_positions = []
    for structure in complete_locations:
        for block in structure:
            block_width = round(blocks[str(block[0])][0],10)
            block_height = round(blocks[str(block[0])][1],10)
            cirsmall_width = additional_object_sizes['4'][0]
            cirsmall_height = additional_object_sizes['4'][1]

            # don't place block on edge if block too thin
            if blocks[str(block[0])][0] < cirsmall_width:
                test_positions = [ [round(block[1],10),round(block[2] + (cirsmall_height/2) + (block_height/2),10)]]
            else:
                test_positions = [ [round(block[1],10),round(block[2] + (cirsmall_height/2) + (block_height/2),10)],
                                   [round(block[1] + (block_width/3),10),round(block[2] + (cirsmall_height/2) + (block_height/2),10)],
                                   [round(block[1] - (block_width/3),10),round(block[2] + (cirsmall_height/2) + (block_height/2),10)] ]
            
            for test_position in test_positions:
                valid_position = True
                for structure in complete_locations:
                    for i in structure:
                        if ( round((test_position[0] - cirsmall_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                             round((test_position[0] + cirsmall_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                             round((test_position[1] + cirsmall_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                             round((test_position[1] - cirsmall_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                            valid_position = False
                for j in final_pig_positions:
                    if ( round((test_position[0] - cirsmall_width/2),10) < round((j[0] + (pig_size[0]/2)),10) and
                         round((test_position[0] + cirsmall_width/2),10) > round((j[0] - (pig_size[0]/2)),10) and
                         round((test_position[1] + cirsmall_height/2),10) > round((j[1] - (pig_size[1]/2)),10) and
                         round((test_position[1] - cirsmall_height/2),10) < round((j[1] + (pig_size[1]/2)),10)):
                        valid_position = False
                for i in final_platforms:
                    for j in i:
                        if ( round((test_position[0] - cirsmall_width/2),10) < round((j[0] + (platform_size[0]/2)),10) and
                             round((test_position[0] + cirsmall_width/2),10) > round((j[0] - (platform_size[0]/2)),10) and
                             round((test_position[1] + platform_distance_buffer + cirsmall_height/2),10) > round((j[1] - (platform_size[1]/2)),10) and
                             round((test_position[1] - platform_distance_buffer - cirsmall_height/2),10) < round((j[1] + (platform_size[1]/2)),10)):
                            valid_position = False
                if valid_position == True:
                    possible_cirsmall_positions.append(test_position)

    return possible_cirsmall_positions




# finds possible positions for valid additional block types

def find_additional_block_positions(complete_locations):
    possible_trihole_positions = []
    possible_tri_positions = []
    possible_cir_positions = []
    possible_cirsmall_positions = []
    if ((trihole_allowed == True) and (additional_nonrectangular_blocks == True)):
        possible_trihole_positions = find_trihole_positions(complete_locations)
    if ((tri_allowed == True) and (additional_nonrectangular_blocks == True)):
        possible_tri_positions = find_tri_positions(complete_locations)
    if ((cir_allowed == True) and (additional_nonrectangular_blocks == True)):
        possible_cir_positions = find_cir_positions(complete_locations)
    if ((cirsmall_allowed == True) and (additional_nonrectangular_blocks == True)):
        possible_cirsmall_positions = find_cirsmall_positions(complete_locations)
    return possible_trihole_positions, possible_tri_positions, possible_cir_positions, possible_cirsmall_positions




# combine all possible additonal block positions into one set

def add_additional_blocks(possible_trihole_positions, possible_tri_positions, possible_cir_positions, possible_cirsmall_positions):
    all_other = []
    for i in possible_trihole_positions:
        all_other.append(['1',i[0],i[1]])
    for i in possible_tri_positions:
        all_other.append(['2',i[0],i[1]])
    for i in possible_cir_positions:
        all_other.append(['3',i[0],i[1]])
    for i in possible_cirsmall_positions:
        all_other.append(['4',i[0],i[1]])

    #randomly choose an additional block position and remove those that overlap it
    #repeat untill no more valid position

    selected_other = []
    while (len(all_other) > 0):
        chosen = all_other.pop(randint(0,len(all_other)-1))
        selected_other.append(chosen)
        new_all_other = []
        for i in all_other:
            if ( round((chosen[1] - (additional_object_sizes[chosen[0]][0]/2)),10) >= round((i[1] + (additional_object_sizes[i[0]][0]/2)),10) or
                 round((chosen[1] + (additional_object_sizes[chosen[0]][0]/2)),10) <= round((i[1] - (additional_object_sizes[i[0]][0]/2)),10) or
                 round((chosen[2] + (additional_object_sizes[chosen[0]][1]/2)),10) <= round((i[2] - (additional_object_sizes[i[0]][1]/2)),10) or
                 round((chosen[2] - (additional_object_sizes[chosen[0]][1]/2)),10) >= round((i[2] + (additional_object_sizes[i[0]][1]/2)),10)):
                new_all_other.append(i)
        all_other = new_all_other

    return selected_other




# add the desired number of pigs to the level

def add_pigs(number_pigs, possible_pig_positions, complete_locations, pig_protect_values, final_platforms,extra_platforms):
    final_pig_positions = []
    pigs_placed_on_ground = False
    num_attempts = 0
    while len(final_pig_positions) < number_pigs and num_attempts < max_attempts:
        pig_values = []         # three different factors are used to calculate the desirability of each possible pig locations
        f1 = []                 # the protection the location provides
        f2 = []                 # how far away the location is from other already selected locations
        f3 = []                 # how likely the location is to have other objects fall on it
        
        if len(possible_pig_positions) > 0:

            for i in pig_protect_values:            # factor 1
                f1.append(i*factor1_weight)

            for pig in possible_pig_positions:      # factor 2
                distance = 1
                for pig2 in final_pig_positions:
                    distance = distance * sqrt((pig[0] - pig2[0])*(pig[0] - pig2[0]) +  (pig[1] - pig2[1])*(pig[1] - pig2[1]))
                if len(final_pig_positions) > 0:
                    f2.append((distance*factor2_weight)/len(final_pig_positions))
                else:
                    f2.append(0.0)

            for pig in possible_pig_positions:      # factor 3
                bonus_found = 0
                for platform in final_platforms:
                    platform_edge1 = platform[0][0]-(platform_size[0]/2.0)
                    platform_edge2 = platform[-1][0]+(platform_size[0]/2.0)
                    if pig[1] < platform[0][1]:
                        if (pig[0] > (platform_edge1 - factor3_distance)) and (pig[0] < platform_edge1):
                            bonus_found = 1
                        if (pig[0] > platform_edge2) and (pig[0] < (platform_edge2 + factor3_distance)):
                            bonus_found = 1
                if bonus_found == 1:
                    f3.append(factor3_bonus)
                else:
                    f3.append(0.0)

            for i in range(len(possible_pig_positions)):
                pig_values.append(f1[i]+f2[i]+f3[i])

            max_value = 0
            max_i = 0
            for value in range(len(pig_values)):
                if pig_values[value] > max_value:
                    max_value = pig_values[value]
                    max_i = value

            final_pig_positions.append(possible_pig_positions[max_i])       # choose the location with the greatest pig value

            # remove locations that are no longer valid
            pig_width = pig_size[0]
            pig_height = pig_size[1]
            pig_choice = possible_pig_positions[max_i]
            new_pig_positions = []
            new_protect_values = []
            for i in range(len(possible_pig_positions)):
                if ( round((pig_choice[0] - pig_width/2),10) >= round((possible_pig_positions[i][0] + pig_width/2),10) or
                     round((pig_choice[0] + pig_width/2),10) <= round((possible_pig_positions[i][0] - pig_width/2),10) or
                     round((pig_choice[1] + pig_height/2),10) <= round((possible_pig_positions[i][1] - pig_height/2),10) or
                     round((pig_choice[1] - pig_height/2),10) >= round((possible_pig_positions[i][1] + pig_height/2),10)):
                    new_pig_positions.append(possible_pig_positions[i])
                    new_protect_values.append(pig_protect_values[i])
            possible_pig_positions = new_pig_positions
            pig_protect_values = new_protect_values

        # if no remaining options then place pigs randomly on the ground  
        else:
            pigs_placed_on_ground = True
            test_position = [uniform(level_width_min, level_width_max),absolute_ground]
            pig_width = pig_size[0]
            pig_height = pig_size[1]
            valid_pig = True
            for structure in complete_locations:
                for i in structure:
                    if ( round((test_position[0] - pig_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                         round((test_position[0] + pig_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                         round((test_position[1] + pig_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                         round((test_position[1] - pig_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                        valid_pig = False
            for i in extra_platforms:
                if ( round((test_position[0] - pig_width/2),10) < round((i[0] + (platform_size[0]/2)),10) and
                     round((test_position[0] + pig_width/2),10) > round((i[0] - (platform_size[0]/2)),10) and
                     round((test_position[1] + pig_height/2),10) > round((i[1] - (platform_size[1]/2)),10) and
                     round((test_position[1] - pig_height/2),10) < round((i[1] + (platform_size[1]/2)),10)):
                    valid_pig = False
            for i in final_pig_positions:
                if ( round((test_position[0] - pig_width/2),10) < round((i[0] + (pig_width/2)),10) and
                     round((test_position[0] + pig_width/2),10) > round((i[0] - (pig_width/2)),10) and
                     round((test_position[1] + pig_height/2),10) > round((i[1] - (pig_height/2)),10) and
                     round((test_position[1] - pig_height/2),10) < round((i[1] + (pig_height/2)),10)):
                    valid_pig = False
            if valid_pig == True:
                final_pig_positions.append(test_position)
            else:
                num_attempts = num_attempts + 1

    print("Number of pigs: ", len(final_pig_positions))
                
    return final_pig_positions,pigs_placed_on_ground




# determines if the line formed by two points intersects block
def line_intersects_block(point1, point2, block):
    return (line_intersects_line(point1,point2,[block[1]-(blocks[str(block[0])][0]/2.0),block[2]-(blocks[str(block[0])][1]/2.0)],[block[1]+(blocks[str(block[0])][0]/2.0),block[2]-(blocks[str(block[0])][1]/2.0)]) or
            line_intersects_line(point1,point2,[block[1]+(blocks[str(block[0])][0]/2.0),block[2]-(blocks[str(block[0])][1]/2.0)],[block[1]+(blocks[str(block[0])][0]/2.0),block[2]+(blocks[str(block[0])][1]/2.0)]) or
            line_intersects_line(point1,point2,[block[1]+(blocks[str(block[0])][0]/2.0),block[2]+(blocks[str(block[0])][1]/2.0)],[block[1]-(blocks[str(block[0])][0]/2.0),block[2]+(blocks[str(block[0])][1]/2.0)]) or
            line_intersects_line(point1,point2,[block[1]-(blocks[str(block[0])][0]/2.0),block[2]+(blocks[str(block[0])][1]/2.0)],[block[1]-(blocks[str(block[0])][0]/2.0),block[2]-(blocks[str(block[0])][1]/2.0)]))

# determines if the line formed by two points intersects platform
def line_intersects_platform(point1, point2, platform):
    return (line_intersects_line(point1,point2,[platform[0]-(platform_size[0]/2.0),platform[1]-(platform_size[1]/2.0)],[platform[0]+(platform_size[0]/2.0),platform[1]-(platform_size[1]/2.0)]) or
            line_intersects_line(point1,point2,[platform[0]+(platform_size[0]/2.0),platform[1]-(platform_size[1]/2.0)],[platform[0]+(platform_size[0]/2.0),platform[1]+(platform_size[1]/2.0)]) or
            line_intersects_line(point1,point2,[platform[0]+(platform_size[0]/2.0),platform[1]+(platform_size[1]/2.0)],[platform[0]-(platform_size[0]/2.0),platform[1]+(platform_size[1]/2.0)]) or
            line_intersects_line(point1,point2,[platform[0]-(platform_size[0]/2.0),platform[1]+(platform_size[1]/2.0)],[platform[0]-(platform_size[0]/2.0),platform[1]-(platform_size[1]/2.0)]))

# determines if the line formed by two points intersects irregular block
def line_intersects_irregular(point1, point2, block):
    return (line_intersects_line(point1,point2,[block[1]-(additional_object_sizes[str(block[0])][0]/2.0),block[2]-(additional_object_sizes[str(block[0])][1]/2.0)],[block[1]+(additional_object_sizes[str(block[0])][0]/2.0),block[2]-(additional_object_sizes[str(block[0])][1]/2.0)]) or
            line_intersects_line(point1,point2,[block[1]+(additional_object_sizes[str(block[0])][0]/2.0),block[2]-(additional_object_sizes[str(block[0])][1]/2.0)],[block[1]+(additional_object_sizes[str(block[0])][0]/2.0),block[2]+(additional_object_sizes[str(block[0])][1]/2.0)]) or
            line_intersects_line(point1,point2,[block[1]+(additional_object_sizes[str(block[0])][0]/2.0),block[2]+(additional_object_sizes[str(block[0])][1]/2.0)],[block[1]-(additional_object_sizes[str(block[0])][0]/2.0),block[2]+(additional_object_sizes[str(block[0])][1]/2.0)]) or
            line_intersects_line(point1,point2,[block[1]-(additional_object_sizes[str(block[0])][0]/2.0),block[2]+(additional_object_sizes[str(block[0])][1]/2.0)],[block[1]-(additional_object_sizes[str(block[0])][0]/2.0),block[2]-(additional_object_sizes[str(block[0])][1]/2.0)]))

# determines if the line formed by two points intersects pig
def line_intersects_pig(point1, point2, pig):
    return (line_intersects_line(point1,point2,[pig[0]-(pig_size[0]/2.0),pig[1]-(pig_size[1]/2.0)],[pig[0]+(pig_size[0]/2.0),pig[1]-(pig_size[1]/2.0)]) or
            line_intersects_line(point1,point2,[pig[0]+(pig_size[0]/2.0),pig[1]-(pig_size[1]/2.0)],[pig[0]+(pig_size[0]/2.0),pig[1]+(pig_size[1]/2.0)]) or
            line_intersects_line(point1,point2,[pig[0]+(pig_size[0]/2.0),pig[1]+(pig_size[1]/2.0)],[pig[0]-(pig_size[0]/2.0),pig[1]+(pig_size[1]/2.0)]) or
            line_intersects_line(point1,point2,[pig[0]-(pig_size[0]/2.0),pig[1]+(pig_size[1]/2.0)],[pig[0]-(pig_size[0]/2.0),pig[1]-(pig_size[1]/2.0)]))

#ccw -> counter-clockwise
def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# determines if two lines intersect
def line_intersects_line(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)




# this method uses a straight line rather than trajectory estimator

def find_reachable_blocks_straight(complete_locations):
    reachable_blocks = []
    for block in complete_locations:
        reachable = True
        for block2 in complete_locations:
            if block2 != block:
                if line_intersects_block([-7.5,-1],[block[1],block[2]],block2):
                    reachable = False
        for i in final_platforms:
            for platform_block in i:
                if line_intersects_platform([-7.5,-1],[block[1],block[2]],platform_block):
                    reachable = False
        for block3 in selected_other:
            if line_intersects_irregular([-7.5,-1],[block[1],block[2]],block3):
                reachable = False
        if reachable == True:
            reachable_blocks.append(block)
    return reachable_blocks




# determines which blocks within the level can be hit directly by birds fired from the slingshot

def find_reachable_blocks(complete_locations,final_pig_positions,selected_other,final_platforms):
    reachable_blocks = []
    angle_interval = pi/(number_shots-1)
    angle = -(pi/2)

    for i in range(number_shots):
        release_point = find_release_point(angle)
        trajectory = find_trajectory(release_point[0],release_point[1])

        for point in trajectory:
            point[0] = round(point[0] + slingshot_x,10)
            point[1] = round(point[1] + slingshot_y,10)
        
        found = 0
        for j in range(len(trajectory)-1):
            point1 = trajectory[j]
            point2 = trajectory[j+1]
            if (found == 0):
                for structure in complete_locations:
                    for block in structure:
                        if line_intersects_block(point1, point2, block):
                            found = 1
                            reachable_blocks.append(block)
                for platform in final_platforms:
                    for platform_block in platform:
                        if line_intersects_platform(point1, point2, platform_block):
                            found = 1
                for irregular in selected_other:
                    if line_intersects_irregular(point1, point2, irregular):
                        found = 1
                for pig in final_pig_positions:
                    if line_intersects_pig(point1, point2, pig):
                        found = 1
                        
        angle = angle + angle_interval

    return reachable_blocks




# determines for each pig within the level the blocks that block a player from hitting it.

def find_blocks_in_way(complete_locations,final_pig_positions,selected_other,final_platforms):
    angle_interval = pi/(number_shots-1)
    angle = -(pi/2)
    final_blocks_in_way = []
    for i in range(number_shots):
        release_point = find_release_point(angle)
        trajectory = find_trajectory(release_point[0],release_point[1])
        blocks_in_way = []
        for point in trajectory:
            point[0] = round(point[0] + slingshot_x,10)
            point[1] = round(point[1] + slingshot_y,10)
        found = 0
        found_pig = 0
        for j in range(len(trajectory)-1):
            point1 = trajectory[j]
            point2 = trajectory[j+1]
            if (found == 0):
                for structure in complete_locations:
                    for block in structure:
                        if line_intersects_block(point1, point2, block):
                            blocks_in_way.append(block)
                for pig in final_pig_positions:
                    if line_intersects_pig(point1, point2, pig):
                        found = 1
                        final_blocks_in_way.append([pig,blocks_in_way])
                for platform in final_platforms:
                    for platform_block in platform:
                        if line_intersects_platform(point1, point2, platform_block):
                            found = 1
                        
        angle = angle + angle_interval

    return final_blocks_in_way




# determines which pigs within the level can be hit directly by birds fired from the slingshot

def find_unprotected_pigs(complete_locations,final_pig_positions,selected_other,final_platforms):
    unprotected_pigs = []
    angle_interval = pi/(number_shots-1)
    angle = -(pi/2)

    for i in range(number_shots):
        release_point = find_release_point(angle)
        trajectory = find_trajectory(release_point[0],release_point[1])

        for point in trajectory:
            point[0] = round(point[0] + slingshot_x,10)
            point[1] = round(point[1] + slingshot_y,10)
        
        found = 0
        for j in range(len(trajectory)-1):
            point1 = trajectory[j]
            point2 = trajectory[j+1]
            if (found == 0):
                for structure in complete_locations:
                    for block in structure:
                        if line_intersects_block(point1, point2, block):
                            found = 1
                for platform in final_platforms:
                    for platform_block in platform:
                        if line_intersects_platform(point1, point2, platform_block):
                            found = 1
                for irregular in selected_other:
                    if line_intersects_irregular(point1, point2, irregular):
                        found = 1
                for pig in final_pig_positions:
                    if line_intersects_pig(point1, point2, pig):
                        found = 1
                        unprotected_pigs.append(pig)
                        
        angle = angle + angle_interval

    return unprotected_pigs




# determines which pigs within the level can be hit by birds fired from the slingshot, even through other blocks
# the total number of pigs minus this gives the number of unhittable (directly) pigs

def find_hittable_pigs(complete_locations,final_pig_positions,selected_other,final_platforms):
    hittable_pigs = []
    angle_interval = pi/(number_shots-1)
    angle = -(pi/2)

    for i in range(number_shots):
        release_point = find_release_point(angle)
        trajectory = find_trajectory(release_point[0],release_point[1])

        for point in trajectory:
            point[0] = round(point[0] + slingshot_x,10)
            point[1] = round(point[1] + slingshot_y,10)
        
        found = 0
        for j in range(len(trajectory)-1):
            point1 = trajectory[j]
            point2 = trajectory[j+1]
            if (found == 0):
                for platform in final_platforms:
                    for platform_block in platform:
                        if line_intersects_platform(point1, point2, platform_block):
                            found = 1
                for pig in final_pig_positions:
                    if line_intersects_pig(point1, point2, pig):
                        found = 1
                        hittable_pigs.append(pig)
                        
        angle = angle + angle_interval

    return hittable_pigs



        
# these functions are all usd by the trajectory estimator (please don't change)

def launchToActual(theta):
    i = 1
    while (i < len(launchAngle)):
        if (theta > launchAngle[i-1] and theta < launchAngle[i]):
            return theta + changeAngle[i-1]
        i = i + 1
    return theta + changeAngle[len(launchAngle)-1]

def getVelocity(theta):
    if (theta < launchAngle[0]):
        return scaleFactor * launchVelocity[0]
    i = 1
    while (i < len(launchAngle)):
        if (theta < launchAngle[i]):
            return scaleFactor * launchVelocity[i-1]
        i = i + 1
    return scaleFactor * launchVelocity[len(launchVelocity)-1]

def find_trajectory(release_x, release_y):
    theta = atan2(release_y, release_x)
    theta = launchToActual(theta)
    velocity = getVelocity(theta)
    ux = velocity * cos(theta)
    uy = velocity * sin(theta)
    a = -0.5 / (ux * ux)
    b = uy / ux
    x = 0.0
    trajectory = []
    while (x < MAX_X):
        xn = x * scale
        y = (a * xn * xn + b * xn)*scale
        trajectory.append([round(x,10), round(y,10)])
        x = x + trajectory_accuracy
    return trajectory

def find_release_point(theta):
    release = [(-100.0 * cos(theta)), (-100.0 * sin(theta))]
    return release




# determins which blocks are vulnerable (are reachable and there removal affects a large number of blocks/pigs)

def find_vulnerable_blocks(complete_locations,final_pig_positions,selected_other,final_platforms):
    reachable_blocks_dup = find_reachable_blocks(complete_locations,final_pig_positions,selected_other,final_platforms)

    # remove duplicate blocks
    reachable_blocks = []
    for i in reachable_blocks_dup:
        if i not in reachable_blocks:
            reachable_blocks.append(i)

    vulnerable_scores = []
    for block in reachable_blocks:
        score = 0
        temp_locations = [item for sublist in complete_locations for item in sublist]
        temp_locations.remove(block)
        to_remove = [1]

        while(to_remove != []):
            to_remove = []

            for item in temp_locations:
                center = item[1]
                edge1 = item[1] - (blocks[str(item[0])][0])/2.0 + check_buffer
                edge2 = item[1] + (blocks[str(item[0])][0])/2.0 - check_buffer
                center_supported = False
                edge1_supported = False
                edge2_supported = False

                edge1_point = [edge1,item[2]-(blocks[str(item[0])][1]/2.0)-0.1]
                edge2_point = [edge2,item[2]-(blocks[str(item[0])][1]/2.0)-0.1]
                center_point = [center,item[2]-(blocks[str(item[0])][1]/2.0)-0.1]

                if (item[2] - (blocks[str(item[0])][1]/2.0) - 0.1) < absolute_ground:
                    edge1_supported = True
                    edge2_supported = True
                    center_supported = True

                error_buffer = 0.01             # rounding errors can sometimes cause inaccuracies for checking edges
                for block2 in temp_locations:
                    if block2 != item:
                        if (block2[1]-error_buffer-(blocks[str(block2[0])][0]/2.0) <= edge1_point[0] and
                            block2[1]+error_buffer+(blocks[str(block2[0])][0]/2.0) >= edge1_point[0] and
                            block2[2]-error_buffer-(blocks[str(block2[0])][1]/2.0) <= edge1_point[1] and
                            block2[2]+error_buffer+(blocks[str(block2[0])][1]/2.0) >= edge1_point[1]):
                            edge1_supported = True
                        if (block2[1]-error_buffer-(blocks[str(block2[0])][0]/2.0) <= edge2_point[0] and
                            block2[1]+error_buffer+(blocks[str(block2[0])][0]/2.0) >= edge2_point[0] and
                            block2[2]-error_buffer-(blocks[str(block2[0])][1]/2.0) <= edge2_point[1] and
                            block2[2]+error_buffer+(blocks[str(block2[0])][1]/2.0) >= edge2_point[1]):
                            edge2_supported = True
                        if (block2[1]-(blocks[str(block2[0])][0]/2.0) <= center_point[0] and
                            block2[1]+(blocks[str(block2[0])][0]/2.0) >= center_point[0] and
                            block2[2]-(blocks[str(block2[0])][1]/2.0) <= center_point[1] and
                            block2[2]+(blocks[str(block2[0])][1]/2.0) >= center_point[1]):
                            center_supported = True

                for i in final_platforms:
                    for j in i:
                        if (j[0]-error_buffer-(platform_size[0]/2.0) <= edge1_point[0] and
                            j[0]+error_buffer+(platform_size[0]/2.0) >= edge1_point[0] and
                            j[1]-error_buffer-(platform_size[1]/2.0) <= edge1_point[1] and
                            j[1]+error_buffer+(platform_size[1]/2.0) >= edge1_point[1]):
                            edge1_supported = True
                        if (j[0]-error_buffer-(platform_size[0]/2.0) <= edge2_point[0] and
                            j[0]+error_buffer+(platform_size[0]/2.0) >= edge2_point[0] and
                            j[1]-error_buffer-(platform_size[1]/2.0) <= edge2_point[1] and
                            j[1]+error_buffer+(platform_size[1]/2.0) >= edge2_point[1]):
                            edge2_supported = True
                        if (j[0]-(platform_size[0]/2.0) <= center_point[0] and
                            j[0]+(platform_size[0]/2.0) >= center_point[0] and
                            j[1]-(platform_size[1]/2.0) <= center_point[1] and
                            j[1]+(platform_size[1]/2.0) >= center_point[1]):
                            center_supported = True

                if vul_robustness == 1:
                    if center_supported == False and (edge1_supported == False or edge2_supported == False):
                        score = score + 1
                        to_remove.append(item)
                if vul_robustness == 2:
                    if edge1_supported == False or edge2_supported == False:
                        score = score + 1
                        to_remove.append(item)
                if vul_robustness == 3:
                    if center_supported == False or edge1_supported == False or edge2_supported == False:
                        score = score + 1
                        to_remove.append(item) 

            for i in to_remove:
                temp_locations.remove(i)

        for other in selected_other:
            other_fine = False
            check_point = [other[1],other[2]-(additional_object_sizes[other[0]][1]/2.0)-0.1]
            if check_point[1] < absolute_ground:
                other_fine = True
            for block2 in temp_locations:
                if (block2[1]-(blocks[str(block2[0])][0]/2.0) <= check_point[0] and
                    block2[1]+(blocks[str(block2[0])][0]/2.0) >= check_point[0] and
                    block2[2]-(blocks[str(block2[0])][1]/2.0) <= check_point[1] and
                    block2[2]+(blocks[str(block2[0])][1]/2.0) >= check_point[1]):
                    other_fine = True
            for i in final_platforms:
                for j in i:
                    if (j[0]-(platform_size[0]/2.0) <= check_point[0] and
                        j[0]+(platform_size[0]/2.0) >= check_point[0] and
                        j[1]-(platform_size[1]/2.0) <= check_point[1] and
                        j[1]+(platform_size[1]/2.0) >= check_point[1]):
                        other_fine = True
            if other_fine == False:
                score = score + 1

        for pig in final_pig_positions:
            pig_fine = False
            check_point = [pig[0],pig[1]-(pig_size[1]/2.0)-0.1]
            if check_point[1] < absolute_ground:
                pig_fine = True
            for block2 in temp_locations:
                if (block2[1]-(blocks[str(block2[0])][0]/2.0) <= check_point[0] and
                    block2[1]+(blocks[str(block2[0])][0]/2.0) >= check_point[0] and
                    block2[2]-(blocks[str(block2[0])][1]/2.0) <= check_point[1] and
                    block2[2]+(blocks[str(block2[0])][1]/2.0) >= check_point[1]):
                    pig_fine = True
            for i in final_platforms:
                for j in i:
                    if (j[0]-(platform_size[0]/2.0) <= check_point[0] and
                        j[0]+(platform_size[0]/2.0) >= check_point[0] and
                        j[1]-(platform_size[1]/2.0) <= check_point[1] and
                        j[1]+(platform_size[1]/2.0) >= check_point[1]):
                        pig_fine = True
            if pig_fine == False:
                score = score + 10

        vulnerable_scores.append(score)

    vulnerable_blocks = []

    for i in range(len(reachable_blocks)):
        if vulnerable_scores[i] >= vulnerable_score_threshold:
            vulnerable_blocks.append(reachable_blocks[i])

    return vulnerable_blocks




# protects vulnerable blocks that belong to ground structures by attempting to build a stack of blocks to the left of it

def protect_vulnerable_blocks1(complete_locations, complete_ground_locations, final_platforms, vulnerable_blocks, final_pig_positions, selected_other):
    vulnerable_blocks.sort(key=lambda x: x[2])
    vulnerable_blocks.reverse()
    for vul in vulnerable_blocks:
        for structure in complete_ground_locations:
            if vul in structure:
                leftmost_point = vul[1]-(blocks[str(vul[0])][0]/2.0)
                if (far_left == True):
                    for block in structure:
                        if block[1]-(blocks[str(block[0])][0]/2.0) < leftmost_point:
                            leftmost_point = block[1]-(blocks[str(block[0])][0]/2.0)

                buffer = uniform(buffer_min,buffer_max)
                height_limit = vul[2] + (blocks[str(vul[0])][1]/2.0) + height_bonus

                number_attempts = 0                      
                new_stack = []
                overlap = True
                    
                while (number_attempts < max_number_attempts):

                    if (overlap == False):
                        new_stack.append(new_block)
                        number_attempts = 0
                    overlap = False
                    choosen_item = choose_item(probability_table_blocks)
                    if new_stack == []:
                        x_position = leftmost_point - blocks[str(choosen_item)][0]/2.0 - buffer 
                        new_block = [choosen_item, x_position, absolute_ground+(blocks[str(choosen_item)][1]/2.0)]
                    else:
                        new_block = [choosen_item, x_position, new_stack[-1][2] + (blocks[str(new_stack[-1][0])][1]/2.0) + (blocks[str(choosen_item)][1]/2.0)]

                    for structure in complete_locations:
                        for block in structure:
                            if ( round((new_block[1] - (blocks[str(new_block[0])][0]/2.0)),10) <= round((block[1] + blocks[str(block[0])][0]/2),10) and
                             round((new_block[1] + (blocks[str(new_block[0])][0]/2.0)),10) >= round((block[1] - blocks[str(block[0])][0]/2),10) and
                             round((new_block[2] + (blocks[str(new_block[0])][1]/2.0)),10) >= round((block[2] - blocks[str(block[0])][1]/2),10) and
                             round((new_block[2] - (blocks[str(new_block[0])][1]/2.0)),10) <= round((block[2] + blocks[str(block[0])][1]/2),10)):
                                overlap = True
                                number_attempts = number_attempts + 1
                                
                    for platforms in final_platforms:
                        for platform in platforms:
                            if ( round((new_block[1] - (blocks[str(new_block[0])][0]/2.0)),10) <= round((platform[0] + platform_distance_buffer + platform_size[0]/2),10) and
                             round((new_block[1] + (blocks[str(new_block[0])][0]/2.0)),10) >= round((platform[0] - platform_distance_buffer - platform_size[0]/2),10) and
                             round((new_block[2] + (blocks[str(new_block[0])][1]/2.0)),10) >= round((platform[1] - platform_distance_buffer - platform_size[1]/2),10) and
                             round((new_block[2] - (blocks[str(new_block[0])][1]/2.0)),10) <= round((platform[1] + platform_distance_buffer + platform_size[1]/2),10)):
                                overlap = True
                                number_attempts = number_attempts + 1

                    for pig in final_pig_positions:
                        if ( round((new_block[1] - (blocks[str(new_block[0])][0]/2.0)),10) <= round((pig[0] + pig_size[0]/2),10) and
                         round((new_block[1] + (blocks[str(new_block[0])][0]/2.0)),10) >= round((pig[0] - pig_size[0]/2),10) and
                         round((new_block[2] + (blocks[str(new_block[0])][1]/2.0)),10) >= round((pig[1] - pig_size[1]/2),10) and
                         round((new_block[2] - (blocks[str(new_block[0])][1]/2.0)),10) <= round((pig[1] + pig_size[1]/2),10)):
                            overlap = True
                            number_attempts = number_attempts + 1

                    for block in selected_other:
                        if ( round((new_block[1] - (blocks[str(new_block[0])][0]/2.0)),10) <= round((block[1] + additional_object_sizes[str(block[0])][0]/2),10) and
                         round((new_block[1] + (blocks[str(new_block[0])][0]/2.0)),10) >= round((block[1] - additional_object_sizes[str(block[0])][0]/2),10) and
                         round((new_block[2] + (blocks[str(new_block[0])][1]/2.0)),10) >= round((block[2] - additional_object_sizes[str(block[0])][1]/2),10) and
                         round((new_block[2] - (blocks[str(new_block[0])][1]/2.0)),10) <= round((block[2] + additional_object_sizes[str(block[0])][1]/2),10)):
                            overlap = True
                            number_attempts = number_attempts + 1

                    if (new_block[2] + (blocks[str(new_block[0])][1]/2.0) > height_limit) and (overlap == False):
                        new_stack.append(new_block)
                        number_attempts = max_number_attempts

                if (new_stack != []):
                    complete_locations.append(new_stack)

    return complete_locations




# finds the blocks in complete_locations that are directly supported by block

def find_above_blocks(block,complete_locations):
    above_blocks = []
    for structure in complete_locations:
        for block2 in structure:
            if block2[2] > block[2]+(blocks[str(block[0])][1]/2.0):
                if ( (round(block[1]-(blocks[str(block[0])][0]/2.0),10) <= round((block2[1]+(blocks[str(block2[0])][0]/2)),10))
                and (round(block[1]+(blocks[str(block[0])][0]/2.0),10) >= round((block2[1]-(blocks[str(block2[0])][0]/2)),10))
                and (round(block[2]-(blocks[str(block[0])][1]/2.0),10) <= round((block2[2]+(blocks[str(block2[0])][1]/2)),10))
                and (round(block[2]+(blocks[str(block[0])][1]/2.0),10) >= round((block2[2]-(blocks[str(block2[0])][1]/2)),10)) ):
                    above_blocks.append(block2)
    return above_blocks




# finds the blocks in complete_locations that directly support block (and functions for other object types)

def find_below_blocks(block,complete_locations):
    below_blocks = []
    for structure in complete_locations:
        for block2 in structure:
            if block2[2] < block[2]-(blocks[str(block[0])][1]/2.0):
                if ( (round(block[1]-(blocks[str(block[0])][0]/2.0),10) <= round((block2[1]+(blocks[str(block2[0])][0]/2)),10))
                and (round(block[1]+(blocks[str(block[0])][0]/2.0),10) >= round((block2[1]-(blocks[str(block2[0])][0]/2)),10))
                and (round(block[2]-(blocks[str(block[0])][1]/2.0),10) <= round((block2[2]+(blocks[str(block2[0])][1]/2)),10))
                and (round(block[2]+(blocks[str(block[0])][1]/2.0),10) >= round((block2[2]-(blocks[str(block2[0])][1]/2)),10)) ):
                    below_blocks.append(block2)
    return below_blocks

def find_below_blocks_other(block,complete_locations):
    below_blocks = []
    for structure in complete_locations:
        for block2 in structure:
            if block2[2] < block[2]-(additional_object_sizes[str(block[0])][1]/2.0):
                if ( (round(block[1]-(additional_object_sizes[str(block[0])][0]/2.0),10) <= round((block2[1]+(blocks[str(block2[0])][0]/2)),10))
                and (round(block[1]+(additional_object_sizes[str(block[0])][0]/2.0),10) >= round((block2[1]-(blocks[str(block2[0])][0]/2)),10))
                and (round(block[2]-(additional_object_sizes[str(block[0])][1]/2.0),10) <= round((block2[2]+(blocks[str(block2[0])][1]/2)),10))
                and (round(block[2]+(additional_object_sizes[str(block[0])][1]/2.0),10) >= round((block2[2]-(blocks[str(block2[0])][1]/2)),10)) ):
                    below_blocks.append(block2)
    return below_blocks

def find_below_blocks_tnt(tnt,complete_locations):
    below_blocks = []
    for structure in complete_locations:
        for block2 in structure:
            if block2[2] < tnt[1]-(tnt_size[1]/2.0):
                if ( (round(tnt[0]-(tnt_size[0]/2.0),10) <= round((block2[1]+(blocks[str(block2[0])][0]/2)),10))
                and (round(tnt[0]+(tnt_size[0]/2.0),10) >= round((block2[1]-(blocks[str(block2[0])][0]/2)),10))
                and (round(tnt[1]-(tnt_size[1]/2.0),10) <= round((block2[2]+(blocks[str(block2[0])][1]/2)),10))
                and (round(tnt[1]+(tnt_size[1]/2.0),10) >= round((block2[2]-(blocks[str(block2[0])][1]/2)),10)) ):
                    below_blocks.append(block2)
    return below_blocks

def find_below_blocks_pig(pig,complete_locations):
    below_blocks = []
    for structure in complete_locations:
        for block2 in structure:
            if block2[2] < pig[1]-(pig_size[1]/2.0):
                if ( (round(pig[0]-(pig_size[0]/2.0),10) <= round((block2[1]+(blocks[str(block2[0])][0]/2)),10))
                and (round(pig[0]+(pig_size[0]/2.0),10) >= round((block2[1]-(blocks[str(block2[0])][0]/2)),10))
                and (round(pig[1]-(pig_size[1]/2.0),10) <= round((block2[2]+(blocks[str(block2[0])][1]/2)),10))
                and (round(pig[1]+(pig_size[1]/2.0),10) >= round((block2[2]-(blocks[str(block2[0])][1]/2)),10)) ):
                    below_blocks.append(block2)
    return below_blocks




# protects vulnerable blocks by attempting to add more blocks to its current row within the structure (additonal support)

def protect_vulnerable_blocks2(complete_locations,final_platforms,final_pig_positions,selected_other, vulnerable_blocks):
    for vul in vulnerable_blocks:
        above_blocks = find_above_blocks(vul,complete_locations)
        for y in above_blocks:
            center = y[1]
            edge1 = y[1] - (blocks[str(y[0])][0])/2.0 + check_buffer
            edge2 = y[1] + (blocks[str(y[0])][0])/2.0 - check_buffer
            midpoint1 = y[1] - (blocks[str(y[0])][0])/4.0
            midpoint2 = y[1] + (blocks[str(y[0])][0])/4.0
            test_locations = [[vul[0],center,vul[2]],[vul[0],edge1,vul[2]],[vul[0],edge2,vul[2]],[vul[0],midpoint1,vul[2]],[vul[0],midpoint2,vul[2]]]

            for i in test_locations:
                overlap = False
                valid = False
                error_buffer = 0.01

                for structure in complete_locations:
                    for block in structure:
                        if ( round((i[1] - (blocks[str(i[0])][0]/2.0)) + error_buffer,10) <= round((block[1] + blocks[str(block[0])][0]/2),10) and
                             round((i[1] + (blocks[str(i[0])][0]/2.0)) - error_buffer,10) >= round((block[1] - blocks[str(block[0])][0]/2),10) and
                             round((i[2] + (blocks[str(i[0])][1]/2.0)) - error_buffer,10) >= round((block[2] - blocks[str(block[0])][1]/2),10) and
                             round((i[2] - (blocks[str(i[0])][1]/2.0)) + error_buffer,10) <= round((block[2] + blocks[str(block[0])][1]/2),10)):
                                overlap = True
         
                for platforms in final_platforms:
                    for platform in platforms:
                        if ( round((i[1] - (blocks[str(i[0])][0]/2.0)) + error_buffer,10) <= round((platform[0] + platform_distance_buffer + platform_size[0]/2),10) and
                         round((i[1] + (blocks[str(i[0])][0]/2.0)) - error_buffer,10) >= round((platform[0] - platform_distance_buffer - platform_size[0]/2),10) and
                         round((i[2] + (blocks[str(i[0])][1]/2.0)) - error_buffer,10) >= round((platform[1] - platform_distance_buffer - platform_size[1]/2),10) and
                         round((i[2] - (blocks[str(i[0])][1]/2.0)) + error_buffer,10) <= round((platform[1] + platform_distance_buffer + platform_size[1]/2),10)):
                            overlap = True

                for pig in final_pig_positions:
                    if ( round((i[1] - (blocks[str(i[0])][0]/2.0)) + error_buffer,10) <= round((pig[0] + pig_size[0]/2),10) and
                     round((i[1] + (blocks[str(i[0])][0]/2.0)) - error_buffer,10) >= round((pig[0] - pig_size[0]/2),10) and
                     round((i[2] + (blocks[str(i[0])][1]/2.0)) - error_buffer,10) >= round((pig[1] - pig_size[1]/2),10) and
                     round((i[2] - (blocks[str(i[0])][1]/2.0)) + error_buffer,10) <= round((pig[1] + pig_size[1]/2),10)):
                        overlap = True

                for block in selected_other:
                    if ( round((i[1] - (blocks[str(i[0])][0]/2.0)) + error_buffer,10) <= round((block[1] + additional_object_sizes[str(block[0])][0]/2),10) and
                     round((i[1] + (blocks[str(i[0])][0]/2.0)) - error_buffer,10) >= round((block[1] - additional_object_sizes[str(block[0])][0]/2),10) and
                     round((i[2] + (blocks[str(i[0])][1]/2.0)) - error_buffer,10) >= round((block[2] - additional_object_sizes[str(block[0])][1]/2),10) and
                     round((i[2] - (blocks[str(i[0])][1]/2.0)) + error_buffer,10) <= round((block[2] + additional_object_sizes[str(block[0])][1]/2),10)):
                        overlap = True

                center = i[1]
                edge1 = i[1] - (blocks[str(i[0])][0])/2 + check_buffer
                edge2 = i[1] + (blocks[str(i[0])][0])/2 - check_buffer
                center_supported = False
                edge1_supported = False
                edge2_supported = False            

                for block in find_below_blocks(i, complete_locations):
                    if ((block[1] - (blocks[str(block[0])][0])/2) <= center and (block[1] + (blocks[str(block[0])][0])/2) >= center):
                        center_supported = True
                    if ((block[1] - (blocks[str(block[0])][0])/2) <= edge1 and (block[1] + (blocks[str(block[0])][0])/2) >= edge1):
                        edge1_supported = True
                    if ((block[1] - (blocks[str(block[0])][0])/2) <= edge2 and (block[1] + (blocks[str(block[0])][0])/2) >= edge2):
                        edge2_supported = True

                push_down = 0.01
                for platforms in final_platforms:
                    for platform in platforms:
                        if ( round(i[1],10) <= round((platform[0] + platform_size[0]/2),10) and
                         round(i[1],10) >= round((platform[0] - platform_size[0]/2),10) and
                         (i[2] > platform[1]) and
                         round((i[2] - push_down - (blocks[str(i[0])][1]/2.0)),10) <= round((platform[1] + platform_size[1]/2),10)):
                            center_supported = True
                        if ( round((i[1] - (blocks[str(i[0])][0]/2.0)),10) <= round((platform[0] + platform_size[0]/2),10) and
                         round((i[1] - (blocks[str(i[0])][0]/2.0)),10) >= round((platform[0] - platform_size[0]/2),10) and
                         (i[2] > platform[1]) and
                         round((i[2] - push_down - (blocks[str(i[0])][1]/2.0)),10) <= round((platform[1] + platform_size[1]/2),10)):
                            edge1_supported = True
                        if ( round((i[1] + (blocks[str(i[0])][0]/2.0)),10) <= round((platform[0] + platform_size[0]/2),10) and
                         round((i[1] + (blocks[str(i[0])][0]/2.0)),10) >= round((platform[0] - platform_size[0]/2),10) and
                         (i[2] > platform[1]) and
                         round((i[2] - push_down - (blocks[str(i[0])][1]/2.0)),10) <= round((platform[1] + platform_size[1]/2),10)):
                            edge2_supported = True

                if (round((i[2] - push_down - (blocks[str(i[0])][1]/2.0)),10) <= absolute_ground):
                    center_supported = True
                    edge1_supported = True
                    edge2_supported = True

                if robustness == 1:
                    if center_supported == True or (edge1_supported == True and edge2_supported == True):
                        valid = True
                if robustness == 2:
                    if edge1_supported == True and edge2_supported == True:
                        valid = True
                if robustness == 3:
                    if center_supported == True and edge1_supported == True and edge2_supported == True:
                        valid = True
                              
                if (overlap == False) and (valid == True):
                    for j in range(len(complete_locations)):
                        if vul in complete_locations[j]:
                            complete_locations[j].append(i)

    return complete_locations




# write level out in desired xml format

def write_level_xml(final_blocks, selected_other, final_pig_positions, final_platforms, number_birds, bird_order, final_materials, final_tnt_positions, extra_platforms_angled, current_level):

    level_name = "level-%s.xml" % current_level
    f = open(level_name, "w")







    f.write('<?xml version="1.0" encoding="utf-16"?>\n')
    f.write('<Level width ="2">\n')
    f.write('<Camera x="0" y="2" minWidth="20" maxWidth="30">\n')
    f.write('<Score highScore ="0">\n')
    f.write('<Birds>\n')
    for i in range(number_birds):
        f.write('<Bird type="%s"/>\n' % bird_types_index[str((bird_order[i]))])
    f.write('</Birds>\n')
    f.write('<Slingshot x="-8" y="-2.5">\n')
    f.write('<GameObjects>\n')

    for index in range(len(final_blocks)):
        i = final_blocks[index]
        j = final_materials[index]
        rotation = 0
        if (i[0] in (3,7,9,11,13)):
            rotation = 90
        f.write('<Block type="%s" material="%s" x="%s" y="%s" rotation="%s" />\n' % (block_names[str(i[0])],materials[str(j)], str(i[1]), str(i[2]), str(rotation)))

    for i in selected_other:
        material = materials[str(choose_item(probability_table_materials))]       # material is chosen randomly
        if i[0] == '1':
            f.write('<Block type="%s" material="%s" x="%s" y="%s" rotation="0" />\n' % (additional_objects[i[0]], material, str(i[1]), str(i[2])))
        if i[0] == '2':
            facing = randint(0,1)
            f.write('<Block type="%s" material="%s" x="%s" y="%s" rotation="%s" />\n' % (additional_objects[i[0]], material, str(i[1]), str(i[2]), str(facing*90.0)))
        if i[0] == '3':
            f.write('<Block type="%s" material="%s" x="%s" y="%s" rotation="0" />\n' % (additional_objects[i[0]], material, str(i[1]), str(i[2])))
        if i[0] == '4':
            f.write('<Block type="%s" material="%s" x="%s" y="%s" rotation="0" />\n' % (additional_objects[i[0]], material, str(i[1]), str(i[2])))

    for i in final_pig_positions:
        f.write('<Pig type="BasicSmall" material="" x="%s" y="%s" rotation="0" />\n' % (str(i[0]),str(i[1])))

    for i in final_tnt_positions:
        f.write('<TNT type="" x="%s" y="%s" rotation="0" />\n' % (str(i[0]),str(i[1])))
        

    for i in final_platforms:
        for j in i:
            f.write('<Platform type="Platform" material="" x="%s" y="%s" />\n' % (str(j[0]),str(j[1])))

    for i in extra_platforms_angled:
            f.write('<Platform type="Platform" material="" x="%s" y="%s" rotation="%s" scaleX="%s" />\n' % (str(i[0]),str(i[1]),str(i[2]),str(i[3])))
        
    f.write('</GameObjects>\n')
    f.write('</Level>\n')

    f.close()




# write out each structure within level on the ground in seperate xml file

def write_structure_xml(all_structures,structure_others,structure_pigs,structure_tnts):
    structure_num = 0
    for jj in range(len(all_structures)):
        structure = all_structures[jj]
        others = structure_others[jj]
        pigs = structure_pigs[jj]
        tnts = structure_tnts[jj]

        lowest_point = 9999.0
        for i in structure:
            temp = i[2]-(blocks[str(i[0])][1]/2.0)
            if temp < lowest_point:
                lowest_point = deepcopy(temp)
        if lowest_point > absolute_ground+0.05:
            difference = lowest_point - absolute_ground
            for index in range(len(structure)):
                structure[index][2] = structure[index][2]-difference
            for index in range(len(others)):
                others[index][2] = others[index][2]-difference
            for index in range(len(pigs)):
                pigs[index][1] = pigs[index][1]-difference
            for index in range(len(tnts)):
                tnts[index][1] = tnts[index][1]-difference
        
        structure_name = "structure-%s.xml" % structure_num
        f = open(structure_name, "w")

        f.write('<?xml version="1.0" encoding="utf-16"?>\n')
        f.write('<Level width ="2">\n')
        f.write('<Camera x="0" y="-1" minWidth="25" maxWidth="40">\n')
        f.write('<Birds>\n')
        f.write('<Bird type="BirdRed"/>\n')
        f.write('</Birds>\n')
        f.write('<Slingshot x="-8" y="-2.5">\n')
        f.write('<GameObjects>\n')
        
        for index in range(len(structure)):
            i = structure[index]
            rotation = 0
            if (i[0] in (3,7,9,11,13)):
                rotation = 90
            f.write('<Block type="%s" material="wood" x="%s" y="%s" rotation="%s" />\n' % (block_names[str(i[0])], str(i[1]), str(i[2]), str(rotation)))

        for index in range(len(others)):
            i = others[index]
            rotation = 0
            if (i[0] in (3,7,9,11,13)):
                rotation = 90
            f.write('<Block type="%s" material="wood" x="%s" y="%s" rotation="%s" />\n' % (additional_objects[str(i[0])], str(i[1]), str(i[2]), str(rotation)))

        for index in range(len(pigs)):
            i = pigs[index]
            f.write('<Pig type="BasicSmall" material="" x="%s" y="%s" rotation="0" />\n' % (str(i[0]),str(i[1])))

        for index in range(len(tnts)):
            i = tnts[index]
            f.write('<TNT type="" x="%s" y="%s" rotation="0" />\n' % (str(i[0]),str(i[1])))

        f.write('</GameObjects>\n')
        f.write('</Level>\n')

        f.close()
        structure_num = structure_num + 1




# randomly swap some blocks with other blocks that have the same height
# (and do not overlap other blocks and fulfill support requirements)

def swap_blocks(complete_locations, final_pig_positions, final_platforms):
    if (block_swapping == True):
        total_swaps = 0
        for i in range(len(complete_locations)):
            for j in range(len(complete_locations[i])):
                test_blocks = []
                test_complete_locations = deepcopy(complete_locations)
                test_complete_locations[i].pop(j);

                for key,value in blocks.items():
                    if probability_table_blocks[key] > 0.0:
                        if key != str(complete_locations[i][j][0]):
                            if blocks[str(complete_locations[i][j][0])][1] == value[1]:
                                test_block_temp = deepcopy(complete_locations[i][j])
                                test_block_temp[0] = int(key)
                                test_blocks.append(test_block_temp)

                shuffle(test_blocks)

                total_prob_amount = 0
                for block in test_blocks:
                    total_prob_amount = total_prob_amount + probability_table_blocks[str(block[0])]

                for block in test_blocks:
                    if uniform(0.0,1.0) < (probability_table_blocks[str(block[0])]/total_prob_amount):
                        temp_block = deepcopy(block)
                        test_blocks.remove(block)
                        test_blocks.insert(0,block)

                swapped = 0
                for test_block in test_blocks:
                    # check no overlap
                    if (swapped == 0):
                        overlap = False
                        valid = True
                        pigs_supported = True
                        error_buffer = 0.01

                        for structure in test_complete_locations:
                            for block in structure:
                                if ( round((test_block[1] - (blocks[str(test_block[0])][0]/2.0)) + error_buffer,10) <= round((block[1] + blocks[str(block[0])][0]/2),10) and
                                     round((test_block[1] + (blocks[str(test_block[0])][0]/2.0)) - error_buffer,10) >= round((block[1] - blocks[str(block[0])][0]/2),10) and
                                     round((test_block[2] + (blocks[str(test_block[0])][1]/2.0)) - error_buffer,10) >= round((block[2] - blocks[str(block[0])][1]/2),10) and
                                     round((test_block[2] - (blocks[str(test_block[0])][1]/2.0)) + error_buffer,10) <= round((block[2] + blocks[str(block[0])][1]/2),10)):
                                        overlap = True
                 
                        for platforms in final_platforms:
                            for platform in platforms:
                                if ( round((test_block[1] - (blocks[str(test_block[0])][0]/2.0)) + error_buffer,10) <= round((platform[0] + platform_distance_buffer + platform_size[0]/2),10) and
                                     round((test_block[1] + (blocks[str(test_block[0])][0]/2.0)) - error_buffer,10) >= round((platform[0] - platform_distance_buffer - platform_size[0]/2),10) and
                                     round((test_block[2] + (blocks[str(test_block[0])][1]/2.0)) - error_buffer,10) >= round((platform[1] - platform_distance_buffer - platform_size[1]/2),10) and
                                     round((test_block[2] - (blocks[str(test_block[0])][1]/2.0)) + error_buffer,10) <= round((platform[1] + platform_distance_buffer + platform_size[1]/2),10)):
                                        overlap = True

                        for pig in final_pig_positions:
                            if ( round((test_block[1] - (blocks[str(test_block[0])][0]/2.0)) + error_buffer,10) <= round((pig[0] + pig_size[0]/2),10) and
                                 round((test_block[1] + (blocks[str(test_block[0])][0]/2.0)) - error_buffer,10) >= round((pig[0] - pig_size[0]/2),10) and
                                 round((test_block[2] + (blocks[str(test_block[0])][1]/2.0)) - error_buffer,10) >= round((pig[1] - pig_size[1]/2),10) and
                                 round((test_block[2] - (blocks[str(test_block[0])][1]/2.0)) + error_buffer,10) <= round((pig[1] + pig_size[1]/2),10)):
                                    overlap = True

                        # check that all stability requirements are still met for all blocks/pigs in rows above and below (and for self)
                        
                        above_blocks = find_above_blocks (complete_locations[i][j], complete_locations)
                        below_blocks = find_below_blocks (complete_locations[i][j], complete_locations)
             
                        blocks_to_test = above_blocks+below_blocks
                        blocks_to_test.append(test_block)
                    
                        test_complete_locations2 = deepcopy(complete_locations)
                        test_complete_locations2[i][j] = test_block

                        for test_blockx in blocks_to_test:
                            center = test_blockx[1]
                            edge1 = test_blockx[1] - (blocks[str(test_blockx[0])][0])/2 + check_buffer
                            edge2 = test_blockx[1] + (blocks[str(test_blockx[0])][0])/2 - check_buffer
                            center_supported = False
                            edge1_supported = False
                            edge2_supported = False

                            for block in find_below_blocks(test_blockx, test_complete_locations2):
                                if ((block[1] - (blocks[str(block[0])][0])/2) <= center and (block[1] + (blocks[str(block[0])][0])/2) >= center):
                                    center_supported = True
                                if ((block[1] - (blocks[str(block[0])][0])/2) <= edge1 and (block[1] + (blocks[str(block[0])][0])/2) >= edge1):
                                    edge1_supported = True
                                if ((block[1] - (blocks[str(block[0])][0])/2) <= edge2 and (block[1] + (blocks[str(block[0])][0])/2) >= edge2):
                                    edge2_supported = True

                            push_down = 0.01
                            for platforms in final_platforms:
                                for platform in platforms:
                                    if ( round(test_blockx[1],10) <= round((platform[0] + platform_size[0]/2),10) and
                                     round(test_blockx[1],10) >= round((platform[0] - platform_size[0]/2),10) and
                                     (test_blockx[2] > platform[1]) and
                                     round((test_blockx[2] - push_down - (blocks[str(test_blockx[0])][1]/2.0)),10) <= round((platform[1] + platform_size[1]/2),10)):
                                        center_supported = True
                                    if ( round((test_blockx[1] - (blocks[str(test_blockx[0])][0]/2.0)),10) <= round((platform[0] + platform_size[0]/2),10) and
                                     round((test_blockx[1] - (blocks[str(test_blockx[0])][0]/2.0)),10) >= round((platform[0] - platform_size[0]/2),10) and
                                     (test_blockx[2] > platform[1]) and
                                     round((test_blockx[2] - push_down - (blocks[str(test_blockx[0])][1]/2.0)),10) <= round((platform[1] + platform_size[1]/2),10)):
                                        edge1_supported = True
                                    if ( round((test_blockx[1] + (blocks[str(test_blockx[0])][0]/2.0)),10) <= round((platform[0] + platform_size[0]/2),10) and
                                     round((test_blockx[1] + (blocks[str(test_blockx[0])][0]/2.0)),10) >= round((platform[0] - platform_size[0]/2),10) and
                                     (test_blockx[2] > platform[1]) and
                                     round((test_blockx[2] - push_down - (blocks[str(test_blockx[0])][1]/2.0)),10) <= round((platform[1] + platform_size[1]/2),10)):
                                        edge2_supported = True

                            if (round((test_blockx[2] - push_down - (blocks[str(test_blockx[0])][1]/2.0)),10) <= absolute_ground):
                                center_supported = True
                                edge1_supported = True
                                edge2_supported = True

                            if robustness == 1:
                                if center_supported == True or (edge1_supported == True and edge2_supported == True):
                                    continue
                                else:
                                    valid = False
                            if robustness == 2:
                                if edge1_supported == True and edge2_supported == True:
                                    continue
                                else:
                                    valid = False
                            if robustness == 3:
                                if center_supported == True and edge1_supported == True and edge2_supported == True:
                                    continue
                                else:
                                    valid = False

                        for pig in final_pig_positions:
                            pig_supported = False
                            for structure in test_complete_locations2:
                                for block in structure:
                                    if ( round((block[1] - (blocks[str(block[0])][0]/2.0)) + error_buffer,10) <= round((pig[0]),10) and
                                         round((block[1] + (blocks[str(block[0])][0]/2.0)) - error_buffer,10) >= round((pig[0]),10) and
                                         round((block[2] + (blocks[str(block[0])][1]/2.0)) - error_buffer,10) >= round((pig[1] - pig_size[1]/2 - 0.01),10) and
                                         round((block[2] - (blocks[str(block[0])][1]/2.0)) + error_buffer,10) <= round((pig[1] - pig_size[1]/2 - 0.01),10)):
                                            pig_supported = True

                            if pig_supported == False:
                                pigs_supported = False

                        if (overlap == False and valid == True and pigs_supported == True):
                            ran_num = uniform(0.0,1.0)
                            if ran_num < prob_swap:
                                total_swaps = total_swaps + 1
                                swapped = 1
                                complete_locations[i][j] = test_block
                    
    return complete_locations




# attempt to protect vulnerable blocks in structures

def protect_vulnerable_blocks(complete_locations, complete_ground_locations, final_platforms, final_pig_positions, selected_other):
    vulnerable_blocks = []
    if (vulnerability_analysis == True):
        vulnerable_blocks = find_vulnerable_blocks(complete_locations,final_pig_positions,selected_other,final_platforms)
        temp_complete_locations = deepcopy(complete_locations)
        if (protection_method1 == True):
            complete_locations = protect_vulnerable_blocks1(complete_locations, complete_ground_locations, final_platforms, vulnerable_blocks, final_pig_positions, selected_other)
        if (vulnerable_blocks != []) and (temp_complete_locations != complete_locations):
            vulnerable_blocks = find_vulnerable_blocks(complete_locations,final_pig_positions,selected_other,final_platforms)
        temp_complete_locations = deepcopy(complete_locations)
        if (protection_method2 == True):
            complete_locations = protect_vulnerable_blocks2(complete_locations,final_platforms,final_pig_positions,selected_other, vulnerable_blocks)
        if (vulnerable_blocks != []) and (temp_complete_locations != complete_locations):
            vulnerable_blocks = find_vulnerable_blocks(complete_locations,final_pig_positions,selected_other,final_platforms)
    return vulnerable_blocks




# set the material of each block

def set_materials(complete_locations, final_pig_positions, vulnerable_blocks):
    final_materials = []
    final_blocks = []
    for ii in complete_locations:
        for jj in ii:
            final_blocks.append(jj)
        
    for i in final_blocks:
        final_materials.append(0)

    if (protection_method3 == True):
        for i in range(len(final_blocks)):
            if final_blocks[i] in vulnerable_blocks:
                final_materials[i] = 3

    index = 0
    blocks_in_way_dup = find_blocks_in_way(complete_locations,final_pig_positions,selected_other,final_platforms)

    blocks_in_way_merged = []
    blocks_in_way = []
    for trajectory in blocks_in_way_dup:
        found = 0
        for pig_traj in blocks_in_way_merged:
            if trajectory[0] == pig_traj[0]:
                pig_traj[1] = pig_traj[1]+trajectory[1]
                found = 1
        if found == 0:
            blocks_in_way_merged.append(trajectory)
    for traj_new in blocks_in_way_merged:
        blocks_in_way.append(traj_new[1])
        
    for grouping in blocks_in_way:
        if (uniform(0.0,1.0) < trajectory_chance):
            material_choice = choose_item(probability_table_materials_trajectory)
            for block in grouping:
                for j in range(len(final_blocks)):
                    if block == final_blocks[j]:
                        if final_materials[j] == 0:
                            final_materials[j] = material_choice
                        
    for structure in complete_locations:
        
        if uniform(0.0,1.0) < cluster_chance:
            all_set = 0
            current_point = randint(0,len(structure)-1)
            #current_point = 0
            start_point = current_point
            material_choice = choose_item(probability_table_materials)
            while (all_set == 0):
                final_materials[index+current_point] = material_choice
                smallest_distance = 9999
                for i in range(len(structure)):
                    if final_materials[index+i] == 0:
                        if sqrt( ((structure[i][1]-structure[start_point][1]) * (structure[i][1]-structure[start_point][1])) +
                                 ((structure[i][2]-structure[start_point][2]) * (structure[i][2]-structure[start_point][2])) ) < smallest_distance:
                            smallest_distance = sqrt( ((structure[i][1]-structure[start_point][1]) * (structure[i][1]-structure[start_point][1])) +
                                                      ((structure[i][2]-structure[start_point][2]) * (structure[i][2]-structure[start_point][2])) )
                            current_point = i
                            if uniform(0.0,1.0) < cluster_swap_prob:
                                material_choice = choose_item(probability_table_materials)
                                start_point = current_point
                if smallest_distance == 9999:
                    all_set = 1
            index = index + len(structure)  
                    
        elif uniform(0.0,1.0) < random_chance:
            for block in structure:
                material_choice = choose_item(probability_table_materials)
                if final_materials[index] == 0:
                    final_materials[index] = material_choice
                index = index + 1
        
        elif len(structure) <= small_threshold:
            material_choice = choose_item(probability_table_materials)
            for block in structure:
                if final_materials[index] == 0:
                    final_materials[index] = material_choice
                index = index + 1

        else:
            current_y = 999
            for block in structure:
                if block[2] != current_y:
                    material_choice = choose_item(probability_table_materials)
                    current_y = block[2]
                if final_materials[index] == 0:
                    final_materials[index] = material_choice
                index = index + 1

    return final_materials, final_blocks




# selects the type and order of the birds, based on level properties

def find_bird_order(complete_locations, final_pig_positions, final_platforms, selected_other, final_materials):
    number_wood = 0
    number_ice = 0
    number_stone = 0
    number_protected = 0
    number_unprotected = 0

    total_number_blocks = len(final_materials)
    total_number_pigs = len(final_pig_positions)

    for i in final_materials:
        if i == 1:
            number_wood = number_wood + 1
        if i == 2: 
            number_ice = number_ice + 1
        if i == 3:
            number_stone = number_stone + 1

    hittable_dup = find_hittable_pigs(complete_locations,final_pig_positions,selected_other,final_platforms)
    hittable_final = []
    for i in hittable_dup:
        if i not in hittable_final:
            hittable_final.append(i)
    number_protected = total_number_pigs-len(hittable_final)

    unprotected_dup = find_unprotected_pigs(complete_locations,final_pig_positions,selected_other,final_platforms)
    unprotected_final = []
    for i in unprotected_dup:
        if i not in unprotected_final:
            unprotected_final.append(i)
    number_unprotected = len(unprotected_final)

    print("Number of wood blocks: ", number_wood)
    print("Number of ice blocks: ", number_ice)
    print("Number of stone blocks: ", number_stone)
    print("Number of protected pigs: ", number_protected)
    print("Number of unprotected pigs: ", number_unprotected)
    
    wood_ratio = number_wood/total_number_blocks
    ice_ratio = number_ice/total_number_blocks
    stone_ratio = number_stone/total_number_blocks
    protected_ratio = number_protected/total_number_pigs
    unprotected_ratio = number_unprotected/total_number_pigs

    total_ratio = wood_ratio + ice_ratio + stone_ratio + protected_ratio + unprotected_ratio

    yellow = wood_ratio/total_ratio * number_yellow_birds_weight
    blue = ice_ratio/total_ratio * number_blue_birds_weight
    black = stone_ratio/total_ratio * number_black_birds_weight
    white = protected_ratio/total_ratio * number_white_birds_weight
    red = unprotected_ratio/total_ratio * number_red_birds_weight

    n = 0.0
    current_birds = [0,0,0,0,0]
    bird_order = []
    while (n < number_birds):

        n = n+1

        new_birds = deepcopy(current_birds)
        new_birds[0] = new_birds[0]+1
        yellow_error = abs((new_birds[0]/n)-yellow)
        blue_error = abs((new_birds[1]/n)-blue)
        black_error = abs((new_birds[2]/n)-black)
        red_error = abs((new_birds[3]/n)-red)
        white_error = abs((new_birds[4]/n)-white)
        total_yellow_error = yellow_error+blue_error+black_error+red_error+white_error

        lowest_error = total_yellow_error
        best_choice = 0

        new_birds = deepcopy(current_birds)
        new_birds[1] = new_birds[1]+1
        yellow_error = abs((new_birds[0]/n)-yellow)
        blue_error = abs((new_birds[1]/n)-blue)
        black_error = abs((new_birds[2]/n)-black)
        red_error = abs((new_birds[3]/n)-red)
        white_error = abs((new_birds[4]/n)-white)
        total_blue_error = yellow_error+blue_error+black_error+red_error+white_error

        if lowest_error > total_blue_error:
            lowest_error = total_blue_error
            best_choice = 1
        if lowest_error == total_blue_error:
            if current_birds[best_choice] > current_birds[1]:
                best_choice = 1

        new_birds = deepcopy(current_birds)
        new_birds[2] = new_birds[2]+1
        yellow_error = abs((new_birds[0]/n)-yellow)
        blue_error = abs((new_birds[1]/n)-blue)
        black_error = abs((new_birds[2]/n)-black)
        red_error = abs((new_birds[3]/n)-red)
        white_error = abs((new_birds[4]/n)-white)
        total_black_error = yellow_error+blue_error+black_error+red_error+white_error

        if lowest_error > total_black_error:
            lowest_error = total_black_error
            best_choice = 2
        if lowest_error == total_black_error:
            if current_birds[best_choice] > current_birds[2]:
                best_choice = 2

        new_birds = deepcopy(current_birds)
        new_birds[3] = new_birds[3]+1
        yellow_error = abs((new_birds[0]/n)-yellow)
        blue_error = abs((new_birds[1]/n)-blue)
        black_error = abs((new_birds[2]/n)-black)
        red_error = abs((new_birds[3]/n)-red)
        white_error = abs((new_birds[4]/n)-white)
        total_red_error = yellow_error+blue_error+black_error+red_error+white_error

        if lowest_error > total_red_error:
            lowest_error = total_red_error
            best_choice = 3
        if lowest_error == total_red_error:
            if current_birds[best_choice] > current_birds[3]:
                best_choice = 3

        new_birds = deepcopy(current_birds)
        new_birds[4] = new_birds[4]+1
        yellow_error = abs((new_birds[0]/n)-yellow)
        blue_error = abs((new_birds[1]/n)-blue)
        black_error = abs((new_birds[2]/n)-black)
        red_error = abs((new_birds[3]/n)-red)
        white_error = abs((new_birds[4]/n)-white)
        total_white_error = yellow_error+blue_error+black_error+red_error+white_error

        if lowest_error > total_white_error:
            lowest_error = total_white_error
            best_choice = 4
        if lowest_error == total_white_error:
            if current_birds[best_choice] > current_birds[4]:
                best_choice = 4

        current_birds[best_choice] = current_birds[best_choice]+1
        bird_order.append(best_choice)

    return bird_order




# add the desired number of tnt to the level

def add_tnt(possible_tnt_positions, final_pig_positions, complete_locations, final_platforms, vulnerable_blocks, selected_other):
    final_tnt_positions = []
    block_placed = True
    tnt_width = tnt_size[0]
    tnt_height = tnt_size[1]
    pig_width = pig_size[0]
    pig_height = pig_size[1]
    to_remove = []
    
    for i in possible_tnt_positions:
        remove_me = False
        for j in final_pig_positions:

            if not( round((j[0] - pig_width/2),10) >= round((i[0] + tnt_width/2),10) or
                     round((j[0] + pig_width/2),10) <= round((i[0] - tnt_width/2),10) or
                     round((j[1] + pig_height/2),10) <= round((i[1] - tnt_height/2),10) or
                     round((j[1] - pig_height/2),10) >= round((i[1] + tnt_height/2),10)):
                remove_me = True
        for j in selected_other:
            if not( round((j[1] - (additional_object_sizes[j[0]][0])/2),10) >= round((i[0] + tnt_width/2),10) or
                     round((j[1] + (additional_object_sizes[j[0]][0])/2),10) <= round((i[0] - tnt_width/2),10) or
                     round((j[2] + (additional_object_sizes[j[0]][1])/2),10) <= round((i[1] - tnt_height/2),10) or
                     round((j[2] - (additional_object_sizes[j[0]][1])/2),10) >= round((i[1] + tnt_height/2),10)):
                remove_me = True
        if (remove_me == True):
            to_remove.append(i)
                
    for k in to_remove:
        possible_tnt_positions.remove(k)
            
    while((block_placed == True) and (len(final_tnt_positions)<number_TNT)):
        block_placed = False
        tnt_values = []         # three factors used
        f1 = []                 # proximity to pigs / weak points (estimated damage)
        f2 = []                 # how far away the location is from other already selected locations (overall dispersion)
        f3 = []                 # how likely the location is to have other objects fall on it (occupancy estimation)

        for position in possible_tnt_positions:
            nearby_vulnerable = 0
            distance_threshold = 1.0
            for i in vulnerable_blocks:
                if (sqrt(((i[1]-position[0])*(i[1]-position[0]))+((i[2]-position[1])*(i[2]-position[1]))) < distance_threshold):
                    nearby_vulnerable = nearby_vulnerable + 1
            for j in final_pig_positions:
                if (sqrt(((j[0]-position[0])*(j[0]-position[0]))+((j[1]-position[1])*(j[1]-position[1]))) < distance_threshold):
                    nearby_vulnerable = nearby_vulnerable + 1
            f1.append(nearby_vulnerable)

            distance = 1
            tnt_f2_weight = 1.0
            for position2 in final_tnt_positions:
                distance = distance * sqrt((position[0] - position2[0])*(position[0] - position2[0]) +  (position[1] - position2[1])*(position[1] - position2[1]))
            if len(final_tnt_positions) > 0:
                f2.append((distance*tnt_f2_weight)/len(final_tnt_positions))
            else:
                f2.append(20.0)

            bonus_found = 0
            for platform in final_platforms:
                platform_edge1 = platform[0][0]-(platform_size[0]/2.0)
                platform_edge2 = platform[-1][0]+(platform_size[0]/2.0)
                if position[1] < platform[0][1]:
                    if (position[0] > (platform_edge1 - factor3_distance)) and (position[0] < platform_edge1):
                        bonus_found = 1
                    if (position[0] > platform_edge2) and (position[0] < (platform_edge2 + factor3_distance)):
                        bonus_found = 1
            if bonus_found == 1:
                f3.append(factor3_bonus)
            else:
                f3.append(0.0)
                    
        for i in range(len(possible_tnt_positions)):
            tnt_values.append(f1[i]+f2[i]+f3[i])

        max_value = 0
        max_i = 0
        for value in range(len(tnt_values)):
            if tnt_values[value] > max_value:
                max_value = tnt_values[value]
                max_i = value
                
        if max_value > TNT_placement_threshold:
            final_tnt_positions.append(possible_tnt_positions[max_i])       # choose the location with the greatest value
            block_placed = True

            # remove locations that are no longer valid
            tnt_choice = possible_tnt_positions[max_i]
            new_tnt_positions = []
            for i in range(len(possible_tnt_positions)):
                if ( round((tnt_choice[0] - tnt_width/2),10) >= round((possible_tnt_positions[i][0] + tnt_width/2),10) or
                     round((tnt_choice[0] + tnt_width/2),10) <= round((possible_tnt_positions[i][0] - tnt_width/2),10) or
                     round((tnt_choice[1] + tnt_height/2),10) <= round((possible_tnt_positions[i][1] - tnt_height/2),10) or
                     round((tnt_choice[1] - tnt_height/2),10) >= round((possible_tnt_positions[i][1] + tnt_height/2),10)):
                    new_tnt_positions.append(possible_tnt_positions[i])
            possible_tnt_positions = new_tnt_positions

    print("Number of TNT: ", len(final_tnt_positions))

    return final_tnt_positions




# add hills to the level under structures

def create_hills(complete_locations, possible_pig_positions,ground_divides):
    extra_platforms = []
    increment_increase = platform_size[0]
    up_amount = 0.0
    previous_end = -9999.0
    max_increase = 9999.0
    for i in range(len(complete_locations)):
        width = find_structure_width(complete_locations[i])
        extra_platforms.append([])

        midpoint = ground_divides[i]+((ground_divides[i+1]-ground_divides[i])/2.0)
        marker_1 = midpoint+increment_increase
        marker_2 = midpoint-increment_increase

        if(previous_end > -9998.0):
            new_start = midpoint - (width/2.0)
            jump_dist = new_start-previous_end
            max_increase = tan(radians(max_slope_angle))*jump_dist

        cur_increase = uniform(0.0,max_slope_increase)-(max_slope_increase/2.0)
        if cur_increase > max_increase:
            cur_increase = max_increase
        if cur_increase < -max_increase:
            cur_increase = -max_increase
        
        up_amount = up_amount+cur_increase
        if up_amount < 0.0:
            up_amount = 0.0
        if up_amount > max_slope_height:
            up_amount = max_slope_height
            
        for j in range(len(complete_locations[i])):
            complete_locations[i][j][2] = complete_locations[i][j][2] + up_amount
        for k in range(len(possible_pig_positions[i])):
            possible_pig_positions[i][k][1] = possible_pig_positions[i][k][1] + up_amount
        
        extra_platforms[i].append([midpoint,up_amount-(platform_size[1]/2.0)+absolute_ground])
        extra_platforms[i].append([midpoint,up_amount-(platform_size[1]*1.5)+absolute_ground])
        extra_platforms[i].append([midpoint,up_amount-(platform_size[1]*2.5)+absolute_ground])
        while marker_1 < (midpoint+width/2.0)-(platform_size[0]/2.0):
            extra_platforms[i].append([marker_1,up_amount-(platform_size[1]/2.0)+absolute_ground])
            extra_platforms[i].append([marker_2,up_amount-(platform_size[1]/2.0)+absolute_ground])
            extra_platforms[i].append([marker_1,up_amount-(platform_size[1]*1.5)+absolute_ground])
            extra_platforms[i].append([marker_2,up_amount-(platform_size[1]*1.5)+absolute_ground])
            extra_platforms[i].append([marker_1,up_amount-(platform_size[1]*2.5)+absolute_ground])
            extra_platforms[i].append([marker_2,up_amount-(platform_size[1]*2.5)+absolute_ground])
            marker_1 = marker_1+increment_increase
            marker_2 = marker_2-increment_increase
        marker_1 = marker_1-increment_increase
        marker_2 = marker_2+increment_increase
        final_jump = (midpoint+width/2.0)-(platform_size[0]/2.0)-marker_1
        marker_1 = marker_1+final_jump
        marker_2 = marker_2-final_jump
        extra_platforms[i].append([marker_1,up_amount-(platform_size[1]/2.0)+absolute_ground])
        extra_platforms[i].append([marker_2,up_amount-(platform_size[1]/2.0)+absolute_ground])
        extra_platforms[i].append([marker_1,up_amount-(platform_size[1]*1.5)+absolute_ground])
        extra_platforms[i].append([marker_2,up_amount-(platform_size[1]*1.5)+absolute_ground])
        extra_platforms[i].append([marker_1,up_amount-(platform_size[1]*2.5)+absolute_ground])
        extra_platforms[i].append([marker_2,up_amount-(platform_size[1]*2.5)+absolute_ground])

        previous_end = marker_1+(platform_size[0]/2.0)
        
    return complete_locations, possible_pig_positions, extra_platforms




# add angle terrain between structure hills (slopes)

def add_angled_terrain(pigs_placed_on_ground,extra_platforms_seperated):
        
    extra_platforms_angled = []

    if (pigs_placed_on_ground == False and add_slopes == True):
        for i in range(len(extra_platforms_seperated)):
            if i < len(extra_platforms_seperated)-1:
                difference_up = extra_platforms_seperated[i+1][0][1] - extra_platforms_seperated[i][0][1]
                difference_across = (extra_platforms_seperated[i+1][-1][0]-(platform_size[0]/2.0)) - (extra_platforms_seperated[i][-2][0]+(platform_size[0]/2.0))
                angle_needed = degrees(atan2(difference_up,difference_across))
                width_needed2 = sqrt(((difference_up*difference_up) + (difference_across*difference_across)))
                width_needed = width_needed2 / platform_size[0]

                temp1 = sqrt(((platform_size[1]/2.0)*(platform_size[1]/2.0))+((width_needed2/2.0)*(width_needed2/2.0)))
                temp2 = atan2(platform_size[1]/2.0,width_needed2/2.0)
                temp3 = abs(angle_needed)+degrees(temp2)

                extra_bit = cos(radians(temp3))*temp1
                extra_bit = (difference_across/2.0)-extra_bit

                if (angle_needed < 0.0):
                    extra_bit = extra_bit * -1.0

                extra_platforms_angled.append([(extra_platforms_seperated[i][-2][0]+extra_bit+(platform_size[0]/2.0))+(difference_across/2.0),
                                               (extra_platforms_seperated[i][0][1])+(difference_up/2.0),angle_needed,width_needed])
                extra_platforms_angled.append([(extra_platforms_seperated[i][-2][0]+extra_bit+(platform_size[0]/2.0))+(difference_across/2.0),
                                               (extra_platforms_seperated[i][0][1])+(difference_up/2.0)-platform_size[1],angle_needed,width_needed])

                if (difference_up > 0.0):
                    extra_platforms_angled.append([(extra_platforms_seperated[i][-2][0]+(platform_size[0]/2.0))+(difference_across/2.0),
                                                   (extra_platforms_seperated[i][0][1]),0.0,width_needed])
                    extra_platforms_angled.append([(extra_platforms_seperated[i][-2][0]+(platform_size[0]/2.0))+(difference_across/2.0),
                                                   (extra_platforms_seperated[i][0][1])-platform_size[1],0.0,width_needed])
                    extra_platforms_angled.append([(extra_platforms_seperated[i][-2][0]+(platform_size[0]/2.0))+(difference_across/2.0),
                                                   (extra_platforms_seperated[i][0][1])-(platform_size[1]*2.0),0.0,width_needed])
                if (difference_up < 0.0):
                    extra_platforms_angled.append([(extra_platforms_seperated[i][-2][0]+(platform_size[0]/2.0))+(difference_across/2.0),
                                                   (extra_platforms_seperated[i+1][0][1]),0.0,width_needed])
                    extra_platforms_angled.append([(extra_platforms_seperated[i][-2][0]+(platform_size[0]/2.0))+(difference_across/2.0),
                                                   (extra_platforms_seperated[i+1][0][1])-platform_size[1],0.0,width_needed])
                    extra_platforms_angled.append([(extra_platforms_seperated[i][-2][0]+(platform_size[0]/2.0))+(difference_across/2.0),
                                                   (extra_platforms_seperated[i+1][0][1])-(platform_size[1]*2.0),0.0,width_needed])

    return extra_platforms_angled




# remove any restricted blocks from the probability table (if all material combinations of this block are banned)

def remove_blocks(restricted_blocks):
    total_prob_removed = 0.0
    new_prob_table = deepcopy(probability_table_blocks)
    for block_name in restricted_blocks:
        for key,value in block_names.items():
            if value == block_name:
                total_prob_removed = total_prob_removed + probability_table_blocks[key]
                new_prob_table[key] = 0.0
    new_total = 1.0 - total_prob_removed
    for key, value in new_prob_table.items():
        new_prob_table[key] = value/new_total
    return new_prob_table





# generate level!
finished_levels = 0
while (finished_levels < number_levels):
    number_ground_structures = randint(minimum_number_ground_structures, maximum_number_ground_structures)
    number_platforms = randint(minimum_number_platform_structures, maximum_number_platform_structures)
    number_pigs = randint(minimum_number_pigs, maximum_number_pigs)
    number_TNT = randint(minimum_number_TNT, maximum_number_TNT)
    
    probability_table_blocks = normalise_dictionary(probability_table_blocks)
    probability_table_materials = normalise_dictionary(probability_table_materials)

    print("")
    print("Generating level: " + str(finished_levels))

    if (finished_levels) < 10:
        level_name = "0"+str(finished_levels)
    else:
        level_name = str(finished_levels)

    number_ground_structures, complete_locations, possible_pig_positions, pig_protect_values, ground_divides = create_ground_structures(number_ground_structures)

    complete_locations, possible_pig_positions,extra_platforms = create_hills(complete_locations, possible_pig_positions,ground_divides)

    extra_platforms_seperated = deepcopy(extra_platforms)
    extra_platforms =  []
    for i in extra_platforms_seperated:
        extra_platforms = extra_platforms + i

    possible_pig_positions_seperated = deepcopy(possible_pig_positions)
    possible_pig_positions = []
    for i in possible_pig_positions_seperated:
        possible_pig_positions = possible_pig_positions + i

    complete_ground_locations = deepcopy(complete_locations)

    number_platforms, final_platforms, platform_centers = create_platforms(number_platforms,complete_locations,possible_pig_positions)

    complete_locations, possible_pig_positions, pig_protect_values = create_platform_structures(final_platforms, platform_centers, complete_locations, possible_pig_positions, pig_protect_values)

    final_pig_positions,pigs_placed_on_ground = add_pigs(number_pigs, possible_pig_positions, complete_locations, pig_protect_values, final_platforms,extra_platforms)
    number_birds = choose_number_birds(final_pig_positions,number_ground_structures,number_platforms)
    number_birds = number_birds+1

    extra_platforms_angled = add_angled_terrain(pigs_placed_on_ground,extra_platforms_seperated)

    final_platforms.append(extra_platforms)

    complete_locations = swap_blocks(complete_locations, final_pig_positions, final_platforms)

    possible_trihole_positions, possible_tri_positions, possible_cir_positions, possible_cirsmall_positions = find_additional_block_positions(complete_locations)
    selected_other = add_additional_blocks(possible_trihole_positions, possible_tri_positions, possible_cir_positions, possible_cirsmall_positions)
    vulnerable_blocks = protect_vulnerable_blocks(complete_locations, complete_ground_locations, final_platforms, final_pig_positions, selected_other)

    final_tnt_positions = add_tnt(possible_pig_positions, final_pig_positions, complete_locations, final_platforms, vulnerable_blocks, selected_other)

    all_structures = []
    for structure in complete_locations:
        all_structures.append(structure)

    structure_others = []
    for i in complete_locations:
        structure_others.append([])

    structure_pigs = []
    for i in complete_locations:
        structure_pigs.append([])

    structure_tnts = []
    for i in complete_locations:
        structure_tnts.append([])

    for bb in selected_other:
        belows = find_below_blocks_other(bb,complete_locations)
        if len(belows)>0:
            below_block = belows[0]
            for i in range(len(complete_locations)):
                if below_block in complete_locations[i]:
                    structure_others[i].append(bb)

    for bb in final_tnt_positions:
        belows = find_below_blocks_tnt(bb,complete_locations)
        if len(belows)>0:
            below_block = belows[0]
            for i in range(len(complete_locations)):
                if below_block in complete_locations[i]:
                    structure_tnts[i].append(bb)

    for bb in final_pig_positions:
        belows = find_below_blocks_pig(bb,complete_locations)
        if len(belows)>0:
            below_block = belows[0]
            for i in range(len(complete_locations)):
                if below_block in complete_locations[i]:
                    structure_pigs[i].append(bb)

    new_all_structures = deepcopy(all_structures)
    new_structure_others = deepcopy(structure_others)
    new_structure_pigs = deepcopy(structure_pigs)
    new_structure_tnts = deepcopy(structure_tnts)

    final_materials, final_blocks = set_materials(complete_locations, final_pig_positions, vulnerable_blocks)

    bird_order = find_bird_order(complete_locations, final_pig_positions, final_platforms, selected_other, final_materials)

    write_level_xml(final_blocks, selected_other, final_pig_positions, final_platforms, number_birds, bird_order, final_materials, final_tnt_positions, extra_platforms_angled, level_name)

    finished_levels = finished_levels + 1

