#!/usr/bin/env python
from enum import Enum
import yaml
import sys
import math

ElevatorState = Enum('ElevatorState', 'MOVING_DOWN MOVING_UP IDLE')
RequestDirection = Enum('RequestDirection', 'DOWN UP')

class Elevator:
    def __init__(self, id):
        self.id = id
        self.state = ElevatorState.IDLE
        self.floor = 0
        self.goal_floors = [] # Sorted list; MOVING_DOWN-Desc ; MOVING_UP-Asc
        self.skip_steps = 0
        self.proposed_requests_count = 0

    def __repr__(self):
        return str(self.id) + "-" + str(self.state) +"-" + str(list(self.goal_floors))

    def fulfil_request(self,request):
        '''
        Fulfill @request.
        Append @request.goal_floor to the sorted list @self.goal_floors
        @self.goal_floors is ascending if the elevator is MOVING_UP else descending if MOVING_DOWN
        '''
        if(request.goal_floor in self.goal_floors):
            return

        if(self.goal_floors):
            final_dest = self.goal_floors[-1]
            if(final_dest > self.floor):
                for i, f in enumerate(list(self.goal_floors)+[sys.maxint]):
                    if(f>request.goal_floor):
                        self.goal_floors.insert(i,request.goal_floor)
                        break

            elif(final_dest < self.floor):
                for i, f in enumerate(list(self.goal_floors)+[-1]):
                    if(f<request.goal_floor):
                        self.goal_floors.insert(i,request.goal_floor)
                        break
        else:
            self.goal_floors.append(request.goal_floor)


    def fulfilment_estimate(self, request):
        '''
        Return an estimate of time that would be needed to fulfill @request based on the present @goal_floors.
        '''
        estimate = None
        if(self.goal_floors):
            if (request.direction==RequestDirection.DOWN and self.state == ElevatorState.MOVING_DOWN):
                if(request.request_floor <= self.floor):
                    # Moving down ; Can pickup
                    estimate=self.floor-request.request_floor
                else:
                    # Moving down ; Cant pickup
                    estimate=abs(self.goal_floors[-1] - self.floor) +\
                           abs(self.goal_floors[-1] - request.request_floor)

            elif(request.direction==RequestDirection.UP and self.state == ElevatorState.MOVING_UP):
                if(request.request_floor >= self.floor):
                    # Moving down ; Can pickup
                    estimate=request.request_floor-self.floor
                else:
                    # Moving up ; Cant pickup
                    estimate=abs(self.goal_floors[-1] - self.floor) +\
                           abs(self.goal_floors[-1] - request.request_floor)

            elif(request.direction==RequestDirection.DOWN and self.state== ElevatorState.MOVING_UP) or\
                (request.direction==RequestDirection.UP and self.state==ElevatorState.MOVING_DOWN):
                # Moving in opposite directions
                estimate=abs(self.goal_floors[-1] - self.floor) +\
                       abs(self.goal_floors[-1] - request.request_floor)
        else:
            # Idle
            estimate=abs(request.request_floor - self.floor)

        return estimate

    def step(self):
        '''
        Move the elevators to the next floors and update the state.
        '''
        if(self.goal_floors):
            # If reached the next goal_floor remove it
            if(self.floor == self.goal_floors[0]):
                self.goal_floors.remove(self.floor)

        if(self.goal_floors):
            # Update state
            if(self.floor < self.goal_floors[0]):
                self.state = ElevatorState.MOVING_UP
            elif(self.floor > self.goal_floors[0]):
                self.state=ElevatorState.MOVING_DOWN
        else:
            self.state = ElevatorState.IDLE

        if(self.state == ElevatorState.MOVING_UP):
            self.floor +=1
        if(self.state == ElevatorState.MOVING_DOWN):
            self.floor -=1


class ElevatorRequest:
    def __init__(self, (request_floor, direction, goal_floor), request_time):
        self.request_floor = request_floor
        self.direction = RequestDirection(direction)
        self.goal_floor = goal_floor
        self.estimated_fulfilment_time = None
        self.request_time = request_time


    def __repr__(self):
        return '{request_floor}-{direction}-{goal_floor}'.\
                format(request_floor=self.request_floor,\
                       direction=RequestDirection(self.direction).name[0],\
                       goal_floor=self.goal_floor)

