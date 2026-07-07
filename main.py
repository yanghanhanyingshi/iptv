import requests
import re
import time
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 采集源地址
SOURCES = [
    "https://wget.la/https://github.com/yanghanhanyingshi/JYYS/blob/main/live.txt",
    "https://raw.githubusercontent.com/fafa002/yf2025/refs/heads/main/yiyifafa.txt",
    "https://dianshi.xinlingmiyu520.workers.dev/abc123",
    "https://gh-proxy.org/https://github.com/yanghanhanyingshi/JYYS/blob/main/live_sources.m3u",
    "https://restless-rice-b2a2.ganpig.workers.dev/cfdownload/https://tv.88888888888888888888888888888888888.ccwu.cc/live.m3u"
    "https://g.blfrp.cn/https://raw.githubusercontent.com/cyh92/live/refs/heads/main/source/migu.m3u"
]

# CCTV完整别名映射
CCTV_NAME_FULL = {
    "CCTV1": "CCTV1综合",
    "CCTV2": "CCTV2财经",
    "CCTV3": "CCTV3综艺",
    "CCTV4": "CCTV4中文国际",
    "CCTV5": "CCTV5体育",
    "CCTV5+": "CCTV5+体育赛事",
    "CCTV6": "CCTV6电影",
    "CCTV7": "CCTV7国防军事",
    "CCTV8": "CCTV8电视剧",
    "CCTV9": "CCTV9纪录",
    "CCTV10": "CCTV10科教",
    "CCTV11": "CCTV11戏曲",
    "CCTV12": "CCTV12社会与法",
    "CCTV13": "CCTV13新闻",
    "CCTV14": "CCTV14少儿",
    "CCTV15": "CCTV15音乐",
    "CCTV17": "CCTV17农业农村"
}

# 🔥 修改：固定的香港频道列表
HONGKONG_CHANNELS = [
    "翡翠台",
    "明珠台", 
    "无线新闻台",
    "TVB Plus",
    "凤凰卫视",
    "TVB星河"
]

