# kingshot-helper

Single-page static helper for the Kingshot mobile game. `index.html` is the whole app; `data/` is refreshed every 4h by GitHub Actions; `scripts/parse_calendar.py` parses the Google Calendar iCal feed.

## Working agreements

- **Reuse shared helpers — do not reduplicate logic.** Before writing new code that filters events, derives status, looks up event metadata, or formats dates, search for an existing helper and use it. Common ones live in the `EVENT LOOKUP HELPERS` section of `index.html`: `getEvent`, `eventFromTitleKey`, `eventFromCalName`, `isCalEventLocked`, `lockedCalendarKeys`, `liveEventsFromCalendar`, `deriveEventStatus`, `fmtDate`. If a helper almost-but-not-quite fits, extend it rather than copy-pasting a variant.
- **One source of truth per concept.** `data/calendar.json` (Google Calendar) is the authoritative server-specific schedule. `liveData.calendar` from kingshot.net is a generic universal cycle and should only be a fallback when calendarData is missing.
- **Stay in `index.html`.** No build step, no bundler, no framework. Vanilla JS, no dependencies. Don't introduce new files unless there's a clear reason.
- **Don't write comments that just restate the code.** Comments should capture the *why* (a non-obvious constraint, a date-convention quirk, a server-state assumption) — not the *what*.

## Local dev

`make dev` runs a static server on :8000. The Claude Code preview server uses :8765 (`.claude/launch.json`). `make data` refreshes `data/events.json` and `data/calendar.json` from upstream.