class ElevatorController:

    def __init__(self):
        self._elevator_count = 16
        self._floor_count = 10
        self._time = 0
        self._elevators = []
        self.init_elevators()
        self._unallocated_requests = []
        self._fulfilment_times = []

    def init_elevators(self):
        for i in range(self._elevator_count):
            self._elevators.append(Elevator(i))

    def status(self):
        elevator_status = []
        for elevator in self._elevators:
            elevator_status.append((elevator.id, elevator.floor))
        return elevator_status

    def step(self):
        self._time = self._time + 1
        self.allocate_elevators()
        for elevator in self._elevators:
            elevator.step()

    def pickup(self, pickups):
        self._unallocated_requests.extend([ElevatorRequest(p, self._time) for p in pickups])

    def run_simulation(self, sim_file, interactive):
        with open(sim_file) as f:
            event_queue = yaml.load(f)
            max_time = max(event_queue.keys())
            for t in range(max_time):
                if t in event_queue:
                    self.pickup(event_queue[t])
                self.pprint_status()
                self.step()
                if(interactive):
                    raw_input()
        self.print_stats()

    def print_stats(self):
        self._fulfilment_times.sort()
        print "Waiting time stats :"
        print "bestcase \t p50 \t p90 \t p99 \t worstcase"
        print '\t', self._fulfilment_times[0], '\t', \
            self._fulfilment_times[int(math.floor(len(self._fulfilment_times)*.5))],'\t', \
            self._fulfilment_times[int(math.floor(len(self._fulfilment_times)*.9))],'\t', \
            self._fulfilment_times[int(math.floor(len(self._fulfilment_times)*.99))], '\t', \
            self._fulfilment_times[-1]

    def pprint_status(self):
        '''
        Pretty-print a grid of elevators.
        '''

        elevators_state = self.status()
        print 'Time : {time}'.format(time=self._time)
        for floor in range(self._floor_count,-1,-1):
            floor_state = "".join(["X " if (elevator.id, floor) in elevators_state \
                                        else "  " \
                                        for elevator in self._elevators])
            print floor_state, \
                "Floor {floor}".format(floor=floor), \
                [request for request in self._unallocated_requests \
                            if request.request_floor == floor]


class MinWaitTimeElevatorController(ElevatorController):

    def __init__(self):
        ElevatorController.__init__(self)

    def allocate_elevators(self):
        '''
        For every Unallocated user request:
            If an elevator can be allocated immediatley allocate it.
            else, Issue a system request to bring the nearest elevator to this floor.
        '''
        for request in list(self._unallocated_requests):
            fulfilment_estimates=[elevator.fulfilment_estimate(request) for elevator in self._elevators]
            min_fulfilment_estimate = min(fulfilment_estimates)
            min_fulfilment_estimate_elevator = self._elevators[fulfilment_estimates.index(min_fulfilment_estimate)]
            if(min_fulfilment_estimate == 0):
                min_fulfilment_estimate_elevator.fulfil_request(request)
                self._fulfilment_times.append(self._time - request.request_time)
                self._unallocated_requests.remove(request)

            else:
                pickup_direction = RequestDirection.UP \
                        if request.request_floor > min_fulfilment_estimate_elevator.floor else RequestDirection.DOWN
                pickup_request = ElevatorRequest((min_fulfilment_estimate_elevator.floor,pickup_direction,request.request_floor), self._time)
                min_fulfilment_estimate_elevator.fulfil_request(pickup_request)




class FCFSElevatorController(ElevatorController):

    def __init__(self):
        ElevatorController.__init__(self)

    def allocate_elevators(self):
        '''
        Allocate elevators in FCFS order.
        Allocate the oldest Unallocated requests to IDLE elevators.

        TODO : Update @_unallocated_requests only after the request if fulfilled.
                Now its updated after allocation.

        '''
        idle_elevators = [elevator for elevator in self._elevators if elevator.state==ElevatorState.IDLE]
        sorted_requests = sorted(self._unallocated_requests, key=lambda x: x.request_time, reverse=True)
        if(idle_elevators and sorted_requests):
            for idle_elevator in idle_elevators:
                if(sorted_requests):
                    next_request = sorted_requests.pop()
                    idle_elevator.goal_floors.append(next_request.request_floor)
                    idle_elevator.goal_floors.append(next_request.goal_floor)
                    # The requst will be fulfilled after reaching the request floor.
                    # Hence append the time to reach the floor
                    self._fulfilment_times.append(self._time - next_request.request_time + abs(next_request.request_floor - idle_elevator.floor))
                    self._unallocated_requests.remove(next_request)



def main():
    elevator_controller = MinWaitTimeElevatorController()
    #elevator_controller = FCFSElevatorController()
    interactive = None
    if(len(sys.argv) > 2):
        interactive = True
    elevator_controller.run_simulation(sys.argv[1], interactive)

if __name__ == '__main__':
    main()
