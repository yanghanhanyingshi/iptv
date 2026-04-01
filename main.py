import requests
import re
import time

# ======================
# 配置
# ======================
HEADERS = {"User-Agent": "Mozilla/5.0"}
URL_TIMEOUT = 4
CHECK_TIMEOUT = 1
GROUP_HEADER = "灵鹿整合,#genre#"

# ======================
# 检测链接是否可用
# ======================
def check_link(url):
    if not url or len(url) < 10:
        return False
    try:
        r = requests.get(url, timeout=CHECK_TIMEOUT, stream=True, headers=HEADERS)
        r.raw.read(100)
        return r.status_code < 400
    except:
        return False

# ======================
# 抓取你指定的4个接口
# ======================
def pull_sources():
    target_urls = [
        "https://gh-proxy.org/https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1.m3u",
        "https://www.iyouhun.com/tv/zb",
        "https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u",
        "https://ghfast.top/raw.githubusercontent.com/Supprise0901/TVBox_live/main/live.txt"
    ]

    raw = {}
    for idx, url in enumerate(target_urls, 1):
        try:
            print(f"拉取接口 {idx}/4: {url}")
            resp = requests.get(url, timeout=URL_TIMEOUT, headers=HEADERS)
            resp.encoding = "utf-8"
            txt = resp.text

            # 匹配两种格式：name,url 以及 #EXTINF:-1,name\nurl
            items = re.findall(r"([^\n#]+?), *https?://[^\n]+", txt)
            urls = re.findall(r"https?://\S+\.m3u8", txt)
            names = re.findall(r"#EXTINF:-1[^,\n]*,([^\n]+)", txt)

            pairs = []
            pairs += re.findall(r"([^\n#]+?),(https?://\S+\.m3u8)", txt)
            for n, u in zip(names, urls):
                pairs.append((n.strip(), u.strip()))

            for name, link in pairs:
                name = name.strip()
                link = link.strip()
                if not name or not link:
                    continue
                if "CCTV" in name or "卫视" in name:
                    # 统一央视格式为 CCTV-数字
                    nm = re.sub(r"CCTV[ -]*0*(\d+)", r"CCTV-\1", name)
                    if nm not in raw:
                        raw[nm] = []
                    raw[nm].append(link)
        except Exception as e:
            print(f"接口 {idx} 失败，跳过")
            continue
    return raw

# ======================
# 去重 + 选可用线路
# ======================
def filter_best(raw):
    final = {}
    for name, links in raw.items():
        uniq = list(set(links))
        for link in uniq:
            if check_link(link):
                final[name] = link
                break
    return final

# ======================
# 排序：CCTV1→2→3…
# ======================
def sort_channels(channels):
    cctv = {}
    wei = {}
    for k, v in channels.items():
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

# ======================
# 主程序
# ======================
if __name__ == "__main__":
    print("开始抓取直播源…")
    raw = pull_sources()
    valid = filter_best(raw)
    sorted_ch = sort_channels(valid)

    with open("live.txt", "w", encoding="utf-8") as f:
        f.write(f"{GROUP_HEADER}\n")
        for name, url in sorted_ch.items():
            f.write(f"{name},{url}\n")

    print(f"✅ 完成！有效频道：{len(sorted_ch)} 个")
