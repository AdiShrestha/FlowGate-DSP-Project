"""Inventory-wide structural checks. Legacy caches remain non-authoritative."""
import argparse
import json
import zipfile
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('legacy_root',type=Path)
    ap.add_argument('output',type=Path)
    args=ap.parse_args()
    root=args.legacy_root/'load-adaptive-iir/data'
    raw=[]; processed=[]
    for path in sorted((root/'raw').glob('*.zip')):
        row={'path':str(path.relative_to(args.legacy_root))}
        try:
            with zipfile.ZipFile(path) as z:
                row['members']=[{'name':x.filename,'bytes':x.file_size} for x in z.infolist()]
                row['crc_bad_member']=z.testzip()
                row['status']='PASS' if row['crc_bad_member'] is None else 'FAIL'
        except Exception as e:row.update(status='ERROR',error=repr(e))
        raw.append(row)
    for path in sorted((root/'processed').glob('*.parquet')):
        row={'path':str(path.relative_to(args.legacy_root))}
        try:
            table=pq.read_table(path)
            t=table.column('timestamp').to_numpy();p=table.column('price').to_numpy()
            row.update(rows=len(t),columns=table.column_names,
                       nonfinite_timestamp=int((~np.isfinite(t)).sum()),
                       nonfinite_price=int((~np.isfinite(p)).sum()),
                       nonpositive_price=int((p<=0).sum()),
                       decreasing_timestamp=int((np.diff(t)<0).sum()),
                       equal_adjacent_timestamp=int((np.diff(t)==0).sum()))
            row['status']='PASS' if not any(row[k] for k in ('nonfinite_timestamp','nonfinite_price','nonpositive_price','decreasing_timestamp')) else 'FAIL'
        except Exception as e:row.update(status='ERROR',error=repr(e))
        processed.append(row)
    args.output.write_text(json.dumps({'scope':'all ZIP CRCs; every processed timestamp/price; no ground-truth or independence validation','raw':raw,'processed':processed},indent=2)+'\n')
    print('raw',len(raw),'processed',len(processed),'total cache rows',sum(x.get('rows',0) for x in processed))
    print('failures',[x for x in raw+processed if x['status']!='PASS'])


if __name__=='__main__':main()
