<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>卫视/央视直播源自动采集+去重+检测</title>
<style>
body{padding:30px;font-family:微软雅黑;background:#f5f5f5;}
h2{text-align:center;color:#222;margin-bottom:25px;}
.item{margin:15px 0;padding:12px;background:#fff;border-radius:8px;}
.link{display:block;margin:8px 0;color:#06c;word-break:break-all;}
.btn{padding:6px 16px;background:#2385ff;color:#fff;border:none;border-radius:4px;cursor:pointer;margin-top:5px;}
.btn:hover{background:#1976e8;}
.tip{color:green;font-size:12px;margin-left:10px;}
</style>
</head>
<body>

<h2>卫视/央视直播源自动采集+去重+检测</h2>

<div class="item">
  <div>直播源① live.txt</div>
  <code class="link" id="url1">https://wget.la/https://raw.githubusercontent.com/yanghanhanyingshi/iptv/main/live.txt</code>
  <button class="btn" onclick="copyText('url1')">一键复制链接</button>
  <span class="tip" id="tip1"></span>
</div>

<div class="item">
  <div>直播源② result.txt</div>
  <code class="link" id="url2">https://wget.la/https://raw.githubusercontent.com/yanghanhanyingshi/iptv/main/result.txt</code>
  <button class="btn" onclick="copyText('url2')">一键复制链接</button>
  <span class="tip" id="tip2"></span>
</div>

<script>
function copyText(id){
  let text = document.getElementById(id).innerText;
  navigator.clipboard.writeText(text).then(()=>{
    let num = id.replace('url','');
    let tipEl = document.getElementById('tip'+num);
    tipEl.innerText="复制成功！";
    setTimeout(()=>tipEl.innerText='',1500);
  })
}
</script>

</body>
</html>

