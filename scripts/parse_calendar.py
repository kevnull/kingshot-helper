#!/usr/bin/env python3
"""Parse Google Calendar iCal and emit data/calendar.json with events for the next 70 days."""
import json, re, sys
from datetime import datetime, date, timedelta

def extract_field(block, field):
    m = re.search(rf'(?m)^{field}[^:]*:(.+?)(?=\r?\n[A-Z]|\r?\nEND:|\Z)', block, re.DOTALL)
    if m:
        val = m.group(1)
        val = re.sub(r'\r?\n[ \t]', '', val)  # unfold
        return val.strip()
    return None

def parse_dt(s):
    s = s.strip()
    if 'T' in s:
        return datetime.strptime(s[:15], '%Y%m%dT%H%M%S').date()
    return datetime.strptime(s[:8], '%Y%m%d').date()

def day_of_week_offset(target_dow, from_date):
    """Days until the next occurrence of target_dow (MO=0..SU=6) from from_date."""
    DOW = {'MO':0,'TU':1,'WE':2,'TH':3,'FR':4,'SA':5,'SU':6}
    cur = from_date.weekday()  # Mon=0
    t = DOW.get(target_dow, 0)
    return (t - cur) % 7

with open('data/calendar.ics') as f:
    content = f.read()

today = date.today()
window_end = today + timedelta(days=70)

# Skip non-event entries and packs
SKIP = {'pack:', 'tundra', 'svs ', 'state transfer', 'google meet'}

blocks = re.split(r'BEGIN:VEVENT\r?\n', content)[1:]

results = []
for raw in blocks:
    summary = extract_field(raw, 'SUMMARY') or '?'
    if any(s in summary.lower() for s in SKIP):
        continue

    dtstart_raw = extract_field(raw, 'DTSTART')
    dtend_raw   = extract_field(raw, 'DTEND')
    rrule       = extract_field(raw, 'RRULE')

    if not dtstart_raw:
        continue
    try:
        start = parse_dt(dtstart_raw)
        end   = parse_dt(dtend_raw) if dtend_raw else start + timedelta(days=1)
    except Exception as e:
        continue

    duration = max(1, (end - start).days)

    if rrule:
        interval_m = re.search(r'INTERVAL=(\d+)', rrule)
        byday_m    = re.search(r'BYDAY=([A-Z,]+)', rrule)
        freq_m     = re.search(r'FREQ=(\w+)', rrule)
        interval   = int(interval_m.group(1)) if interval_m else 1
        freq       = freq_m.group(1) if freq_m else 'WEEKLY'

        # Walk occurrences
        cur = start
        for _ in range(200):
            if cur > window_end:
                break
            occ_end = cur + timedelta(days=duration)
            if cur >= today - timedelta(days=14):
                results.append({
                    'name':  summary,
                    'start': cur.isoformat(),
                    'end':   occ_end.isoformat(),
                })
            step = timedelta(weeks=interval) if freq == 'WEEKLY' else timedelta(days=interval)
            cur += step
    else:
        if today - timedelta(days=14) <= start <= window_end:
            results.append({
                'name':  summary,
                'start': start.isoformat(),
                'end':   (start + timedelta(days=duration)).isoformat(),
            })

results.sort(key=lambda x: x['start'])

out = {
    '_generatedAt': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'events': results
}
with open('data/calendar.json', 'w') as f:
    json.dump(out, f, indent=2)

print(f"calendar.json: {len(results)} events through {window_end}")
for ev in results:
    print(f"  {ev['start']} → {ev['end']}  {ev['name']}")
