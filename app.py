#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config.from_object('config') # db URI from the config.py file
# db = SQLAlchemy(app)
migrate = Migrate(app, db)       # database migration using Flask-Migrate

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))           # genre as an Array
    website_link = db.Column(db.String(120))          # website link is not in the above _items
    seek_talent = db.Column(db.String(120))        # Seeking talent is not in the above
    seeking_description = db.Column(db.String(500))

    show = db.relationship('Shows', backref='Venue', lazy=True) # On Parent Model, passs child model using db.relationships

    def __repr__(self):
      return f"Venue ID: {self.id}, Venue Name: {self.name}, Venue City: {self.city}, Venue State: {self.state}, Venue Address: {self.address}, Venue Phone: {self.phone}, Venue Image-Link: {self.image_link}, FB-Link: {self.facebook_link}, Venue Genres: {self.genres}, Venue Website-link: {self.website_link}, Venue Seek talent: {self.seek_talent}"

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seek_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))

    # On Parent Model, passs child model using db.relationships
    show = db.relationship('Shows', backref='Artist', lazy=True)

    def __repr__(self):
      return f"Venue ID: {self.id}, Venue Name: {self.name}, Venue City: {self.city}, Venue State: {self.state}, Venue Address: {self.address}, Venue Phone: {self.phone}, Venue Image-Link: {self.image_link}, FB-Link: {self.facebook_link}, Venue Genres: {self.genres}, Venue Website-link: {self.website_link}, Venue Seek Venue: {self.seek_venue}"

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Shows(db.Model):    # Shows table
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    show_start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)

    def __repr__(self):
      return f"Show ID: {self.id}, Show Start: {self.show_start}, Show Artist: {self.artist_id}, Show Venue: {self.venue_id}"

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  area_list = []
  venues = Venue.query.order_by('city').all()
  for venue in venues: area_list.append({'city': venue.city, 'state': venue.state})
  area_list = list({ v['state']: v for v in area_list}.values())
  for area in area_list:
    venue_list = []
    for venue in venue:
      if (venue.city == area['city']) and (venue.state == area['state']):
        venue_list.append({
          'id': venue.id,
          'name': venue.name,
          # len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
          'num_upcoming_shows': len(list(filter(lambda s: s.start_time > datetime.now(), venue.shows)))
          # 'num_upcoming_shows': Shows.query.filter(isUpcomingShow(Shows.show_start)).filter(Shows.venue_id == venue.id).count()  
        })
    data.append({
      **area,
      'venues': venue_list  # "venues" as the data-variable accepting the venue_list
    })
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '').strip()
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  venue_list = []
  for venue in venues:
	  venue_list.append({
			'id': venue.id,
			'name': venue.name,
			'num_upcoming_shows': len(list(filter(lambda s: s.start_time > datetime.now(), venue.shows)))
		})

  response = {
		'count': len(venues),
		'data': venue_list
	}

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)	
  setattr(venue, "genres", venue.genres.split(","))
  past_shows = list(filter(lambda s: s.start_time < datetime.now(), venue.shows))  
  shows_l = []
  for show in past_shows:
    show_2 = {}
    show_2['artist_name'] = show.artist.name
    show_2['artist_id'] = show.artist.id
    show_2['artist_image_link'] = show.artists.image_link
    show_2['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    shows_l.append(show_2)
  
  setattr(venue, "past_shows", shows_l)
  setattr(venue, "past_shows_count", len(past_shows))

  upcoming_shows = list(filter(lambda s: s.start_time > datetime.now(), venue.shows))  
  shows_l = []
  for show in past_shows:
    show_2 = {}
    show_2['artist_name'] = show.artist.name
    show_2['artist_id'] = show.artist.id
    show_2['artist_image_link'] = show.artists.image_link
    show_2['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    shows_l.append(show_2)
  
  setattr(venue, "upcoming_shows", shows_l)
  setattr(venue, "upcoming_shows_count", len(upcoming_shows))

  # if not venue: return redirect(url_for('index'))	
  # venue_data = {
	# 	'id': venue.id,
	# 	'name': venue.name,
	# 	'genres': venue.genres,
	# 	'address': venue.address,
	# 	'city': venue.city,
	# 	'state': venue.state,
	# 	'phone': venue.phone.international,
	# 	'website': venue.website_link,
	# 	'facebook_link': venue.facebook_link,
	# 	'seeking_talent': venue.seeking_talent,
	# 	'seeking_description': venue.seeking_description,
	# 	'image_link': venue.image_link,
	# }

  # data = {
	# 	**venue_data,
	# 	'past_shows': [],
	# 	'upcoming_shows': [],
	# 	'past_shows_count': 0,
  #   'upcoming_shows_count': 0
	# }

  # for show in venue.shows:
  #     show_dict = {
  #       'artist_id': show.artist_id,
  #       'artist_name': show.artist.name,
  #       'artist_image_link': show.artist.image_link,
  #       'start_time': show.start_time
  #     }

  #     if isUpcomingShow(show.start_time):
  #       data['upcoming_shows'].append(show_dict)
  #     else:
  #       data['past_shows'].append(show_dict)
	
  # data['upcoming_shows_count'] = len(data['upcoming_shows'])

  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)

  try:
    new_venue = Venue(
      name=form.name.date,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=",".join(form.genres.data),
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data,
      website_link=form.website_link.data,
    )
    db.session.add(new_venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except Exception:
    db.session.rollback()
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("Selected Venue has been deleted succesfully.")
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  artists = db.session.query(Artist.id, Artist.name).all()

  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(
    Artist.name.ilike(f"${search_term}$") |
    Artist.city.ilike(f"${search_term}$") |
    Artist.state.ilike(f"${search_term}$")
  ).all()

  response={
    "count": len(artists),
    "data": []
  }

  for artist in artists:
    art = {}
    art["name"] = artist.name
    art["id"] = artist.id

    upcoming_shows = 0
    for show in artist.shows:
      if show.start_time > datetime.now():
        upcoming_shows += 1
    art["upcoming_shows"] = upcoming_shows

    response["data"].append(art)


  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)
  setattr(artist, 'genres', artist.genres.split(','))

  past_shows = list(filter(lambda s: s.start_time < datetime.now(), artist.shows))
  shows_l = []
  for show in past_shows:
    show_2 = {}
    show_2["venue_name"] = show.venues.name
    show_2["venue_id"] = show.venues.id
    show_2["venue_image_link"] = show.venues.image_link
    show_2["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    shows_l.append(show_2)
  
  setattr(artist, "past_shows", shows_l)
  setattr(artist, "past_shows_count", len(past_shows))

  upcoming_shows = list(filter(lambda s: s.start_time > datetime.now(), artist.shows))
  shows_l = []
  for show in upcoming_shows:
    show_2 = {}
    show_2["venue_name"] = show.venues.name
    show_2["venue_id"] = show.venues.id
    show_2["venue_image_link"] = show.venues.image_link
    show_2["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    shows_l.append(show_2)
  
  setattr(artist, "upcoming_shows", shows_l)
  setattr(artist, "upcoming_shows_count", len(upcoming_shows))

  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form.genres.data - artist.genres.split(",")
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)
  try:
    artist = Artist.queryget(artist_id)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres=",".join(form.genres.data)
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.website_link = form.website_link.data
    db.session.add(artist)
    db.session.commit()
    flash("Artist "+artist.name+" was edited succesfully")
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form.genres.data = venue.genres.split(",")
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.genres=",".join(form.genres.data)
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.seeking_venue = form.seeking_venue.data
    venue.seeking_description = form.seeking_description.data
    venue.website_link = form.website_link.data
    db.session.add(venue)
    db.session.commit()
    flash("Venue "+form.name.data+" was edited succesfully")
  except Exception:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
    new_artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genre=",".join(form.genre.data),
      image_link= form.image_link.data,
      facebook_link=form.facebook_link.data,
      website_link=form.website_link.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data,
    )
    db.session.add(new_artist)
    db.session.commit()

  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception:
  # TODO: on unsuccessful db insert, flash an error instead.    
    db.session.rollback()
    flash('Artist' + request.form['name'] + ' was unsuccessfully !')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  data = []

  shows = Shows.query.all()
  for show in shows:
    show_l = {}
    show_l['venue_id'] = show.venues.id
    show_l['venue_name'] = show.venues.name
    show_l['artist_id'] = show.artists.id
    show_l['artist_name'] = show.artists.name
    show_l['artist_image_link'] = show.artists.image_link
    show_l['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    data.append(show_l)

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)

  try:
    new_show = Shows(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data,
    )
    db.session.add(new_show)
    db.session.commit()

  # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except Exception:
    db.session.rollback()
    flash("Show was unsuccessful")

  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.commit()
    
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
