CH="chromium-browser --headless=new --no-sandbox --disable-gpu --window-size=1400,1000 --virtual-time-budget=8000"
for w in 375 768 1280; do
 D=/tmp/cro$RANDOM$RANDOM
 printf '<html><body style="margin:0"><iframe id=f src="/index.html" style="width:%spx;height:16000px;border:0"></iframe><script>const f=document.getElementById("f");f.onload=()=>{document.title="SW="+f.contentDocument.body.scrollWidth+" W="+f.clientWidth+" sub="+f.contentDocument.querySelector(".sub").textContent.slice(0,18);};</script></body></html>' $w > ovf.html
 echo -n "$w: "; DISPLAY=:0 timeout 60 $CH --user-data-dir=$D --dump-dom "http://127.0.0.1:8123/ovf.html?cb=$RANDOM" 2>/dev/null | grep -o '<title>[^<]*' 
done
