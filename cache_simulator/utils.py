from random import randint

dash = "================="

def show_params(strs, params):
    print(dash + "Parameters" + dash)
    for s,p in zip(strs, params):
        print("%-25s : %s" %(s, str(p)))
    print(dash + dash)

# miss type
COLD_MISS = 0
INTER_TASK_MISS = 1
INTRA_TASK_MISS = 2

import math
def dec_to_bin(dec, length):
    binary = ''
    while dec > 0:
        dec, mod = divmod(dec, 2)
        binary += str(mod)
    if len(binary) < length:
        for c in range(length - len(binary)):
            binary += '0'
    return binary[::-1]

def build_bitmap(bits):
    map = []
    for i in range(pow(2, bits)): # 2^4
        map.append(dec_to_bin(i, bits))
    return map
    
def get_indices(mask, target):
    indices = []
    _from = 0
    while _from < len(mask):
        cand = mask.find(target, _from)
        if cand != -1:
            indices.append(cand)
            _from = cand + 1
        else:
            _from += 1
    return indices

def spread_map(map, indices, length):
    spreaded = []
    for i in range(len(map)): # color 개수
        line = ''
        cur_idx = 0
        for l in range(length): # bit 수
            if cur_idx < len(indices) and l == indices[cur_idx]:
                line += map[i][cur_idx]
                cur_idx += 1
            else:
                line += "-"
        spreaded.append(line)
    return spreaded

def is_color(color, bitmap):
    assert len(color) == len(bitmap)
    for i in range(len(color)):
        if color[i] == '-':
            continue
        else:
            if color[i] != bitmap[i]:
                return False
    return True

def map_set_to_color(color_mask, bitmap):
    map = []
    color_map = build_bitmap(color_mask.count('1'))
    indices = get_indices(color_mask, '1')
    colors = spread_map(color_map, indices, len(color_mask))
    for i in range(len(bitmap)):
        for c in range(len(colors)):
            if is_color(colors[c], bitmap[i]):
                map.append(c)
    return map 

def get_bit_len(dec):
    bit_len = -1
    while dec > 0:
        dec, _ = divmod(dec, 2)
        bit_len += 1
    return bit_len
