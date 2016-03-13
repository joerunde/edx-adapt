import json, sys, requests
host = sys.argv[1]
user = sys.argv[2]
answer = int(sys.argv[3])
headers = {'Content-type': 'application/json'}


r = requests.get('http://'+host+':9000/api/v1/course/CMUSTAT101/user/'+user, headers=headers)
r = r.json()
print "First user status: "
print r
print
print

if r['next'] is not None:
    payload = {'problem':str(r['next']['problem_name'])}
    r = requests.post('http://'+host+':9000/api/v1/course/CMUSTAT101/user/'+user+'/pageload', data=json.dumps(payload), headers=headers)
    #print 'http://'+host+':9000/api/v1/course/CMUSTAT101/user/'+user+'/pageload'
    #print payload
    print "Pageload reply: "
    print r.json()
    print
    print

    r = requests.get('http://'+host+':9000/api/v1/course/CMUSTAT101/user/'+user, headers=headers)
    r = r.json()
    print "Second user status: "
    print r
    print
    print


payload = {'problem':r['current']['problem_name'], 'correct':answer, 'attempt':1}

print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ANSWERING " + str(answer) + " TO PROBLEM: " + str(r['current']['problem_name'])

r = requests.post('http://'+host+':9000/api/v1/course/CMUSTAT101/user/'+user+'/interaction', data=json.dumps(payload), headers=headers)
print "Question attempt post: "
print r.json()
print
print





"""
payload = json.dumps({'user_id':user})
r = requests.post('http://'+host+':9000/api/v1/course/CMUSTAT101/user', data=payload, headers=headers)
print str(r) + str(r.json())

# give no problems (hopefully)
p = {'pg': 0.25, 'ps': 0.25, 'pi': 0.99, 'pt': 0.5, 'threshold':0.5}
skills = ['center', 'shape', 'spread', 'x axis', 'y axis', 'h to d', 'd to h', 'histogram']

for skill in skills:
    payload = json.dumps({'course_id':'CMUSTAT101', 'params': p, 'user_id':user, 'skill_name':skill})
    r = requests.post('http://'+host+':9000/api/v1/parameters', data=payload, headers=headers)
    print str(r) + str(r.json())

"""