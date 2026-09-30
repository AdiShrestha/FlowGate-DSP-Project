"""Reconstruct ignored raw inputs from recorded digests, without replacing evidence."""
import argparse
import json
import ssl
import urllib.request
from pathlib import Path
from flowgate.acquisition import sha256_file


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--destination',type=Path,required=True)
    ap.add_argument('--ca-file',type=Path,help='Optional trusted PEM CA bundle; TLS verification remains mandatory')
    args=ap.parse_args()
    manifest=json.loads(args.manifest.read_text())
    args.destination.mkdir(parents=True,exist_ok=True)
    context=ssl.create_default_context(cafile=str(args.ca_file) if args.ca_file else None)
    for row in manifest['records']:
        name=Path(row['path']).name
        expected=f"https://data.binance.vision/data/spot/daily/trades/{row['symbol']}/{name}"
        if row['url']!=expected or row['status']!='provider_checksum_verified':
            raise ValueError('unsupported acquisition source/status')
        target=args.destination/name
        if target.exists():
            if sha256_file(target)!=row['sha256']:
                raise ValueError(f'existing archive hash mismatch: {target}')
            print(f'verified existing {name}')
            continue
        partial=target.with_suffix('.zip.partial')
        if partial.exists():
            raise FileExistsError(f'failed/unfinished attempt retained at {partial}; inspect before retry')
        with urllib.request.urlopen(expected,context=context,timeout=60) as response, partial.open('xb') as out:
            for block in iter(lambda:response.read(1024*1024),b''):
                out.write(block)
        if sha256_file(partial)!=row['sha256']:
            raise ValueError(f'provider bytes changed; failed attempt retained at {partial}')
        partial.rename(target)
        print(f'verified acquired {name}')


if __name__=='__main__':main()
