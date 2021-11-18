from random import randint

class MM:
    hit_cnt = 0
    miss_cnt = 0

    def __init__(self, page_table, cache):
        self.page_table = page_table
        self.cache = cache


    def get_access_cnt(self):
        access = self.hit_cnt + self.miss_cnt
        return access

    def get_hit_cnt(self):
        return self.hit_cnt
    
    def get_miss_cnt(self):
        return self.miss_cnt

    # move to PAS?
    def lookup_cache(self, pa):
        task_id = pa.get_task_id()
        color = pa.get_color()
        set = pa.get_set_idx()
        line = pa.get_line_idx()
        data = pa.get_data_idx()
        #print("[MM:is_pa_in_cache(pa)] (task %d) pa color: %d, set: %d, line : %d, data: %d"%(task_id, color, set, line, data))

        # TODO: rename free_lists. have different meaning from page table free lists  
        for w in range(self.cache.get_ways()):
            # or use getter??
            addr = self.cache.free_lists[set][w]
            c_line_color = addr.get_color()
            c_line_set = addr.get_set_idx()
            c_line = addr.get_line_idx()    
            #print("[MM:lookup_cache(pa)] cache line color: %d, set: %d, line : %d"%(c_line_color, c_line_set, c_line))   

            if set == c_line_set and line == c_line:
                if color == c_line_color:
                    MM.hit_cnt += 1
                    return True
                else:
                    # exception
                    print("[WARNING] pa color != cache line color. sth went wrong!")
            #else:
                #print("pa set or line != cache set or line")
        return False

    def handle_cache_miss(self, pa):
        # random replacement policy
        w = randint(0, self.cache.get_ways()-1)
        miss_type = self.cache.replace(pa, w)
        MM.miss_cnt += 1    
        return miss_type

    def get_page_table(self):
        return self.page_table

    def get_cache(self):
        return self.cache