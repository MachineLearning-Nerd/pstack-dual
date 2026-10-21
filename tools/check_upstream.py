#!/usr/bin/env python3
"""Audit snapshot coverage and require fresh reviews for masked upstream changes."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re


ROOT = Path(__file__).resolve().parent.parent
SHA256 = re.compile(r'[0-9a-f]{64}\Z')
DISPOSITIONS = {'overridden', 'synthesized', 'source-only', 'dormant-reference', 'adapted'}


def safe_path(value: object) -> bool:
    return (isinstance(value, str) and bool(value) and '\\' not in value
            and not PurePosixPath(value).is_absolute()
            and all(part not in {'', '.', '..'} for part in value.split('/')))


def load_json(path: Path, errors: list[str]) -> object:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as error:
        errors.append(f'cannot read {path.name}: {error}')
        return None


def route(source: str) -> tuple[str | None, str]:
    for prefix, destination in (
        ('pstack/skills/', 'skills/'),
        ('cursor-team-kit/skills/', 'skills/'),
        ('pstack/docs/guide/', 'docs/guide/'),
        ('pstack/docs/harness/', 'docs/harness/'),
        ('pstack/assets/', 'assets/'),
        ('pstack/automations/', 'automations/'),
    ):
        if source.startswith(prefix):
            target = destination + source[len(prefix):]
            disposition = 'dormant-reference' if destination in {'automations/', 'docs/harness/'} else 'adapted'
            parts = PurePosixPath(target).parts
            if destination == 'skills/' and (
                    target == 'skills/poteto-mode/SKILL.md'
                    or (len(parts) == 3 and parts[-1] == 'LICENSE')
                    or (len(parts) == 4 and parts[-2:] == ('agents', 'openai.yaml'))):
                disposition = 'synthesized'
            return target, disposition
    if source == 'pstack/agents/comment-sicko.md':
        return 'skills/pstack-harness/references/comment-sicko.md', 'adapted'
    if source == 'pstack/agents/poteto-agent.md':
        return None, 'synthesized'
    return None, 'source-only'


def audit(root: Path, snapshot: Path | None = None, lock: dict | None = None,
          reviews: dict | None = None, check_generated: bool = True) -> dict:
    root = Path(root).resolve()
    snapshot = Path(snapshot) if snapshot is not None else root / 'upstream'
    errors: list[str] = []
    if lock is None:
        lock = load_json(root / 'upstream.lock.json', errors)
    if reviews is None:
        reviews = load_json(root / 'upstream-reviews.json', errors)
    locked: dict[str, str] = {}
    if not isinstance(lock, dict) or not isinstance(lock.get('files'), dict):
        errors.append('lock must contain a files object')
    else:
        if (not isinstance(lock.get('commit'), str)
                or not re.fullmatch(r'[0-9a-f]{40}', lock['commit'])):
            errors.append('lock requires a full lowercase commit ID')
        if lock.get('repository') != 'https://github.com/cursor/plugins.git':
            errors.append('lock must name the official cursor/plugins repository')
        if not isinstance(lock.get('pstack_version'), str) or not lock['pstack_version']:
            errors.append('lock requires a pstack_version')
        for source, digest in lock['files'].items():
            if not safe_path(source):
                errors.append(f'unsafe lock path: {source!r}')
            elif not isinstance(digest, str) or not SHA256.fullmatch(digest):
                errors.append(f'invalid lock hash: {source}')
            else:
                locked[source] = digest

    reviewed: dict[str, dict] = {}
    additions: set[str] = set()
    if (not isinstance(reviews, dict) or type(reviews.get('version')) is not int or reviews.get('version') != 1
            or not isinstance(reviews.get('reviews'), dict)
            or not isinstance(reviews.get('additions'), list)):
        errors.append('review policy requires version 1, a reviews object, and an additions list')
    else:
        for source, entry in reviews['reviews'].items():
            if not safe_path(source):
                errors.append(f'unsafe review path: {source!r}')
                continue
            if not isinstance(entry, dict):
                errors.append(f'invalid review entry: {source}')
                continue
            if (not isinstance(entry.get('sha256'), str)
                    or not SHA256.fullmatch(entry['sha256'])):
                errors.append(f'invalid review hash: {source}')
            if (not isinstance(entry.get('disposition'), str)
                    or entry['disposition'] not in DISPOSITIONS):
                errors.append(f'invalid review disposition: {source}')
            if not isinstance(entry.get('reason'), str) or not entry['reason'].strip():
                errors.append(f'review requires a nonempty reason: {source}')
            evidence = entry.get('evidence')
            if not isinstance(evidence, list) or not evidence:
                errors.append(f'review requires evidence files: {source}')
            else:
                for reference in evidence:
                    if not safe_path(reference):
                        errors.append(f'unsafe evidence path for {source}: {reference!r}')
                    elif (not (root / reference).is_file()
                          or not (root / reference).resolve().is_relative_to(root)):
                        errors.append(f'missing or external evidence for {source}: {reference}')
            reviewed[source] = entry
        for addition in reviews['additions']:
            if not safe_path(addition):
                errors.append(f'unsafe addition path: {addition!r}')
            elif addition in additions:
                errors.append(f'duplicate addition: {addition}')
            else:
                additions.add(addition)

    actual: dict[str, str] = {}
    if not snapshot.is_dir():
        errors.append('snapshot directory is missing')
    else:
        for path in sorted(snapshot.rglob('*')):
            source = path.relative_to(snapshot).as_posix()
            if path.is_symlink():
                errors.append(f'snapshot symlink is unsupported: {source}')
            elif path.is_file():
                actual[source] = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != locked:
        errors.append('snapshot differs from locked file hashes')
    for relative in ('pstack/.cursor-plugin/plugin.json', 'pstack/plugin.json'):
        if relative in actual:
            manifest = load_json(snapshot / relative, errors)
            if (not isinstance(manifest, dict) or not isinstance(lock, dict)
                    or manifest.get('version') != lock.get('pstack_version')):
                errors.append(f'manifest version differs from lock: {relative}')
    for source in sorted(reviewed.keys() - actual.keys()):
        errors.append(f'stale review for removed source: {source}')

    overrides: set[str] = set()
    for path in sorted((root / 'overrides').rglob('*')):
        relative = path.relative_to(root / 'overrides').as_posix()
        if path.is_symlink():
            errors.append(f'override symlink is unsupported: {relative}')
        elif path.is_file():
            overrides.add(relative)
    for addition in sorted(additions - overrides):
        errors.append(f'stale addition without override: {addition}')

    files: list[dict] = []
    covered_overrides: set[str] = set()
    targets: dict[str, str] = {}
    for source, digest in sorted(actual.items()):
        target, disposition = route(source)
        if target is not None:
            if target in targets:
                errors.append(f'multiple source files map to {target}: {targets[target]}, {source}')
            targets[target] = source
            relative = target.removeprefix('skills/') if target.startswith('skills/') else None
            if relative in overrides:
                disposition = 'overridden'
                covered_overrides.add(relative)
        required = disposition != 'adapted'
        entry = reviewed.get(source)
        if required and entry is None:
            errors.append(f'review required ({disposition}): {source}')
        if entry is not None:
            if entry.get('sha256') != digest:
                errors.append(f'review hash differs from current source: {source}')
            if entry.get('disposition') != disposition:
                errors.append(f'review disposition must be {disposition}: {source}')
        if check_generated and target is not None:
            generated = root / target
            if not generated.is_file():
                errors.append(f'missing generated payload: {target} (from {source})')
            elif not generated.resolve().is_relative_to(root):
                errors.append(f'external generated payload: {target}')
            elif (disposition in {'adapted', 'dormant-reference'} and (Path(source).suffix != '.md'
                  or source == 'pstack/agents/comment-sicko.md')
                  and generated.read_bytes() != (snapshot / source).read_bytes()):
                errors.append(f'generated bytes differ from source: {target}')
        files.append({'source': source, 'target': target, 'sha256': digest,
                      'disposition': disposition, 'review_required': required})
    for relative in sorted(overrides - covered_overrides - additions):
        errors.append(f'orphan override requires explicit addition: {relative}')
    for relative in sorted(additions & covered_overrides):
        errors.append(f'addition collides with upstream source: {relative}')
    counts = dict(sorted(Counter(row['disposition'] for row in files).items()))
    counts.update({'files': len(files), 'reviews': len(reviewed), 'additions': len(additions),
                   'errors': len(errors)})
    return {'valid': not errors, 'errors': errors, 'files': files, 'counts': counts,
            'generated_checked': check_generated,
            'scope': 'Source accounting and review freshness, not semantic parity or live host behavior.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--no-generated', action='store_true',
                        help='audit incoming snapshot and review policy before generating')
    args = parser.parse_args()
    result = audit(args.root, check_generated=not args.no_generated)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        verdict = 'VERIFIED' if result['valid'] else 'NOT VERIFIED'
        print(f"{verdict}: {result['counts']['files']} source files; "
              f"{result['counts']['reviews']} reviews; {len(result['errors'])} errors")
        for error in result['errors']:
            print(f'  {error}')
    raise SystemExit(0 if result['valid'] else 1)


if __name__ == '__main__':
    main()
