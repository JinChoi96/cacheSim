from utils import *

class Param:        
    def __init__(self, name = "", sole = False, partitioning = True, translate_level = 1,\
        seq_acc_ratio = [0.9, 0.9, 0.9, 0.9],
        color_list = [[0,1,2,3,4,5,6], [7], [7], [7]],
        colors = 8,
        line_size = 4,
        cache_capacity = 256,
        cache_ways = 8,
        pa_capacity = 8192,
        data_size = 128):

        self.iteration = 1000
        self.ticks = 700
        self.name = name

        # pas params
        self.sole = sole
        self.partitioning = partitioning if self.sole is False else False   # when False, colors is set to 1
        self.colors = colors if self.partitioning else 1
        self.line_size = line_size
        self.cache_capacity = cache_capacity
        self.cache_ways = cache_ways
        self.pa_capacity = pa_capacity # enough space than data size 
        self.translate_level = translate_level if self.partitioning else 1
        self.stage_2_translate_offset = 2 if self.translate_level == 2 else 0

        # task params
        self.hit_time = 0.001
        self.miss_penalty = 0.015
        self.base        = ['r', 'r', 'r', 'r', 'x', 'r', 'r', 'r', 'r', 'r']
        self.interfere   = ['r', 'x', 'x', 'r', 'r', 'x', 'x', 'x', 'x', 'r']


        self.data_size = data_size
        self.execution_pattern_type  = ['b','i', 'i', 'i']  # b : base, i : interfere 
        self.seq_acc_ratio = seq_acc_ratio
        # self.seq_acc_ratio = [0.9, 0.9, 0.9, 0.9]  # 1 : sequential, 0 : random 
        # self.color_list_of_task = [
        #     [0,1,2,3,4,5,6],
        #     [7],
        #     [7],
        #     [7]
        #     ] if self.partitioning else [[0],[0],[0],[0]]
        self.color_list_of_task = color_list if self.partitioning else [[0],[0],[0],[0]]

        if self.sole == True:
            # self.partitioning = False
            self.execution_pattern_type = ['b']
            self.seq_acc_ratio = [0.9]
            self.color_list_of_task = [[0]]
        
        # used for PAS construction
        self.page_param = {
            "name" : "IPA",
            "type" : 'page table',
            "colors" : self.colors,
            "line_size" : self.line_size,
            "cache_capacity" : self.cache_capacity,
            "cache_ways" : self.cache_ways,
            "pa_capacity" : self.pa_capacity,
            "partitioning" : self.partitioning
        }

        self.stage_2_page_table = {
            "name" : "PA",
            "type" : "page table",
            "colors" : self.colors,
            "line_size" : self.line_size,
            "cache_capacity" : self.cache_capacity,
            "cache_ways" : self.cache_ways,
            "pa_capacity" : self.pa_capacity, # assume IPAS == PAS,
            "stage_2_translate_offset" : self.stage_2_translate_offset,
            "partitioning" : self.partitioning
        }

        self.cache_param = {
            "name" : "CACHE",
            "type" : 'cache',
            "colors" : self.colors,
            "line_size" : self.line_size,
            "cache_capacity" : self.cache_capacity,
            "cache_ways" : self.cache_ways,
            "pa_capacity" : self.pa_capacity
        }    

        # assertion
        assert self.ticks % len(self.base) == 0
        assert self.pa_capacity % self.line_size == 0  

        if self.partitioning is True:
            assert self.colors > 1 

        assert len(self.execution_pattern_type) == len(self.color_list_of_task) == len(self.seq_acc_ratio)
        assert (self.cache_capacity / (self.line_size * self.cache_ways)) / self.colors >= 1\
            , 'cache capacity should be larger than %d'%(self.line_size * self.cache_ways * self.colors)

        assert self.pa_capacity / self.colors >= len(self.execution_pattern_type) * self.data_size,\
            'pa_capacity should be larger than %d'%(len(self.execution_pattern_type) * self.data_size * self.colors)

        
    def show_params_list(self):
        # parameter list
        param_str = ["name", "ticks", "execution pattern type", "access pattern", "partitioning","translate level", "translate offset","colors", "lines size", \
            "cache capacity", "cache ways", "cache sets", "ipa capacity" ]

        cache_sets = int(self.cache_capacity / (self.cache_ways * self.line_size))
        show_params(param_str, [self.name, self.ticks, self.execution_pattern_type, self.seq_acc_ratio, self.partitioning, self.translate_level, self.stage_2_translate_offset, self.colors, self.line_size,\
                    self.cache_capacity, self.cache_ways, cache_sets, self.pa_capacity ])
