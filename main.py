import requests
import os
import time

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win10; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

# ==============================================
# 🔴 自动检测链接是否能播放（失效直接丢掉）
# ==============================================
def is_alive(url):
    if not url:
        return False
    try:
        res = requests.get(
            url,
            headers=HEADERS,
            timeout=3,
            stream=True,
            allow_redirects=True
        )
        return res.status_code in (200, 206, 301, 302)
    except:
        return False

# ==============================================
# 全央视 + 全卫视（已填好）
# ==============================================
def get_iptv_full():
    return {
        # === 央视全频道 ===
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

        # === 全国卫视 ===
        "湖南卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226001/1/index.m3u8",
        "浙江卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226005/1/index.m3u8",
        "江苏卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226006/1/index.m3u8",
        "东方卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226010/1/index.m3u8",
        "北京卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226008/1/index.m3u8",
        "广东卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226015/1/index.m3u8",
        "深圳卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226020/1/index.m3u8",
        "山东卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226011/1/index.m3u8",
        "河南卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226012/1/index.m3u8",
        "安徽卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226009/1/index.m3u8",
        "湖北卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226016/1/index.m3u8",
        "四川卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226018/1/index.m3u8",
        "重庆卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226017/1/index.m3u8",
        "天津卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226013/1/index.m3u8",
        "河北卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226014/1/index.m3u8",
        "辽宁卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226019/1/index.m3u8",
        "江西卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226021/1/index.m3u8",
        "贵州卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226022/1/index.m3u8",
        "山西卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226023/1/index.m3u8",
        "陕西卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226024/1/index.m3u8",
        "广西卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226025/1/index.m3u8",
        "福建东南卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226033/1/index.m3u8",
        "云南卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226034/1/index.m3u8",
        "海南卫视": "https://dbiptv.sn.chinamobile.com/PLTV/88888888/224/3221226035/1/index.m3u8",
    }

# ==============================================
# 主程序：去重 + 失效检测 + 只保留有效源
# ==============================================
if __name__ == "__main__":
    print("🔍 开始检测所有频道...")

    # 加载所有源
    sources = get_iptv_full()

    # 去重 + 存活检测
    valid = {}
    seen_urls = set()

    for name, url in sources.items():
        if url and url not in seen_urls:
            if is_alive(url):
                seen_urls.add(url)
                valid[name] = url
                print(f"✅ {name}")
            else:
                print(f"❌ {name} (失效，已丢弃)")

    # 写入最终纯净源
    with open("live.txt", "w", encoding="utf-8") as f:
        for n, u in valid.items():
            f.write(f"{n},{u}\n")

    print(f"\n🎉 完成！最终有效源：{len(valid)} 个")
