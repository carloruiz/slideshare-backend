
def aws_s3_uri(bucket_name, *args):
    uri = 's3://%s/' % bucket_name
    for arg in args:
        uri += '{}/'.format(arg)
    return uri

def aws_s3_url(bucket_name, *args):
    uri = 'https://s3.amazonaws.com/%s/' % bucket_name
    for arg in args:
        uri += '{}/'.format(arg)
    return uri
