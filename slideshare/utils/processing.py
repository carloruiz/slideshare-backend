import time
import subprocess as sp

def gen_err(userid, err_str):
    return {
        "userid": userid,
        "err": err_str,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    }

def run_subprocess(args, userid, exception=Exception, timeout=30):
    try:
        res = sp.run(args=args, stderr=sp.PIPE, timeout=timeout)
        if res.returncode != 0:
            err = gen_err(userid, res.stderr.decode('utf-8'))
            print(err)
            return 1
    except exception as e:
        err = gen_err(userid, filename, str(e))
        print(err)
        return 1
    
    return 0

