from Addr import *
from utils import *

class PAS:
    def __init__(self, **kwargs):
        self.global_pas = []
        self.global_pas_offset = 0

        self.name = kwargs.get('name', '')
        self.type = kwargs.get('type', '')
        self.colors = kwargs.get('colors', 1)
        self.line_size = kwargs.get('line_size', 1)
        self.cache_capacity = kwargs.get('cache_capacity', 1)
        self.ways = kwargs.get('cache_ways', 1)
        self.ipa_capacity = kwargs.get('ipa_capacity', 1)
        
        self.cache_sets = int(self.cache_capacity / (self.ways * self.line_size))
        self.ipa_lines = int(self.ipa_capacity / self.line_size)
        
        self.sets_per_color = int(self.cache_sets / self.colors)
        if type == 'page table':
            self.size_per_color = int(self.ipa_capacity / self.colors)
        else:
            self.size_per_color = int(self.cache_capacity / self.colors)

        self.free_lists = []

        self.set_to_color = self._set_to_color()

#        print('[PAS %s] cache sets : %d, ipa lines: %d, sets per color : %d, size per color: %d' %
#            (self.type, self.cache_sets, self.ipa_lines, self.sets_per_color, self.size_per_color))

        for c in range(self.colors):
            self.allocate_pas_per_color(c)

        self.init_free_lists()


    def get_ways(self):
        return self.ways

    def _set_to_color(self):
        map = []
        for c in range(self.colors):
            for s in range(int(self.cache_sets / self.colors)):
                map.append(c)
        return map 

    def init_free_lists(self):
        # init free lists according to its type
        if self.type == 'page table':
            ## TODO : refactoring
            lists = []
            data_idx = -1
            for l in range(self.ipa_lines):
                for d in range(self.line_size):
                    data_idx += 1
                    lists.append(Addr(-1, -1, -1, l, data_idx))
            

            data_idx = -1
            while data_idx < (self.ipa_lines * self.line_size) -1:
                set_idx = -1
                for s in range(self.cache_sets): # 4 
                    set_idx +=1 
                    for l in range(self.line_size): # 2
                        data_idx += 1   
                        lists[data_idx].set_set_idx(set_idx)
    #                    lists[data_idx].set_color(self.set_to_color(set_idx))
                        #print("%s"%(lists[data_idx]))


            data_idx = -1
            while data_idx < (self.ipa_lines * self.line_size) -1:
                data_idx += 1
                set = lists[data_idx].get_set_idx()
                color = self.set_to_color[set]
                lists[data_idx].set_color(color)


            for c in range(self.colors):
                self.free_lists.append([])

            for d in range(len(lists)):
                color = lists[d].get_color()
                self.free_lists[color].append(lists[d])
                #print(lists[d])


        if self.type == 'cache':
            # Sets X Ways matrix
            for s in range(self.cache_sets):
                addr = Addr(-1, -1, s, -1)
                self.free_lists.append([])
                for w in range(self.ways):
                    self.free_lists[s].append(addr)

        #self.show_free_lists()
        return

    def show_free_lists(self):
        if self.type == 'page table':
            print(dash + 'Page table free list' + dash)
            for c in range(self.colors):
                print('color %d => %d lines (%d sets)'%(c, len(self.free_lists[c]) / self.line_size, self.sets_per_color))
            print(dash+dash)

        if self.type == 'cache':
            print(dash + 'Cache' + dash)
            print('Initialize cache : %d (sets) arrays (colors : %d, max length of each set (=way): %d)' \
                % (len(self.free_lists), self.colors, len(self.free_lists[0])))    
            print(dash+dash)

    def get_free_lists(self):
        return self.free_lists

    def show_detail_free_lists(self):
        if self.type == 'page table':
            for c in range(len(self.free_lists)):
                for d in range(len(self.free_lists[c])):
                    print(self.free_lists[c][d])
        if self.type == 'cache':
            for c in range(len(self.free_lists)):
                for d in range(len(self.free_lists[c])):
                    print(self.free_lists[c][d])
        return


    def allocate_pas_per_color(self, c):
        self.global_pas.append([[self.global_pas_offset, self.global_pas_offset + self.size_per_color], c])
        self.global_pas_offset += self.size_per_color
        return

    def get_free_frame(self, task):
        # get a frame for each task
        frame = []
        color = task.get_color()
        #print(len(self.free_lists[color]))
        for d in range(task.get_data_size()):
            addr = self.free_lists[color].pop(0)
            addr.set_id(task.get_id())
            addr.set_data_idx(d)
            # print(addr)
            frame.append(addr)
            
        return frame

    def replace(self, pa, way_idx):
        set = pa.get_set_idx()
        prev_addr = self.free_lists[set][way_idx]
        self.free_lists[set][way_idx] = pa
        if prev_addr.get_task_id() == -1:
            #print("cold miss")
            return COLD_MISS
        elif prev_addr.get_task_id() != pa.get_task_id() :
            #print("conflict from other task (%d -> %d)" %(pa.get_task_id(), prev_addr.get_task_id()))
            return INTER_TASK_MISS
        else :
            #print("replacement in set: %d (color: %d)"%(set, pa.get_color()))
            return INTRA_TASK_MISS

    def show_global_pas(self):
        print(dash + self.name + dash)
        if self.type == 'cache':
            print(" %d-way set associative" % self.ways)
        for i in range(self.colors):
            print("(%5d - %-5d) - color %d (%d sets)" % (self.global_pas[i][0][0], self.global_pas[i][0][1], self.global_pas[i][1], self.sets_per_color))
        print(dash + dash)
        return
