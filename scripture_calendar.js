/**
 * scripture_calendar.js
 * Embrace My Faith — Liturgical calendar with dynamic Easter-based seasons
 *
 * Exposes:  window.EMFCalendar  (browser)
 *           module.exports       (Node / CommonJS)
 *
 * Key API
 *   EMFCalendar.getEaster(year)          → Date
 *   EMFCalendar.getCategory(date)        → string
 *   EMFCalendar.getSeasonMap(year)       → array of { start, end, label }
 *   EMFCalendar.getDayOfYear(date)       → number  (1 = Jan 1)
 *   EMFCalendar.getDailyScripture(date)  → Promise<{ verse, reference, date, category, dayOfYear }>
 */

(function (global) {
  'use strict';

  // ═══════════════════════════════════════════════════════════════════════════
  // 1.  EASTER  —  Anonymous Gregorian algorithm
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Returns Easter Sunday for the given year as a Date (local midnight).
   * Range: March 22 – April 25 (Gregorian calendar).
   */
  function getEaster(year) {
    var a = year % 19;
    var b = Math.floor(year / 100);
    var c = year % 100;
    var d = Math.floor(b / 4);
    var e = b % 4;
    var f = Math.floor((b + 8) / 25);
    var g = Math.floor((b - f + 1) / 3);
    var h = (19 * a + b - d - g + 15) % 30;
    var i = Math.floor(c / 4);
    var k = c % 4;
    var l = (32 + 2 * e + 2 * i - h - k) % 7;
    var m = Math.floor((a + 11 * h + 22 * l) / 451);
    var month = Math.floor((h + l - 7 * m + 114) / 31); // 1-based
    var day   = ((h + l - 7 * m + 114) % 31) + 1;
    return ymd(year, month, day);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 2.  DATE HELPERS
  // ═══════════════════════════════════════════════════════════════════════════

  /** Create a local-midnight Date from year, 1-based month, day. */
  function ymd(y, m, d) {
    return new Date(y, m - 1, d);
  }

  /** Return a new Date that is `n` days after `date` (n may be negative). */
  function addDays(date, n) {
    var d = new Date(date);
    d.setDate(d.getDate() + n);
    return d;
  }

  /** Strip hours/minutes/seconds so two dates are comparable by calendar day. */
  function strip(date) {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate());
  }

  /** True if two dates fall on the same calendar day. */
  function sameDay(a, b) {
    return a.getFullYear() === b.getFullYear() &&
           a.getMonth()    === b.getMonth()    &&
           a.getDate()     === b.getDate();
  }

  /** True if `d` is within [start, end] inclusive (calendar-day comparison). */
  function inRange(d, start, end) {
    return d >= start && d <= end;
  }

  /**
   * Nth occurrence of a weekday in a month.
   *   weekday : 0 = Sunday … 6 = Saturday
   *   n       : 1 = first, 2 = second, etc.
   * e.g. nthWeekday(2026, 5, 0, 2) → 2nd Sunday in May 2026
   */
  function nthWeekday(year, month, weekday, n) {
    var first  = ymd(year, month, 1);
    var offset = (weekday - first.getDay() + 7) % 7;
    return ymd(year, month, 1 + offset + (n - 1) * 7);
  }

  /**
   * Last occurrence of a weekday in a month.
   * e.g. lastWeekday(2026, 5, 1) → last Monday in May 2026
   */
  function lastWeekday(year, month, weekday) {
    // day 0 of month+1 = last day of month
    var last = new Date(year, month, 0);
    var offset = (last.getDay() - weekday + 7) % 7;
    return addDays(last, -offset);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 3.  SEASON MAP  —  ordered list of { label, start, end } for a given year
  //     Single-day holidays are included as zero-width ranges (start === end).
  //     Years 2024–2028: calculated fresh each app load (in-memory cache only).
  //     Years 2029+    : calculated once, persisted in localStorage keyed by
  //                      year, and force-refreshed every January 1st.
  // ═══════════════════════════════════════════════════════════════════════════

  var _seasonMapCache  = {};
  var PERSIST_FROM_YEAR = 2029;          // first year that uses localStorage

  /** Store Date objects as millisecond timestamps for lossless JSON round-trip. */
  function _serializeMap(map) {
    return JSON.stringify(map.map(function (s) {
      return { label: s.label, start: s.start.getTime(), end: s.end.getTime() };
    }));
  }

  /** Restore a season map that was previously serialized by _serializeMap. */
  function _deserializeMap(json) {
    return JSON.parse(json).map(function (s) {
      return { label: s.label, start: new Date(s.start), end: new Date(s.end) };
    });
  }

  function _storageKey(year) { return 'emf_calendar_' + year; }

  /**
   * Build and return the full season map for `year`.
   * Seasons are checked in the order they appear here; the first match wins.
   * Single-day holidays come first so they override any enclosing season.
   *
   * Cache hierarchy (fastest → slowest):
   *   1. In-memory  _seasonMapCache  — always checked first
   *   2. localStorage (years 2029+)  — read on first miss, skips recalculation
   *   3. Full calculation            — result written to both caches
   */
  function getSeasonMap(year) {
    // ── 1. In-memory hit ────────────────────────────────────────────────────
    if (_seasonMapCache[year]) return _seasonMapCache[year];

    // ── 2. localStorage hit (2029+ only) ────────────────────────────────────
    if (year >= PERSIST_FROM_YEAR) {
      try {
        var stored = localStorage.getItem(_storageKey(year));
        if (stored) {
          _seasonMapCache[year] = _deserializeMap(stored);
          return _seasonMapCache[year];
        }
      } catch (e) { /* localStorage unavailable — fall through to calculation */ }
    }

    var easter     = getEaster(year);

    // ── Easter-relative landmarks ──────────────────────────────────────────
    var ashWed     = addDays(easter, -46); // Ash Wednesday (start of Lent)
    var palmSunday = addDays(easter,  -7); // Palm Sunday
    var holySat    = addDays(easter,  -1); // Holy Saturday (end of Holy Week)
    var easterEnd  = addDays(easter,   6); // Saturday after Easter

    // ── Fixed single-day holidays ──────────────────────────────────────────
    var valentines  = ymd(year,  2, 14);
    var mothersDay  = nthWeekday(year,  5, 0, 2);  // 2nd Sunday in May
    var memorialDay = lastWeekday(year, 5, 1);      // Last Monday in May
    var fathersDay  = nthWeekday(year,  6, 0, 3);  // 3rd Sunday in June
    var july4       = ymd(year,  7,  4);
    var veteransDay = ymd(year, 11, 11);
    var newYearsEve = ymd(year, 12, 31);

    // ── Thanksgiving: Monday of Thanksgiving week → Nov 30 ────────────────
    var thanksgivingDay = nthWeekday(year, 11, 4, 4); // 4th Thursday in Nov
    var thanksStart     = addDays(thanksgivingDay, -3); // Monday of that week
    var thanksEnd       = ymd(year, 11, 30);

    // ── Seasonal ranges ────────────────────────────────────────────────────
    var newYearStart  = ymd(year,  1,  1);
    var newYearEnd    = ymd(year,  1,  7);
    var winterStart   = ymd(year,  1,  8);         // day after New Year week
    var winterEnd     = addDays(ashWed,  -1);       // day before Ash Wednesday
    var lentStart     = ashWed;
    var lentEnd       = addDays(palmSunday, -1);    // day before Palm Sunday
    var holyWeekStart = palmSunday;
    var holyWeekEnd   = holySat;
    var easterStart   = easter;
    var springStart   = addDays(easterEnd, 1);      // day after Easter week
    var springEnd     = ymd(year,  6, 20);
    var summerStart   = ymd(year,  6, 21);
    var summerEnd     = ymd(year,  8, 13);
    var btsStart      = ymd(year,  8, 14);          // Back to School
    var btsEnd        = ymd(year,  8, 31);
    var fallStart     = ymd(year,  9,  1);
    var fallEnd       = addDays(thanksStart, -1);   // day before Thanksgiving week
    var adventStart   = ymd(year, 12,  1);
    var adventEnd     = ymd(year, 12, 24);
    var christmasStart = ymd(year, 12, 25);
    var christmasEnd  = ymd(year, 12, 31);

    // ── Build ordered map ─────────────────────────────────────────────────
    // Single-day holidays MUST come before seasons so they take precedence
    // on that one day (e.g. Veterans Day falls inside Thanksgiving season).
    var map = [
      // ── Single-day holidays ──
      { label: "New Year's Eve",  start: newYearsEve,  end: newYearsEve  },
      { label: "Valentine's Day", start: valentines,   end: valentines   },
      { label: "Mother's Day",    start: mothersDay,   end: mothersDay   },
      { label: "Memorial Day",    start: memorialDay,  end: memorialDay  },
      { label: "Father's Day",    start: fathersDay,   end: fathersDay   },
      { label: "Independence Day",start: july4,        end: july4        },
      { label: "Veterans Day",    start: veteransDay,  end: veteransDay  },

      // ── Easter-relative seasons ──
      { label: "New Year",        start: newYearStart, end: newYearEnd   },
      { label: "Christmas",       start: christmasStart,end: christmasEnd },
      { label: "Advent",          start: adventStart,  end: adventEnd    },
      { label: "Easter",          start: easterStart,  end: easterEnd    },
      { label: "Holy Week",       start: holyWeekStart,end: holyWeekEnd  },
      { label: "Lent",            start: lentStart,    end: lentEnd      },
      { label: "Winter",          start: winterStart,  end: winterEnd    },
      { label: "Spring",          start: springStart,  end: springEnd    },
      { label: "Summer",          start: summerStart,  end: summerEnd    },
      { label: "Back to School",  start: btsStart,     end: btsEnd       },
      { label: "Fall",            start: fallStart,    end: fallEnd      },
      { label: "Thanksgiving",    start: thanksStart,  end: thanksEnd    },
    ];

    // ── 3b. Persist to localStorage for 2029+ ───────────────────────────────
    if (year >= PERSIST_FROM_YEAR) {
      try { localStorage.setItem(_storageKey(year), _serializeMap(map)); } catch (e) {}
    }

    _seasonMapCache[year] = map;
    return map;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 3b. CALENDAR CACHE INIT  —  called automatically on script load
  //     On Jan 1 of any year ≥ 2029: wipes stale localStorage entries for the
  //     current year and next year, then recalculates and re-persists both.
  //     On all other days the existing localStorage entries are used as-is;
  //     no recalculation occurs unless an entry is missing.
  // ═══════════════════════════════════════════════════════════════════════════

  function initCalendarCache() {
    var now  = new Date();
    var year = now.getFullYear();

    // Nothing to do before 2029 — in-memory cache handles those years fine.
    if (year < PERSIST_FROM_YEAR) return;

    var isJan1 = now.getMonth() === 0 && now.getDate() === 1;

    if (isJan1) {
      // Force-refresh current year and next year so the new year's
      // Easter-relative dates (Ash Wednesday, Palm Sunday, etc.) are correct.
      [year, year + 1].forEach(function (y) {
        delete _seasonMapCache[y];                          // clear in-memory
        try { localStorage.removeItem(_storageKey(y)); } catch (e) {}
        getSeasonMap(y);                                    // recalculate + persist
      });
    } else {
      // Not Jan 1 — warm the in-memory cache from localStorage if present.
      // getSeasonMap already does this lazily; calling it here front-loads
      // the work so the first getCategory() call is instant.
      [year, year + 1].forEach(function (y) { getSeasonMap(y); });
    }
  }

  // Auto-run once when the script is loaded.
  initCalendarCache();

  // ═══════════════════════════════════════════════════════════════════════════
  // 4.  GET CATEGORY  —  what season / holiday is a given date?
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Returns the seasonal or holiday label for `date`.
   * Categories follow the season map above; the first match wins.
   */
  function getCategory(date) {
    var d   = strip(date);
    var map = getSeasonMap(d.getFullYear());

    for (var i = 0; i < map.length; i++) {
      var s = map[i];
      if (inRange(d, strip(s.start), strip(s.end))) {
        return s.label;
      }
    }
    return 'General'; // safety fallback (should not occur for valid dates)
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 5.  DAY OF YEAR
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Returns the 1-based day of the year for `date`.
   * Jan 1 = 1, Dec 31 = 365 (or 366 in a leap year).
   */
  function getDayOfYear(date) {
    var d     = strip(date);
    var start = new Date(d.getFullYear(), 0, 1);
    return Math.round((d - start) / 86400000) + 1;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 6.  SCRIPTURE LOADER  (cached after first fetch)
  // ═══════════════════════════════════════════════════════════════════════════

  var _scriptureCache = null;

  /**
   * Fetch /daily_scriptures.json once and cache in memory.
   * Returns a Promise that resolves to the array of scripture objects.
   */
  async function loadScriptures() {
    if (_scriptureCache) return _scriptureCache;
    var resp = await fetch('/daily_scriptures.json');
    if (!resp.ok) throw new Error('Failed to load daily_scriptures.json');
    _scriptureCache = await resp.json();
    return _scriptureCache;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 7.  GET DAILY SCRIPTURE  —  the main public API
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Given a Date (defaults to today), returns a Promise that resolves to:
   * {
   *   verse      : string  — the scripture text (no quotes)
   *   reference  : string  — e.g. "Psalm 46:10"
   *   date       : string  — MM-DD key used to look up the entry
   *   category   : string  — liturgical/seasonal label (shifts with Easter)
   *   dayOfYear  : number  — 1–365 (or 366 in a leap year)
   * }
   *
   * Scripture selection:
   *   The verse is keyed by the calendar date (MM-DD) so the same verse
   *   always appears on the same calendar day — giving 365 unique verses
   *   with no repeats.  The *category* label is what shifts with Easter
   *   from year to year.
   *
   * Fallback: if no matching entry is found (shouldn't happen with a
   *   complete JSON), the first entry in the file is returned.
   */
  async function getDailyScripture(date) {
    date = date ? new Date(date) : new Date();

    var scriptures = await loadScriptures();

    // Build MM-DD key and look up the matching entry
    var mm  = String(date.getMonth() + 1).padStart(2, '0');
    var dd  = String(date.getDate()).padStart(2, '0');
    var key = mm + '-' + dd;

    var entry = null;
    for (var i = 0; i < scriptures.length; i++) {
      if (scriptures[i].date === key) { entry = scriptures[i]; break; }
    }

    // Fallback: use day-of-year index (handles any gaps in the JSON)
    if (!entry) {
      var doy = getDayOfYear(date);
      entry = scriptures[(doy - 1) % scriptures.length] || scriptures[0];
    }

    return {
      verse:     entry.verse,
      reference: entry.reference,
      date:      entry.date,
      category:  getCategory(date),
      dayOfYear: getDayOfYear(date)
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // 8.  EXPORTS
  // ═══════════════════════════════════════════════════════════════════════════

  var EMFCalendar = {
    /** Calculate Easter Sunday for a given year → Date */
    getEaster:         getEaster,

    /** Get the ordered season/holiday map for a year → array */
    getSeasonMap:      getSeasonMap,

    /** Determine the liturgical/seasonal category for a date → string */
    getCategory:       getCategory,

    /** Day of year (1-based) for a date → number */
    getDayOfYear:      getDayOfYear,

    /**
     * Primary API: fetch today's (or any date's) scripture + category.
     * Returns a Promise → { verse, reference, date, category, dayOfYear }
     */
    getDailyScripture: getDailyScripture,

    /** Pre-load the scripture JSON (optional; getDailyScripture auto-loads) */
    loadScriptures:     loadScriptures,

    /**
     * Refresh localStorage season cache for the current + next year.
     * Called automatically on script load; only does real work on Jan 1, 2029+.
     * Expose so host apps can call it manually if needed (e.g. after a timezone
     * change or if localStorage was cleared mid-year).
     */
    initCalendarCache:  initCalendarCache,
  };

  // Support both browser globals and CommonJS (Node.js for tests)
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = EMFCalendar;
  } else {
    global.EMFCalendar = EMFCalendar;
  }

}(typeof window !== 'undefined' ? window : this));
