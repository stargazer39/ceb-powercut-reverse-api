from time import sleep


def retry_util(func, *args):
    exception = ""

    for _ in range(4):
        try:
            return func(*args)
        except Exception as e:
            exception = e
            sleep(.2)
            continue
    
    raise exception