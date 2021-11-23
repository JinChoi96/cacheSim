from utils import *

class Task:
    global_vas = []
    global_vas_offset = 0
    task_num = 0


    def __init__(self, **kwargs):
        Task.task_num += 1
        
        self.ipas = []
        self.pas = []
        self.mm = kwargs.get('mm', '')

        self.execution_time = 0.0
        self.ticks = kwargs.get('ticks', 0)

        self.id = kwargs.get('id', -1)
        self.cpu_core = kwargs.get('cpu_core', -1)
        self.data_size = kwargs.get('data_size', -1) # as for now, data unit is a word (occupies an address line)
        self.color_list = kwargs.get('color_list', [])

        self.hit_time = kwargs.get('hit_time', 1)
        self.miss_penalty = kwargs.get('miss_penalty', 2)

        self.base = kwargs.get('base', [])
        self.interfere = kwargs.get('interfere', [])

        self.translate_level = kwargs.get('translate_level', 1)

        self.seq_acc_ratio = kwargs.get('seq_acc_ratio', 0)
        self.access_idx = 0
        
        self.execution_pattern_type = kwargs.get('execution_pattern_type', '')
        self.execution_pattern = self.generate_pattern()
        self.access_pattern = self.generate_access_pattern(self.seq_acc_ratio)

        # miss count
        self.cold_miss = 0
        self.inter_task_miss = 0
        self.intra_task_miss = 0
        self.miss_other = 0
        self.hit = 0

        # allocate va and pa
        self.allocate_vas()
        self.allocate_pas(1)
        if self.translate_level == 2:
            self.allocate_pas(2)
        #self.show_pas()


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

    def get_colors_of_task(self, pas):
        _colors = []
        for i in range(100):
            _colors.append(0)
            for s in range(len(pas)):
                if pas[s].color == i:
                    _colors[i] += 1
        return [i for i, e in enumerate(_colors) if e != 0]

    def show_pas(self):
        if self.translate_level == 1:
            print("task %d's color: %s"%(self.id, self.get_colors_of_task(self.ipas)))
            # print(dash + "IPA of Task %d" %(self.id) + dash)
            # for i in range(len(self.ipas)):
            #     print("[VA] : %d "%(self.vas[0]+i) + " => [IPA] " + str(self.ipas[i]))
            # print(dash + dash)
        elif self.translate_level == 2:
            print("task %d's color: %s"%(self.id, self.get_colors_of_task(self.pas)))
            # print(dash + "PA of Task %d" %(self.id) + dash)
            # for i in range(len(self.pas)):
            #     print("  [IPA] : %s "%(self.ipas[i]))
            #     print("=> [PA] : " + str(self.pas[i]))
            # print(dash + dash)


    def __str__(self):
        return "[Task] id : %-5s core: %-5s data size: %-5s color: %-5s vas: %-10s type: %s" \
            % (self.id, self.cpu_core, self.data_size, self.color_list, self.vas, self.execution_pattern_type)
    
    # getter and setter 
    def get_color_list(self):
        return self.color_list

    def get_data_size(self):
        return self.data_size

    def get_id(self):
        return self.id

    def get_size(self):
        return Task.global_vas[len(Task.global_vas)-1][0][1]

    def allocate_vas(self):
        self.vas = [Task.global_vas_offset, Task.global_vas_offset + self.data_size]
        Task.global_vas.append([self.vas, self.color_list]) # [start, end-1]
        Task.global_vas_offset += self.data_size
        return

    def allocate_pas(self, level):
        self.ipas = self.mm.get_page_table().get_free_frame(self, None)
        if level == 2:
            self.pas = self.mm.get_stage_2_page_table().get_free_frame(self, self.ipas)
        return

    def generate_pattern(self):
        unit = self.base if self.execution_pattern_type == 'b' else self.interfere
        assert self.ticks % len(unit) == 0
        pattern = []
        for _ in range(int(self.ticks / len(unit))):
            pattern += unit
        return pattern

    def va_to_ipa(self, offset):
        return self.ipas[offset]

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
        print("[Task %d (colors %s)] hit: %d, miss: %d (cold : %d, inter task : %d, intra task: %d, other: %d)" \
            % (self.id, self.color_list, self.hit, self.get_total_miss(), self.cold_miss, self.inter_task_miss, self.intra_task_miss, self.miss_other))

    def read(self, idx):
        # change to reference value
        offset = idx
        if self.translate_level == 1:
            pa = self.va_to_ipa(offset) # pa : Addr
        elif self.translate_level == 2:
            pa = self.va_to_pa(offset)
        # print("[Task: read()] va : %-5s <-> pa: %s" %(str(self.vas[0] + offset), pa))
        
        if self.mm.lookup_cache(pa):
            self.hit += 1
            return self.hit_time
        else:
            # TODO : error or exception handling
            miss_type = self.mm.handle_cache_miss(pa)
            self.count_miss(miss_type)
            return self.hit_time + self.miss_penalty

    def generate_access_pattern(self, seq_access_ratio):
        access_idx = []
        seq_idx = 0
        seq_cnt = int(seq_access_ratio * 10) # assume seq_access_ratio is 0.x 
        rand_cnt = len(self.base) - seq_cnt
        # bug
        #rand_cnt = int((1 - seq_access_ratio) * 10)
        iterations = int(len(self.execution_pattern) / len(self.base))
        for i in range(iterations):
            for s in range(seq_cnt):
                access_idx.append(seq_idx)
                seq_idx = (seq_idx + 1) % self.data_size
            for r in range(rand_cnt):
                rand_idx = randint(0, self.data_size-1)
                access_idx.append(rand_idx)
        return access_idx

    def execute(self, tick):
        assert tick < self.ticks
        pat = self.execution_pattern[tick]
        if pat == 'r':
            acc_idx = self.access_pattern[self.access_idx]
            self.access_idx += 1
            self.execution_time += self.read(acc_idx)
            return 
        elif pat == 'x':
            # do nothing
            return
        else:
            print('undefined pattern')
            return