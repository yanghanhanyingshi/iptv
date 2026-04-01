import requests
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 采集源
SOURCES = [
    "https://wget.la/https://github.com/adminouyang/231006/blob/main/py/卫视/output/ipv4/result.txt",
    "https://wget.la/https://github.com/adminouyang/231006/blob/main/py/TV/output/ipv4/result.txt"
]

# 频道顺序
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

# 抓取页面
def fetch_text(url):
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"抓取失败: {url} | {e}")
        return ""

# 解析频道行
def parse_channels(text):
    lines = text.splitlines()
    channels = []
    pat = re.compile(r"^(.+?),\s*(https?://.+)", re.IGNORECASE)
    for line in lines:
        line = line.strip()
        match = pat.match(line)
        if match:
            name, uri = match.groups()
            channels.append((name.strip(), uri.strip()))
    return channels

# 统一频道名称
def normalize_name(name):
    u = name.upper().replace(" ", "")
    # 处理 CCTV
    if re.search(r"CCTV[- ]?\d+", u):
        num = re.search(r"(\d+)", u).group(1)
        if num == "5" and ("5+" in u or "5PLUS" in u):
            return "CCTV5+"
        return f"CCTV{num}"
    # 卫视匹配
    for ws in WEISHI_ORDER:
        if ws in name:
            return ws
    return None

# 主程序
def main():
    all_links = []
    for url in SOURCES:
        print(f"正在抓取：{url}")
        txt = fetch_text(url)
        chs = parse_channels(txt)
        all_links.extend(chs)

    # 按频道归类
    channel_map = {key: [] for key in ALL_ORDER}
    for name, uri in all_links:
        key = normalize_name(name)
        if key in channel_map:
            channel_map[key].append(uri)

    # 构造输出
    out = ["灵鹿整合,#genre#"]
    for key in ALL_ORDER:
        for uri in channel_map[key]:
            out.append(f"{key},{uri}")

    # 写入文件
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    print(f"完成！共 {len(out)-1} 条源，已保存为 result.txt")

if __name__ == "__main__":
    main()
