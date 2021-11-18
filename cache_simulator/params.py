from utils import *

class Param:        
    def __init__(self):
        self.iteration = 5
        self.ticks = 1000

        # pas params
        self.partitioning = False    # when False, colors is set to 1
        self.colors = 2 if self.partitioning else 1
        self.line_size = 4
        self.cache_capacity = 64
        self.cache_ways = 8
        self.ipa_capacity = 1024

        # task params
        self.hit_time = 1
        self.miss_penalty = 15
        self.base        = ['r', 'r', 'r', 'r', 'r']
        self.interfere   = ['r', 'x', 'x', 'r', 'r']


        self.data_size = 256 #16
        self.execution_pattern_type  = ['b', 'i', 'i']   # b : base, i : interfere 
        # TODO : add access pattern itm (seq + rand)
        self.access_pattern = ['seq', 'seq', 'seq']       # seq : sequential, rand : random
        self.color_of_task           = [0,1,1]

        # parameter list
        self.param_str = ["ticks", "execution pattern type", "access pattern", "partitioning", "colors", "lines size", \
            "cache capacity", "cache ways", "ipa capacity" ]
        
        # used for PAS construction
        self.page_param = {
            "name" : "IPA",
            "type" : 'page table',
            "colors" : self.colors,
            "line_size" : self.line_size,
            "cache_capacity" : self.cache_capacity,
            "cache_ways" : self.cache_ways,
            "ipa_capacity" : self.ipa_capacity
        }
        self.cache_param = {
            "name" : "CACHE",
            "type" : 'cache',
            "colors" : self.colors,
            "line_size" : self.line_size,
            "cache_capacity" : self.cache_capacity,
            "cache_ways" : self.cache_ways,
            "ipa_capacity" : self.ipa_capacity
        }    

        # assertion
        assert self.ipa_capacity % self.line_size == 0  

        if self.partitioning is True:
            assert self.colors > 1 
        else:
            for i in range(len(self.color_of_task)):
                self.color_of_task[i] = 0
        assert max(self.color_of_task) < self.colors
        assert len(self.execution_pattern_type) == len(self.color_of_task)
        assert (self.cache_capacity / (self.line_size * self.cache_ways)) / self.colors >= 1

        show_params(self.param_str, [self.ticks, self.execution_pattern_type, self.access_pattern, self.partitioning, self.colors, self.line_size,\
            self.cache_capacity, self.cache_ways, self.ipa_capacity ])

