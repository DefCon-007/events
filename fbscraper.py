from __future__ import print_function

import os
import re
import json
from dateutil.parser import parse, tz
import urllib.request
import time
from pprint import pprint
import facepy
from facepy import GraphAPI

# from frontend import write_html

# Put Facebook 'Access Token' in a plain text file ACCESS_TOKEN in same dir.
# To get an access token follow this SO answer:
# http://stackoverflow.com/a/16054555/1780891

with open('./ACCESS_TOKEN', 'r') as f:
	access_token = f.readline().rstrip('\n')

graph = GraphAPI(access_token)

def get_comments(post_id):
	base_query = post_id + '/comments'

	# scrape the first page
	print('scraping:', base_query)
	comments = graph.get(base_query)
	data = comments['data']
	return data


def get_picture(post_id, dir="."):
	base_query = post_id + '?fields=object_id'
	try:
		pic_id = graph.get(base_query)['object_id']
	except KeyError:
		return None

	try:
		pic = graph.get('{}?fields=images'.format(pic_id))
		return (pic['images'][0]['source'])
		# f_name = "{}/{}.png".format(dir, pic_id)
		# f_handle = open(f_name, "wb")
		# f_handle.write(pic)
		# f_handle.close()
		# return "{}.png".format(pic_id)
	except facepy.FacebookError:
		return None


def get_event_picture(post_id):
	base_query = post_id + '?fields=object_id'
	try:
		pic_id = graph.get(base_query)['object_id']
	except KeyError:
		return None
	try:
		pic = graph.get('{}?fields=cover'.format(pic_id))
		try :
			picLink = pic['cover']['source']
		except :
			picLink = None
		return (picLink)
		# urllib.request.urlretrieve(pic['cover']['source'] , "{}/{}.png".format(dir, pic_id))
		# return "{}.png".format(pic_id)
	except facepy.FacebookError:
		return None


def get_link(post_id):
	base_query = post_id + '?fields=link'

	try:
		link = graph.get(base_query)['link']
	except KeyError:
		return None

	return link


def get_event(post_id, page_id):
	base_query = page_id + '/events'
	all_events = graph.get(base_query)
	for event in all_events['data']:
		if event['id'] in post_id:
			if 'description' in event.keys():
				description = event['description']
			else :
				description = "No description provided"
			DateTime = prettify_date([{'created_time': event['start_time']}])
			startDate = DateTime[0]['real_date']
			startTime = DateTime[0]['real_time']
			if "place" in event.keys(): 
				placeName = event['place']['name']
				if "location" in event["place"].keys() :
					placeLocation = event['place']['location']
				else :
					placeLocation = None 
			else : 
				placeName = None 
			if "name" in event.keys(): 
				name = event["name"]
			else :
				name = None
			try : 
				attenders = event["attending_count"]
			except KeyError :
				attenders = 0 

			# return message
			eventDict = {"id" : post_id,
						 "link" : get_link(post_id),
						 "pic" : get_event_picture(post_id),
						 "description":description,
						 "startDate" : startDate,
						 "startTime" : startTime,
						 "placeName" : placeName,
						 "name" : name,
						 "placeLocation" : placeLocation,
						 "attenders" : attenders}
			if placeLocation :
				eventDict["placeLocation"]["longitude"] = float(eventDict["placeLocation"]["longitude"])
				eventDict["placeLocation"]["latitude"] = float(eventDict["placeLocation"]["latitude"])
			return (eventDict)


def get_shared_post(post_id):
	print (post_id)
	base_query = post_id + '?fields=parent_id'
	# getting id of the original post
	try :	
		parent_id = graph.get(base_query)['parent_id']
		query = parent_id + '?fields=message'
	except KeyError :
		query = post_id + '?fields=message'
	try :
		original_message = graph.get(query)['message']
	except KeyError :
		original_message = ""
	return original_message

def get_video(post_id) :
	video_id = post_id.split('_')[1]
	base_url = video_id + "?fields=embeddable"
	try : 
		embed_flag = graph.get(base_url)['embeddable'] 
	except facepy.exceptions.OAuthError:
		return ""
	if embed_flag : #checking if the video is embedddable 
		embed_html_url=video_id + '?fields=from,source'
		query = graph.get(embed_html_url)
		video_url = query['source']
		page_name = query['from']['name']
		msg = """<b>{} shared the following video\n\n
				<video width="320" height="240" controls>
				<source src="{}" >
				 Your browser does not support the video tag.
					</video>""".format(page_name,video_url)
		return msg
	else : 
		return ""
