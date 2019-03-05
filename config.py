import os

config = {}

config['PRODUCTION']        = 1
config['FLASK_APP']         = 'slideshare'
config['FLASK_ENV']         = 'production'
config['SECRET_KEY']        = os.environ['SECRET_KEY']

config['S3_THUMB_BUCKET']   = 'slide-share-thumbs'
config['S3_PPT_BUCKET']     = 'slide-sharing-platform'

config['DB_NAME']           = 'slideshare'
config['DB_USER']           = 'csr2131'
config['DB_HOST']           = 'slideshare-prod.cshgvdefxewm.us-east-1.rds.amazonaws.com'
config['DB_URI_PRODUCTION'] = 'postgresql://{}:{}@{}:5432/{}'.format(
                                    config["DB_USER"], os.environ['DB_PASSWORD'], config["DB_HOST"], config["DB_NAME"])
config['DB_URI_LOCAL']      = 'postgresql://carloruiz@localhost:5432/slideshare'
config['DB_URI']            = config['DB_URI_PRODUCTION'] if config['PRODUCTION'] else config['DB_URI_LOCAL']