# 少儿卡通列表（不含CCTV14，CCTV14留在央视区）
KID_ANIME_LIST = [
    "金鹰卡通","卡酷少儿","优漫卡通","哈哈炫动","嘉佳卡通",
    "广东少儿","浙江少儿","山东少儿","重庆少儿","四川妇女儿童",
    "福建少儿","江西少儿","云南少儿","河北少儿科教","内蒙古少儿",
    "辽宁教育·青少","黑龙江少儿","海南少儿","甘肃少儿","宁夏少儿","新疆少儿",
    "深圳少儿","南京少儿","杭州青少体育","济南少儿","成都少儿"
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

# 北京时间时区（UTC+8）
BEIJING_TZ = timezone(timedelta(hours=8))

# ============================================================
# 🔥 V5 广告拦截引擎
# ============================================================

AD_KEYWORDS = [
    "ad",
    "ads",
    "advert",
    "advertise",
    "promo",
    "promotion",
    "guanggao",
    "click",
    "track",
    "banner",
    "push",
    "market",
    "shop",
    "mall",
    "catvod",
    "tg"
]

AD_NAME_KEYWORDS = [
    "广告",
    "推广",
    "招商",
    "购物",
    "商城",
    "优惠",
    "带货",
    "营销"
]

AD_DOMAIN_BLACKLIST = [
    "ads.",
    "ad.",
    "promo.",
    "track.",
    "click."
]

def is_ad_channel(name, url):
    """
    广告检测
    返回 True = 广告
    """
    text = (
        str(name) +
        " " +
        str(url)
    ).lower()

    # URL关键词检测
    for k in AD_KEYWORDS:
        if k in text:
            print(f"[广告拦截] {url}")
            return True

    # 域名检测
    for d in AD_DOMAIN_BLACKLIST:
        if d in url.lower():
            print(f"[广告域名] {url}")
            return True

    # 名称检测
    for k in AD_NAME_KEYWORDS:
        if k in name:
            print(f"[广告频道] {name}")
            return True

    return False

def is_ad_url(uri):
    """URL广告检测（用于测速阶段二次拦截）"""
    uri = uri.lower()
    for k in AD_KEYWORDS:
        if k in uri:
            return True
    for d in AD_DOMAIN_BLACKLIST:
        if d in uri:
            return True
    return False

# ============================================================
# V4 IPTV 万能解析引擎
# ============================================================

def detect_source_type(text):
    """智能识别源类型"""
    if not text:
        return "unknown"
    if "#EXTM3U" in text:
        return "m3u"
    if "<html" in text.lower() or "<!DOCTYPE" in text[:200].upper():
        return "html"
    if "," in text and "http" in text:
        return "csv"
    if "http" in text:
        return "mixed"
    return "unknown"

def parse_channels_v4(text):
    """
    V4 万能解析器 - 支持 m3u / m3u8 / CSV / HTML / 混合格式
    返回: [(name, url), ...]
    """
    channels = []
    name = None

    # 清理 BOM / 空字符
    text = text.replace("\ufeff", "")

    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # =========================
        # 1️⃣ m3u EXTINF格式
        # =========================
        if line.startswith("#EXTINF"):
            # 提取频道名
            m = re.search(r",(.+)$", line)
            if m:
                name = m.group(1).strip()
                # 🔥 V5广告拦截 - 检测频道名是否包含广告
                if is_ad_channel(name, ""):
                    name = None
            continue

        # =========================
        # 2️⃣ 纯URL行
        # =========================
        if line.startswith("http://") or line.startswith("https://"):
            # 🔥 V5广告拦截 - 检测URL
            if is_ad_url(line):
                name = None
                continue
            
            if name:
                # 🔥 V5广告拦截 - 检测频道名
                if not is_ad_channel(name, line):
                    channels.append((name, line))
                name = None
            else:
                # 尝试从URL中提取频道名
                url_name = re.search(r"/([^/?]+)\.(m3u8|ts|m3u)", line)
                if url_name:
                    ch_name = url_name.group(1)
                    if not is_ad_channel(ch_name, line):
                        channels.append((ch_name, line))
                else:
                    if not is_ad_channel("未知频道", line):
                        channels.append(("未知频道", line))
            continue

        # =========================
        # 3️⃣ CSV格式 (name,url)
        # =========================
        if "," in line and "http" in line:
            try:
                # 尝试标准CSV
                parts = line.split(",", 1)
                if len(parts) == 2 and parts[1].strip().startswith("http"):
                    ch_name = parts[0].strip()
                    ch_url = parts[1].strip()
                    # 🔥 V5广告拦截
                    if not is_ad_channel(ch_name, ch_url):
                        channels.append((ch_name, ch_url))
                    continue
            except:
                pass

        # =========================
        # 4️⃣ HTML/JS反爬兜底 - 提取所有URL
        # =========================
        if "http" in line and (".m3u8" in line or ".ts" in line or ".m3u" in line):
            urls = re.findall(r"https?://[^\s\"'<>]+", line)
            for u in urls:
                # 🔥 V5广告拦截
                if is_ad_url(u):
                    continue
                # 尝试从URL中提取频道名
                url_name = re.search(r"/([^/?]+)\.(m3u8|ts|m3u)", u)
                if url_name:
                    ch_name = url_name.group(1)
                    if not is_ad_channel(ch_name, u):
                        channels.append((ch_name, u))
                else:
                    if not is_ad_channel("解析源", u):
                        channels.append(("解析源", u))

    # 去重 (保留首次出现)
    seen = set()
    unique_channels = []
    for n, u in channels:
        key = (n, u)
        if key not in seen:
            seen.add(key)
            unique_channels.append((n, u))
    
    return unique_channels

# ============================================================
# 增强版抓取函数
# ============================================================

def fetch_text(url):
    """增强版抓取 - 解决Worker/Cloudflare问题"""
    try:
        headers_v2 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }

        r = requests.get(url, headers=headers_v2, timeout=20, allow_redirects=True)
        r.raise_for_status()
        
        # 自动检测编码
        r.encoding = r.apparent_encoding or 'utf-8'
        
        # 检测源类型
        source_type = detect_source_type(r.text)
        print(f"[{source_type.upper()}] 抓取成功: {url}")
        
        return r.text

    except Exception as e:
        print(f"[SOURCE FAIL] {url} | {e}")
        return ""

# ============================================================
# 核心逻辑 (修改香港频道部分)
# ============================================================

