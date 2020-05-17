# Quickstart for plaid-python

To run this application locally, first install it and then run either of the flows described below. Additionally, please also refer to the [Quickstart guide](https://plaid.com/docs/quickstart).

## Installing the quickstart app
``` bash
git clone https://github.com/plaid/quickstart.git
cd quickstart/python

# If you use virtualenv
# virtualenv venv
# source venv/bin/activate

pip install -r requirements.txt
```

## The canonical flow
``` bash
# Start the Quickstart with your API keys from the Dashboard
# https://dashboard.plaid.com/account/keys
#
# PLAID_PRODUCTS is a comma-separated list of products to use when
# initializing Link, see https://plaid.com/docs/#item-product-access
# for complete list.

# PLAID_COUNTRY_CODES is a comma-separated list of countries to use when
# initializing Link, see plaid.com/docs/faq/#does-plaid-support-international-bank-accounts-
# for a complete list

PLAID_CLIENT_ID='CLIENT_ID' \
PLAID_SECRET='SECRET' \
PLAID_PUBLIC_KEY='PUBLIC_KEY' \
PLAID_ENV='sandbox' \
PLAID_PRODUCTS='transactions' \
PLAID_COUNTRY_CODES='US' \
python server.py

# Go to http://localhost:5000
```

## The OAuth redirect flow
Some European institutions require an OAuth redirect authentication flow, where the end user is redirected to the bank’s website or mobile app to authenticate. For this flow, you should provide two additional configuration parameters, `PLAID_OAUTH_NONCE` and `PLAID_OAUTH_REDIRECT_URI`.

``` bash
# You will need to whitelist the PLAID_OAUTH_REDIRECT_URI for
# your client ID through the Plaid developer dashboard at
# https://dashboard.plaid.com/team/api.
#
# Set PLAID_OAUTH_NONCE to a unique identifier such as a UUID.
# The nonce must be at least 16 characters long.
#
# Start the Quickstart with your API keys from the Dashboard
# https://dashboard.plaid.com/account/keys
#
# PLAID_PRODUCTS is a comma-separated list of products to use when
# initializing Link, see https://plaid.com/docs/#item-product-access
# for complete list.

PLAID_CLIENT_ID='CLIENT_ID' \
PLAID_SECRET='SECRET' \
PLAID_PUBLIC_KEY='PUBLIC_KEY' \
PLAID_ENV='sandbox' \
PLAID_PRODUCTS='transactions' \
PLAID_COUNTRY_CODES='GB,FR,ES,IE,NL' \
PLAID_OAUTH_REDIRECT_URI='http://localhost:5000/oauth-response.html' \
PLAID_OAUTH_NONCE='nice-and-long-nonce' \
python server.py

# Go to http://localhost:5000
```
