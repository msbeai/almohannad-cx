#!/bin/bash
# انشر التغييرات إلى almohannad.cx — أمر واحد يفعل كل شيء:
#   ./publish.sh
# يولّد أغلفة المقالات الجديدة، يبني الموقع، وينشره على نتلفاي.
set -e
cd "$(dirname "$0")"

echo "==> 1/3 توليد أغلفة المقالات الجديدة (إن وجدت)…"
STARTED_DEV=0
if ! curl -s -o /dev/null --max-time 2 http://localhost:4321/cover-template.html; then
  echo "    تشغيل خادم التطوير مؤقتًا…"
  npm run dev >/dev/null 2>&1 &
  DEV_PID=$!
  STARTED_DEV=1
  until curl -s -o /dev/null --max-time 2 http://localhost:4321/cover-template.html; do sleep 1; done
fi
python3 scripts/make_covers.py
if [ "$STARTED_DEV" = "1" ]; then kill $DEV_PID 2>/dev/null || true; fi

echo "==> 2/3 بناء الموقع…"
npm run build

echo "==> 3/3 النشر إلى almohannad.cx…"
npx -y netlify-cli deploy --prod --dir dist --site 93321ec1-ade7-4c8a-b0ea-8c6d3a4b09e1

echo ""
echo "✅ تم النشر! تفقد موقعك على https://almohannad.cx"
