#!/bin/bash
# Persistent monitor heartbeat. Emits a compact line either:
#   - on any change to calls / cost / inflight set        (fast feedback while active)
#   - or every HEARTBEAT_EVERY_N ticks                    (still-alive signal while idle)
# Tick period is TICK_S seconds. Default: TICK_S=30, HEARTBEAT_EVERY_N=10 (5 min).
#
# Idle period: 1 line per HEARTBEAT_EVERY_N*TICK_S seconds.
# Active period: up to 1 line per TICK_S seconds.

set -u
cd /Users/ren/IdeaProjects/Paper/elixir
TICK_S=${TICK_S:-30}
HEARTBEAT_EVERY_N=${HEARTBEAT_EVERY_N:-10}

prev_calls=0
prev_cost=0
prev_inflight=""
ticks_since_emit=0

while true; do
    # Window position
    read -r W_IDX W_REM <<<"$(python3 - <<'PY'
import datetime, zoneinfo
kst = zoneinfo.ZoneInfo("Asia/Seoul")
now = datetime.datetime.now(kst)
anchor = datetime.datetime(2026,5,21,3,10,tzinfo=kst)
WIN = 5*3600
if now < anchor:
    print(-1, int((anchor-now).total_seconds())//60)
else:
    el = (now-anchor).total_seconds()
    idx = int(el//WIN)
    rem = WIN - int(el%WIN)
    print(idx, rem//60)
PY
)"
    # Aggregate counts via dashboard.py (parsing global line)
    read -r calls tokens cost <<<"$(python3 experiments/_monitoring/dashboard.py 2>/dev/null \
        | awk '/global/ {
            # global line:  HH:MM:SSKST  global  calls=N  err=...  tokens=Xk  cost=$Y...
            for (i=1;i<=NF;i++) {
                if ($i ~ /^calls=/)  { split($i,a,"="); c=a[2] }
                if ($i ~ /^tokens=/) { split($i,a,"="); t=a[2] }
                if ($i ~ /^cost=\$/) { split($i,a,"\\$"); co=a[2] }
            }
            print c, t, co
        }')"
    # Default if empty
    calls=${calls:-0}
    tokens=${tokens:-0}
    cost=${cost:-0}

    # In-flight runners
    inflight=$(ps -ef 2>/dev/null \
        | grep -E "(run\.py|run_self_consistency\.py|llm_recheck\.py|search\.py|dedup\.py)" \
        | grep -v grep \
        | awk '{
            for (i=8; i<=NF; i++) {
                if ($i ~ /\.py$/) {
                    split($i, p, "/")
                    printf "%s ", p[length(p)]
                    break
                }
            }
        }')
    inflight=${inflight:-none}

    # Compute deltas (numeric — convert calls easily; tokens has k/M suffix so leave as is)
    d_calls=$(( calls - prev_calls ))
    d_cost=$(python3 -c "print(f'{${cost} - ${prev_cost}:+.3f}')" 2>/dev/null || echo "?")

    # Window header text
    if [ "$W_IDX" = "-1" ]; then
        win_txt="pre-anchor"
    else
        win_txt="win=$W_IDX rem=${W_REM}m"
    fi

    now_kst=$(TZ=Asia/Seoul date +%H:%M:%S)

    # Emit if any of the meaningful fields changed, OR if HEARTBEAT_EVERY_N
    # ticks have passed since the last emit (still-alive signal).
    ticks_since_emit=$((ticks_since_emit + 1))
    if [ "$calls" != "$prev_calls" ] || [ "$cost" != "$prev_cost" ] || [ "$inflight" != "$prev_inflight" ] || [ "$ticks_since_emit" -ge "$HEARTBEAT_EVERY_N" ]; then
        marker=""
        if [ "$calls" = "$prev_calls" ] && [ "$cost" = "$prev_cost" ] && [ "$inflight" = "$prev_inflight" ]; then
            marker=" (idle-heartbeat)"
        fi
        echo "$now_kst KST  $win_txt  calls=${calls}(+${d_calls}) tokens=${tokens} cost=\$${cost}(${d_cost})  inflight:${inflight}${marker}"
        ticks_since_emit=0
    fi

    prev_calls=$calls
    prev_cost=$cost
    prev_inflight=$inflight
    sleep "$TICK_S"
done
