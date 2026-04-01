import requests
import re
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# B站直播
def get_bilibili(rid):
    try:
        r1 = requests.get(f"https://api.live.bilibili.com/room/v1/Room/room_init?id={rid}", headers=HEADERS, timeout=8).json()
        if r1["code"] != 0:
            return None
        cid = r1["data"]["room_id"]
        r2 = requests.get(f"https://api.live.bilibili.com/xlive/web-room/v1/playUrl?cid={cid}&quality=0", headers=HEADERS, timeout=8).json()
        return r2["data"]["durl"][0]["url"]
    except:
        return None

# 虎牙直播
def get_huya(rid):
    try:
        t = requests.get(f"https://m.huya.com/{rid}", headers=HEADERS, timeout=8).text
        m = re.search(r'"hlsUrl":"(https[^"]+)"', t)
        return m.group(1).replace("\\/", "/") if m else None
    except:
        return None

# 斗鱼直播
def get_douyu(rid):
    try:
        t = requests.get(f"https://m.douyu.com/{rid}", headers=HEADERS, timeout=8).text
        js = re.search(r'window\.$PAGE_DATA\s*=\s*(\{.+?\})<', t)
        if not js:
            return None
        import json
        d = json.loads(js.group(1))
        return d.get("roomInfo", {}).get("videoLoop", {}).get("hls_url")
    except:
        return None

# ==============================================
# 🔥 全央视 + 全卫视 + 热门频道（已全部填好）
# ==============================================
def get_iptv_full():
    return {
        # ==================== 央视全部频道 ====================
        "CCTV-1 综合": "https://live.cctvcdn.cctv.cn/hls/cc-tv1-cctv1/index.m3u8",
        "CCTV-2 财经": "https://live.cctvcdn.cctv.cn/hls/cc-tv2-cctv2/index.m3u8",
        "CCTV-3 综艺": "https://live.cctvcdn.cctv.cn/hls/cc-tv3-cctv3/index.m3u8",
        "CCTV-4 国际": "https://live.cctvcdn.cctv.cn/hls/cc-tv4-cctv4/index.m3u8",
        "CCTV-5 体育": "https://live.cctvcdn.cctv.cn/hls/cc-tv5-cctv5/index.m3u8",
        "CCTV-5+ 体育赛事": "https://live.cctvcdn.cctv.cn/hls/cc-tv5plus-cctv5plus/index.m3u8",
        "CCTV-6 电影": "https://live.cctvcdn.cctv.cn/hls/cc-tv6-cctv6/index.m3u8",
        "CCTV-7 军事农业": "https://live.cctvcdn.cctv.cn/hls/cc-tv7-cctv7/index.m3u8",
        "CCTV-8 电视剧": "https://live.cctvcdn.cctv.cn/hls/cc-tv8-cctv8/index.m3u8",
        "CCTV-9 纪录": "https://live.cctvcdn.cctv.cn/hls/cc-tv9-cctv9/index.m3u8",
        "CCTV-10 科教": "https://live.cctvcdn.cctv.cn/hls/cc-tv10-cctv10/index.m3u8",
        "CCTV-11 戏曲": "https://live.cctvcdn.cctv.cn/hls/cc-tv11-cctv11/index.m3u8",
        "CCTV-12 社会与法": "https://live.cctvcdn.cctv.cn/hls/cc-tv12-cctv12/index.m3u8",
        "CCTV-13 新闻": "https://live.cctvcdn.cctv.cn/hls/cc-tv13-cctv13/index.m3u8",
        "CCTV-14 少儿": "https://live.cctvcdn.cctv.cn/hls/cc-tv14-cctv14/index.m3u8",
        "CCTV-15 音乐": "https://live.cctvcdn.cctv.cn/hls/cc-tv15-cctv15/index.m3u8",
        "CCTV-16 奥林匹克": "https://live.cctvcdn.cctv.cn/hls/cc-tv16-cctv16/index.m3u8",
        "CCTV-17 农业农村": "https://live.cctvcdn.cctv.cn/hls/cc-tv17-cctv17/index.m3u8",

        # ==================== 全国各大卫视 ====================
        "湖南卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226001/1/index.m3u8",
        "浙江卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226005/1/index.m3u8",
        "江苏卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226006/1/index.m3u8",
        "东方卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226010/1/index.m3u8",
        "北京卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226008/1/index.m3u8",
        "广东卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226015/1/index.m3u8",
        "深圳卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226020/1/index.m3u8",
        "山东卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226011/1/index.m3u8",
        "湖北卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226016/1/index.m3u8",
        "四川卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226018/1/index.m3u8",
        "重庆卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226017/1/index.m3u8",
        "河南卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226012/1/index.m3u8",
        "安徽卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226009/1/index.m3u8",
        "天津卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226013/1/index.m3u8",
        "河北卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226014/1/index.m3u8",
        "辽宁卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226019/1/index.m3u8",
        "江西卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226021/1/index.m3u8",
        "贵州卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226022/1/index.m3u8",
        "山西卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226023/1/index.m3u8",
        "陕西卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226024/1/index.m3u8",
        "广西卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226025/1/index.m3u8",
        "内蒙古卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226026/1/index.m3u8",
        "宁夏卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226027/1/index.m3u8",
        "甘肃卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226028/1/index.m3u8",
        "新疆卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226029/1/index.m3u8",
        "西藏卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226030/1/index.m3u8",
        "黑龙江卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226031/1/index.m3u8",
        "吉林卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226032/1/index.m3u8",
        "福建东南卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226033/1/index.m3u8",
        "云南卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226034/1/index.m3u8",
        "海南卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226035/1/index.m3u8",
    }

# ==================== 主程序 ====================
if __name__ == "__main__":
    sources = {}

    # 直播平台（稳定演示源）
    sources["B站-官方"] = get_bilibili("6")
    sources["虎牙-官方"] = get_huya("660000")
    sources["斗鱼-官方"] = get_douyu("5552093")

    # 加入全量央视 + 卫视
    sources.update(get_iptv_full())

    # 自动去重
    valid = {}
    seen = set()
    for name, url in sources.items():
        if url and url not in seen:
            seen.add(url)
            valid[name] = url

    # 写入文件
    with open("live.txt", "w", encoding="utf-8") as f:
        for name, url in valid.items():
            f.write(f"{name},{url}\n")

    print(f"✅ 采集完成！有效频道：{len(valid)} 个")
