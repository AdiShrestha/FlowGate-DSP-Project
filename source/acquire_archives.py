"""Reconstruct ignored raw inputs from recorded digests, without replacing evidence."""
import argparse
from pathlib import Path
from flowgate.download import reconstruct


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',type=Path,required=True)
    ap.add_argument('--destination',type=Path,required=True)
    ap.add_argument('--ca-file',type=Path,help='Optional trusted PEM CA bundle; TLS verification remains mandatory')
    args=ap.parse_args()
    for receipt in reconstruct(args.manifest,args.destination,ca_file=args.ca_file):
        print(f"{receipt['status']}: {receipt['archive']} ({receipt['attempt_id']})")


if __name__=='__main__':main()
