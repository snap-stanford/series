import sys
sys.stdout = open('turn_per_hour', 'w')

time = [0.0] * 64
turns = [0] * 64
total_hours = 0.0

with open('stats_time', 'r') as f:
    for line in f:
        contents = line.strip().split('\t')
        if contents[0].isdigit():
            uid = int(contents[0])
            hours = float(contents[2])
            time[uid] = hours
            total_hours += hours

with open('../stats/turn_stats/turn_stats.txt', 'r') as f:
    for line in f:
        contents = line.strip().split('\t')
        uid = int(contents[0])
        num_turns = int(contents[2])
        turns[uid] = num_turns

            
total_turns = sum(turns)

for i in range(0, 64):
    print turns[i] / time[i]

print total_turns / total_hours
