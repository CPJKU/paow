import numpy as np
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import scipy
import json
import copy
import xml.etree.ElementTree as ET
import cv2 as cv


DEFAULT_NODE = json.loads("{\"force_scale\":false,\"probability\":100,\"midi_data\":{\"Primary\":60,\"Secondary\":100,\"Channel\":1,\"RawChannel\":0,\"Duration\":1.0,\"Repeat\":0,\"Root\":0,\"Scale\":0},\"relative_midi_data\":{\"Primary\":0,\"RangedPrimary\":0,\"Secondary\":0,\"Channel\":0,\"Duration\":0.0,\"Repeat\":0,\"Root\":0,\"Scale\":0,\"RangeFields\":{\"Primary\":{\"Up\":false,\"Down\":false},\"Secondary\":{\"Up\":false,\"Down\":false},\"Channel\":{\"Up\":false,\"Down\":false},\"Duration\":{\"Up\":false,\"Down\":false},\"Repeat\":{\"Up\":false,\"Down\":false}},\"Pass\":{\"Primary\":false,\"Secondary\":false,\"Channel\":false,\"Duration\":false,\"Repeat\":false}},\"pass\":false,\"label\":\"\",\"color\":{\"B\":255,\"G\":255,\"R\":255,\"A\":255},\"group_data\":{\"Groups\":[false,false,false,false,false,false,false,false,false,false]},\"mute\":false,\"Start\":false,\"ID\":0,\"IsMIDIPoint\":true,\"Origin\":\"-287.07684, -120.8461\",\"PathMode\":0,\"SignalMode\":0,\"SerializablePathTo\":[],\"SerializablePathFrom\":[],\"SerializableLogicPathTo\":[],\"SerializableLogicPathFrom\":[]}")
DEFAULT_EDGE = json.loads("{\"source_id\":0,\"target_id\":3,\"origin_part\":1,\"destination_part\":7,\"origin_position\":4,\"weight\":1,\"logic\":false,\"PathMode\":0}")

def nodewriter(position, 
               pitch, 
               id,
               start = False):
    
    new_node = copy.deepcopy(DEFAULT_NODE)
    if start:
        new_node["Start"] = True
    new_node['Origin'] = "{0:10.4f},{1:10.4f}".format(position[0],position[1])
    new_node['ID'] = int(id)
    new_node['PathMode'] = int(2)
    new_node['midi_data']['Primary'] = int(pitch)
    initstring = '{"type":1,"json":"' + json.dumps(new_node).replace("\"","\\\"").replace(" ","") + '"}'
    return initstring

def edgewriter(start, 
               end):
    
    new_edge = copy.deepcopy(DEFAULT_EDGE)
    new_edge['source_id'] = int(start) 
    new_edge['target_id'] = int(end) 
    new_edge['PathMode'] = int(2)
    initstring = '{"type":5,"json":"' + json.dumps(new_edge).replace("\"","\\\"").replace(" ","") + '"}'
    return initstring

def cont2vectors(contour, 
                 file, width, height, 
                 pitches, modulo, distance_threshold,
                 id_prepend):

    prev_node = None
    counter = 0 
    
    dist = distance_threshold + 10
    start = True
    for node in contour:
        
        if prev_node is not None:
            start = False
            dist = np.sqrt(np.sum(np.power(node-prev_node, 2)))
        if dist > distance_threshold:
            file.write(nodewriter([node[0]-width/2, 
                                    node[1]-height/2], 
                        pitches[counter%modulo], 
                        id=counter+id_prepend, 
                        start=start) + "\n")
            
            counter += 1
            prev_node = node

    ids = np.arange(id_prepend,counter+id_prepend)

    for k in [0]:#range(4,-1,-1):
        connects1 = np.copy(ids)[::k+1]
        for st, en in zip(connects1[:-1],connects1[1:]):
            file.write(edgewriter(st, en) + "\n")
        file.write(edgewriter(connects1[-1], connects1[0]) + "\n")

    return counter
    
def file_writer(file, 
                list_of_contours, list_of_pitches, list_of_modulos, 
                width, height, thresholds):
    file.write(r'{"type":0,"json":"\"1.1.6.8\""}' + '\n')

    id_prepend = 0
    for contour, pitches, modulo, distance_threshold in zip(list_of_contours, list_of_pitches, list_of_modulos, thresholds):
        print(modulo, id_prepend)
        counter = cont2vectors(contour, file, width, height, pitches, modulo, distance_threshold, id_prepend)

        id_prepend += counter

    file.write(r'{"type":6,"json":"{\"tempo\":182.0,\"grid_size\":4,\"beat_division\":4,\"beat_division_selector_index\":1,\"doc_scale\":5,\"scale_selector_index\":4,\"doc_root\":0,\"root_selector_index\":0,\"clock_source\":2,\"camera_position\":\"0, 0\"}"}' +'\n')

## n-gonals, https://oeis.org/wiki/Polygonal_numbers
SEQS = [
    [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105, 120, 136, 153, 171, 190, 210, 231, 253, 276],
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225, 256, 289, 324, 361, 400, 441, 484],
    [0, 1, 5, 12, 22, 35, 51, 70, 92, 117, 145, 176, 210, 247, 287, 330, 376, 425, 477, 532, 590, 651],
    [0, 1, 6, 15, 28, 45, 66, 91, 120, 153, 190, 231, 276, 325, 378, 435, 496, 561, 630, 703, 780, 861],
    [0, 1, 7, 18, 34, 55, 81, 112, 148, 189, 235, 286, 342, 403, 469, 540, 616, 697, 783, 874, 970, 1071],
    [0, 1, 8, 21, 40, 65, 96, 133, 176, 225, 280, 341, 408, 481, 560, 645, 736, 833, 936, 1045, 1160],
    [0, 1, 9, 24, 46, 75, 111, 154, 204, 261, 325, 396, 474, 559, 651, 750, 856, 969, 1089, 1216, 1350]
]

if __name__ == "__main__":


    cont_path = r"_SET_PATH_"
    save_path = r"_SET_PATH_"
    
    g = cv.imread(cont_path)
    imgray = cv.cvtColor(g, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(imgray, 127, 255, 0)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    svg_lines = [c[:,0,:].astype(float) for c in contours[1:]]
    WIDTH = 2250.0
    HEIGHT = 1500.0
    WIDTH_IN = float(thresh.shape[1])
    HEIGHT_IN = float(thresh.shape[1])
    
    svg_lines_normalized = list()
    for line in svg_lines:
        new_line = np.copy(line)
        new_line[:,0] *= HEIGHT/HEIGHT_IN
        new_line[:,1] *= WIDTH/WIDTH_IN
        svg_lines_normalized.append(new_line.astype(int))
    
    octagonal_numbers = SEQS[np.random.randint(len(SEQS))]
    pitches = np.array(octagonal_numbers) % 24 + 70
    pitches_list = [pitches]*len(svg_lines)
    modulo_list = np.random.randint(3,len(octagonal_numbers), len(svg_lines))
    distance_thresholds = np.random.randint(100, 200,size=len(svg_lines))

    with open(save_path, "w") as f:
        file_writer(f, 
                    svg_lines_normalized, pitches_list, modulo_list,
                    WIDTH, HEIGHT, distance_thresholds)