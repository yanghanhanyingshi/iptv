import requests
import re
import time

# 暴力超时配置（GitHub环境专用）
HEADERS = {"User-Agent": "Mozilla/5.0"}
# 单个接口最多等3秒，超时直接扔
URL_TIMEOUT = 3
# 链接检测最多等1秒
CHECK_TIMEOUT = 1

# 1. 极简存活检测（只看状态，不耗资源）
def check_link(url):
    if not url or len(url) < 10:
        return False
    # 央视/移动源直接过，不检测
    if "cctv.cn" in url or "chinamobile.com" in url:
        return True
    try:
        # 用GET只取前100字节，最快
        r = requests.get(url, timeout=CHECK_TIMEOUT, headers=HEADERS, stream=True)
        r.raw.read(100)  # 只读一点点，确认能连
        return r.status_code < 400
    except:
        return False

# 2. 单线程拉取（逐个来，不卡线程）
def get_sources():
    # 你指定的4个接口
    urls = [
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/ipv4/result.m3u",
        "https://ghfast.top/raw.githubusercontent.com/Supprise0901/TVBox_live/main/live.txt",
        "https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.txt"
    ]
    
    all_data = {}
    for idx, url in enumerate(urls):
        try:
            print(f"📥 拉取接口 {idx+1}/4: {url}")
            # 3秒超时，超时直接跳过这个接口
            resp = requests.get(url, timeout=URL_TIMEOUT, headers=HEADERS)
            resp.encoding = "utf-8"
            # 匹配 频道名,链接
            lines = re.findall(r"([^\n#]+?),(https?://.+?\.m3u8)", resp.text)
            for name, link in lines:
                n = name.strip()
                l = link.strip()
                # 只留央视+卫视
                if n and l and ("CCTV" in n or "卫视" in n):
                    if n not in all_data:
                        all_data[n] = []
                    all_data[n].append(l)
        except:
            print(f"❌ 接口 {idx+1}/4 超时/失败，跳过")
            continue
    return all_data

# 3. 极简去重+选最快
def filter_sources(raw):
    final = {}
    for name, links in raw.items():
        # 去重
        unique_links = list(set(links))
        # 找第一个能用的
        for link in unique_links:
            if check_link(link):
                final[name] = link
                break
    return final

# 主程序（极简，无多余逻辑）
if __name__ == "__main__":
    start = time.time()
    print("🔍 开始拉取（极简模式，10秒必完）...")
    
    # 拉取源
    raw = get_sources()
    # 过滤有效源
    valid = filter_sources(raw)
    
    # 写入文件
    with open("live.txt", "w", encoding="utf-8") as f:
        for name, url in sorted(valid.items()):
            f.write(f"{name},{url}\n")
    
    # 输出结果
    cost = round(time.time() - start, 2)
    print(f"✅ 完成！耗时 {cost} 秒 | 有效频道：{len(valid)} 个")
