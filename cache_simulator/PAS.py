from Addr import *
from utils import *

class PAS:
    def __init__(self, **kwargs):
        self.global_pas = []
        self.global_pas_offset = 0

        self.name = kwargs.get('name', '')
        self.type = kwargs.get('type', '')
        self.colors = kwargs.get('colors', 1)
        self.partitioning = kwargs.get('partitioning', False)
        # self.color_mask = kwargs.get('color_mask', '')
        if self.partitioning == True:
            self.color_mask = '110'
            assert self.colors == pow(2,(self.color_mask.count('1')))
        self.line_size = kwargs.get('line_size', 1)
        self.cache_capacity = kwargs.get('cache_capacity', 1)
        self.ways = kwargs.get('cache_ways', 1)
        self.pa_capacity = kwargs.get('pa_capacity', 1)
        self.stage_2_translate_offset = kwargs.get('stage_2_translate_offset', 0)

        self.cache_sets = int(self.cache_capacity / (self.ways * self.line_size))
        assert self.stage_2_translate_offset < self.pa_capacity
        self.ipa_lines = int(self.pa_capacity / self.line_size)

        if self.partitioning == True:
            assert self.cache_sets == pow(2, len(self.color_mask)),\
                'cache sets %d should be the same with 2^%d'%(self.cache_sets, len(self.color_mask))

        self.sets_per_color = int(self.cache_sets / self.colors)
        if type == 'page table':
            self.size_per_color = int(self.pa_capacity / self.colors)
        else:
            self.size_per_color = int(self.cache_capacity / self.colors)

        self.free_lists = []

        if self.partitioning == True:
            self.set_to_color = self._set_to_color()


#        print('[PAS %s] cache sets : %d, ipa lines: %d, sets per color : %d, size per color: %d' %
#            (self.type, self.cache_sets, self.ipa_lines, self.sets_per_color, self.size_per_color))

        for c in range(self.colors):
            self.allocate_pas_per_color(c)

        self.init_free_lists()


    def get_ways(self):
        return self.ways

    def _set_to_color(self):
        bit_len = get_bit_len(self.cache_sets)
        bitmap = build_bitmap(bit_len)

        map = map_set_to_color(self.color_mask, bitmap)
        return map


    def mock_show_lists(self, lists):
        print(dash + "[PAS: init_free_lists()] show lists" + dash)
        for i in range(len(lists)):
            print(lists[i])
        print(dash + dash)

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
                if self.partitioning == True:
                    color = self.set_to_color[set]
                else:
                    color = 0
                lists[data_idx].set_color(color)

            if self.name == "IPA":
                for c in range(self.colors):
                    self.free_lists.append([])

                for d in range(len(lists)):
                    color = lists[d].get_color()
                    self.free_lists[color].append(lists[d])
                    #print(lists[d])
                
                #self.mock_show_lists(lists)
            elif self.name == "PA":
                self.free_lists = lists

            #self.show_free_lists()

        if self.type == 'cache':
            # Sets X Ways matrix
            for s in range(self.cache_sets):
                addr = Addr(-1, -1, s, -1)
                self.free_lists.append([])
                for w in range(self.ways):
                    self.free_lists[s].append(addr)

        return

    def show_free_lists(self):
        if self.type == 'page table':
            print(dash + 'Page table free list' + dash)
            if self.name == "PA":
                print("%d lines"%(len(self.free_lists)))
            if self.name == "IPA":
                for c in range(self.colors):
                    #print('[color %d] => '%(c))
                    #for a in self.free_lists[c]:
                    #    print(a)
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

    def get_free_frame(self, task, ipas):
        frame = []
        if ipas == None:
            # get a frame for each task
            color = task.get_color()
            #print(len(self.free_lists[color]))
            for d in range(task.get_data_size()):
                addr = self.free_lists[color].pop(0)
                addr.set_id(task.get_id())
                addr.set_data_idx(d)
                # print(addr)
                frame.append(addr)

        elif ipas:
            for addr in ipas:
                set = addr.get_set_idx()
                new_set = (set + self.stage_2_translate_offset) % self.cache_sets
                color = self.set_to_color[new_set]
                new_addr = Addr(addr.get_task_id(), color, new_set, addr.get_line_idx(), addr.get_data_idx())
                frame.append(new_addr)
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
