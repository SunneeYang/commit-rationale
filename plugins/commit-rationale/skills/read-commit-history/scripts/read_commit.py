#!/usr/bin/env python3
"""Read one local commit message in bounded, explicitly resumable chunks.

This is a read-only fallback for tool output truncation, not a history database
or an automatic relevance classifier. Offsets count decoded Unicode characters.
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys


def git(repo, *args):
    result = subprocess.run(
        ['git', '-C', str(repo), '--no-pager', *args],
        capture_output=True, check=False,
    )
    if result.returncode:
        raise ValueError(result.stderr.decode('utf-8', errors='replace').strip())
    return result.stdout


def read_message(repo, revision, offset=0, max_chars=6000):
    if offset < 0 or not 1 <= max_chars <= 20000:
        raise ValueError('offset must be nonnegative; max-chars must be 1..20000')
    # Resolve before show: --end-of-options rejects option injection and the
    # commit peel rejects trees/blobs. No shell, hooks, fetches, or message eval.
    oid = git(repo, 'rev-parse', '--verify', '--end-of-options',
              revision + '^{commit}').decode('ascii').strip()
    message_bytes = git(repo, '-c', 'i18n.logOutputEncoding=UTF-8',
                        'show', '-s', '--format=%B', oid, '--')
    message = message_bytes.decode('utf-8', errors='strict')
    if offset > len(message):
        raise ValueError('offset is beyond the end of this commit message')
    end = min(offset + max_chars, len(message))
    return {
        'commit': oid,
        'offset': offset,
        'next_offset': end if end < len(message) else None,
        'total_chars': len(message),
        'has_more': end < len(message),
        'message': message[offset:end],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('commit', help='A local commit revision, resolved to a full object ID')
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--max-chars', type=int, default=6000)
    args = parser.parse_args()
    try:
        result = read_message(args.repo, args.commit, args.offset, args.max_chars)
    except (OSError, ValueError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
