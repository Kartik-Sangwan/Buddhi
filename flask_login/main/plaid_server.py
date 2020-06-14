from main import app, db, session
from main.models import User, Post
import base64
import os
import datetime
import plaid
import json
import time
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

# Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
PLAID_CLIENT_ID = '5ed7b65c2aafa90012d29f77'
PLAID_SECRET = '53701984c4b9f78e60616e904b2217'
PLAID_PUBLIC_KEY = 'c203d55fa2f9f8254cdf3d0e7a4e59'
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use `development` to test with live users and credentials and `production`
# to go live
PLAID_ENV = 'sandbox'
# PLAID_PRODUCTS is a comma-separated list of products to use when initializing
# Link. Note that this list must contain 'assets' in order for the app to be
# able to create and retrieve asset reports.
PLAID_PRODUCTS = 'liabilities'

# PLAID_COUNTRY_CODES is a comma-separated list of countries for which users
# will be able to select institutions from.
PLAID_COUNTRY_CODES = 'CA'

# Parameters used for the OAuth redirect Link flow.
#
# Set PLAID_OAUTH_REDIRECT_URI to 'http://localhost:5000/oauth-response.html'
# The OAuth redirect flow requires an endpoint on the developer's website
# that the bank website should redirect to. You will need to whitelist
# this redirect URI for your client ID through the Plaid developer dashboard
# at https://dashboard.plaid.com/team/api.
PLAID_OAUTH_REDIRECT_URI = 'http://127.0.0.1:5000/oauth-response.html'
# Set PLAID_OAUTH_NONCE to a unique identifier such as a UUID for each Link
# session. The nonce will be used to re-open Link upon completion of the OAuth
# redirect. The nonce must be at least 16 characters long.
PLAID_OAUTH_NONCE = '123456789123456789'

client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')


# Way to store identifiers - access_tokens and item_ids at the server side - connects users with Financial instiutions
# Associate these with the users
#
#

@app.route('/plaid_authenticate')
def plaid_authenticate():
  return render_template(
    'index.ejs',
    plaid_public_key=PLAID_PUBLIC_KEY,
    plaid_environment=PLAID_ENV,
    plaid_products=PLAID_PRODUCTS,
    plaid_country_codes=PLAID_COUNTRY_CODES,
  )

# This is an endpoint defined for the OAuth flow to redirect to.
@app.route('/oauth-response.html')
def oauth_response():
  return render_template(
    'oauth-response.ejs',
    plaid_public_key=PLAID_PUBLIC_KEY,
    plaid_environment=PLAID_ENV,
    plaid_products=PLAID_PRODUCTS,
    plaid_country_codes=PLAID_COUNTRY_CODES,
  )

# We store the access_token in memory - in production, store it in a secure
# persistent data store.
access_token = None
# The payment_token is only relevant for the UK Payment Initiation product.
# We store the payment_token in memory - in production, store it in a secure
# persistent data store.
payment_token = None
payment_id = None

# Exchange token flow - exchange a Link public_token for
# an API access_token
# https://plaid.com/docs/#exchange-token-flow
@app.route('/get_access_token', methods=['POST'])
def get_access_token():
  global access_token
  public_token = request.form['public_token']
  try:
    exchange_response = client.Item.public_token.exchange(public_token)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))

  pretty_print_response(exchange_response)
  access_token = exchange_response['access_token']

  # adding access token to the user
  user = User.query.filter_by(username=session['username']).first()
  user.access_token = access_token
  print(user.access_token, "\n")
  db.session.commit()

  return jsonify(exchange_response)


# NOTE: jsonify removed
@app.route('/auth', methods=['GET'])
def get_auth(employee_access_token):
  try:
    auth_response = client.Auth.get(employee_access_token)
  except plaid.errors.PlaidError as e:
    return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } }
  # pretty_print_response(auth_response)
  return {'error': None, 'auth': auth_response}

# Test access token - access-sandbox-1c098ada-aa37-425f-9879-5577c59b6a83

@app.route('/liabilities-get', methods=["GET"])
def get_liabilities(employee_access_token):
# def get_liabilities():
  # print(access_token, "\n\n")
  try:
    response = client.Liabilities.get("access-sandbox-1c098ada-aa37-425f-9879-5577c59b6a83")
  except plaid.errors.PlaidError as e:
    return {'error':{'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type}}
  liabilities = response['liabilities']
  pretty_print_response(liabilities["student"])
  return {'error': None, 'info': liabilities}

# Retrieve Transactions for an Item
# https://plaid.com/docs/#transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
  # Pull transactions for the last 30 days
  start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
  end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
  try:
    transactions_response = client.Transactions.get(access_token, start_date, end_date)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))
  pretty_print_response(transactions_response)
  return jsonify({'error': None, 'transactions': transactions_response})

# Retrieve Identity data for an Item
# https://plaid.com/docs/#identity
@app.route('/identity', methods=['GET'])
def get_identity():
  try:
    identity_response = client.Identity.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(identity_response)
  return jsonify({'error': None, 'identity': identity_response})

