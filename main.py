import requests
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0.0.0 Safari/537.36"
}

# 存活检测（过滤失效链接）
def is_url_alive(url):
    if not url:
        return False
    try:
        res = requests.head(url, headers=HEADERS, timeout=4, allow_redirects=True)
        return res.status_code in (200, 301, 302)
    except:
        try:
            res = requests.get(url, headers=HEADERS, timeout=3, stream=True)
            return res.status_code in (200, 301, 302)
        except:
            return False

# B站
def get_bilibili(rid):
    try:
        r1 = requests.get(f"https://api.live.bilibili.com/room/v1/Room/room_init?id={rid}", headers=HEADERS).json()
        if r1["code"] != 0:return None
        cid = r1["data"]["room_id"]
        r2 = requests.get(f"https://api.live.bilibili.com/xlive/web-room/v1/playUrl?cid={cid}&quality=0", headers=HEADERS).json()
        return r2["data"]["durl"][0]["url"]
    except:return None

# 虎牙
def get_huya(rid):
    try:
        t = requests.get(f"https://m.huya.com/{rid}", headers=HEADERS).text
        m = re.search(r'"hlsUrl":"(https[^"]+)"',t)
        return m.group(1).replace("\\/","/") if m else None
    except:return None

# 斗鱼
def get_douyu(rid):
    try:
        t = requests.get(f"https://m.douyu.com/{rid}", headers=HEADERS).text
        js = re.search(r'window\.$PAGE_DATA\s*=\s*(\{.+?\})<',t)
        if not js:return None
        d = json.loads(js.group(1))
        return d.get("roomInfo",{}).get("videoLoop",{}).get("hls_url")
    except:return None

# 抖音简易公开流
def get_douyin(rid):
    try:
        t = requests.get(f"https://live.douyin.com/{rid}", headers=HEADERS).text
        m = re.search(r'"hls_pull_url":"(https[^"]+)"',t)
        return m.group(1).replace("\\u002F","/") if m else None
    except:return None

# 快手简易流
def get_kuaishou(fid):
    try:
        t = requests.get(f"https://v.kuaishou.com/{fid}", headers=HEADERS, allow_redirects=True).text
        m = re.search(r'"playUrl":"(https.+?\.m3u8)"',t)
        return m.group(1).replace("\\/","/") if m else None
    except:return None

# 央视卫视IPTV固定源
def get_iptv():
    return {
        "CCTV1综合":"https://live.cctvcdn.cctv.cn/hls/cc-tv1-cctv1/index.m3u8",
        "CCTV4中文国际":"https://live.cctvcdn.cctv.cn/hls/cc-tv4-cctv4/index.m3u8",
        "CCTV5体育":"https://live.cctvcdn.cctv.cn/hls/cc-tv5-cctv5/index.m3u8",
        "CCTV13新闻":"https://live.cctvcdn.cctv.cn/hls/cc-tv13-cctv13/index.m3u8",
        "湖南卫视":"https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226001/1/index.m3u8",
        "浙江卫视":"https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226005/1/index.m3u8"
    }

if __name__ == "__main__":
    src = {}

    # 自定义直播间（后续你改这里就行）
    src["B站-官方区"] = get_bilibili("6")
    src["虎牙-官方"] = get_huya("660000")
    src["斗鱼-主推"] = get_douyu("5552093")
    src["抖音-测试"] = get_douyin("")     # 填你的抖音房间号
    src["快手-测试"] = get_kuaishou("")   # 填你的快手短链ID

    # 加入IPTV
    src.update(get_iptv())

    # 去重 + 存活过滤
    valid = {}
    dup = set()
    for name,url in src.items():
        if url and url not in dup:
            if is_url_alive(url):
                dup.add(url)
                valid[name] = url

    # 写出live.txt
    with open("live.txt","w",encoding="utf-8") as f:
        for n,u in valid.items():
            f.write(f"{n},{u}\n")

    print(f"完成！有效源数量：{len(valid)}")
