import os
import subprocess
from aiohttp import web
import re
import asyncio

def ip检查(filename, ip):
    原ip = ''
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    with open(filename, 'r') as fp:
        f_str = fp.read()
        match = re.search(ip_pattern, f_str)
        原ip = match.group(0)
    if 原ip and (ip not in 原ip):
        with open(filename, 'w') as fp:
            f_str = f_str.replace(原ip, ip)
            fp.write(f_str)
    subprocess.run(['sh', 'run.sh'])
    return 原ip

async def handle(request):
    try:
        ip = request.match_info.get('ip', "None")
        if ip != "None":
            text = "反向代理当前ip:" + ip检查("/root/run.sh",ip)
        else:
            text = "内部错误"
        return web.Response(text=text)
    except:
        return web.Response(text="内部错误")

async def worker():
    port = 30088
    app = web.Application()
    app.add_routes([web.get('/', handle),
                    web.get('/updateipaddr/{ip}', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"反代ip更新线程：http://0.0.0.0:{port}")
    # 保持主函数持续运行
    while True:
        await asyncio.sleep(1)  # 每小时执行一次异步操作，防止事件循环退出

def run():
    try:
        asyncio.run(worker())
    except KeyboardInterrupt:
        print("Server stopped manually")

if __name__ == '__main__':
    run()