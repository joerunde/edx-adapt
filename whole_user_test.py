import sys, os

name = sys.argv[1]

os.system('python user_setup_test.py localhost ' + name)
for c in range(100):
    os.system('python question_test.py localhost ' + name + ' 0')
