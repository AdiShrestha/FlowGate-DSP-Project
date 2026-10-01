"""Checksummed HTTPS reconstruction with an append-only attempt history.

These receipts describe acquisition, not experimental results or natural
labels. Failed network requests and partial bytes remain visible. Atomic
publication refuses to overwrite a target created by another process.
"""
import json
import os
import ssl
import uuid
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from .acquisition import sha256_file
from .manifest import read_acquisition_manifest


def _now():
    return datetime.now(timezone.utc).isoformat()


def reconstruct(manifest_path, destination, *, ca_file=None):
    manifest = read_acquisition_manifest(manifest_path)
    # Resolve TLS trust before creating an attempt or making a request.
    context = ssl.create_default_context(cafile=str(ca_file) if ca_file else None)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for row in manifest['records']:
        name = Path(row['path']).name
        target = destination / name
        attempts = destination / '.acquisition_attempts' / name
        attempts.mkdir(parents=True, exist_ok=True)
        attempt = attempts / uuid.uuid4().hex
        attempt.mkdir()
        partial = attempt / 'archive.partial'
        receipt_path = attempt / 'receipt.json'
        receipt = {'schema_version': 1, 'source_id': row['source_id'],
                   'url': row['url'], 'expected_sha256': row['sha256'],
                   'started_at_utc': _now(), 'status': 'STARTED',
                   'tls_verification': 'required', 'archive': name,
                   'attempt_id': attempt.name}
        def save():
            staged = attempt / 'receipt.tmp'
            staged.write_text(json.dumps(receipt, indent=2, allow_nan=False) + '\n')
            staged.replace(receipt_path)
        save()
        try:
            if target.exists():
                digest = sha256_file(target)
                if digest != row['sha256']:
                    raise ValueError('existing archive hash mismatch; target retained')
                receipt.update(status='VERIFIED_EXISTING', observed_sha256=digest,
                               bytes=target.stat().st_size)
            else:
                with partial.open('xb') as out, urllib.request.urlopen(row['url'], context=context, timeout=60) as response:
                    for block in iter(lambda: response.read(1024 * 1024), b''):
                        out.write(block)
                digest = sha256_file(partial)
                receipt.update(observed_sha256=digest, bytes=partial.stat().st_size)
                if digest != row['sha256']:
                    raise ValueError('acquired bytes differ from recorded provider digest')
                # link() is an atomic no-replace operation on this filesystem.
                os.link(partial, target)
                partial.unlink()
                receipt['status'] = 'VERIFIED_ACQUIRED'
        except BaseException as error:
            receipt.update(status='FAILED_RETAINED', error_type=type(error).__name__,
                           error=str(error), partial_bytes=partial.stat().st_size if partial.exists() else None,
                           finished_at_utc=_now())
            save()
            raise
        receipt['finished_at_utc'] = _now()
        save()
        yield receipt
