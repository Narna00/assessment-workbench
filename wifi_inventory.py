"""Compare a normalized passive Wi-Fi CSV export to an owned-BSSID inventory."""
import argparse
import csv
import json
from pathlib import Path
import re
import sys


def bssid(value):
    value=value.strip().lower()
    if not re.fullmatch(r'(?:[0-9a-f]{2}:){5}[0-9a-f]{2}',value):
        raise ValueError('Malformed BSSID')
    return value


def compare(rows,owned):
    allow={bssid(item) for item in owned}
    observations={}
    for row in rows:
        key=bssid(row['bssid'])
        record=observations.setdefault(key,{'bssid':key,'owned':key in allow,'ssids':set(),'channels':set()})
        record['ssids'].add(row['ssid'])
        record['channels'].add(row['channel'])
    return [{'bssid':key,'owned':value['owned'],'ssids':sorted(value['ssids']),'channels':sorted(value['channels'])} for key,value in sorted(observations.items())]


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv',type=Path)
    parser.add_argument('owned',type=Path,help='JSON array of exact BSSIDs')
    args=parser.parse_args()
    try:
        with args.csv.open(encoding='utf-8',newline='') as stream:
            result=compare(csv.DictReader(stream),json.loads(args.owned.read_text(encoding='utf-8')))
        print(json.dumps({'observations':result,'warning':'Unknown means unverified ownership, not rogue AP.'},indent=2))
    except (OSError,ValueError,KeyError,TypeError) as error:
        print(f'error: {error}',file=sys.stderr)
        sys.exit(2)
