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
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)# Seeking talent is not in the above
    seeking_description = db.Column(db.String(500))   # A description field

    # On Parent Model, passs child model using db.relationships
    show = db.relationship('Shows', backref='venue', lazy=True)

    def __repr__(self):
      return f"Venue ID: {self.id}, Venue Name: {self.name}, Venue City: {self.city}, Venue State: {self.state}, Venue Address: {self.address}, Venue Phone: {self.phone}, Venue Image-Link: {self.image_link}, FB-Link: {self.facebook_link}, Venue Genres: {self.genres}, Venue Website-link: {self.website_link}, Venue Seek talent: {self.seeking_talent}"

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
    website_link = db.Column(db.String(120))        # A wesbiste link field
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)# A Seeking venue boolean type
    seeking_description = db.Column(db.String(500)) # A description field

    # On Parent Model, passs child model using db.relationships
    show = db.relationship('Shows', backref='artist', lazy=True)

    def __repr__(self):
      return f"Venue ID: {self.id}, Venue Name: {self.name}, Venue City: {self.city}, Venue State: {self.state}, Venue Address: {self.address}, Venue Phone: {self.phone}, Venue Image-Link: {self.image_link}, FB-Link: {self.facebook_link}, Venue Genres: {self.genres}, Venue Website-link: {self.website_link}, Venue Seek Venue: {self.seeking_venue}"

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Shows(db.Model):    # Shows table
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)  # Set a primary identifier
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)# Choosing a datetime format to add to the show attribute
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)# Child relationship linking the entry to an artist
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)# Child relationship linking the entry to an venue

    def __repr__(self):
      return f"Show ID: {self.id}, Show Start: {self.start_time}, Show Artist: {self.artist_id}, Show Venue: {self.venue_id}"

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
  data = []         # Init empty list
  results = Venue.query.distinct(Venue.city, Venue.state).all() # All the results from the venue table
  for result in results:
      dict_citystate = {
          "city": result.city,
          "state": result.state
      }
      venues = Venue.query.filter_by(city=result.city, state=result.state).all()  # All the results to a variable

      list_venues = []
      for venue in venues:
        list_venues.append({
          "id":venue.id,
          "name": venue.name,             # Dict all the venues to a lists var
          "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.show)))
        })
      dict_citystate["venues"] = list_venues
      data.append(dict_citystate)           # On the data var add the dict of data
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get("search_term", "")
  response = {}     # Init empty response dictionary
  venues = list(Venue.query.filter( # Add all the queried results to a variable
    Venue.name.ilike(f"${search_term}$") |
    Venue.state.ilike(f"${search_term}$") |
    Venue.city.ilike(f"${search_term}$")
  ).all())
  response["count"] = len(venues) # Add the number of results to the response dict
  response["data"] = []           # Empty list

  for venue in venues:
    ven_shows = {
      "id": venue.id,
      "name": venue.name,       # Dict all the venues from the search results
      "num_upcoming_shows": len(list(filter(lambda s: s.start_time > datetime.now(), venue.shows)))
    }
    response["data"].append(ven_shows)# Add items to the list in the dictionary
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)	
  setattr(venue, "genres", venue.genres.split(","))
  past_shows = list(filter(lambda s: s.start_time < datetime.now(), venue.show))  
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

  upcoming_shows = list(filter(lambda s: s.start_time > datetime.now(), venue.show))
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

  if form.validate():
    try:
      new_venue = Venue(
        name=form.name.data,
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
  else:
    flash("Venue was not listed!")

    # return render_template('pages/home.html')
    return redirect(url_for('venues'))

  @app.route('/venues/<venue_id>', methods=['DELETE'])
  def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail. 
    venue = Venue.query.get(venue_id)
    if venue:
      try:
        venue_name = venue.name
        db.session.delete(venue_name)
        db.session.commit()
        flash("Selected Venue has been deleted succesfully.")
      except:
        db.session.rollback()
      finally:
        db.session.close()
    else:
      return redirect(url_for('venues'))
  

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  artists = db.session.query(Artist.id, Artist.name).all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(        # Query all the artists based on the input
    Artist.name.ilike(f"${search_term}$") |
    Artist.city.ilike(f"${search_term}$") |
    Artist.state.ilike(f"${search_term}$")
  ).all()                               # Store these results in a variable

  response={
    "count": len(artists),      # Add the num of artists to the dict
    "data": []                  # Init empty list in data var in dict
  }

  for artist in artists:
    art = {}
    art["name"] = artist.name   # Add the name to the art-dictionary
    art["id"] = artist.id

    upcoming_shows = 0          # Now for the upcoming shows enry
    for show in artist.shows:
      if show.start_time > datetime.now():# All the upcoming shows
        upcoming_shows += 1
    art["upcoming_shows"] = upcoming_shows # Place these in the art-dictionary

    response["data"].append(art)      # Add all to the response["data"] field


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

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form.genres.data - artist.genres.split(",")
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  if form.validate():
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
  else:
    flash("Artist was not edited!")

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form.genres.data = venue.genres.split(",")
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  if form.validate():
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
  else:
    flash("Venue was not edited!")
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
  if form.validate():
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
      flash('Artist' + request.form['name'] + ' was added unsuccessfully !')
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    finally:
      db.session.close()
  else:
    flash("Artist was not added!")

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
  if form.validate():
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
      flash("Show was unsuccessfully added!")

    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
      db.session.commit()
  else:
    flash("Show was not added")
    
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
