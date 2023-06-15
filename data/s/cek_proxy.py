
import aiohttp
import asyncio
import aiofiles, sqlite3



LIST_URL = [
    'https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt',
    'https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt',
    'https://raw.githubusercontent.com/caliwyr/Proxy-List/main/http.txt',
    'https://raw.githubusercontent.com/zuoxiaolei/proxys/main/proxys/proxys.txt',
    'https://raw.githubusercontent.com/saisuiu/Lionkings-Http-Proxys-Proxies/main/free.txt',
    'https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/premium.txt',
    'https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/working.txt',
    'https://raw.githubusercontent.com/saschazesiger/Free-Proxies/master/proxies/http.txt',
    'https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
    'https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt'
]


class DatabaseProxy:
    def __init__(self) -> None:
        self.tabel  = "proxy"
        self.conn   = sqlite3.connect('proxy.db')
        self.cursor = self.conn.cursor()
        
    def create_tabel(self):
        self.cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS
        %s([proxy] TEXT)
        """ % (self.tabel)
        )
        self.conn.commit()
    
    def input_data(self, proxies):
        self.cursor.execute(
            "insert into {} values(?)".format(self.tabel),(proxies,)
        )
        self.conn.commit()
    
    def delete_data(self, proxies):
        self.cursor.execute(
            "DELETE FROM {} WHERE proxy=?".format(self.tabel), (proxies,)
        )
        self.conn.commit()
    
    def print_db(self):
        self.cursor.execute(
            "SELECT * FROM {}".format(self.tabel)
        )
        return self.cursor.fetchall()


async def proxy_lazada(session, proxies):
    try:
        async with session.get(
            'https://pages.lazada.co.id/wow/gcp/id/ug-newuser/nulp?source=homepage_free_buy&source=homepage_free_buy&item=7447890484,7400654849,7099562384&itemId=7447890484,7400654849,7099562384&price_max=120000.0&price_min=0.0&spm=a211g0.home.combinedNUC.voucher1&laz_event_id=422_1685126965416_75405',
            proxy=f'http://{proxies}'
        
        ) as resp:
            assert resp.status == 200
            print(f'[+] {proxies}')
            DatabaseProxy().input_data(
                proxies=proxies
            )
            return proxies
    except:pass


async def cek_proxy(client, url):
    async with client.get(url) as resp:
        res = await resp.text()
        return res.splitlines()


async def get_proxy():
    async with aiohttp.ClientSession() as client:
        result = await asyncio.gather(
            *[
                asyncio.ensure_future(
                    cek_proxy(client, url.strip())
                ) for url in LIST_URL
            ]
        )
        hasil_proxy = sum(result, [])
        return hasil_proxy


async def get_proxy_lazada():
    DatabaseProxy().create_tabel()
    list_proxy = await get_proxy()
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[
                asyncio.ensure_future(
                    proxy_lazada(session, proxy)
                ) for proxy in list_proxy
            ]
        )



# asyncio.run(
#     get_proxy_lazada()
# )

