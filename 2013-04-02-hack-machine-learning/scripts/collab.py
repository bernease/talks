from __future__ import print_function
import json
import urllib

## Add token and user ID ##

token = r'BAACEdEose0cBABdzv4wfLOFgZBcXbhJouczmMnSo3fNfbcDZB4KPUlCtEpGgsZCmGMB4FqytN9iyZBIHZAnnNoQCK8E77ZCevqEgnYQR6QYh2aGX55hoko'
my_id = r'765583928'
since_date = r'2013-03-01'
min_likes = 5
min_comments = 2


## Read in friend ID's ##

# reads text from url
friends_json = urllib.urlopen(r'https://graph.facebook.com/' + my_id + 
	r'?fields=friends.fields(id)&access_token=' + token).read()

# converts to python
friends = json.loads(friends_json)

# clean up
friends = friends['friends']['data']

# how many friends do you have?
print("I have", len(friends), "friends on Facebook.", sep=' ')

# initialize dictionary of friends with similarity count = 0
friend_sim = {}
total_sim = 0
for keypair in friends:
	friend_sim[keypair['id']] = 0.0

# create friend list
friend_list = friend_sim.keys()

# could also use friend_sim = dict(zip(friend_list, [0] * len(friend_list)))
# 	if created friend_list first

# create unseen_posts dictionary
unseen_posts = []

## Populate friend_sim dictionary ##
for friend_id in friend_sim.keys():
  
	# reads text from url
	statuses_json = urllib.urlopen(r'https://graph.facebook.com/' + my_id + 
		r'?fields=friends.uid(' + friend_id + r').fields(statuses)&since=' +
		since_date + '&access_token=' + token).read()

	# converts to python
	statuses = json.loads(statuses_json)

	# check if length = 2, if not no statuses
	if len(statuses['friends']['data'][0]) != 2:
		break

	# clean up a bit
	statuses = statuses['friends']['data'][0]['statuses']['data']

	## For each status, pull results ##
	for status in statuses:

		if ('likes' not in status.keys()): continue
		if ('comments' not in status.keys()): continue
		if ('message' not in status.keys()): continue
		
		# make unique list of likers
		likers = []
		for like in status['likes']['data']:
			if like['id'] in friend_list:
				likers.append(like['id'])

		# make unique list of commenters
		commenters = []
		for comment in status['comments']['data']:
			if comment['from']['id'] in friend_list:
				commenters.append(comment['from']['id'])

		# if I liked/commented, add to similarity
		if (my_id in likers) or (my_id in commenters):
			
			# +1 to total_sim
			total_sim += 1

			# +1 similarity for friends who are likers
			for liker_id in likers:
				if (liker_id != my_id) and (liker_id in friend_list):
					friend_sim[liker_id] += 1

			# +2 similarity for friends who are commenters
			for commenter_id in commenters:
				if (commenter_id != my_id) and (commenter_id in friend_list):
					friend_sim[commenter_id] += 2

		# otherwise (I didn't like/comment), push to unseen if within thres
		else:

			#if (len(status['likes']['data'])>=min_likes and 
			#	len(status['comments']['data'])>=min_comments):
			unseen_posts.append([status['id'],status['message'],
				list(likers)[:],list(commenters)[:],len(status['likes']['data']),
				len(status['comments']['data']),0])


## Adjust similarity scores to fraction ##
for friend_id in friend_list:
	if (total_sim != 0): friend_sim[friend_id] /= total_sim

#print(friend_sim)


## Calculate simlarity scores for each unseen post ##
#print(unseen_posts)

for post in unseen_posts:

	# Add similarity-weighted likes
	for liker in post[3]:
		post[6] += 1 * friend_sim[liker]

	# Add similarity-weighted comments
	for commenter in post[3]:
		post[6] += 2 * friend_sim[commenter]


## Sort posts based on scores ##

result = sorted(unseen_posts, key=lambda x: x[6])
print(result)