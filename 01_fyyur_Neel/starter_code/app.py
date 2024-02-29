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
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# Completed: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name}'

    # Completed: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist {self.id} {self.name}'

    # Completed: implement any missing fields, as a database migration using Flask-Migrate

# Completed Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
   __tablename__ = "shows"

   id = db.Column(db.Integer, primary_key=True)
   venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
   artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
   start_time = db.Column(db.DateTime, default=datetime.now(), nullable=False)

   def __repr__(self):
      return f'<Show {self.id} {self.artist_id} at {self.venue_id} {self.start_time}'
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
  # Completed: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  places = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  answer = []

  for place in places:
     result = Venue.query.filter(Venue.state == place.state).filter(Venue.city == place.city).all()

     venue_related_data = []

     for venue in result:
        venue_related_data.append({
           'id': venue.id,
           'name': venue.name,
           'num_upcoming_shows': len(db.session.query(Show).filter(Show.start_time>datetime.now()).all())
        })

        answer.append({
           'city': place.city,
           'state': place.state,
           'venues': venue_related_data
        })
  return render_template('pages/venues.html', areas=answer)
  
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Completed: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '')
  result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  length = len(result)

  answer = {"count": length, 
            "data": result}
  
  return render_template('pages/search_venues.html', results=answer, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # Completed: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.get(venue_id)
  if not venue:
    return redirect(url_for('index'))
  
  upcoming_shows, past_shows = [], []
  upcoming_count, past_count = 0, 0

  for show in venue.shows:
    if show.start_time > datetime.now():
      upcoming_count +=1
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
      })
    if show.start_time < datetime.now():
       past_count +=1
       past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
      })

  data = {
     "id": venue.id,
     "name": venue.name,
     "genres": [venue.genres],
     "address": venue.address,
     "city": venue.city,
     "state": venue.state,
     "phone": venue.phone,
     "website": venue.website_link,
     "facebook_link": venue.facebook_link,
     "seeking_talent": venue.seeking_talent,
     "seeking_description": venue.seeking_description,
     "image_link": venue.image_link,
     "past_shows": past_shows,
     "upcoming_shows": upcoming_shows,
     "past_shows_count": past_count,
     "upcoming_shows_count": upcoming_count
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Completed: insert form data as a new Venue record in the db, instead
  # Completed: modify data to be the data object returned from db insertion
  form = VenueForm()
  try:
    seeking_talent = True if form.seeking_talent.data == "Yes" else False
    create_venue = Venue(
      name=form.name.data.strip(),
      city=form.city.data.strip(),
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=form.genres.data,
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      seeking_talent=seeking_talent,
      website_link=form.website_link.data,
      seeking_description=form.seeking_description.data
      )
    
    db.session.add(create_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # Completed: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except Exception as e:
     print(e)
     flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
     db.session.rollback()
  finally:
     db.session.close()
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Completed: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
     Venue.query.filter(Venue.id == venue_id).delete()
     db.session.commit()
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
  # Completed: replace with real data returned from querying the database

  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Completed: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')

  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()   # Wildcards search before and after

  response = {
      "count": len(artists),
      "data": artists}

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # Completed: replace with real artist data from the artist table, using artist_id
  
  artist = Artist.query.get(artist_id)
  if not artist:
    return redirect(url_for('index'))

  upcoming_shows, past_shows = [], []
  upcoming_count, past_count = 0, 0

  for show in artist.shows:
    if show.start_time > datetime.now():
      upcoming_count +=1
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": str(show.start_time)
      })
    if show.start_time <= datetime.now():
       past_count +=1
       past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": str(show.start_time)
      })
      

  data = {
     "id": artist.id,
     "name": artist.name,
     "genres": [artist.genres],
     "city": artist.city,
     "state": artist.state,
     "phone": artist.phone,
     "website": artist.website_link,
     "facebook_link": artist.facebook_link,
     "seeking_venue": artist.seeking_venue,
     "seeking_description": artist.seeking_description,
     "image_link": artist.image_link,
     "past_shows": past_shows,
     "upcoming_shows": upcoming_shows,
     "past_shows_count": past_count,
     "upcoming_shows_count": upcoming_count
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()

  if not artist: 
     return redirect(url_for('index'))
  
  # Completed: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Completed: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first()

  if not venue:
     return redirect(url_for('index'))

  # Completed: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # Completed: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  # Completed: insert form data as a new Venue record in the db, instead
  # Completed: modify data to be the data object returned from db insertion
  form = ArtistForm()
  try:
    seeking_venue = True if form.seeking_venue.data == "Yes" else False
    create_artist = Artist(
        name=form.name.data.strip(),
        city=form.city.data.strip(),
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        seeking_venue=seeking_venue,
        website_link=form.website_link.data,
        seeking_description=form.seeking_description.data
    )
    db.session.add(create_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    # Completed: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' was not listed')
    db.session.rollback()
  finally:
    db.session.close()
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # Completed: replace with real venues data.
  
  data = Show.query.join(Venue, Venue.id == Show.venue_id).join(Artist, Artist.id == Show.artist_id).all()

  answer = []

  for s in data:
     answer.append({
        "venue_id": s.venue_id,
        "venue_name": s.venue.name,
        "artist_id": s.artist_id,
        "artist_name": s.artist.name,
        "artist_image_link": s.artist.image_link,
        "start_time": str(s.start_time)
     })
  return render_template('pages/shows.html', shows=answer)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # Completed: insert form data as a new Show record in the db, instead
  try:
    show = Show(
        artist_id=request.form['artist_id'],
        venue_id=request.form['venue_id'],
        start_time=request.form['start_time']
    )
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except Exception as e:
    print(e)
    # Completed: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    flash('An error occurred. Show could not be listed')
    db.session.rollback()
  finally:
    db.session.close()
  
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
