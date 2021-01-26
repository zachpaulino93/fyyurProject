#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
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
import datetime
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Genre(db.Model):
    __tablename__ = "genre"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String)

artist_genre_table = db.Table('artist_genre_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True)
)
venue_genre_table = db.Table('venue_genre_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=True)
    seeking_talent_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)
    genres = db.relationship('Genre', secondary=venue_genre_table, backref=db.backref('venues'))

    def __repr__(self):
        return 'f< Venue {self.name}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=True)
    seeking_venue_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)
    #genres = db.Column(db.ARRAY(db.String), nullable=False)
    genres = db.relationship('Genre', secondary=artist_genre_table, backref=db.backref('artists'))

    def __repr__(self):
        return 'f< Artist {self.name}>'

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return 'f< Show {self.artist_id} {self.venue_id}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  try:
      today = datetime.datetime.now()
      venues = db.session.query(Venue.state).distinct().all()
      data = []

      for v in venues:
         venue_shows = Show.query.filter_by(venue_id=Venue.id).all()
         num_upcoming = 0

         for show in venue_shows:
             if show.start_time > today:
                 num_upcoming +=1
             else:
                 pass

         venue_list = []
         cities = db.session.query(Venue.city, Venue.name, Venue.id).filter(Venue.state == v)

         for city in cities:
             venue_list.append({
                "id": city[2],
                "name": city[1],
                "num_upcoming_shows": num_upcoming
                })
         data.append({
           "city": city[0],
           "state": v[0],
           "venues": venue_list
         })

  except:
      print(sys.exc_info())
      flash("something went wrong oh noooo please try agian")
      render_template(url_for('pages/home.html'))

  finally:
        return render_template('pages/venues.html', areas=data)
"""
    data=[{
      "city": "San Francisco",
      "state": "CA",
      "venues": [{
        "id": 1,
        "name": "The Musical Hop",
        "num_upcoming_shows": 0,
      }, {
        "id": 3,
        "name": "Park Square Live Music & Coffee",
        "num_upcoming_shows": 1,
      }]
    }, {
      "city": "New York",
      "state": "NY",
      "venues": [{
        "id": 2,
        "name": "The Dueling Pianos Bar",
        "num_upcoming_shows": 0,
      }]
    }]
"""

