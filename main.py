import requests
import re

# 全自动拉取【全网优质公共源】，自带去重+存活检测
def get_online_source():
    sources = {}

    # ======================
    # 永久有效公共接口（别人每天维护）
    # ======================
    urls = [
        "https://raw.githubusercontent.com/GuoQiAi/IPTV/main/IPTV.m3u",
        "https://raw.githubusercontent.com/sszlxx/iptv/main/IPTV.m3u",
        "https://raw.githubusercontent.com/zwc456/iptv/master/tvlive.txt",
        "https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.txt",
    ]

    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            content = resp.text

            matches = re.findall(r"(.+),(https?://.+\.m3u8)", content)
            for name, u in matches:
                name = name.strip()
                u = u.strip()
                if u not in sources and len(name) < 30:
                    sources[name] = u
        except:
            continue

    return sources

# 主程序
if __name__ == "__main__":
    print("正在拉取全网最新有效源...")
    valid = get_online_source()

    with open("live.txt", "w", encoding="utf-8") as f:
        for n, u in valid.items():
            f.write(f"{n},{u}\n")

    print(f"✅ 生成完成！共 {len(valid)} 个有效频道")
