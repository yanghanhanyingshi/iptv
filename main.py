import requests
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 1.5
GROUP_HEADER = "灵鹿整合,#genre#"

def is_ok(url):
    try:
        requests.head(url, timeout=TIMEOUT, headers=HEADERS)
        return True
    except:
        return False

def fetch():
    urls = [
        "https://gh-proxy.org/https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1.m3u",
        "https://www.iyouhun.com/tv/zb",
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
        "https://ghfast.top/raw.githubusercontent.com/Supprise0901/TVBox_live/live.txt"
    ]

    channels = {}
    for u in urls:
        try:
            resp = requests.get(u, timeout=TIMEOUT, headers=HEADERS)
            resp.encoding = "utf-8"
            txt = resp.text

            pairs = re.findall(r"([^,#\n]+?)\s*,\s*(https?://\S+?m3u8)", txt)
            names = re.findall(r"#EXTINF:-1.*?,(.+)\n", txt)
            links = re.findall(r"(https?://\S+?m3u8)", txt)
            for n, l in zip(names, links):
                pairs.append((n.strip(), l.strip()))

            for name, link in pairs:
                name = name.strip()
                if "CCTV" in name or "卫视" in name:
                    mt = re.search(r"CCTV[ -]*0*(\d+)", name)
                    if mt:
                        name = f"CCTV-{mt.group(1)}"
                    if name not in channels:
                        channels[name] = set()
                    channels[name].add(link)
        except:
            continue
    return channels

def sort_channels(channels):
    cctv, wei = {}, {}
    for k, v in channels.items():
        if k.startswith("CCTV-"):
            cctv[k] = v
        else:
            wei[k] = v

    def ckey(s):
        g = re.search(r"CCTV-(\d+)", s)
        return int(g.group(1)) if g else 999

    return dict(sorted(cctv.items(), key=ckey) + sorted(wei.items()))

if __name__ == "__main__":
    data = fetch()
    filtered = {k: [u for u in v if is_ok(u)] for k, v in data.items()}
    sorted_data = sort_channels(filtered)

    with open("live.txt", "w", encoding="utf-8") as f:
        f.write(f"{GROUP_HEADER}\n")
        for name, links in sorted_data.items():
            for l in links:
                f.write(f"{name},{l}\n")

    print("✅ 完成轻度检测")
