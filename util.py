import requests
import time

# some website limits us on how many requests we can send in a second/minute/hour
def retriable_send_request(url):
    success = False
    retry_cnt = 0
    max_retry_count = 3
    while not success and retry_cnt < max_retry_count:
        try:
            success = True
            req = requests.get(url, allow_redirects=True)
            txt = req.text
            req.close()
            return txt
        except requests.exceptions.ConnectionError as e:
            print(f"Got connection error {e} for {url}, will retry after sleeping for some time")
            time.sleep(3)
            retry_cnt += 1
            success = False
    print(f"Still cannot download {url} after retrying {max_retry_count} times, please manually retry")
    return None