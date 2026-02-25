from datetime import datetime

# number normalization: 1834013 -> 1,834,013
# date normalization: 20260104 -> 2026-01-04

def format_number(n: int) -> str:
    if n == 0:
        return "0"
    return f"{n:,}"

def format_date(value: str) -> str:
    if value == "":
        return ""
    return datetime.strptime(str(value), "%Y%m%d").strftime("%Y-%m-%d")

def format_time(n: int) -> str:
    secs = n%60
    mins = int(n/60)
    hours = 0

    if mins >= 60:
        hours = int(mins/60)
        mins = mins%60

    time = ""
    if hours > 0:
        time = time + f"{hours}h"

    if mins > 0:
        time = time + f"{mins}m"

    if secs > 0:
        time = time + f"{secs}s"

    return time
