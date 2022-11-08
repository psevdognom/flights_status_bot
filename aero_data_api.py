from io import StringIO

from aiohttp import request, ClientSession

from settings import AERO_DATA_BOX_HEADERS


class AeroDataBox:


    def __init__(self, headers):
        self._headers = headers

    async def make_request(self, url):
        async with ClientSession(headers=self._headers) as session:
            async with session.get(url) as r:
                pass



if __name__ == '__main__':
    # import pandas as pd
    # from pandas.compat import StringIO
    with open('airports.dat', 'r') as f:
        # df = pd.read_csv(StringIO(f.readline()), sep=",", engine='python')
        # print(df.head)
        print(f.readline().split(',')[0:14])

    pass