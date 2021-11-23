from utils import *

class Param:        
    def __init__(self):
        self.iteration = 10
        self.ticks = 700

        # pas params
        self.partitioning = True    # when False, colors is set to 1
        self.colors = 4 if self.partitioning else 1
        self.line_size = 4
        self.cache_capacity = 256
        self.cache_ways = 8
        self.pa_capacity = 4096 # enough space than data size 
        self.translate_level = 2 if self.partitioning else 1
        self.stage_2_translate_offset = 2 if self.translate_level == 2 else 0

        # task params
        self.hit_time = 0.001
        self.miss_penalty = 0.015
        self.base        = ['r', 'r', 'r', 'r', 'x', 'r', 'r', 'r', 'r', 'r']
        self.interfere   = ['r', 'x', 'x', 'r', 'r', 'x', 'x', 'x', 'x', 'r']


        self.data_size = 128 #16
        self.execution_pattern_type  = ['b','i', 'i', 'i']   # b : base, i : interfere 
        self.seq_acc_ratio = [0.9, 0.9, 0.9, 0.9]             # 1 : sequential, 0 : random 
        self.color_list_of_task = [[0,1,2],[3],[3],[3]] if self.partitioning else [[0],[0],[0],[0]]

        # parameter list
        self.param_str = ["ticks", "execution pattern type", "access pattern", "partitioning","translate level", "translate offset","colors", "lines size", \
            "cache capacity", "cache ways", "cache sets", "ipa capacity" ]
        
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

        cache_sets = int(self.cache_capacity / (self.cache_ways * self.line_size))
        show_params(self.param_str, [self.ticks, self.execution_pattern_type, self.seq_acc_ratio, self.partitioning, self.translate_level, self.stage_2_translate_offset, self.colors, self.line_size,\
            self.cache_capacity, self.cache_ways, cache_sets, self.pa_capacity ])

