import sys, os
from threading import Thread

def stress(name):
    os.system('python whole_user_test.py ' + name)

for i in range(int(sys.argv[1])):
    t = Thread(target=stress, args=( ('user' + str(i),) ))
    t.start()