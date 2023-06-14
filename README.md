Sync script can be used for synchronization two folders, source folder and replica folder at a spefic interval of time.
Synchronization will be one-way, replica folder will be modified to exactly match content of the source folder.
The script will sync not only files but nested dirs also.
All operations are stored to log files and printed to the console output.

How to use sync script from CLI

There are 4 positional args:
1. path to source folder
2. path to replica folder
3. path to log file
4. time interval in minutes: positive integer

Example: python sync.py /source /replica /file.log 1

Python version: 3.6 or above
