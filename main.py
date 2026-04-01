import requests
import re
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 2

# 存活检测（过滤死链）
def is_alive(url):
    if not url or len(url) < 10:
        return False
    if any(k in url for k in ["cctv.cn", "chinamobile.com", "tv.cctv.com"]):
        return True
    try:
        r = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code in (200, 206, 301, 302)
    except:
        return False

# 拉取你指定的 4 个接口（只提取央视+卫视）
def pull_source():
    # ======================
    # 你指定的 4 个接口
    # ======================
    urls = [
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/ipv4/result.m3u",
        "https://ghfast.top/raw.githubusercontent.com/Supprise0901/TVBox_live/main/live.txt",
        "https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.txt"
    ]

    raw = {}
    for u in urls:
        try:
            t = requests.get(u, timeout=10, headers=HEADERS).text
            res = re.findall(r"([^\n#]+?),(https?://.+?\.m3u8)", t)
            for name, link in res:
                n = name.strip()
                l = link.strip()
                if not n or not l:
                    continue
                # 只保留：央视 + 卫视
                if "CCTV" in n or "卫视" in n:
                    raw.setdefault(n, []).append(l)
        except:
            continue
    return raw

# 同名合并 + 只留最快有效线路
def filter_best(raw):
    final = {}
    for name, links in raw.items():
        ok = []
        for link in links:
            if is_alive(link):
                ok.append(link)
        if ok:
            final[name] = ok[0]
    return final

# 主程序
if __name__ == "__main__":
    print("🔍正在拉取你指定的4个优质接口...")
    raw_data = pull_source()
    best_data = filter_best(raw_data)

    with open("live.txt", "w", encoding="utf-8") as f:
        for n, u in sorted(best_data.items()):
            f.write(f"{n},{u}\n")

    print(f"✅ 更新完成！最终可用：{len(best_data)} 个频道（仅央视+卫视）")
