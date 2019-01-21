import os 

DB = {
    'NAME': 'slideshare',
    'USER': 'csr2131',
    'PASSWORD': os.environ['DB_PASSWORD'],
    'HOST': 'slideshare-prod.cshgvdefxewm.us-east-1.rds.amazonaws.com',
    'PORT': '5432',
}

if __name__ == '__main__':
    print(DB)
