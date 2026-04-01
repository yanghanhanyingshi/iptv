import requests
import re
import json
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0.0.0 Safari/537.36"
}

# 存活检测（宽松版，避免误判）
def is_url_alive(url):
    if not url:
        return False
    try:
        res = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
        return 200 <= res.status_code < 400
    except:
        try:
            res = requests.get(url, headers=HEADERS, timeout=5, stream=True)
            return 200 <= res.status_code < 400
        except:
            return False

# B站
def get_bilibili(rid):
    try:
        r1 = requests.get(f"https://api.live.bilibili.com/room/v1/Room/room_init?id={rid}", headers=HEADERS, timeout=10).json()
        if r1["code"] != 0:
            return None
        cid = r1["data"]["room_id"]
        r2 = requests.get(f"https://api.live.bilibili.com/xlive/web-room/v1/playUrl?cid={cid}&quality=0", headers=HEADERS, timeout=10).json()
        return r2["data"]["durl"][0]["url"]
    except Exception as e:
        print(f"B站采集失败: {e}")
        return None

# 虎牙
def get_huya(rid):
    try:
        t = requests.get(f"https://m.huya.com/{rid}", headers=HEADERS, timeout=10).text
        m = re.search(r'"hlsUrl":"(https[^"]+)"', t)
        return m.group(1).replace("\\/", "/") if m else None
    except Exception as e:
        print(f"虎牙采集失败: {e}")
        return None

# 斗鱼
def get_douyu(rid):
    try:
        t = requests.get(f"https://m.douyu.com/{rid}", headers=HEADERS, timeout=10).text
        js = re.search(r'window\.$PAGE_DATA\s*=\s*(\{.+?\})<', t)
        if not js:
            return None
        d = json.loads(js.group(1))
        return d.get("roomInfo", {}).get("videoLoop", {}).get("hls_url")
    except Exception as e:
        print(f"斗鱼采集失败: {e}")
        return None

# IPTV 稳定源
def get_iptv():
    return {
        "CCTV1综合": "https://live.cctvcdn.cctv.cn/hls/cc-tv1-cctv1/index.m3u8",
        "CCTV5体育": "https://live.cctvcdn.cctv.cn/hls/cc-tv5-cctv5/index.m3u8",
        "CCTV13新闻": "https://live.cctvcdn.cctv.cn/hls/cc-tv13-cctv13/index.m3u8",
        "湖南卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226001/1/index.m3u8",
        "浙江卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226005/1/index.m3u8"
    }

# ==========================
# 主程序（强制生成文件版）
# ==========================
if __name__ == "__main__":
    print("=== 开始采集直播源 ===")
    src = {}

    # 稳定可运行的平台
    src["B站-官方"] = get_bilibili("6")
    src["虎牙-官方"] = get_huya("660000")
    src["斗鱼-官方"] = get_douyu("5552093")

    # IPTV
    src.update(get_iptv())

    # 去重 + 存活检测
    valid = {}
    seen = set()
    for name, url in src.items():
        if url and url not in seen:
            if is_url_alive(url):
                seen.add(url)
                valid[name] = url
                print(f"✅ 有效源: {name} -> {url[:50]}...")
            else:
                print(f"❌ 失效源: {name} -> {url[:50]}...")

    # 强制生成 live.txt（即使0个有效源也生成空文件，避免找不到）
    print(f"\n=== 开始写入 live.txt，有效源数量: {len(valid)} ===")
    with open("live.txt", "w", encoding="utf-8") as f:
        for n, u in valid.items():
            f.write(f"{n},{u}\n")
    
    # 验证文件是否生成
    if os.path.exists("live.txt"):
        print(f"✅ live.txt 生成成功！文件大小: {os.path.getsize('live.txt')} 字节")
        # 打印文件内容
        print("\n=== live.txt 内容 ===")
        with open("live.txt", "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("❌ 错误：live.txt 生成失败！")
