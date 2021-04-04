#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Artist, Show
import sys
import re

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
# Local postgres URI provided in config.py
# Connection is established with local database fyyurdb
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# Please see models.py - In the interest of Seperation of Concerns!
# Import is done above

#----------------------------------------------------------------------------#
# My Helper Functions
#----------------------------------------------------------------------------#
# Proprietary function to sort out genres
def modify_genres(genre_data):
  # join incoming list with elements with a "*"
  join_delimeter = '*'
  joined_genres_list = join_delimeter.join(genre_data)
  # Use regex to replace special characters with ', ' to match what we need "a, b, c"
  special_characters = '[^A-Za-z0-9*& ]'
  genres = re.sub(special_characters, '', joined_genres_list).replace(join_delimeter, ', ')
  return genres

def form_error_handling(form):
  message = []
  for field, err in form.errors.items():
      message.append(field + ' ' + '|'.join(err))
  flash('Error(s): ' + str(message)[1:-1])

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

  # Group venues by city and state, filter by city and state, fetch ID and Name of the venue
  venue_data = []
  try:
    city_state_group = Venue.query.with_entities(Venue.city, Venue.state).group_by(
      Venue.city, Venue.state).all()

    for city, state in city_state_group:
      venue = Venue.query.with_entities(Venue.id, Venue.name).filter_by(
        city=city, state=state).order_by('id').all()
      
      venue_data.append({
        'city': city,
        'state': state,
        'venues': venue,
      })
  except ValueError as e:
    flash(f'Error: {str(e)}')
  return render_template('pages/venues.html', areas=venue_data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.

  # Get the form input, filter on the venue model, fetch models that contain the search term
  # Use "ilike" for case-insensitive
  try:
    search_input = request.form.get('search_term')
    venue_results = Venue.query.filter(Venue.name.ilike(f'%{search_input}%')).all()
    response={
      'count': len(venue_results),
      'data': venue_results
    }
  except ValueError as e:
    flash(f'Error: {str(e)}')
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # Filter the artist table and fetch the artist requested
  # Initialise containers for counting past and upcoming show, 
  show_venue_data = {}
  show_venue_data['upcoming_shows'] = []
  show_venue_data['past_shows']= []
  show_venue_data['upcoming_shows_count'] = 0
  show_venue_data['past_shows_count'] = 0

  venue_data = Venue.query.get_or_404(venue_id)

  try:
    # If artist exist, now get shows related to artist and deduce upcoming and past shows, utilise relationship
    shows_data = venue_data.shows
    # For all shows...
    for show in shows_data:
      show.artist_name = show.artist.name
      show.artist_image_link = show.artist.image_link
      if show.start_time > datetime.now(): # In the future...
        show.start_time = format_datetime(str(show.start_time))
        show_venue_data['upcoming_shows'].append(show)
        show_venue_data['upcoming_shows_count'] += 1
      else: # Past...
        show.start_time = format_datetime(str(show.start_time))
        show_venue_data['past_shows'].append(show)
        show_venue_data['past_shows_count'] += 1
    # Now construct the rest of the data that is straight forward
    show_venue_data['id'] = venue_data.id
    show_venue_data['name'] = venue_data.name
    show_venue_data['genres'] = venue_data.genres.split(',')
    show_venue_data['address'] = venue_data.address
    show_venue_data['city'] = venue_data.city
    show_venue_data['state'] = venue_data.state
    show_venue_data['phone'] = venue_data.phone
    show_venue_data['image_link'] = venue_data.image_link
    show_venue_data['website'] = venue_data.website_link
    show_venue_data['facebook_link'] = venue_data.facebook_link
    show_venue_data['seeking_talent'] = venue_data.seeking_talent
    show_venue_data['seeking_description'] = venue_data.seeking_description
  except ValueError as e:
    flash(f'An error occured: {str(e)}')
  return render_template('pages/show_venue.html', venue=show_venue_data)

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
  incoming_venue_data = VenueForm(request.form, csrf_enabled=False)
  return_page = ''

  if incoming_venue_data.validate():
    return_page = 'index'
    try:
      # Creating the Venue model from incoming form data 
      new_venue_data = Venue(
        name = incoming_venue_data.name.data,
        city = incoming_venue_data.city.data,
        state = incoming_venue_data.state.data,
        address = incoming_venue_data.address.data,
        phone = incoming_venue_data.phone.data,
        image_link = incoming_venue_data.image_link.data,
        facebook_link = incoming_venue_data.facebook_link.data,
        website_link = incoming_venue_data.website_link.data,
        genres = modify_genres(incoming_venue_data.genres.data),
        seeking_talent = incoming_venue_data.seeking_talent.data,
        seeking_description = incoming_venue_data.seeking_description.data,
      )
      # Now add and commit Venue table to the database so that we are using real data
      db.session.add(new_venue_data)
      db.session.commit()
      flash(f'Venue {incoming_venue_data.name.data} was successfully listed!')
    except ValueError as e:
      db.session.rollback()
      flash(f'Venue {incoming_venue_data.name.data} could not be listed! Error: {str(e)}')
    finally:
      db.session.close()
  else:
    return_page = 'create_venue_submission'
    form_error_handling(incoming_venue_data)

  return redirect(url_for(return_page))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue_data = Venue.query.get(venue_id)
    db.session.delete(venue_data)
    db.session.commit()
    flash(f'Venue {venue_data.name} deleted!')
  except ValueError as e:
    db.session.rollback()
    flash(f'Error: {venue_data.name} could not be deleted! Error: {str(e)}')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  # Extract ALL IDs and names of of artists from the model, order by ID 
  try:
    artist_data = Artist.query.with_entities(Artist.id, Artist.name).order_by('id').all()
  except ValueError as e:
    flash(f'Error: {str(e)}')
  return render_template('pages/artists.html', artists=artist_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  try:
    search_input = request.form.get('search_term')
    artist_results = Artist.query.filter(Artist.name.ilike(f'%{search_input}%')).all()
    response={
      'count': len(artist_results),
      'data': artist_results
    }
  except ValueError as e:
    flash(f'Error: {str(e)}')
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  # Filter the artist table and fetch the artist requested
  artist_data = Artist.query.get_or_404(artist_id)
  # Get the shows. Initialise containers for counting past and upcoming show
  show_artist_data = {}
  show_artist_data['upcoming_shows'] = []
  show_artist_data['past_shows'] = []
  show_artist_data['upcoming_shows_count'] = 0
  show_artist_data['past_shows_count'] = 0
  
  # If artist exist, now get shows related to artist and deduce upcoming and past shows
  try:
    shows_data = artist_data.shows
    # For all shows...
    for show in shows_data:
      #show.id = show.venue.id
      show.venue_name = show.venue.name
      show.venue_image_link = show.venue.image_link
      if show.start_time > datetime.now(): # In the future...
        show.start_time = format_datetime(str(show.start_time))
        show_artist_data['upcoming_shows'].append(show)
        show_artist_data['upcoming_shows_count'] += 1
      else: # Past...
        show.start_time = format_datetime(str(show.start_time))
        show_artist_data['past_shows'].append(show)
        show_artist_data['past_shows_count'] += 1

    # Now construct the rest of the data that is straight forward
    show_artist_data['id'] = artist_data.id
    show_artist_data['name'] = artist_data.name
    show_artist_data['genres'] = artist_data.genres.split(',')
    show_artist_data['city'] = artist_data.city
    show_artist_data['state'] = artist_data.state
    show_artist_data['phone'] = artist_data.phone
    show_artist_data['website'] = artist_data.website_link
    show_artist_data['facebook_link'] = artist_data.facebook_link
    show_artist_data['seeking_venue'] = artist_data.seeking_venue
    show_artist_data['seeking_description'] = artist_data.seeking_description
    show_artist_data['image_link'] = artist_data.image_link
  except ValueError as e:
    flash(f'Error: {str(e)}')
  return render_template('pages/show_artist.html', artist=show_artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

  # TODO: populate form with fields from artist with ID <artist_id>
  # return render_template('forms/edit_artist.html', form=form, artist=current_artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(request.form, csrf_enabled=False)
  return_page = ''

  if form.validate():
    return_page = 'show_artist'
    try:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = modify_genres(form.genres.data)
      artist.image_link = form.image_link.data
      artist.facebook_link = form.facebook_link.data
      artist.website_link = form.website_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data

      db.session.commit()
      flash(f'Artist {form.name.data} was successfully edited!')
    except ValueError as e:
      db.session.rollback()
      flash(f'An error occurred in {form.name.data}. Error: {str(e)}')
    finally:
      db.session.close()
  else:
    return_page = 'edit_artist'
    form_error_handling(form)

  return redirect(url_for(return_page, artist_id=artist_id))
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

  # # TODO: populate form with values from venue with ID <venue_id>
  # return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(request.form, csrf_enabled=False)
  return_page = ''

  if form.validate():
    return_page = 'show_venue'
    try:
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.genres = modify_genres(form.genres.data)
      venue.image_link = form.image_link.data
      venue.facebook_link = form.facebook_link.data
      venue.website_link = form.website_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data

      db.session.commit()
      flash(f'Venue {form.name.data} was successfully edited!')
    except ValueError as e:
      db.session.rollback()
      flash(f'An error occurred in {form.name.data}. Error: {str(e)}')
    finally:
      db.session.close()
  else:
    return_page = 'edit_venue'
    form_error_handling(form)

  return redirect(url_for(return_page, venue_id=venue_id))

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
  incoming_artist_data = ArtistForm(request.form, csrf_enabled=False)
  return_page = ''

  if incoming_artist_data.validate():
    try:
      return_page = 'index'
      # Creating new artist model to provide real data
      new_artist_data = Artist(
        name = incoming_artist_data.name.data,
        city = incoming_artist_data.city.data,
        state = incoming_artist_data.state.data,
        phone = incoming_artist_data.phone.data,
        genres =  modify_genres(incoming_artist_data.genres.data),
        image_link = incoming_artist_data.image_link.data,
        facebook_link = incoming_artist_data.facebook_link.data,
        website_link = incoming_artist_data.website_link.data,
        seeking_venue = incoming_artist_data.seeking_venue.data,
        seeking_description = incoming_artist_data.seeking_description.data
      )
      # Add and commit artist table data to database
      db.session.add(new_artist_data)
      db.session.commit()
      flash(f'Artist {incoming_artist_data.name.data} was successfully listed!')
    except ValueError as e:
      # If there are any errors, rollback changes
      db.session.rollback()
      flash(f'An error occured. Artist {incoming_artist_data.name.data} could not be listed! Error: {str(e)}')
    finally:
      db.session.close()
  else:
    return_page = 'create_artist_submission'
    form_error_handling(incoming_artist_data)

  return redirect(url_for(return_page))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # Get all the data from show model, order them by earliest start time
  # Use relationship built into models to extract venue and artist information
  # This is where the backref comes into play
  show_data = Show.query.order_by('start_time').all()
  new_show_data = []
  for show in show_data:
    # Creating and assigning show details in the structure required
    show.venue_id = show.venue.id
    show.venue_name = show.venue.name
    show.artist_id = show.artist.id
    show.artist_name = show.artist.name
    show.artist_image_link = show.artist.image_link
    show.start_time = format_datetime(str(show.start_time))

    # Append the show detail into the overall container that will list all shows
    new_show_data.append(show)
  return render_template('pages/shows.html', shows=new_show_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  incoming_show_data = ShowForm(request.form, csrf_enabled=False)
  return_page = ''

  if incoming_show_data.validate():
    artist_exist = Artist.query.filter(Artist.id == incoming_show_data.artist_id.data).one_or_none()
    venue_exist = Venue.query.filter(Venue.id == incoming_show_data.venue_id.data).one_or_none()
    if artist_exist is not None and venue_exist is not None:
      return_page = 'index'
      try:
        # Creating new show model based on form input
        new_show_data = Show(
          venue_id = incoming_show_data.venue_id.data,
          artist_id = incoming_show_data.artist_id.data,
          start_time = incoming_show_data.start_time.data
        )
        # Adding and commiting to database
        db.session.add(new_show_data)
        db.session.commit()
        flash('Show was successfully listed!')
      except ValueError as e:
        # If errors occur, roll back changes to database
        # TODO: on unsuccessful db insert, flash an error instead.
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
      finally:
        db.session.close()
    else:
      return_page = 'create_show_submission'
      flash('Either Artist or Venue ID does not exist... Please check the details!')
  else:
    return_page = 'create_show_submission'
    form_error_handling(incoming_show_data)

  return redirect(url_for(return_page))


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
