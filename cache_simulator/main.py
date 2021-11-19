from Task import *
from PAS import *
from Addr import *
from MM import *
from utils import *
from params import *

import statistics

def initialize_mm(param):
    
    # initialize page table or free_lists[colors]
    page_table = PAS(**param.page_param)
    #page_table.show_global_pas()

    stage_2_page_table = PAS(**param.stage_2_page_table)

    cache = PAS(**param.cache_param)
    #cache.show_global_pas()

    mm = MM(page_table, stage_2_page_table, cache)

    return page_table, stage_2_page_table, cache, mm

def initialize_task(mm):
    # initialize tasks
    task_set = []
    #print(dash+"Tasks"+dash)
    for i in range(len(param.execution_pattern_type)):
        # TODO : move params to json  
        task_param = {
            "id"        : i,
            "cpu_core"  : i,
            "data_size" : param.data_size,
            "color"     : param.color_of_task[i],
            "execution_pattern_type"   : param.execution_pattern_type[i],
            "ticks"     : param.ticks,
            "mm"        : mm,
            "hit_time"  : param.hit_time,
            "miss_penalty" : param.miss_penalty,
            "base"      : param.base,
            "interfere" : param.interfere,
            "seq_acc_ratio"  : param.seq_acc_ratio[i],
            "translate_level" : param.translate_level
        }
        task_set.append(Task(**task_param))
        #print(task_set[i])
    #print(dash+dash)

    # As for now, no swapping
    assert param.pa_capacity >= task_set[0].get_size()

    #task_set[0].show_global_vas()

    return task_set

if __name__ == "__main__":
    param = Param()
    executions = []
    misses = []

    for i in range(len(param.execution_pattern_type)):
        executions.append([])
        misses.append([])

    for iter in range(param.iteration):  
        # initialize
        page_table, stage_2_page_table, cache, mm = initialize_mm(param)
        task_set = initialize_task(mm)

        # execute tasks as their access pattern for amount of ticks 
        for tick in range(param.ticks):
            for task in task_set:
                task.execute(tick)
        # termination
        Task.terminate()

        for t in range(len(task_set)):
            executions[t].append(task_set[t].execution_time)
            misses[t].append(task_set[t].get_total_miss())

    print(dash + "Execution time (%d iters)"%(param.iteration) + dash)
    for t in range(len(task_set)):
        if param.iteration == 1:
            _mean = executions[t][0]
            _stdev = 0
        else:
            _mean = statistics.mean(executions[t])
            _stdev = statistics.stdev(executions[t])
        print('[task %d (%s)] Execution time average : %f min: %f max: %f stdev: %f'%\
            (t, task_set[t].execution_pattern_type, _mean, min(executions[t]), max(executions[t]), _stdev))
    print(dash + dash)

    print(dash + "Miss counts" + dash)
    print("ave access: %d, hit: %d, miss: %d"%(mm.get_access_cnt()/param.iteration, mm.get_hit_cnt()/param.iteration, mm.get_miss_cnt()/param.iteration))
    for t in task_set:
        t.show_cache_count()
    print(dash + dash)

    
