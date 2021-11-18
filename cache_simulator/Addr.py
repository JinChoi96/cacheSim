class Addr:
    def __init__(self, task=-1, color=-1, set=-1, line=-1, data=-1):
        self.task_id = task
        self.color = color
        self.set_idx = set
        self.line_idx = line
        self.data_idx = data

    def __str__(self):
        return "[Addr] task : %-5s dataId: %-5s color: %-5s setId: %-5s lineId: %-5s" \
            % (self.task_id, self.data_idx, self.color, self.set_idx, self.line_idx)
    
    def get_task_id(self):
        return self.task_id

    def get_set_idx(self):
        return self.set_idx
    
    def get_line_idx(self):
        return self.line_idx
    
    def get_color(self):
        return self.color

    def get_data_idx(self):
        return self.data_idx

    def set_color(self, color):
        self.color = color
        
    def set_set_idx(self, idx):
        self.set_idx = idx

    def set_id(self, id):
        self.task_id = id

    def set_data_idx(self, data):
        self.data_idx = data
