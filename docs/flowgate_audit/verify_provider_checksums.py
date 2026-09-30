"""Retrieve official checksum bytes with verified TLS; never download substitutions."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import ssl
import urllib.request
from pathlib import Path


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('raw_dir',type=Path)
    ap.add_argument('output',type=Path)
    args=ap.parse_args()
    try:
        import certifi
        context=ssl.create_default_context(cafile=certifi.where())
        ca_source='certifi bundle'
    except ImportError:
        context=ssl.create_default_context();ca_source='system default'
    def check(path):
        symbol=path.name.split('-trades-')[0]
        url=f'https://data.binance.vision/data/spot/daily/trades/{symbol}/{path.name}.CHECKSUM'
        row={'filename':path.name,'checksum_url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        try:
            with urllib.request.urlopen(url,context=context,timeout=30) as response:
                raw=response.read(8192);row['http_status']=response.status
            text=raw.decode('ascii').strip();parts=text.split()
            if len(parts)!=2 or len(parts[0])!=64 or parts[1].lstrip('*')!=path.name:
                raise ValueError('unexpected provider checksum schema')
            int(parts[0],16)
            h=hashlib.sha256()
            with path.open('rb') as stream:
                for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
            row.update(provider_checksum_text=text,provider_sha256=parts[0].lower(),local_sha256=h.hexdigest(),
                       checksum_bytes_sha256=hashlib.sha256(raw).hexdigest())
            row['status']='VERIFIED_MATCH' if row['provider_sha256']==row['local_sha256'] else 'MISMATCH'
        except Exception as e:row.update(status='ERROR',error=repr(e))
        return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        rows=list(executor.map(check,sorted(args.raw_dir.glob('*.zip'))))
    args.output.write_text(json.dumps({'tls_verification':True,'ca_source':ca_source,'records':rows},indent=2)+'\n')
    from collections import Counter
    print(dict(Counter(x['status'] for x in rows)))


if __name__=='__main__':main()
