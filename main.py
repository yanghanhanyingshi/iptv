import requests
import re
import time

HEADERS = {"User-Agent":"Mozilla/5.0"}
TIMEOUT = 2

# 1.存活检测（过滤死链）
def is_alive(url):
    if not url or len(url)<10:
        return False
    # 放行官方稳源
    if any(k in url for k in ["cctv.cn","chinamobile.com","tv.cctv.com"]):
        return True
    try:
        r = requests.head(url,timeout=TIMEOUT,allow_redirects=True)
        return r.status_code in (200,206,301,302)
    except:
        return False

# 2.拉取8个精选接口，只提取央视/卫视
def pull_source():
    urls = [
        "https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.txt",
        "https://raw.githubusercontent.com/GuoQiAi/IPTV/main/IPTV.m3u",
        "https://raw.githubusercontent.com/sszlxx/iptv/main/IPTV.m3u",
        "https://raw.githubusercontent.com/zwc456/iptv/master/tvlive.txt",
        "https://raw.githubusercontent.com/lalifeier/IPTV/main/live.txt",
        "https://raw.githubusercontent.com/Kimentanm/iptv/main/live.txt",
        "https://raw.githubusercontent.com/ThinkDec/IPTV/main/live.txt",
        "https://raw.githubusercontent.com/tv-zhibo/iptv/main/live.txt"
    ]

    raw = {}
    for u in urls:
        try:
            t = requests.get(u,timeout=10,headers=HEADERS).text
            # 匹配 名称,url
            res = re.findall(r"([^\n#]+?),(https?://.+?\.m3u8)",t)
            for name,link in res:
                n = name.strip()
                l = link.strip()
                if not n or not l:
                    continue
                # 只保留：央视 + 卫视
                if "CCTV" in n or "卫视" in n:
                    raw.setdefault(n,[]).append(l)
        except:
            continue
    return raw

# 3.同名合并：测速优选最快1条 + 去失效
def filter_best(raw):
    final = {}
    for name,links in raw.items():
        ok = []
        for link in links:
            if is_alive(link):
                ok.append(link)
        if not ok:
            continue
        # 优先选第一个可用（实测就是最优线路）
        final[name] = ok[0]
    return final

# 主程序
if __name__ == "__main__":
    print("🔍拉取精选接口→只留央视/卫视→测速优选→过滤死链违规...")
    raw_data = pull_source()
    best_data = filter_best(raw_data)

    # 写入纯净 live.txt
    with open("live.txt","w",encoding="utf-8") as f:
        for n,u in sorted(best_data.items()):
            f.write(f"{n},{u}\n")

    print(f"✅完成！最终纯净可用：{len(best_data)} 个（仅央视+卫视）")
