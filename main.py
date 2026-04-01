import requests
import re
import time

# ======================
# 核心配置（防卡死+极速）
# ======================
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
URL_TIMEOUT = 3  # 单个接口最多等3秒，超时直接跳过
CHECK_TIMEOUT = 1  # 链接检测最多等1秒

# ======================
# 1. 存活检测（过滤死链）
# ======================
def check_link(url):
    if not url or len(url) < 10:
        return False
    # 央视/移动官方源直接放行，不检测
    if "cctv.cn" in url or "chinamobile.com" in url:
        return True
    try:
        # 极简请求：只取前100字节，确认能连接
        resp = requests.get(
            url,
            timeout=CHECK_TIMEOUT,
            headers=HEADERS,
            stream=True,  # 不加载完整文件
            allow_redirects=True
        )
        resp.raw.read(100)  # 只读少量数据，极速判断
        return resp.status_code < 400
    except:
        return False

# ======================
# 2. 拉取指定的4个接口
# ======================
def pull_sources():
    # 你指定的4个核心接口
    target_urls = [
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/ipv4/result.m3u",
        "https://ghfast.top/raw.githubusercontent.com/Supprise0901/TVBox_live/main/live.txt",
        "https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.txt"
    ]
    
    raw_data = {}  # 格式：{频道名: [链接1, 链接2...]}
    for idx, url in enumerate(target_urls, 1):
        try:
            print(f"📥 正在拉取接口 {idx}/4: {url}")
            # 3秒超时保护，超时直接跳过
            resp = requests.get(url, timeout=URL_TIMEOUT, headers=HEADERS)
            resp.encoding = "utf-8"
            # 匹配「频道名,链接」格式
            matches = re.findall(r"([^\n#]+?),(https?://.+?\.m3u8)", resp.text)
            # 只保留央视+卫视
            for name, link in matches:
                clean_name = name.strip()
                clean_link = link.strip()
                if clean_name and clean_link and ("CCTV" in clean_name or "卫视" in clean_name):
                    if clean_name not in raw_data:
                        raw_data[clean_name] = []
                    raw_data[clean_name].append(clean_link)
        except:
            print(f"❌ 接口 {idx}/4 超时/失败，跳过")
            continue
    return raw_data

# ======================
# 3. 去重+合并+选最快线路
# ======================
def filter_best_sources(raw):
    final_data = {}
    for name, links in raw.items():
        # 第一步：去重链接
        unique_links = list(set(links))
        # 第二步：找第一个能用的链接（最快）
        for link in unique_links:
            if check_link(link):
                final_data[name] = link
                break
    return final_data

# ======================
# 4. 自定义排序（核心：央视按数字，卫视按拼音）
# ======================
def custom_sort(channels):
    # 第一步：分离央视和卫视
    cctv_channels = {}
    satellite_channels = {}
    for name, url in channels.items():
        if "CCTV" in name:
            cctv_channels[name] = url
        else:
            satellite_channels[name] = url
    
    # 第二步：央视按数字排序（CCTV1→CCTV2→CCTV3...）
    def cctv_sort_key(name):
        # 提取CCTV后面的数字（处理 "CCTV-1" "CCTV1" "CCTV 1" 等格式）
        num_match = re.search(r'CCTV[ -]*(\d+)', name)
        if num_match:
            return int(num_match.group(1))
        return 99  # 非数字央视（如CCTV高清）放最后
    
    sorted_cctv = dict(sorted(cctv_channels.items(), key=lambda x: cctv_sort_key(x[0])))
    
    # 第三步：卫视按名称拼音排序（整齐不乱）
    sorted_satellite = dict(sorted(satellite_channels.items()))
    
    # 第四步：合并（央视在前，卫视在后）
    sorted_all = {}
    sorted_all.update(sorted_cctv)
    sorted_all.update(sorted_satellite)
    
    return sorted_all

# ======================
# 主程序（极简，无冗余）
# ======================
if __name__ == "__main__":
    start_time = time.time()
    print("🔍 开始拉取直播源（防卡死+有序排序）...")
    
    # 拉取原始数据
    raw_sources = pull_sources()
    # 过滤有效源
    valid_sources = filter_best_sources(raw_sources)
    # 自定义排序（央视按数字，卫视按拼音）
    sorted_sources = custom_sort(valid_sources)
    
    # 写入live.txt（UTF-8编码，避免乱码）
    with open("live.txt", "w", encoding="utf-8") as f:
        # 按自定义顺序写入
        for name, url in sorted_sources.items():
            f.write(f"{name},{url}\n")
    
    # 输出结果，确认完成
    cost_time = round(time.time() - start_time, 2)
    print(f"✅ 全部完成！")
    print(f"⏱️  总耗时：{cost_time} 秒")
    print(f"📺 有效频道数：{len(sorted_sources)} 个（央视+卫视，已排序）")
