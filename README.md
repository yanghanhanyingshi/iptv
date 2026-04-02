<!-- 双直播源合集友链 -->
<a href="https://wget.la/https://github.com/yanghanhanyingshi/iptv/blob/main/live.txt" target="_blank">直播源①</a>
&nbsp;&nbsp;|&nbsp;&nbsp;
<a href="https://wget.la/https://github.com/yanghanhanyingshi/iptv/blob/main/result.txt" target="_blank">直播源②</a>
    document.getElementById(tipId).innerText="复制成功！";
    setTimeout(()=>document.getElementById(tipId).innerText="",1500);
  })
}
</script>

</body>
</html>
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

