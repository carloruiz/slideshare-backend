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
        print("inside subprocess") 
        res = sp.run(args=args, stdout=sp.PIPE, stderr=sp.PIPE, timeout=timeout)
        if res.returncode != 0:
            err = gen_err(userid, res.stderr.decode('utf-8'))
            print(res)
            return 1
    except exception as e:
        err = gen_err(userid, str(e))
        print(err)
        return 1
    
    print(res)

    return 0

