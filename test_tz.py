import datetime

def parse_pdf_date(m_str):
    if not m_str: return None
    raw = str(m_str).replace('D:', '').replace("'", "")
    if len(raw) < 14: return None
    dt_part = raw[:14]
    tz_part = raw[14:]
    tz = datetime.timezone.utc
    if tz_part:
        if tz_part.startswith('+') or tz_part.startswith('-'):
            sign = 1 if tz_part[0] == '+' else -1
            digits = tz_part[1:].replace(':', '')
            hours = int(digits[:2]) if len(digits) >= 2 else 0
            mins = int(digits[2:4]) if len(digits) >= 4 else 0
            tz = datetime.timezone(sign * datetime.timedelta(hours=hours, minutes=mins))
    try:
        dt = datetime.datetime.strptime(dt_part, '%Y%m%d%H%M%S')
        return dt.replace(tzinfo=tz)
    except Exception:
        return None

dt = parse_pdf_date("D:20260103160508+05'30'")
print('Parsed dt:', dt.isoformat())
tz_s = dt.strftime('%z')
tz_formatted = f"{tz_s[:3]}:{tz_s[3:]}" if len(tz_s) >= 5 else '+05:30'
print('Date line:', dt.strftime('%Y.%m.%d'))
print('Time line:', f"{dt.strftime('%H:%M:%S')} {tz_formatted}")