@app.route('/venues/search', methods=['POST'])
def search_venues():

    try:
        # lets grab our search_term from request to form get through our route and run a query all names with a filter
        search_term = request.form.get('search_term', '').strip()
        venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
        venue_list = []
        today = datetime.datetime.now()
        # lets iterate through the venues one at a time and see if they have any upcoming shows
        for venue in venues:
            venue_shows = Show.query.filter_by(venue_id=venue.id).all()
            num_upcoming = 0
            for show in venue_shows:
                if show.start_time > today:
                    num_upcoming +=1
            # now we want to append the venues either way to a dictionary /json so the website can read it
            venue_list.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming
            })
        response={
            "count": len(venues),
            "data": venue_list
        }
        return render_template('pages/search_venues.html', results=response, search_term=search_term)
    except:
        flash('An error occured while seraching, please try again')
        return redirect(url_for('venues'))

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


      today = datetime.datetime.now()
      upcoming_shows_q = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time > today).all()
      upcoming_shows = []
      past_shows_q = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time < today).all()
      past_shows = []
      ven = db.session.query(Venue).filter(Venue.id == venue_id)
      genre = [ genre.name for genre in db.session.query(Genre.name).all()]
      for show in past_shows_q:
          past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.artist_image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
          })

      for show in upcoming_shows_q:
          upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist_name,
            "artist_image_link": show.artist_image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
          })

      for v in ven:
          data = {
            "id": v.id,
            "name": v.name,
            "genres": genre,
            "address": v.address,
            "city": v.city,
            "state": v.state,
            "phone": v.phone,
            "website": v.website,
            "facebook_link": v.facebook_link,
            "seeking_talent": v.seeking_talent,
            "seeking_talent_description": v.seeking_talent_description,
            "image_link": v.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  error = False
  data = request.form
  try:

      name = data['name']
      city = data['city']
      phone = data['phone']
      state = data['state']
      address = data['address']
      genres = form.genres.data
      website = data['website']
      # image_link = data['image_link']
      facebook_link = data['facebook_link']
      # had to revrse because i set defualt to yes under Venue seeking talend BOOLEAN
      seeking_talent = False if form.seeking_talent.data == 'yes' else True
      seeking_talent_description = form.seeking_talent_description.data
      g_list = []
      new_venue = Venue(name=name, city=city, state=state, genres=g_list, address=address, phone=phone, website=website, facebook_link=facebook_link, seeking_talent=seeking_talent, seeking_talent_description=seeking_talent_description)
      flash(g_list)
      flash('g list above')
      for g in genres:
          get_genre = Genre.query.filter_by(name=g).one_or_none()
          if get_genre:
              g_list.append(get_genre)
              flash(get_genre)
              flash(g_list)
          else:
              flash(g)
              g_list.append(g)
              add_genre_to_db = Genre(name=g)
              db.session.add(add_genre_to_db)
      db.session.add(new_venue)
      db.session.commit()

  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
      flash('An error occured. Venue ' + request.form['name'] +' could not be listed.')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('an error occured. Venue ' + venue_id + ' could not be removed from database')
  if not error:
      flash(f'Venue {venue_id} has been successfully deleted!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artist_name = db.session.query(Artist.name, Artist.id).all()
  for name in artist_name:
      flash(name[0:])
      data.append({
        "id": name[1],
        "name": name[0]
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
   search_term = request.form.get('search_term', '')
   artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
   artist_list = []
   today = datetime.datetime.now()

   for artist in artists:
       artist_shows = Show.query.filter_by(artist_id=artist.id).all()
       flash(Artist.name)
       num_upcoming = 0
       for show in artist_shows:
           if show.start_time > today:
               num_upcoming +=1

       artist_list.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming
       })
   response={
        "count": len(artists),
        "data": artist_list
        }
   return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  today = datetime.datetime.now()
  upcoming_shows_q = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time > today).all()
  upcoming_shows = []
  past_shows_q = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time < today).all()
  past_shows = []
  artist = db.session.query(Artist).filter(Artist.id == artist_id)

  for show in past_shows_q:
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist_name,
        "artist_image_link": show.artist_image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })

  for show in upcoming_shows_q:
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist_name,
        "artist_image_link": show.artist_image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })

  for a in artist:
      data = {
        "id": a.id,
        "name": a.name,
        "genres": a.genres,
        "city": a.city,
        "state": a.state,
        "phone": a.phone,
        "website": a.website,
        "facebook_link": a.facebook_link,
        "seeking_talent": a.seeking_venue,
        "seeking_talent_description": a.seeking_venue_description,
        "image_link": a.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
      }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist:
      form.id.data = artist.id
      form.name.data = artist.name
      form.genres.data = artist.genres
      form.city.data = artist.city
      form.state.data = artist.state
      form.phone.data = artist.phone
      form.website.data = artist.website
      form.facebook_link.data = artist.facebook_link
      form.seeking_venue.data = artist.seeking_venue
      form.seeking_venue_description = artist.seeking_venue_description
      form.image_link.data = artist.image_link
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue:
      form.name.data = venue.name
      form.city.data = venue.city
      form.state.data = venue.state
      form.phone.data = venue.phone
      form.address.data = venue.address
      form.genres.data = venue.genres
      form.image_link.data = venue.image_link
      form.facebook_link.data = venue.facebook_link
      form.website.data = venue.website
      form.seeking_talent.data = venue.seeking_talent
      form.seeking_talent_description.data = venue.seeking_talent_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    venue = Venue.query.get(venue_id)
    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.phone = request.form['phone']
        venue.address = request.form['address']
        venue.genres = request.form.getlist['genres']
        venue.image_link = request.form['image_link']
        venue.website = request.form['website']
        venue.seeking_talent = True if 'seeking_talent' in request.form else False
        venue.seeking_description = request.form['seeking_description']

        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occured. venue could not be changed')
  # TODO: take values from the form submitted, and update existing
    if not error:
        flash('venue was successful updated.')
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  form = ArtistForm()
  data = request.form
  try:

      name = data['name']
      city = data['city']
      flash(city)
      phone = data['phone']
      flash(phone)
      state = data['state']
      flash(state)
      genres = form.genres.data
      flash(genres)
      #website = data['website']
      # image_link = data['image_link']
      facebook_link = data['facebook_link']
      flash(facebook_link)
      #seeking_venue = data['seeking_venue']
      #seeking_venue_description = data['seeking_venue_description']
      new_artist = Artist(name=name, city=city, phone=phone, state=state, facebook_link=facebook_link)
      flash(new_artist)
      db.session.add(new_artist)
      db.session.commit()

  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  # on successful db insert, flash success
  if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
        flash(f'An error occurred. Artist {name} could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []

    return render_template('pages/shows.html', shows=data)
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
'''
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
'''


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
'''
if __name__ == '__main__':
    app.run(host='0,0,0,0')

# Or specify port manually:
'''
# using this so i can access this from any computer on my network
# sql database is also running on a rasberry pi
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
