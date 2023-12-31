import asyncio
import httpx
import argparse
import time

def parse_args():
    parser = argparse.ArgumentParser(description="a parser")

    parser.add_argument('-r', '--request', type=int, help='total requests')
    parser.add_argument('-c', '--clients', type=int, default=1, help='How many clients to create')
    parser.add_argument('-p', "--protocol", choices=['http1', 'http2'], default='http1', help="HTTP protocol version")
    parser.add_argument('--get', action='store_true', help='GET method')
    parser.add_argument('--head', action='store_true', help='HEAD method')
    parser.add_argument('--options', action='store_true', help='OPTIONS method')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0', help='Show versions')

    return parser.parse_args()

async def send_request(client, url, method):
    try:
        response = await client.request(method, url)
        return 200 <= response.status_code < 400
    except Exception as e:
        print(f"Error: {e}")
        return False

async def worker(url, http_version, method, request_count):
    success_count = 0
    failure_count = 0

    async with httpx.AsyncClient(http2=http_version) as client:
        for _ in range(request_count):
            if await send_request(client, url, method):
                success_count += 1
            else:
                failure_count += 1

    return success_count, failure_count

async def main():
    args = parse_args()

    # 配置
    TARGET_URL = 'https://httpbin.org/'
    CLIENT_COUNT = args.clients
    REQUEST_PER_CLIENT = 100 if args.request is None else args.request // CLIENT_COUNT
    HTTP_VERSION = args.protocol == 'http2'  # http2 -> True, http1 -> false

    method = 'GET'
    if args.head:
        method = 'HEAD'
    elif args.options:
        method = 'OPTIONS'

    start_time = time.time()

    tasks = [worker(TARGET_URL, HTTP_VERSION, method, REQUEST_PER_CLIENT) for _ in range(CLIENT_COUNT)]
    results = await asyncio.gather(*tasks)

    total_success = sum(success for success, failure in results)
    total_failure = sum(failure for success, failure in results)

    elapsed_time = time.time() - start_time
    total_requests = total_success + total_failure

    print(f"Total requests: {total_requests}")
    print(f"Successful requests: {total_success}")
    print(f"Failed requests: {total_failure}")
    print(f"Time taken: {elapsed_time:.2f} seconds")
    print(f"Requests per second: {total_requests / elapsed_time:.2f}")

if __name__ == '__main__':
    asyncio.run(main())
