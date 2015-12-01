import random
import yaml

events = {}

MAX_FLOOR = 10

for i in range(200):
    time = random.randrange(1,100)
    if(i%3 == 0):
        time = 20  # Sudden spike @ 20
    request_floor = random.randrange(0,MAX_FLOOR+1)
    # request_floor = 0 # Morning rush
    goal_floor = random.randrange(0,MAX_FLOOR+1)
    # goal_floor = 0 # Evacuate building
    request_direction = None
    if(request_floor > goal_floor):
        request_direction = 1
    elif(request_floor < goal_floor):
        request_direction = 2
    else:
        continue
    event = [request_floor, request_direction, goal_floor]
    if time in events:
        events[time].append(event)
    else:
        events[time] = [event]

events[102] = []

with open('sudden_spike.yaml','w') as f:
    f.write(yaml.dump(events))
