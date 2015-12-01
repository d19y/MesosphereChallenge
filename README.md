<pre>

Start time : 8:50 AM

Python version used : 2.7
Dependencies : pyyaml & enum

To install
sudo pip install enum
sudo pip install pyyaml

To run the program

python elevator.py events_yaml_file [interactive]

This would print the status similar to

Time : 81
      X X   X   X         X X X  Floor 10 [10-D-7]
                  X              Floor 9 [9-D-2]
                                 Floor 8 [8-D-4, 8-D-4]
                                 Floor 7 []
                      X          Floor 6 [6-U-7]
                                 Floor 5 []
  X                              Floor 4 []
    X                            Floor 3 [3-U-5]
X         X                      Floor 2 [2-U-9]
              X     X            Floor 1 [1-U-4]
                        X        Floor 0 [0-U-8]


events_yaml_file:

        A yaml file that has a sequence of requests the controller would receive

        15:
        - [0, 2, 8]

        The above entry means that @ time = 15 (Key),  A Request [request_floor, direction(1=>DOWN, 2=>UP), goal_floor] is received.
        This request corresponds to from "Floor-0" go "UP" to "Floor-8"

        There would be multiple request of this format.

        Use request_generator.py to generate files of these format.

        The 4 files included are

        random_events.yaml - Random sequence of events
        evacuate_building.yaml - All requests to goal floor 0
        morning_rush.yaml - All requests from request floor 0
        sudden_spike.yaml - 30 % of requests occour @ T=20


interactive:

        Use this to step by time. Press <ENTER> to go to next step.
        This is optional

        Press and hold the <ENTER> key to see the simulation.


Example to run random_events.yaml

python elevator.py random_events.yaml interactive - to run one step @ a time.
python elevator.py random_events.yaml  -  To run all @ once


Approach :

The algorithm (MinWaitTime) tries to minimize the overall waiting time for a request to be served.

  For every Unallocated user request:
      If an elevator can be allocated immediatley in the same floor, allocate it.
      else, Issue a system request to bring the nearest elevator to this floor.

The actual fulfilment of the request is pushed to as late as possible and allocated to the elevator that reaches the request floor first.

A note on vocab:

Allocated Elevators : Best candidate elevator which can fulfil this request. A System request is issued to this elevators to add the @request_floor to its @goal_floors. Allocated Elevators for a request could change over time based on the sequence of events.


Fulfilling Elevator : The elevator that actually fulfils a user request.

There is also an incomplete FCFS implementation to calculate the performance of the MInWaitTime approach against FCFS.

MInWaitTime approach is better that FCFS as it groups requests if grouping is possible and chooses the nearest elevator to fulfil the request.


FCFS vs MinWaitTime


                          bestcase 	 p50 	 p90 	 p99 	 worstcase
Random events
FCFSElevator                    	1 	6 	 10 	 14 	 15
MinWaitTimeElevator:            	1 	4 	 8 	   15 	15


Morning rush
FCFSElevator                    	1 	16 	 24 	29 	  30
MinWaitTimeElevator:            	1 	 3 	  6 	 9 	  10

Evacuate building
FCFSElevator                    	2 	13 	 24 	 30 	 30
MinWaitTimeElevator:            	1 	 5 	 17 	 22 	 22

Sudden spike @ t=20
FCFSElevator                    	2   21 	 34 	 37 	 40
MinWaitTimeElevator:            	1 	8 	 16 	 18 	 19


Known issues :

FCFS Elevator pretty-print removes an entry from the unfillfilled requests before its actually fulfilled.
How ever the fulfilment_times are correct.


Possible enhancements :

If multiple elevators are idle move them as far as possible to reduce the access time.

</pre>
