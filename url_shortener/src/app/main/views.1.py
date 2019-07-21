from flask import Blueprint, render_template, jsonify, request, redirect, flash
from app.main.forms import SubmitUrlForm
from base64 import b64encode
from hashlib import blake2b
from urllib.parse import urlparse
from app.models import *
import random
from flask import current_app as app
from app import memcached_client

main = Blueprint('main', __name__)
shortened = {}
DIGEST_SIZE = 9  # 72 bits of entropy.

# ------------------------
# view controller routes
# ------------------------
@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
def submit_url():
    """Form to allow user to submit url"""
    form = SubmitUrlForm() 
    if request.method == 'POST':
        url = request.form['url']
    
        if form.validate():
            result = shorten_url(url)

            flash('Your new short URL is: %s' % (str(result)), 'success')
        else:
            flash('All the form fields are required.', 'warning')
    
    return render_template('main/submit.html', form=form)

# ------------------------
# helper methods
# ------------------------
def shorten(url):
    """Shortens a url by generating a 9 byte hash, and then
    converting it to a 12 character long base 64 url friendly string.

    Parameters:
    url - the url to be shortened.

    Return values:
    String, the unique shortened url, acting as a key for the entered long url.
    """
    url_hash = blake2b(str.encode(url), digest_size=DIGEST_SIZE)

    while url_hash in shortened:
        url += str(random.randint(0, 9))
        url_hash = blake2b(str.encode(url), digest_size=DIGEST_SIZE)

    b64 = b64encode(url_hash.digest(), altchars=b'-_')
    return b64.decode('utf-8')


def bad_request(message):
    response = jsonify({'message': message})
    response.status_code = 400
    return response


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        app.logger.error('Invalid request, %s is not a valid url' % (url))
        return False


def short_me():
    short_url = shorten(url)

    # check cache
    app.logger.debug('Checking cache for: %s' % (short_url))
    result = get_from_cache(short_url)

    if result is None:
        app.logger.debug('Couldn\'t find in cache!')
        # check database for short url
        try:
            result = Url.get(url = short_url).url
        except Url.DoesNotExist:
            # create new short url
            app.logger.debug('Couldn\'t find in database!\n Inserting %s == %s' % (url, short_url))
            Url.create(
                long_url = url,
                short_url = short_url
            )
            memcached_client.set(short_url, url)
            result = short_url
    return result


# ------------------------
# api routes
# ------------------------
@main.route('/shorten_url', methods=['POST'])
def shorten_url(url):
    """POST endpoint that looks for a supplied string called "url",
    contained inside a json object. Then validates this url and
    either returns an error response as appropriate, or generates a
    shortened url, stores the shortened url, and then returns it - if valid.

    Parameters:
    None. However, the global request object should contain the aforementioned json.

    Return values:
    A response signifying success or error.
    Successes contain the shortened url, errors contain an appropriate message.
    """
    if not request.json:
        return bad_request('Url must be provided in json format.')
    
    if 'url' not in request.json:
        return bad_request('Url parameter not found.')
    
    url = request.json['url']
    # For redirection purposes, we want to append http at some point.
    if url[:4] != 'http':
        url = 'http://' + url

    if not is_valid_url(url):
        return bad_request('Provided url is not valid.')

    shortened_url = shorten(url)
    shortened[shortened_url] = url

    return jsonify({'shortened_url': shortened_url}), 201


def get_from_cache(short_url):
    return memcached_client.get(short_url).decode('utf-8')


@main.route('/<short_url>', methods=['GET'])
def get_shortened(short_url):
    """GET endpoint that takes an short_url and redirects if successfull.
    Otherwise returns a bad request.

    Arguments:
    short_url, the string representing a shortened url.

    Return values:
    A Flask redirect, with code 302.
    """
    result = get_from_cache(short_url)
    if result is None: # not in cache
        app.logger.debug('short_url %s was not found in cache' % (short_url))
        try:
            result = Url.get(url = alias).long_url
        except Url.DoesNotExist:
            app.logger.debug('short_url %s was not found in db' % (short_url))
            return bad_request('Oops! Unknown short url...')

    if result[:4] != 'http':
        result = 'http://' + result
    return redirect(result, code=302)

@main.route('/urls/<page>', methods=['GET'])
def get_all(page):
    page = int(page)
    page_limit = 10
    for i in Url.select():
        print(i)
    return Url.select().paginate(page*page_limit,page*page_limit+page_limit)
    #return jsonify({'2': Url.select().paginate(page*page_limit,page*page_limit+page_limit)}), 200
    