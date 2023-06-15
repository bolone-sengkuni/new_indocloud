import time, re, os, sqlite3
from bs4 import BeautifulSoup
import struct, hmac, base64
import random, hashlib
from ctypes import c_int
from datetime import datetime
import asyncio, radar
from rich import print as pprint
import aiofiles, httpx
from cek_proxy import *


DIR = os.path.dirname(os.path.abspath(__file__))


class Database:
    def create_tabel(cursor,con,tabel):
        cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS
        %s([uuid] TEXT,
        [time] TEXT,
        [info] TEXT)
        """ % (tabel)
        )
        con.commit()

    def input_data(cursor,con,tabel, uuids, timer, info):
        cursor.execute(
            "insert into {} values(?,?,?)".format(tabel),(uuids, timer, info)
        )
        con.commit()



def random_date():
    return radar.random_datetime(
        start = datetime(
            year=2023, 
            month=3, 
            day=24, 
            hour=11, 
            minute=20, 
            second=23, 
            microsecond=datetime.now().microsecond
            ),
        stop = datetime(
            year=datetime.now().year,
            month=datetime.now().month, 
            day=datetime.now().day, 
            hour=12, 
            minute=21,
            second=23,
            microsecond=712993
            )
        ).timestamp()



def hashCode(str):
    res = c_int(0)
    if not isinstance(str, bytes):
        str = str.encode()
    for i in bytearray(str):
        res = c_int(c_int(res.value * 0x1f).value + i)
    return res.value


def generateUtdid():
    times = random_date()
    timer = int(times)
    i31 = random.randrange(1 << 31)
    imei = hashCode(str(i31))
    msg = struct.pack('!2i2bi', timer, i31, 3, 0, imei)
    key = b'd6fc3a4a06adbde89223bvefedc24fecde188aaa9161'
    data = hmac.new(key, msg, hashlib.sha1).digest()
    msg += struct.pack('!i', hashCode(base64.standard_b64encode(data)))
    return [int(times * 1000), base64.standard_b64encode(msg).decode('utf-8')]




async def cek_vocher(client, uuids, timer):
    headers={
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "id-ID,en-US;q=0.9",
        "cookie": f"utdid={uuids}; hng=ID|id|IDR|360; la_darkmode_type=light",
        "host": "pages.lazada.co.id",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Linux; U; Android 11; zh-CN; Redmi Note 7 Build/RQ3A.211001.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.100 UWS/3.22.1.227 Mobile Safari/537.36 AliApp(LA/7.26.1) UCBS/2.11.1.1 TTID/600000@lazada_android_7.26.1 WindVane/8.5.0 1080X2134",
        "x-app-ver": "7.26.1",
        "x-appkey": "23867946",
        "x-requested-with": "com.lazada.android",
        "x-utdid": uuids
    }
    respon = await client.get(
        url='https://pages.lazada.co.id/wow/gcp/id/ug-newuser/nulp?source=homepage_free_buy&source=homepage_free_buy&item=7447890484,7400654849,7099562384&itemId=7447890484,7400654849,7099562384&price_max=120000.0&price_min=0.0&spm=a211g0.home.combinedNUC.voucher1&laz_event_id=422_1685126965416_75405'
        ,headers=headers
    )
    hasil = respon.text
    soup  = BeautifulSoup(hasil, "html.parser")
    try:
        text  = soup.body.get_text(separator=u' ')
        cek   = text.strip().split('Ambil')[0]
        if re.search(r'Selamat Datang di Lazada Promo Menarik hanya untuk Pengguna Baru!', cek):
            return [uuids, timer, "Selamat Datang di Lazada!"]
        else:
            return [uuids, timer, cek.split('Pengguna Baru')[1].strip().replace(' Khusus', '')]
    except:
        return None


async def running_cek(proxy):
    async with httpx.AsyncClient(proxies=proxy) as client:
        result = await asyncio.gather(
            *[
                asyncio.ensure_future(cek_vocher(
                    client=client, uuids=generateUtdid()[1], timer=generateUtdid()[0]
                ))
                for _ in range(5)
            ]
        )
        return result


async def parse_hasil(con, proxy):
    proxies = {
        'all://': f"http://{proxy}",
    }
    hasil = await running_cek(proxy=proxies)
    for parse in hasil:
        try:
            assert parse == None
            pprint('[bold][+] [yellow][CHAPCTA]')
            DatabaseProxy().delete_data(proxies=proxy)
            break
        except:
            cursor = con.cursor()
            if re.search(r'Ongkir', parse[-1]):
                pprint(f'[bold][+] [green]{parse[0]}[white]::[blue]{parse[1]}[white]::[royal_blue1]{parse[-1]}[white]')
                Database.create_tabel(cursor=cursor, con=con, tabel='ongkir')
                Database.input_data(
                    cursor=cursor,
                    con=con,
                    tabel='ongkir',
                    uuids=parse[0], 
                    timer=parse[1],
                    info=parse[-1]
                )
            elif re.search('45', parse[-1]):
                pprint(f'[bold][+] [green]{parse[0]}[white]::[blue]{parse[1]}[white]::[sea_green2]{parse[-1]}[white]')
                Database.create_tabel(cursor=cursor, con=con,tabel='diskon30')
                Database.input_data(
                    cursor=cursor,
                    con=con,
                    tabel='diskon30',
                    uuids=parse[0], 
                    timer=parse[1],
                    info=parse[-1]
                )
            elif re.search('21', parse[-1]):
                pprint(f'[bold][+] [green]{parse[0]}[white]::[blue]{parse[1]}[white]::[sea_green2]{parse[-1]}[white]')
                Database.create_tabel(cursor=cursor, con=con,tabel='diskon20')
                Database.input_data(
                    cursor=cursor,
                    con=con,
                    tabel='diskon20',
                    uuids=parse[0], 
                    timer=parse[1],
                    info=parse[-1]
                )
            elif re.search('Selamat Datang di Lazada!', parse[-1]):      
                pprint(f'[bold][+] [green]{parse[0]}[white]::[blue]{parse[1]}[white]::[magenta]{parse[-1]}[white]')
            else:
                pprint(f'[bold][+] [green]{parse[0]}[white]::[blue]{parse[1]}[white]::[orange3]{parse[-1]}[white]')
                Database.create_tabel(cursor=cursor, con=con,tabel='kado')
                Database.input_data(
                    cursor=cursor,
                    con=con,
                    tabel='kado',
                    uuids=parse[0], 
                    timer=parse[1],
                    info=parse[-1]
                )


async def run_cek():
    await get_proxy_lazada()
    for i in range(1000000000000):
        proxi_list = DatabaseProxy().print_db()
        proxies = random.choice(proxi_list)[0]
        try:
            waktu = datetime.now().strftime('%d%m%Y')
            with sqlite3.connect(f'{DIR}/data/rdp_tandon_{waktu}.db') as con:
                pprint(f"[bold][+][cyan2] {proxies}")
                await parse_hasil(
                    con=con,
                    proxy=proxies
                )
        except httpx.ConnectError:
            DatabaseProxy().delete_data(proxies=proxies)
            continue
        except:
            pprint(f"[bold][+][cyan2] {proxies}[white]::[red]PROXY ERROR")
            DatabaseProxy().delete_data(proxies=proxies)
            continue


while True:
    try:
        asyncio.run(run_cek())
    except KeyboardInterrupt as e:break
    except:
        pprint('[bold][+] [red][KONEKSI ERROR]')
        continue




