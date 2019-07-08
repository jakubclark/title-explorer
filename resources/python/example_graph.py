import asyncio
import json

import aiohttp


async def post(session, url, data):
    async with session.post(url, json=data) as response:
        return await response.text()


async def main():
    with open('example_graph.json') as f:
        titles = json.load(f)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for title in titles:
            url = 'http://localhost:8080/api/title'
            tasks.append(post(session, url, title))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
