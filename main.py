import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 你的两个数据源
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

def fetch(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.text
    except:
        return ""

def parse(text):
    lines = text.splitlines()
    res = []
    pat = re.compile(r"(.+?),(https?://.+)")
    for line in lines:
        line = line.strip()
        m = pat.match(line)
        if m:
            n, u = m.groups()
            res.append((n.strip(), u.strip()))
    return res

def clean(name):
    u = name.upper().replace(" ", "")
    if "CCTV" in u:
        num = re.search(r"(\d+)", u)
        if num:
            n = num.group(1)
            if n == "5" and "5+" in u:
                return "CCTV5+"
            return f"CCTV{n}"
    for ws in WEISHI_ORDER:
        if ws in name:
            return ws
    return None

def main():
    all = []
    for url in SOURCES:
        all.extend(parse(fetch(url)))

    channel_map = {k: [] for k in ALL_ORDER}
    for n, u in all:
        k = clean(n)
        if k in channel_map:
            channel_map[k].append(u)

    out = ["灵鹿整合,#genre#"]
    for key in ALL_ORDER:
        for uri in channel_map[key]:
            out.append(f"{key},{uri}")

    # 重点：文件名必须是 txt
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    main()
