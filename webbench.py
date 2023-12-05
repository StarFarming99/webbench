import time
import threading
import httpx
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="一个复杂的命令行参数解析示例")

    parser.add_argument('-t', '--time', type=int, help='运行多长时间，单位：秒')
    parser.add_argument('-c', '--clients', type=int, default=1, help='创建多少个客户端，默认1个')
    parser.add_argument('--get', action='store_true', help='使用 GET请求方法')
    parser.add_argument('--head', action='store_true', help='使用 HEAD请求方法')
    parser.add_argument('--options', action='store_true', help='使用 OPTIONS请求方法')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0', help='显示版本号')

    return parser.parse_args()


args = parse_args()

# 配置
TARGET_URL = 'https://www.google.com/'
THREAD_COUNT = args.clients
REQUEST_PER_THREAD = 100 if args.time is None else args.time // THREAD_COUNT

success_count = 0
failure_count = 0
lock = threading.Lock()


def worker():
    global success_count, failure_count

    proxies = None
    method = 'GET'  # Default method
    if args.head:
        method = 'HEAD'
    elif args.options:
        method = 'OPTIONS'

    with httpx.Client(http2=True, proxies=proxies) as client:
        for _ in range(REQUEST_PER_THREAD):
            try:
                request_func = getattr(client, method.lower())
                response = request_func(TARGET_URL)
                if 200 <= response.status_code < 400:
                    with lock:
                        success_count += 1
                else:
                    with lock:
                        failure_count += 1
            except Exception as e:
                print(f"Error: {e}")
                with lock:
                    failure_count += 1


def main():
    start_time = time.time()

    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    elapsed_time = time.time() - start_time
    total_requests = success_count + failure_count

    print(f"Total requests: {total_requests}")
    print(f"Successful requests: {success_count}")
    print(f"Failed requests: {failure_count}")
    print(f"Time taken: {elapsed_time:.2f} seconds")
    print(f"Requests per second: {total_requests / elapsed_time:.2f}")


if __name__ == '__main__':
    main()
