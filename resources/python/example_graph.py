import asyncio

import aiohttp

ids = [
    'tt0371746',
    'tt0800080',
    'tt1228705',
    'tt0800369',
    'tt0458339',
    'tt0848228',
    'tt1300854',
    'tt1981115',
    'tt1843866',
    'tt2015381',
    'tt2395427',
    'tt0478970',
    'tt3498820',
    'tt1211837',
    'tt3896198',
    'tt2250912',
    'tt3501632',
    'tt1825683',
    'tt4154756',
    'tt4154756',
    'tt5095030',
    'tt5095030',
    'tt4154664',
    'tt4154796',
    'tt6320628'
]


async def fetch(session, url, id):
    async with session.get(url, params={'id': id}) as response:
        return await response.text()


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for id in ids:
            url = 'http://localhost:8080/api/search?'
            tasks.append(fetch(session, url, id))
        results = await asyncio.gather(*tasks)
        for res in results:
            print(res)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
