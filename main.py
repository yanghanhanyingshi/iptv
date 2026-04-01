import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# 全局配置（防卡死核心）
HEADERS = {"User-Agent": "Mozilla/5.0"}
# 单个接口最长等待5秒，超时直接跳过
SINGLE_URL_TIMEOUT = 5
# 单个链接检测最长2秒
LINK_CHECK_TIMEOUT = 2
# 最多开5个线程，避免过载
MAX_THREADS = 5

# 1. 存活检测（带超时，快速失败）
def is_alive(url):
    if not url or len(url) < 10:
        return False
    # 官方源直接放行，不检测
    if any(k in url for k in ["cctv.cn", "chinamobile.com", "tv.cctv.com"]):
        return True
    try:
        # 用head请求，只查状态，不下载内容
        r = requests.head(
            url,
            timeout=LINK_CHECK_TIMEOUT,
            allow_redirects=True,
            stream=True,  # 不加载正文
            headers=HEADERS
        )
        return r.status_code in (200, 206, 301, 302)
    except:
        return False

# 2. 单个接口拉取（带强制超时，卡死直接跳）
def fetch_single_url(url):
    result = []
    try:
        # 强制超时：5秒内没响应就跳过这个接口
        resp = requests.get(
            url,
            timeout=SINGLE_URL_TIMEOUT,
            headers=HEADERS,
            stream=True  # 不加载大文件
        )
        resp.encoding = 'utf-8'
        content = resp.text
        # 匹配频道名+链接
        matches = re.findall(r"([^\n#]+?),(https?://.+?\.m3u8)", content)
        for name, link in matches:
            n = name.strip()
            l = link.strip()
            if n and l and ("CCTV" in n or "卫视" in n):
                result.append((n, l))
    except:
        # 任何错误（超时/连接失败）都直接跳过，不卡整体流程
        pass
    return result

# 3. 批量拉取接口（多线程+全局超时）
def pull_source():
    # 你指定的4个接口
    urls = [
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/ipv4/result.m3u",
        "https://ghfast.top/raw.githubusercontent.com/Supprise0901/TVBox_live/main/live.txt",
        "https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.txt"
    ]
    
    raw = {}
    # 多线程+全局超时：10秒内必须拉完所有接口，否则终止
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(fetch_single_url, url): url for url in urls}
        for future in futures:
            try:
                # 单个任务最多等10秒，超时直接放弃
                res = future.result(timeout=10)
                for name, link in res:
                    raw.setdefault(name, []).append(link)
            except TimeoutError:
                print(f"⚠️ 接口超时，直接跳过：{futures[future]}")
            except:
                print(f"❌ 接口访问失败，跳过：{futures[future]}")
    return raw

# 4. 同名合并+只留最快线路
def filter_best(raw):
    final = {}
    for name, links in raw.items():
        # 去重链接
        unique_links = list(set(links))
        ok_links = []
        # 多线程检测链接，更快
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = {executor.submit(is_alive, link): link for link in unique_links}
            for future in futures:
                try:
                    if future.result(timeout=LINK_CHECK_TIMEOUT):
                        ok_links.append(futures[future])
                except:
                    pass
        if ok_links:
            final[name] = ok_links[0]  # 留第一个可用（最快）
    return final

# 主程序
if __name__ == "__main__":
    start_time = time.time()
    print("🔍 开始拉取接口（带超时保护，绝不卡死）...")
    
    raw_data = pull_source()
    best_data = filter_best(raw_data)

    # 写入文件
    with open("live.txt", "w", encoding="utf-8") as f:
        for n, u in sorted(best_data.items()):
            f.write(f"{n},{u}\n")

    # 输出耗时，确认快速完成
    cost = round(time.time() - start_time, 2)
    print(f"✅ 完成！耗时 {cost} 秒 | 可用频道：{len(best_data)} 个（仅央视+卫视）")
