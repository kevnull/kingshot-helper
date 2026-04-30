.PHONY: dev data

# Local dev server — serves repo root so ./data/*.json resolves
dev:
	@echo "→ http://localhost:8000"
	@python3 -m http.server 8000

# Pull fresh data from kingshot.net (mirrors the GitHub Action)
data:
	curl -sf https://kingshot.net/api/events -H "Accept: application/json" -o data/events.json
	@python3 -c "import json,datetime; d=json.load(open('data/events.json')); d['_fetchedAt']=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'); json.dump(d, open('data/events.json','w')); print('KvK days:', d['kvk']['timeLeft']['days']); print('Active events:', len(d['calendar']['activeEvents']))"
	CAL_ID="e6196c2703be23e87e027067c77f8990c4434a659a08fc9c3612f60c83b42c0e@group.calendar.google.com"; \
	  ENCODED=$$(python3 -c "import urllib.parse; print(urllib.parse.quote('$$CAL_ID'))"); \
	  curl -sf "https://calendar.google.com/calendar/ical/$$ENCODED/public/basic.ics" -o data/calendar.ics
	python3 scripts/parse_calendar.py
