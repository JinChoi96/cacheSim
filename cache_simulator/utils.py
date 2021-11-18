dash = "================="

def show_params(strs, params):
    print(dash + "Parameters" + dash)
    for s,p in zip(strs, params):
        print("%-25s : %s" %(s, str(p)))
    print(dash + dash)

# miss type
COLD_MISS = 0
INTER_TASK_MISS = 1
INTRA_TASK_MISS = 2