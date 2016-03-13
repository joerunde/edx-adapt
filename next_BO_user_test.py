import json, sys, requests
host = sys.argv[1]
user = sys.argv[2]
headers = {'Content-type': 'application/json'}


payload = json.dumps({'user_id':user})
r = requests.post('http://'+host+':9000/api/v1/course/CMUSTAT101/user', data=payload, headers=headers)
print str(r) + str(r.json())

response = requests.post('http://'+host+':9000/api/v1/course/CMUSTAT101/user/' + user + '/LoadBOParams', headers=headers)
print str(r) + str(r.json())
"""
# give no problems (hopefully)
p = {'pg': 0.25, 'ps': 0.25, 'pi': 0.99, 'pt': 0.5, 'threshold':0.5}
skills = ['center', 'shape', 'spread', 'x axis', 'y axis', 'h to d', 'd to h', 'histogram']

for skill in skills:
    payload = json.dumps({'course_id':'CMUSTAT101', 'params': p, 'user_id':user, 'skill_name':skill})
    r = requests.post('http://'+host+':9000/api/v1/parameters', data=payload, headers=headers)
    print str(r) + str(r.json())
"""
