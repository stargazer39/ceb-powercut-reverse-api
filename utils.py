def retry_util(func, *args):
    exception = ""

    for _ in range(4):
        try:
            return func(*args)
        except Exception as e:
            exception = e
            continue
    
    raise exception