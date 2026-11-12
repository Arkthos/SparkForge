"""Portable entry point for the earlier authored checkpoint verifier.

The historical copies were not byte-identical. Both now share the stronger
size, digest, duplicate, path and archive checks; this is consolidation, not a
claim that the original source files were duplicates.
"""

from zipfile import BadZipFile

from .._common import safe_main
from .verify_checkpoint import digest, main as verify_main, safe_path, verify


def main(argv=None):
    return verify_main(argv)


if __name__ == "__main__":
    try:
        safe_main(main)
    except BadZipFile:
        print('{"status":"FAIL","error_type":"INVALID_CHECKPOINT_ARCHIVE"}')
        raise SystemExit(1) from None
