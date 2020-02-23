# Entity Comparison in Knowledge Graphs

The implementation of the MSSQ_Approx is given in the MSSQApproximation.py file.
The LUBM1 input dataset is given in lubm1.ttl file.
Download the code and the dataset into the same folder.

To run the algorithm on a random pair of entities, run in command line:
$ python3 Launcher.py

You can also choose any two entities from LUBM1 and run the algorithm on them:
$ python3 Launcher.py '<http://www.Department1.University0.edu/UndergraduateStudent273>' '<http://www.Department1.University0.edu/UndergraduateStudent389>'

The algorithm will output approximated MSSQs for the input data of depth 1, 2 and 3.
