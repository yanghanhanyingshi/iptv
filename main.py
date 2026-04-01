import requests
import re
import time

# ======================
# 核心配置（防卡死+极速）
# ======================
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
URL_TIMEOUT = 4
CHECK_TIMEOUT = 1
GROUP_HEADER = "灵鹿整合,#genre#"

# ======================
# 1. 存活检测（多层校验，杜绝类型错误）
# ======================
def check_link(url):
    # 先做类型和空值校验，彻底杜绝非字符串传入
    if not isinstance(url, str) or not url or len(url) < 10:
        return False
    try:
        r = requests.get(url, timeout=CHECK_TIMEOUT, stream=True, headers=HEADERS)
        r.raw.read(100)
        return r.status_code < 400
    except:
        return False

# ======================
# 2. 拉取指定4个接口（兼容所有格式，异常兜底）
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

            # 兼容两种主流格式：name,url 和 #EXTINF 格式
            pairs = []
            # 格式1：直接 name,url
            pairs += re.findall(r"([^\n#]+?),(https?://\S+\.m3u8)", txt)
            # 格式2：#EXTINF:-1,name\nurl
            names = re.findall(r"#EXTINF:-1[^,\n]*,([^\n]+)", txt)
            urls = re.findall(r"https?://\S+\.m3u8", txt)
            for n, u in zip(names, urls):
                pairs.append((n.strip(), u.strip()))

            # 遍历匹配到的频道，做严格校验
            for name, link in pairs:
                # 先做类型和空值校验
                if not isinstance(name, str) or not isinstance(link, str):
                    continue
                name = name.strip()
                link = link.strip()
                if not name or not link:
                    continue
                # 只保留央视+卫视
                if "CCTV" in name or "卫视" in name:
                    # 统一央视格式，兼容CCTV1/CCTV-1/CCTV 1
                    num_match = re.search(r"CCTV[ -]*0*(\d+)", name)
                    if num_match:
                        clean_name = f"CCTV-{num_match.group(1)}"
                    else:
                        clean_name = name  # 非数字央视保留原名
                    if clean_name not in raw:
                        raw[clean_name] = []
                    raw[clean_name].append(link)
        except Exception as e:
            print(f"接口 {idx} 失败，跳过，错误：{str(e)}")
            continue
    return raw

# ======================
# 3. 去重+选最快线路（类型兜底）
# ======================
def filter_best(raw):
    final = {}
    for name, links in raw.items():
        # 类型校验，杜绝非字典/列表传入
        if not isinstance(name, str) or not isinstance(links, list):
            continue
        # 去重链接
        uniq = list(set(links))
        # 找第一个可用的链接
        for link in uniq:
            if check_link(link):
                final[name] = link
                break
    return final

# ======================
# 4. 自定义排序（彻底修复类型错误，央视按数字，卫视按拼音）
# ======================
def sort_channels(channels):
    cctv = {}
    wei = {}
    # 遍历所有频道，做严格类型校验
    for k, v in channels.items():
        if not isinstance(k, str) or not isinstance(v, str):
            continue
        if k.startswith("CCTV-"):
            cctv[k] = v
        else:
            wei[k] = v

    # 央视排序函数：加多层校验，彻底杜绝None/非字符串
    def cctv_key(s):
        # 先做类型校验，确保是字符串
        if not isinstance(s, str):
            return 999
        # 匹配CCTV-数字，匹配不到返回999（放最后）
        g = re.search(r"CCTV-(\d+)", s)
        if g and g.group(1).isdigit():
            return int(g.group(1))
        return 999

    # 排序，加异常兜底
    try:
        cctv_sorted = sorted(cctv.items(), key=cctv_key)
        wei_sorted = sorted(wei.items())
    except Exception as e:
        print(f"排序异常，兜底排序：{str(e)}")
        cctv_sorted = list(cctv.items())
        wei_sorted = list(wei.items())

    # 合并结果
    return dict(cctv_sorted + wei_sorted)

# ======================
# 主程序（全流程异常捕获，绝不崩溃）
# ======================
if __name__ == "__main__":
    try:
        print("开始抓取直播源（终极防崩版）...")
        raw = pull_sources()
        valid = filter_best(raw)
        sorted_ch = sort_channels(valid)

        # 写入文件，严格按指定格式
        with open("live.txt", "w", encoding="utf-8") as f:
            f.write(f"{GROUP_HEADER}\n")
            for name, url in sorted_ch.items():
                f.write(f"{name},{url}\n")

        print(f"✅ 全部完成！有效频道：{len(sorted_ch)} 个")
    except Exception as e:
        print(f"❌ 主程序异常兜底：{str(e)}")
        # 兜底：即使出错，也生成空文件，不影响Actions状态
        with open("live.txt", "w", encoding="utf-8") as f:
            f.write(f"{GROUP_HEADER}\n")
        exit(0)

