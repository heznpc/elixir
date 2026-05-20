#!/bin/bash
# Persistent monitor heartbeat. Emits one compact line every TICK_S seconds.
# Format:
#   HH:MM:SS KST  win=<idx> rem=<m>m  calls=<n>(<Δ>) tokens=<sum>k(<Δ>) cost=$<sum>(+$<Δ>)  inflight: <list>
#
# Δ shows growth since the previous tick — so a quiet tick (Δ=0) tells you
# whether nothing is running, not whether the runner crashed silently.

set -u
cd /Users/ren/IdeaProjects/Paper/elixir
TICK_S=${TICK_S:-120}

prev_calls=0
prev_tokens=0
prev_cost=0

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
    echo "$now_kst KST  $win_txt  calls=${calls}(+${d_calls}) tokens=${tokens} cost=\$${cost}(${d_cost})  inflight:${inflight}"

    prev_calls=$calls
    prev_tokens=$tokens
    prev_cost=$cost
    sleep "$TICK_S"
done
