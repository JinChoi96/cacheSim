from random import randint
from utils import *

class Task:
    global_vas = []
    global_vas_offset = 0
    task_num = 0


    def __init__(self, **kwargs):
        Task.task_num += 1
        
        self.pas = []
        self.mm = kwargs.get('mm', '')

        self.execution_time = 0
        self.ticks = kwargs.get('ticks', 0)

        self.id = kwargs.get('id', -1)
        self.cpu_core = kwargs.get('cpu_core', -1)
        self.data_size = kwargs.get('data_size', -1) # as for now, data unit is a word (occupies an address line)
        self.color = kwargs.get('color', -1)

        self.hit_time = kwargs.get('hit_time', 1)
        self.miss_penalty = kwargs.get('miss_penalty', 2)

        self.base = kwargs.get('base', [])
        self.interfere = kwargs.get('interfere', [])

        self.access_pattern = kwargs.get('access_pattern', '')
        self.access_idx = 0

        self.allocate_vas()
        
        self.execution_pattern_type = kwargs.get('execution_pattern_type', '')
        self.execution_pattern = self.generate_pattern()

        # miss count
        self.cold_miss = 0
        self.inter_task_miss = 0
        self.intra_task_miss = 0
        self.miss_other = 0
        self.hit = 0


    def terminate():
        Task.global_vas = []
        Task.global_vas_offset = 0
        Task.task_num = 0

    def get_total_miss(self):
        return self.cold_miss + self.inter_task_miss + self.intra_task_miss + self.miss_other

    # log functions
    def show_global_vas(self):
        print(dash + "VAS" + dash)
        for i in range(Task.task_num):
            print("(%5d - %-5d) - task %d color %d" % (Task.global_vas[i][0][0], Task.global_vas[i][0][1], i, Task.global_vas[i][1]))
        print(dash + dash)
        return

    def show_pas(self):
        print(dash + "PA of Task %d" %(self.id) + dash)
        for i in range(len(self.pas)):
            print("[VA] : %d "%(self.vas[0]+i) + " => [PA] " + str(self.pas[i]))
        print(dash + dash)
    
    def __str__(self):
        return "[Task] id : %-5s core: %-5s data size: %-5s color: %-5s vas: %-10s type: %s" \
            % (self.id, self.cpu_core, self.data_size, self.color, self.vas, self.execution_pattern_type)
    
    # getter and setter 
    def get_color(self):
        return self.color

    def get_data_size(self):
        return self.data_size

    def get_id(self):
        return self.id

    def get_size(self):
        return Task.global_vas[len(Task.global_vas)-1][0][1]

    def set_pas(self):
        frame = self.mm.get_page_table().get_free_frame(self)
        self.pas = frame
        return

    # 
    def allocate_vas(self):
        self.vas = [Task.global_vas_offset, Task.global_vas_offset + self.data_size]
        Task.global_vas.append([self.vas, self.color]) # [start, end-1]
        Task.global_vas_offset += self.data_size
        return

    def insert_to_pas(self, addr):
        self.pas.append(addr)

    def generate_pattern(self):
        unit = self.base if self.execution_pattern_type == 'b' else self.interfere
        assert self.ticks % len(unit) == 0
        pattern = []
        for _ in range(int(self.ticks / len(unit))):
            pattern += unit
        return pattern

    def va_to_pa(self, offset):
        return self.pas[offset]

    def count_miss(self, miss_type):
        if miss_type == COLD_MISS:
            self.cold_miss += 1
        elif miss_type == INTER_TASK_MISS:
            self.inter_task_miss += 1
        elif miss_type == INTRA_TASK_MISS:
            self.intra_task_miss += 1
        else:
            self.miss_other += 1

    def show_cache_count(self):
        print("[Task %d (color %d)] hit: %d, miss: %d (cold : %d, inter task : %d, intra task: %d, other: %d)" \
            % (self.id, self.color, self.hit, self.get_total_miss(), self.cold_miss, self.inter_task_miss, self.intra_task_miss, self.miss_other))

    def read(self, idx):
        # change to reference value

        offset = idx
        pa = self.va_to_pa(offset) # pa : Addr
        # print("[Task: read()] va : %-5s <-> pa: %s" %(str(self.vas[0] + offset), pa))
        
        if self.mm.lookup_cache(pa):
            self.hit += 1
            return self.hit_time
        else:
            # TODO : error or exception handling
            miss_type = self.mm.handle_cache_miss(pa)
            self.count_miss(miss_type)
            return self.hit_time + self.miss_penalty

    def execute(self, tick):
        assert tick < self.ticks
        pat = self.execution_pattern[tick]
        if pat == 'r':
            if self.access_pattern == 'rand':
                self.access_idx = randint(0, self.data_size-1)
            else:
                self.access_idx = (self.access_idx + 1) % self.data_size

            self.execution_time += self.read(self.access_idx)
            return 
        elif pat == 'x':
            # do nothing
            return
        else:
            print('undefined pattern')
            return