import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

SOURCES = [
    "https://wget.la/https://github.com/adminouyang/231006/blob/main/py/卫视/output/ipv4/result.txt",
    "https://wget.la/https://github.com/adminouyang/231006/blob/main/py/TV/output/ipv4/result.txt"
]

CCTV_ORDER = [
    "CCTV1", "CCTV2", "CCTV3", "CCTV4", "CCTV5", "CCTV5+", "CCTV6", "CCTV7",
    "CCTV8", "CCTV9", "CCTV10", "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15", "CCTV17"
]

WEISHI_ORDER = [
    "北京卫视", "天津卫视", "河北卫视", "山西卫视", "内蒙古卫视",
    "辽宁卫视", "吉林卫视", "黑龙江卫视", "东方卫视", "江苏卫视",
    "浙江卫视", "安徽卫视", "福建卫视", "江西卫视", "山东卫视",
    "河南卫视", "湖北卫视", "湖南卫视", "广东卫视", "广西卫视",
    "重庆卫视", "四川卫视", "贵州卫视", "云南卫视", "陕西卫视",
    "甘肃卫视", "青海卫视", "宁夏卫视", "新疆卫视", "旅游卫视"
]

ALL_ORDER = CCTV_ORDER + WEISHI_ORDER

def fetch_text(url):
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"抓取失败 {url}: {e}")
        return ""

def parse_channels(text):
    lines = text.splitlines()
    channels = []
    pat = re.compile(r"^(.+?),\s*(https?://.+)", re.IGNORECASE)
    for line in lines:
        line = line.strip()
        m = pat.match(line)
        if m:
            name, uri = m.groups()
            channels.append((name.strip(), uri.strip()))
    return channels

def normalize_name(name):
    s = name.upper().replace(" ", "")
    if re.search(r"CCTV[-]?\d+", s):
        num = re.search(r"(\d+)", s).group(1)
        if num == "5" and ("5+" in s):
            return "CCTV5+"
        return f"CCTV{num}"
    for ws in WEISHI_ORDER:
        if ws in name:
            return ws
    return None

def main():
    all_links = []
    for url in SOURCES:
        print(f"抓取: {url}")
        txt = fetch_text(url)
        chs = parse_channels(txt)
        all_links.extend(chs)

    channel_map = {k: [] for k in ALL_ORDER}
    for name, uri in all_links:
        key = normalize_name(name)
        if key in channel_map:
            channel_map[key].append(uri)

    out = ["灵鹿整合,#genre#"]
    for key in ALL_ORDER:
        for uri in channel_map[key]:
            out.append(f"{key},{uri}")

    with open("result.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    print(f"完成，共 {len(out)-1} 条源 → result.txt")

if __name__ == "__main__":
    main()