def get_feed(page_id, pages=15):
	# check last update time
	# try:
	# 	old_data = json.load(open('docs/{}.json'.format(page_id), 'r'))
	# 	last_post_time = parse(old_data[0]['created_time'])
	# except FileNotFoundError:
	# 	old_data = []
	# 	last_post_time = parse("1950-01-01T12:05:06+0000")

	base_query = page_id + '/feed?limit=10'

	# scrape the first page
	print('scraping:', base_query)
	feed = graph.get(base_query)
	data = feed['data']

	# data = []
	eventData = []
	# is_new_post = (parse(new_page_data[0]['created_time']) > last_post_time)

	# if is_new_post:
	# 	data = new_page_data

	# determine the next page
	next_page = feed['paging']['next']
	next_search = re.search('.*(\&until=[0-9]+)', next_page, re.IGNORECASE)
	if next_search:
		the_until_arg = next_search.group(1)

	pages = pages - 1

	# scrape the rest of the pages
	while (next_page is not False) and pages > 0:
		the_query = base_query + the_until_arg
		print('baking:', the_query)
		try:
			feed = graph.get(the_query)
			new_page_data = feed['data']
			# is_new_post = (
			# 	parse(new_page_data[0]['created_time']) > last_post_time)

			data.extend(new_page_data)
		except facepy.exceptions.OAuthError:
			print('start again at', the_query)
			break

		# determine the next page, until there isn't one
		try:
			next_page = feed['paging']['next']
			next_search = re.search(
				'.*(\&until=[0-9]+)', next_page, re.IGNORECASE)
			if next_search:
				the_until_arg = next_search.group(1)
		except IndexError:
			print('last page...')
			next_page = False
		pages = pages - 1
		for post_dict in data:
			# post_dict['pic'] = get_picture(post_dict['id'], dir='docs')
			# post_dict['link'] = get_link(post_dict['id'])
			if "story" in post_dict :  #Events and shared post have story key
				if "event" in post_dict['story'] :
					try :
						eventDetails = get_event(post_dict['id'], page_id)
						eventDetails["created_time"] = post_dict["created_time"]
					# post_dict['pic'] = get_event_picture(post_dict['id'],)
						eventData.append(eventDetails)
					except :
						pass
				# elif "shared" in post_dict['story'] :

				# 	post_dict['message'] = '<b>' + post_dict['story'] + '</b>' + '\n\n' + get_shared_post(post_dict['id']) 

			  #  print (post_dict['message'])
			# else :
			# 	if not "message" in post_dict :
			# 		post_dict['message'] = get_video(post_dict['id'])

			
	# data.extend(old_data)
	# data.sort(key=lambda x: parse(x['created_time']), reverse=True)
	# pprint (eventData)
	# for data in eventData :
	# 	query = "INSERT INTO "
	# json.dump(eventData, open('docs/{}.json'.format(page_id), 'w'))

	return eventData


def remove_duplicates(data):
	uniq_data = []
	for item in data:
		if item not in uniq_data:
			uniq_data.append(item)

	return uniq_data


def prettify_date(data):
	for item in data:
		date = parse(item['created_time'])
		tzlocal = tz.gettz('Asia/Kolkata')
		local_date = date.astimezone(tzlocal)
		item['real_date'] = local_date.strftime('%d-%m-%Y')
		item['real_time'] = local_date.strftime('%I:%M%p')
	return data


def get_aggregated_feed(pages):
	"""
	Aggregates feeds give a list of pages and their ids.

	Input: A list of tuples
	Output: Combined list of posts sorted by timestamp
	"""
	data = list()
	for page_name, _id in pages:
		page_data = get_feed(_id)
		for data_dict in page_data:
			data_dict['pageName'] = page_name
		data.extend(page_data)

	data.sort(key=lambda x: parse(x['created_time']), reverse=True)
	return data


if __name__ == "__main__":
	# Great thanks to https://gist.github.com/abelsonlive/4212647
	news_pages = [('The Scholar\'s Avenue', 'scholarsavenue'),
				  ('Awaaz IIT Kharagpur', 'awaaziitkgp'),
				  ('Technology Students Gymkhana', 'TSG.IITKharagpur'),
				  ('Technology IIT KGP', 'iitkgp.tech'),
				  ('Metakgp', 'metakgp'),
				("KOSS" , "kossiitkgp"),
				("Spring Fest" , "springfest.iitkgp"),
				("Kshitij" , "ktj.iitkgp")]
	# for_later = ['Cultural-IIT-Kharagpur']
	# news_pages = [('Test Page', 'utilobot')]

	data = get_aggregated_feed(news_pages)
	data = remove_duplicates(data)
	# data = prettify_date(data)

	json.dump(data, open('./events.json', 'w'))
# 	write_html(data, 'docs/index.html')

# 	localtime = str(time.asctime( time.localtime(time.time()) ))
# 	stamp="            <font size=2 color=\"white\"><div align=\"right\"><b>Last updated: "+localtime+" IST</b></div></font>\n"
# 	fn=open("docs/index.html","r+")
# 	fo=open("docs/indext.html","w")
# 	while (True):
#   		abc=fn.readline()
#   		fo.write(abc)
#   		if not abc: break
#   		if (abc[:30]=="            <!Time stamp here>"):    fo.write(stamp)
# fn.close()
# fo.close()
# os.system("mv docs/indext.html docs/index.html")