#!/bin/sh
# =============================================================================
# File    : scripts/summarise.sh
# Purpose : Summarise a saved monitor log.
# Usage   : scripts/summarise.sh evidence/t4-at-rest-log.txt
# Input   : lines of "<ISO-8601 timestamp> <OK|FAIL> <body or error>"
#           Any other line (for example a "###" switch marker) is ignored.
# Output  : total and failed requests, first/last timestamp, responses per
#           distinct version, first/last time each version was seen, and the
#           mixed-version window (seconds) for every pair of versions whose
#           observation intervals overlap.
# =============================================================================
if [ $# -ne 1 ] || [ ! -r "$1" ]; then
  echo "usage: $0 <monitor-log>" >&2
  exit 2
fi

awk '
# ISO-8601 UTC timestamp -> seconds since 1970 (days-from-civil algorithm).
function epoch(t,   y, m, d, hh, mi, ss, era, yoe, mp, doy, doe) {
  y = substr(t, 1, 4) + 0;  m = substr(t, 6, 2) + 0;  d = substr(t, 9, 2) + 0
  hh = substr(t, 12, 2) + 0; mi = substr(t, 15, 2) + 0; ss = substr(t, 18, 2) + 0
  if (m <= 2) y--
  era = int(y / 400); yoe = y - era * 400
  mp = (m + 9) % 12
  doy = int((153 * mp + 2) / 5) + d - 1
  doe = yoe * 365 + int(yoe / 4) - int(yoe / 100) + doy
  return (era * 146097 + doe - 719468) * 86400 + hh * 3600 + mi * 60 + ss
}
$2 == "OK" || $2 == "FAIL" {
  total++
  if (first == "") first = $1
  last = $1
  if ($2 == "FAIL") { fail++; next }
  if (match($0, /"version":"[^"]*"/)) {
    v = substr($0, RSTART + 11, RLENGTH - 12)
    cnt[v]++
    if (!(v in vfirst)) vfirst[v] = $1
    vlast[v] = $1
  } else {
    unparsed++
  }
}
END {
  printf "total requests  : %d\n", total
  printf "failed requests : %d\n", fail + 0
  printf "first timestamp : %s\n", first
  printf "last timestamp  : %s\n", last
  if (unparsed > 0) printf "OK without a version field: %d\n", unparsed

  n = 0
  for (v in cnt) keys[++n] = v
  for (i = 2; i <= n; i++) {                      # insertion sort of version names
    k = keys[i]; j = i - 1
    while (j >= 1 && keys[j] > k) { keys[j + 1] = keys[j]; j-- }
    keys[j + 1] = k
  }
  print "responses per version:"
  for (i = 1; i <= n; i++)
    printf "  %-14s %6d   first seen %s   last seen %s\n", keys[i], cnt[keys[i]], vfirst[keys[i]], vlast[keys[i]]

  found = 0
  for (i = 1; i <= n; i++) for (j = i + 1; j <= n; j++) {
    a = keys[i]; b = keys[j]
    lo = (epoch(vfirst[a]) > epoch(vfirst[b])) ? epoch(vfirst[a]) : epoch(vfirst[b])
    hi = (epoch(vlast[a])  < epoch(vlast[b]))  ? epoch(vlast[a])  : epoch(vlast[b])
    if (hi >= lo) {
      printf "mixed-version window (%s + %s): %d s\n", a, b, hi - lo
      found = 1
    }
  }
  if (!found && n > 1) print "mixed-version window: none (versions never overlapped)"
}' "$1"
