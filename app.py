from flask import Flask, render_template, url_for, request, session, redirect
from flask_session import Session
import MySQLdb
import json
from flask import jsonify
from datetime import datetime,timedelta
app = Flask(__name__)
sess = Session()

@app.route("/all-events")
def allEvents() :
	eventsList = json.load(open("./events.json" , "r"))
	for event in eventsList :
		for key in event.keys() :
			if event["placeLocation"] :
				for key in event["placeLocation"].keys() :
					print ("{} - {}".format(key,type(event["placeLocation"][key])))

	return jsonify(success=True, data=json.loads(json.dumps(eventsList)))

@app.route("/events-on-date", methods=["POST"])
def eventsOnDate() :
	form_dict = request.form.to_dict()
	dateQuery = datetime.strptime(form_dict["date"],'%d-%m-%Y')
	eventsList = json.load(open("./events.json" , "r"))
	eventsToday = list()

	for event in eventsList :
		eventDate = datetime.strptime(event["startDate"],'%d-%m-%Y')
		print (eventDate)
		print (dateQuery)
		if dateQuery == eventDate :
			eventsToday.append(event)
	return jsonify(success=True, data=json.loads(json.dumps(eventsToday)))


app.secret_key = 'events'
app.config['SESSION_TYPE'] = 'filesystem'

sess.init_app(app)
app.debug = True

if __name__ == "__main__" :
	app.run(debug=True)