import os

config = {
    'PRODUCTION'        : True,
    'FLASK_APP'         : 'slidegraph',
    'FLASK_ENV'         : 'production',
    'SECRET_ENV'        : os.environ['SECRET_KEY'],
    
    'DEV_ORIGIN'        : 'http://localhost:3000',
    'PRODUCTION_ORIGIN' : 'http://slidegraph.net.s3-website-us-east-1.amazonaws.com/',
    
    'S3_THUMB_BUCKET'   : 'slide-share-thumbs',
    'S3_PPT_BUCKET'     : 'slide-sharing-platform',
    
    'DB_NAME'           : 'slideshare',
    'DB_USER'           : 'csr2131',
    'DB_HOST'           : 'slideshare-prod.cshgvdefxewm.us-east-1.rds.amazonaws.com',
    'DB_URI_PRODUCTION' : 'postgresql://{}:{}@{}:5432/{}'.format(
                                        config["DB_USER"], os.environ['DB_PASSWORD'], 
                                        config["DB_HOST"], config["DB_NAME"]),
    'DB_URI_LOCAL'      :  'postgresql://carloruiz@localhost:5432/slideshare'
}

config['ORIGIN'] = config['PRODUCTION_ORIGIN'] if config['PRODUCTION'] else config['DEV_ORIGIN'] 
config['DB_URI'] = config['DB_URI_PRODUCTION'] if config['PRODUCTION'] else config['DB_URI_LOCAL']