# Retrieve real-time balance data for each of an Item's accounts
# https://plaid.com/docs/#balance
@app.route('/balance', methods=['GET'])
def get_balance():
  try:
    balance_response = client.Accounts.balance.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(balance_response)
  return jsonify({'error': None, 'balance': balance_response})

# Retrieve an Item's accounts
# https://plaid.com/docs/#accounts
@app.route('/accounts', methods=['GET'])
def get_accounts():
  try:
    accounts_response = client.Accounts.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(accounts_response)
  return jsonify({'error': None, 'accounts': accounts_response})

# Create and then retrieve an Asset Report for one or more Items. Note that an
# Asset Report can contain up to 100 items, but for simplicity we're only
# including one Item here.
# https://plaid.com/docs/#assets
@app.route('/assets', methods=['GET'])
def get_assets():
  try:
    asset_report_create_response = client.AssetReport.create([access_token], 10)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(asset_report_create_response)

  asset_report_token = asset_report_create_response['asset_report_token']

  # Poll for the completion of the Asset Report.
  num_retries_remaining = 20
  asset_report_json = None
  while num_retries_remaining > 0:
    try:
      asset_report_get_response = client.AssetReport.get(asset_report_token)
      asset_report_json = asset_report_get_response['report']
      break
    except plaid.errors.PlaidError as e:
      if e.code == 'PRODUCT_NOT_READY':
        num_retries_remaining -= 1
        time.sleep(1)
        continue
      return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

  if asset_report_json == None:
    return jsonify({'error': {'display_message': 'Timed out when polling for Asset Report', 'error_code': e.code, 'error_type': e.type } })

  asset_report_pdf = None
  try:
    asset_report_pdf = client.AssetReport.get_pdf(asset_report_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

  return jsonify({
    'error': None,
    'json': asset_report_json,
    'pdf': base64.b64encode(asset_report_pdf),
  })

# Retrieve investment holdings data for an Item
# https://plaid.com/docs/#investments
@app.route('/holdings', methods=['GET'])
def get_holdings():
  try:
    holdings_response = client.Holdings.get(access_token)
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })
  pretty_print_response(holdings_response)
  return jsonify({'error': None, 'holdings': holdings_response})

# Retrieve Investment Transactions for an Item
# https://plaid.com/docs/#investments
@app.route('/investment_transactions', methods=['GET'])
def get_investment_transactions():
  # Pull transactions for the last 30 days
  start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
  end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
  try:
    investment_transactions_response = client.InvestmentTransactions.get(access_token,
                                                                         start_date,
                                                                         end_date)
  except plaid.errors.PlaidError as e:
    return jsonify(format_error(e))
  pretty_print_response(investment_transactions_response)
  return jsonify({'error': None, 'investment_transactions': investment_transactions_response})

# This functionality is only relevant for the UK Payment Initiation product.
# Retrieve Payment for a specified Payment ID
@app.route('/payment', methods=['GET'])
def payment():
  global payment_id
  payment_get_response = client.PaymentInitiation.get_payment(payment_id)
  pretty_print_response(payment_get_response)
  return jsonify({'error': None, 'payment': payment_get_response})

# Retrieve high-level information about an Item
# https://plaid.com/docs/#retrieve-item
@app.route('/item', methods=['GET'])
def item():
  global access_token
  item_response = client.Item.get(access_token)
  institution_response = client.Institutions.get_by_id(item_response['item']['institution_id'])
  pretty_print_response(item_response)
  pretty_print_response(institution_response)
  return jsonify({'error': None, 'item': item_response['item'], 'institution': institution_response['institution']})

@app.route('/set_access_token', methods=['POST'])
def set_access_token():
  global access_token
  access_token = request.form['access_token']
  item = client.Item.get(access_token)
  return jsonify({'error': None, 'item_id': item['item']['item_id']})

# This functionality is only relevant for the UK Payment Initiation product.
# Sets the payment token in memory on the server side. We generate a new
# payment token so that the developer is not required to supply one.
# This makes the quickstart easier to use.
@app.route('/set_payment_token', methods=['POST'])
def set_payment_token():
  global payment_token
  global payment_id
  try:
    create_recipient_response = client.PaymentInitiation.create_recipient(
      'Harry Potter',
      'GB33BUKB20201555555555',
      {
        'street': ['4 Privet Drive'],
        'city': 'Little Whinging',
        'postal_code': '11111',
        'country': 'GB',
      },
    )
    recipient_id = create_recipient_response['recipient_id']

    create_payment_response = client.PaymentInitiation.create_payment(
      recipient_id,
      'payment_ref',
      {
        'currency': 'GBP',
        'value': 12.34,
      },
    )
    payment_id = create_payment_response['payment_id']

    create_payment_token_response = client.PaymentInitiation.create_payment_token(payment_id)
    payment_token = create_payment_token_response['payment_token']
  except plaid.errors.PlaidError as e:
    return jsonify({'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type } })

  return jsonify({'error': None, 'payment_token': payment_token})

def pretty_print_response(response):
  print(json.dumps(response, indent=2, sort_keys=True))

def format_error(e):
  return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, 'error_message': e.message } }

if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 5000))
