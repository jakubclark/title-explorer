import asyncio
import json

import aiohttp


async def post(session, url, data):
    async with session.post(url, json=data) as response:
        return await response.text()


async def main():
    """
    Create a graph, with the top ~250 TV Shows and the top ~250 Movies
    """
    with open('example_graph.json', encoding='utf-8') as f:
        titles = json.load(f)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for title in titles:
            url = 'http://localhost:8080/api/title'
            print(f'POST title="{title["title"]}" | type="{title["type"]}"')
            tasks.append(post(session, url, title))
        results = await asyncio.gather(*tasks)
        for res in results:
            print(res)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
