import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 采集源地址
SOURCES = [
    "https://wget.la/https://github.com/adminouyang/231006/blob/main/py/卫视/output/ipv4/result.txt",
    "https://wget.la/https://github.com/adminouyang/231006/blob/main/py/TV/output/ipv4/result.txt"
]

# 排序模板：央视+卫视固定顺序
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

# 测速超时配置
TEST_TIMEOUT = 3
MAX_WORKERS = 30

def fetch_text(url):
    """抓取源文本"""
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"抓取失败: {url} | {str(e)}")
        return ""

def parse_channels(text):
    """解析一行 名称,url"""
    channels = []
    pat = re.compile(r"^(.+?),\s*(https?://.+)", re.IGNORECASE)
    for line in text.splitlines():
        line = line.strip()
        m = pat.match(line)
        if m:
            name, uri = m.groups()
            channels.append((name.strip(), uri.strip()))
    return channels

def normalize_name(name):
    """频道标准化统一命名"""
    raw = name.upper().replace(" ", "")
    # CCTV5+特殊识别
    if "CCTV5+" in raw or ("CCTV5" in raw and "+" in raw):
        return "CCTV5+"
    cctv_mat = re.search(r"CCTV[-_]?(\d+)", raw)
    if cctv_mat:
        return f"CCTV{cctv_mat.group(1)}"
    # 卫视匹配
    for ws in WEISHI_ORDER:
        if ws in name:
            return ws
    return None

def check_url_alive(uri):
    """HTTPHEAD测速去死链"""
    try:
        # 优先HEAD
        r = requests.head(uri, timeout=TEST_TIMEOUT, headers=headers, allow_redirects=True)
        if r.status_code in (200, 301, 302, 304):
            return True, uri
    except:
        pass
    # HEAD失败改用GET片段探测
    try:
        r = requests.get(uri, timeout=TEST_TIMEOUT, headers=headers, stream=True)
        for _ in r.iter_content(chunk_size=1024):
            return True, uri
    except:
        return False, uri
    return False, uri

def batch_filter_urls(uri_list):
    """多线程批量测速过滤"""
    valid = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        res = exe.map(check_url_alive, uri_list)
    for ok, u in res:
        if ok:
            valid.append(u)
    return valid

def save_file(content_list, fname):
    """保存文件编码utf8"""
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(content_list))

def main():
    # 1.全量抓取合并
    all_raw = []
    for src in SOURCES:
        print(f"正在抓取源: {src}")
        txt = fetch_text(src)
        chs = parse_channels(txt)
        all_raw.extend(chs)

    # 2.标准化归类
    channel_map = {k:[] for k in ALL_ORDER}
    name_url_dict = {}
    for nm, url in all_raw:
        std_nm = normalize_name(nm)
        if std_nm in channel_map:
            channel_map[std_nm].append(url)

    # 3.测速清洗每个频道链接，剔除死链
    print("开始多线程测速过滤死链...")
    valid_map = {}
    for chn, uris in channel_map.items():
        if not uris:
            valid_map[chn] = []
            continue
        unique_uris = list(dict.fromkeys(uris)) #去重
        ok_uris = batch_filter_urls(unique_uris)
        valid_map[chn] = ok_uris

    # 4.生成标准输出内容
    out_lines = ["灵鹿整合,#genre#"]
    raw_all_lines = ["灵鹿整合,#genre#"]
    for chn in ALL_ORDER:
        # 测速后可用：live.txt
        for vu in valid_map[chn]:
            out_lines.append(f"{chn},{vu}")
        # 原始未测速全量：result.txt
        for ru in channel_map[chn]:
            raw_all_lines.append(f"{chn},{ru}")

    # 5.双文件落地
    save_file(out_lines, "live.txt")
    save_file(raw_all_lines, "result.txt")

    print(f"✅ 处理完成！有效可用源: {len(out_lines)-1} 条")
    print("已生成: live.txt(测速可用) + result.txt(原始全量未测速)")
    print("🔔 可配置GitHub Actions 12小时Cron定时自动爬取更新")

if __name__ == "__main__":
    main()
