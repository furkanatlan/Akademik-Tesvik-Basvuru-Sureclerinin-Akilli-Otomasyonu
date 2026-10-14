#!/bin/sh
# Paylaşımlı tarayıcı: kullanıcı WoS/Scopus girişini bu tarayıcıda (noVNC üzerinden) yapar,
# backend/worker aynı oturumu CDP ile kullanarak tarama ve ekran görüntüsü alır.
#   noVNC (kullanıcı ekranı) : http://localhost:6080/vnc.html
#   CDP (yalnızca iç ağ)     : browser:9223
export DISPLAY=:99
W=${BROWSER_WIDTH:-1440}
H=${BROWSER_HEIGHT:-900}

# Container yeniden başlatıldığında kalan kilit/geçici dosyaları temizle (yoksa Xvfb açılmaz)
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 /browser-profile/.org.chromium.Chromium.*

Xvfb :99 -screen 0 "${W}x${H}x24" -nolisten tcp &
for _ in 1 2 3 4 5 6 7 8 9 10; do
  [ -e /tmp/.X11-unix/X99 ] && break
  sleep 0.5
done
x11vnc -display :99 -forever -shared -nopw -quiet -rfbport 5900 >/dev/null 2>&1 &
websockify --web /usr/share/novnc 6080 localhost:5900 >/dev/null 2>&1 &
# Chromium CDP portunu yalnızca 127.0.0.1'e açar; socat ile iç ağa yönlendirilir
socat TCP-LISTEN:9223,fork,reuseaddr TCP:127.0.0.1:9222 &

CHROME=$(ls -d /ms-playwright/chromium-*/chrome-linux/chrome | head -1)
echo "Paylaşımlı tarayıcı hazır: noVNC 6080, CDP 9223 ($CHROME)"

# Kullanıcı pencereyi kapatırsa tarayıcı yeniden açılır; oturum /browser-profile'da kalıcıdır
while true; do
  rm -f /browser-profile/SingletonLock
  "$CHROME" --no-sandbox --no-first-run --no-default-browser-check --disable-dev-shm-usage \
    --user-data-dir=/browser-profile --remote-debugging-port=9222 \
    --hide-crash-restore-bubble --disable-session-crashed-bubble --disable-features=Translate \
    --restore-last-session \
    --window-position=0,0 --window-size="${W},${H}" --lang=tr-TR \
    about:blank >/dev/null 2>&1
  sleep 2
done
