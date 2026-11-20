#!/usr/bin/env python3
"""BareBones Projects. Read canonical star records without modifying master CSV."""
import argparse,json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen
def main():
 p=argparse.ArgumentParser();p.add_argument('--base',default='http://127.0.0.1:8090');p.add_argument('--output',default='data/alt_database_stars.json');args=p.parse_args()
 parsed=urlparse(args.base)
 if parsed.scheme!='https' and not(parsed.scheme=='http' and parsed.hostname in ('localhost','127.0.0.1','::1')):raise ValueError('HTTPS required')
 with urlopen(args.base.rstrip('/')+'/api/v1/entities?kind=star',timeout=8) as response:data=json.load(response)
 if data.get('schema_version')!='1' or not isinstance(data.get('entries'),list):raise ValueError('Invalid canonical response')
 if any(e.get('kind')!='star' or e.get('visibility')!='public' for e in data['entries']):raise ValueError('Invalid star data')
 target=Path(args.output);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(data,indent=2)+'\n')
 print(len(data['entries']),'approved stars exported')
if __name__=='__main__':main()
