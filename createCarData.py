import os
import numpy as np
import json
import shutil

users = json.load(open('sessionsinfo.json'))
usersToSimpleId = {}

carid_to_num = {}
with open('car_id') as cid:
	for line in cid:
		line = line.strip().split()
		carid_to_num[line[1]] = line[0]

directory = '/dfs/scratch0/silei/vw_project/snapshots/'
filesInDirectory = os.listdir(directory)
usercount=0
for user in users:
	usersToSimpleId[user] = usercount
	print user,usercount
	if not os.path.exists('new_data/'+str(usercount)):
		os.makedirs('new_data/'+str(usercount))
	else:
		shutil.rmtree('new_data/'+str(usercount))
		os.makedirs('new_data/'+str(usercount))
	for date in users[user]:
		if not os.path.exists('new_data/'+str(usercount)+'/'+date):
			os.makedirs('new_data/'+str(usercount)+'/'+date)
		else:
			shutil.rmtree('new_data/'+str(usercount))
			os.makedirs('new_data/'+str(usercount)+'/'+date)	
		carid = carid_to_num[users[user][date]['car_id']]
		for i in xrange(len(users[user][date]['sessions'])):
			inputfile = directory+'snapshots_'+carid+'_'+users[user][date]['sessions'][i]['id']+'.dat'
			ofp = open('new_data/'+str(usercount)+'/'+date+'/snapshots_'+str(usercount)+'_'+date+'_'+carid+'_'+str(i)+'.dat','w+')
			with open(inputfile) as ifp:
				#date time sm1 sm2 sm3 lat long.....
				idx,beginidx,nextidx,beginlat,endlat,beginlong,endlong = 0,0,10,0,0,0,0
				lines = ifp.readlines()	
				sessioncount = len(lines)
				for line in lines:
					line = line.strip().split()
					if idx%10 != 0 and idx < nextidx and beginlat > 48 and endlat > 48 and beginlong > 11 and endlong > 11:
						line[5] = "%.6f" % (beginlat+(endlat-beginlat)*1.0/(nextidx-beginidx)*(idx%10))
						line[6] = "%.6f" % (beginlong+(endlong-beginlong)*1.0/(nextidx-beginidx)*(idx%10))
					elif idx%10 == 0:
						beginidx,nextidx = idx,min(idx+10,sessioncount-1)
						beginlat,beginlong = float(line[5]),float(line[6])
						endlat,endlong = float(lines[nextidx].strip().split()[5]),float(lines[nextidx].strip().split()[6])
					idx = idx + 1
					ofp.write('\t'.join(line)+'\n')
	usercount = usercount + 1	
				