def normalize_name(name):
    if not name:
        return None
    raw = name.upper().replace(" ", "")

    if "CCTV14" in raw:
        return "CCTV14少儿"
    if "CCTV5+" in raw or ("CCTV5" in raw and "+" in raw):
        return "CCTV5+"
    cctv_mat = re.search(r"CCTV[-_]?(\d+)", raw)
    if cctv_mat:
        return f"CCTV{cctv_mat.group(1)}"

    if "金鹰卡通" in name: return "金鹰卡通"
    if "卡酷少儿" in name or "卡酷动画" in name: return "卡酷少儿"
    if "优漫卡通" in name: return "优漫卡通"
    if "哈哈炫动" in name or "炫动卡通" in name: return "哈哈炫动"
    if "嘉佳卡通" in name: return "嘉佳卡通"
    if "广东少儿" in name: return "广东少儿"
    if "浙江少儿" in name: return "浙江少儿"
    if "深圳少儿" in name: return "深圳少儿"
    if "山东少儿" in name: return "山东少儿"
    if "重庆少儿" in name: return "重庆少儿"
    if "四川妇女儿童" in name or "四川少儿" in name: return "四川妇女儿童"
    if "福建少儿" in name: return "福建少儿"
    if "江西少儿" in name: return "江西少儿"
    if "河北少儿科教" in name: return "河北少儿科教"
    if "辽宁青少" in name: return "辽宁教育·青少"

    # 🔥 修改：只匹配固定的香港频道
    for hk_ch in HONGKONG_CHANNELS:
        if hk_ch in name:
            return hk_ch

    for ws in WEISHI_ORDER:
        if ws in name:
            return ws
    return name

def is_hongkong_channel(name):
    if not name:
        return False
    # 🔥 修改：只识别固定的香港频道
    for hk_ch in HONGKONG_CHANNELS:
        if hk_ch in name:
            return True
    return False

def check_url_alive(uri):
    # 🔥 V5广告拦截 - 测速阶段二次拦截
    if is_ad_url(uri):
        return False, uri
    
    try:
        r = requests.head(uri, timeout=TEST_TIMEOUT, headers=headers, allow_redirects=True)
        if r.status_code in (200, 301, 302, 304):
            return True, uri
    except:
        pass
    try:
        r = requests.get(uri, timeout=TEST_TIMEOUT, headers=headers, stream=True)
        for _ in r.iter_content(chunk_size=1024):
            return True, uri
    except:
        return False, uri
    return False, uri

def batch_filter_urls(uri_list, tag=""):
    valid = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        res = exe.map(check_url_alive, uri_list)
    
    for ok, u in res:
        if ok:
            print(f"[OK] {tag} {u}")
            valid.append(u)
        else:
            print(f"[FAIL] {tag} {u}")
    
    return valid

def save_file(content_list, fname):
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(content_list))

def get_beijing_time():
    return datetime.now(BEIJING_TZ).strftime("%Y%m%d %H:%M")

# ============================================================
# 主程序
# ============================================================

