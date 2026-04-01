import requests
import re
import time

# ======================
# 配置
# ======================
HEADERS = {"User-Agent": "Mozilla/5.0"}
URL_TIMEOUT = 5
LINK_TIMEOUT = 1.5
GROUP_HEADER = "灵鹿整合,#genre#"

# 测速：返回耗时，越小越快
def test_speed(url):
    try:
        st = time.time()
        requests.head(url, timeout=LINK_TIMEOUT, headers=HEADERS)
        return time.time() - st
    except:
        return 999

# 拉取4个源
def fetch_all():
    sources = [
        "https://gh-proxy.org/https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1.m3u",
        "https://www.iyouhun.com/tv/zb",
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
        "https://ghfast.top/raw.githubusercontent.com/Supprise0901/TVBox_live/main/live.txt"
    ]

    items = {}
    for url in sources:
        try:
            r = requests.get(url, timeout=URL_TIMEOUT, headers=HEADERS)
            r.encoding = "utf-8"
            txt = r.text

            pairs = []
            # txt 格式
            pairs += re.findall(r"([^,#\n]+?)\s*,\s*(https?://\S+\.m3u8)", txt)
            # m3u 格式
            names = re.findall(r"#EXTINF:-1.*?,(.+)\n", txt)
            urls  = re.findall(r"(https?://\S+\.m3u8)", txt)
            for n, u in zip(names, urls):
                pairs.append((n.strip(), u.strip()))

            for name, link in pairs:
                name = name.strip()
                link = link.strip()
                if not name or not link:
                    continue
                if "CCTV" in name or "卫视" in name:
                    # 统一央视名称
                    m = re.search(r"CCTV[ -]*0*(\d+)", name)
                    if m:
                        name = f"CCTV-{m.group(1)}"
                    if name not in items:
                        items[name] = set()
                    items[name].add(link)
        except:
            continue
    return items

# 测速排序 + 只保留快的
def sort_by_speed(items):
    result = {}
    for name, urls in items.items():
        ranked = []
        for u in urls:
            t = test_speed(u)
            if t < 999:
                ranked.append((t, u))
        # 越快越靠前
        ranked.sort(key=lambda x: x[0])
        result[name] = [u for t, u in ranked]
    return result

# 频道排序：CCTV1→2→3…
def sort_channels(channel_links):
    cctv = {}
    wei = {}
    for k, v in channel_links.items():
        if k.startswith("CCTV-"):
            cctv[k] = v
        else:
            wei[k] = v

    def cctv_key(s):
        g = re.search(r"CCTV-(\d+)", s)
        return int(g.group(1)) if g else 999

    cctv_sorted = sorted(cctv.items(), key=cctv_key)
    wei_sorted = sorted(wei.items())
    return dict(cctv_sorted + wei_sorted)

# 主程序
if __name__ == "__main__":
    data = fetch_all()
    ranked = sort_by_speed(data)
    sorted_ch = sort_channels(ranked)

    with open("live.txt", "w", encoding="utf-8") as f:
        f.write(f"{GROUP_HEADER}\n")
        for name, links in sorted_ch.items():
            for url in links:
                f.write(f"{name},{url}\n")

    print("✅ 完成：去重 + 测速排序")
