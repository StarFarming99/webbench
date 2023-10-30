import time
import threading
import httpx
import argparse


def parser():
    parser = argparse.ArgumentParser(description="一个复杂的命令行参数解析示例")

    # 添加命令行参数
    parser.add_argument('-f', '--force', action='store_true', help='不需要等待服务器响应')
    parser.add_argument('-r', '--reload', action='store_true', help='发送重新加载请求')
    parser.add_argument('-t', '--time', type=int, help='运行多长时间，单位：秒')
    parser.add_argument('-p', '--proxy', type=str, help='使用代理服务器来发送请求，格式：server:port')
    parser.add_argument('-c', '--clients', type=int, default=1, help='创建多少个客户端，默认1个')
    parser.add_argument('--get', action='store_true', help='使用 GET请求方法')
    parser.add_argument('--head', action='store_true', help='使用 HEAD请求方法')
    parser.add_argument('--options', action='store_true', help='使用 OPTIONS请求方法')
    parser.add_argument('--trace', action='store_true', help='使用 TRACE请求方法')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0', help='显示版本号')

    # 解析参数
    args = parser.parse_args()



# 配置
TARGET_URL = 'https://www.google.com/'
THREAD_COUNT = 10  # 同时并发的线程数
REQUEST_PER_THREAD = 100  # 每个线程发送的请求数

success_count = 0
failure_count = 0
lock = threading.Lock()


def worker():
    global success_count, failure_count

    with httpx.Client(http2=True) as client: # get
        for _ in range(REQUEST_PER_THREAD):
            try:
                response = client.get(TARGET_URL)
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