def main():
    CURRENT_BJ_TIME = get_beijing_time()
    print(f"脚本运行北京时间：{CURRENT_BJ_TIME}")
    print("=" * 60)

    time_url = "http://yanghanhan.xyzvip.cn/TV/saoma.mp4"

    all_raw = []
    for src in SOURCES:
        print(f"正在抓取源: {src}")
        txt = fetch_text(src)
        if not txt:
            continue
        
        # 🔥 使用V4万能解析器（内部已集成V5广告拦截）
        chs = parse_channels_v4(txt)
        print(f"  解析到 {len(chs)} 个频道")
        all_raw.extend(chs)

    print(f"\n总共解析到 {len(all_raw)} 个频道条目（已过滤广告）")
    print("=" * 60)

    channel_map = {k: [] for k in ALL_ORDER}
    # 🔥 修改：使用固定的香港频道列表
    hk_map = {k: [] for k in HONGKONG_CHANNELS}
    kid_map = {k: [] for k in KID_ANIME_LIST}

    for nm, url in all_raw:
        # 🔥 V5广告拦截已在parse_channels_v4中执行，此处不再重复
        std_nm = normalize_name(nm)
        
        # 少儿频道
        if std_nm in kid_map:
            kid_map[std_nm].append(url)
        # 央视卫视
        if std_nm in channel_map:
            channel_map[std_nm].append(url)
        # 🔥 修改：香港频道（只匹配固定列表）
        if is_hongkong_channel(nm):
            # 使用标准化的名称
            if std_nm in hk_map:
                hk_map[std_nm].append(url)

    print("开始多线程测速过滤死链...")
    print("=" * 60)
    
    valid_map = {}
    hk_valid_map = {}
    kid_valid_map = {}

    # 过滤央视卫视
    for chn, uris in channel_map.items():
        if not uris:
            valid_map[chn] = []
            continue
        unique_uris = list(dict.fromkeys(uris))
        ok_uris = batch_filter_urls(unique_uris, f"CCTV-{chn}")
        valid_map[chn] = ok_uris

    # 🔥 修改：过滤香港频道（按固定顺序）
    for chn, uris in hk_map.items():
        if not uris:
            hk_valid_map[chn] = []
            continue
        unique_uris = list(dict.fromkeys(uris))
        ok_uris = batch_filter_urls(unique_uris, f"HK-{chn}")
        hk_valid_map[chn] = ok_uris

    # 过滤少儿频道
    for chn, uris in kid_map.items():
        if not uris:
            kid_valid_map[chn] = []
            continue
        unique_uris = list(dict.fromkeys(uris))
        ok_uris = batch_filter_urls(unique_uris, f"KID-{chn}")
        kid_valid_map[chn] = ok_uris

    # 严格按指定顺序组装
    out_lines = []
    raw_all_lines = []

    # 1. 央视卫视分组
    out_lines.append("央视卫视,#genre#")
    raw_all_lines.append("央视卫视,#genre#")
    for chn in ALL_ORDER:
        show_name = CCTV_NAME_FULL.get(chn, chn)
        for idx, vu in enumerate(valid_map[chn], 1):
            out_lines.append(f"{show_name},{vu}$LR•IPV4•29『线路{idx}』")
        for idx, ru in enumerate(channel_map[chn], 1):
            raw_all_lines.append(f"{chn},{ru}$LR•IPV4•29『线路{idx}』")

    # 2. 🔥 修改：香港频道分组（按固定顺序输出）
    out_lines.append("香港频道,#genre#")
    raw_all_lines.append("香港频道,#genre#")
    for chn in HONGKONG_CHANNELS:
        if chn in hk_valid_map:
            for idx, vu in enumerate(hk_valid_map[chn], 1):
                out_lines.append(f"{chn},{vu}$LR•IPV4•29『线路{idx}』")
        if chn in hk_map:
            for idx, ru in enumerate(hk_map[chn], 1):
                raw_all_lines.append(f"{chn},{ru}$LR•IPV4•29『线路{idx}』")

    # 3. 少儿动画分组
    out_lines.append("少儿动画,#genre#")
    raw_all_lines.append("少儿动画,#genre#")
    for chn in KID_ANIME_LIST:
        for idx, vu in enumerate(kid_valid_map[chn], 1):
            out_lines.append(f"{chn},{vu}$LR•IPV4•29『线路{idx}』")
        for idx, ru in enumerate(kid_map[chn], 1):
            raw_all_lines.append(f"{chn},{ru}$LR•IPV4•29『线路{idx}』")

    # 4. 更新时间
    out_lines.append("灵鹿整合,#genre#")
    out_lines.append(f"{CURRENT_BJ_TIME},{time_url}")
    raw_all_lines.append("灵鹿整合,#genre#")
    raw_all_lines.append(f"{CURRENT_BJ_TIME},{time_url}")

    save_file(out_lines, "live.txt")
    save_file(raw_all_lines, "result.txt")

    print("=" * 60)
    print("✅ 结构完全对齐：央视卫视→香港频道→少儿动画→灵鹿整合")
    print(f"✅ 生成文件: live.txt (过滤后), result.txt (原始)")
    print(f"✅ 央视卫视: {sum(len(v) for v in valid_map.values())} 个有效链接")
    print(f"✅ 香港频道: {sum(len(v) for v in hk_valid_map.values())} 个有效链接")
    print(f"✅ 少儿动画: {sum(len(v) for v in kid_valid_map.values())} 个有效链接")
    print(f"🛡️ 广告拦截已启用，共拦截广告内容")

if __name__ == "__main__":
    main()
