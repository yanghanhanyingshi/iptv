import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# 采集源
SOURCES = [
    "https://wget.la/https://github.com/adminouyang/231006/blob/main/py/卫视/output/ipv4/result.txt",
    "https://wget.la/https://github.com/adminouyang/231006/blob/main/py/TV/output/ipv4/result.txt"
]

# 固定排序顺序
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

# 抓取文本
def get_raw(url):
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.text
    except:
        return ""

# 解析频道
def parse_channels(text):
    lines = text.splitlines()
    res = []
    pat = re.compile(r'(.+?),(https?://.+)', re.I)
    for line in lines:
        line = line.strip()
        m = pat.match(line)
        if m:
            name, uri = m.groups()
            res.append((name.strip(), uri.strip()))
    return res

# 核心：统一格式为 CCTV1、CCTV2...
def normalize_channel_name(name):
    s = name.lower()
    # 去掉所有中文、空格、符号
    s = re.sub(r'[^\w\s]', '', s)
    s = re.sub(r'\s+', '', s)
    # 匹配 cctv数字
    match = re.search(r'cctv(\d+)', s)
    if match:
        num = match.group(1)
        if num == '5':
            # 判断CCTV5+
            if '5+' in name or '5plus' in s:
                return 'CCTV5+'
        return f'CCTV{num}'
    # 卫视原样返回
    for ws in WEISHI_ORDER:
        if ws in name:
            return ws
    return name

# 匹配排序key
def match_key(name):
    cn = normalize_channel_name(name)
    for key in ALL_ORDER:
        if key == cn:
            return key
    return None

def main():
    all_raw = []
    for url in SOURCES:
        print(f"抓取：{url}")
        txt = get_raw(url)
        chs = parse_channels(txt)
        all_raw.extend(chs)

    # 按频道分组
    channel_map = {key: [] for key in ALL_ORDER}
    for name, uri in all_raw:
        key = match_key(name)
        if key:
            channel_map[key].append(uri)

    # 构造输出
    out_lines = ["灵鹿整合,#genre#"]
    for key in ALL_ORDER:
        for uri in channel_map[key]:
            out_lines.append(f"{key},{uri}")

    final = "\n".join(out_lines)
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(final)

    print("生成完成：result.txt")
    print(f"总计有效线路：{len(out_lines)-1} 条")

if __name__ == '__main__':
    main()
