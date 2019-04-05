
def aws_s3_uri(bucket_name, resourceid, ext=''):
    return 's3://{}/{}{}'.format(bucket_name, resourceid, ext)

def aws_s3_url(bucket_name, resourceid, ext=''):
    uri = 'https://s3.amazonaws.com/{}/{}{}'.format(bucket_name, resourceid, ext)
    return uri
