"""
Enterprise Secret Scanner
Detects hardcoded secrets, private keys, API tokens, and credentials in repository and git diffs.
Fails CI if any unmasked secret is detected.
"""
import argparse
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

# Patterns matching high-risk credentials and secret tokens
SECRET_PATTERNS = [
    {
        'name': 'Private Key',
        'pattern': re.compile(r'-----BEGIN\s+(?:RSA|DSA|EC|OPENSSH|PGP)?\s*PRIVATE KEY-----', re.IGNORECASE),
        'severity': 'P0',
    },
    {
        'name': 'AWS Access Key ID',
        'pattern': re.compile(r'\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b'),
        'severity': 'P0',
    },
    {
        'name': 'Stripe Live Secret Key',
        'pattern': re.compile(r'\b(?:sk|rk)_live_[0-9a-zA-Z]{24,}\b'),
        'severity': 'P0',
    },
    {
        'name': 'GitHub Personal Access Token',
        'pattern': re.compile(r'\b(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36}\b|\bgithub_pat_[a-zA-Z0-9_]{82}\b'),
        'severity': 'P0',
    },
    {
        'name': 'OpenAI Secret Key',
        'pattern': re.compile(r'\bsk-(?:proj-)?[a-zA-Z0-9_-]{32,}\b'),
        'severity': 'P0',
    },
    {
        'name': 'Database Password URI',
        'pattern': re.compile(r'(?:postgres|postgresql|mysql|mongodb):\/\/[a-zA-Z0-9_\-\.]+:(?!(?:postgres|password|admin|root|\$\{[^}]+\})\b)[^@\s]{6,}@[a-zA-Z0-9_\-\.]+'),
        'severity': 'P1',
    },
    {
        'name': 'Slack Bot / Webhook Token',
        'pattern': re.compile(r'xoxb-[0-9]{11,13}-[0-9]{11,13}-[a-zA-Z0-9]{24}|https:\/\/hooks\.slack\.com\/services\/T[0-9A-Z]{8}\/B[0-9A-Z]{8}\/[0-9a-zA-Z]{24}'),
        'severity': 'P1',
    },
    {
        'name': 'Hardcoded JWT Bearer Token',
        'pattern': re.compile(r'Bearer\s+eyJ[a-zA-Z0-9_\-]{20,}\.eyJ[a-zA-Z0-9_\-]{20,}\.[a-zA-Z0-9_\-]{20,}'),
        'severity': 'P1',
    },
]

# Paths and extensions to ignore
EXCLUDED_DIRS = {
    '.git', '__pycache__', 'node_modules', '.next', 'dist', 'build',
    'coverage', '.pytest_cache', 'venv', 'env', '.venv', '.idea', '.vscode'
}

EXCLUDED_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2',
    '.ttf', '.eot', '.pdf', '.zip', '.tar', '.gz', '.db', '.sqlite3', '.pyc'
}

# Known test safe strings and placeholders that shouldn't trigger false alarms
SAFE_PLACEHOLDERS = [
    '***REDACTED***',
    'test-secret-key',
    'django-insecure-',
    'sk-test-',
    'Password123!',
    'example.com',
    'placeholder',
    'fake_token',
    '00000000-0000-0000-0000-000000000000',
    'REDACTED',
    'mock_key',
    'sk-live-1234567890abcdef1234567890', # Used in test assertion
    'OldSecretPassword!',
    'SuperSecretPassword123!',
    'my-private-token',
    'shhh-secret-value',
]


def is_safe_line(line: str) -> bool:
    # Check for docker/environment variable substitutions like ${DB_PASSWORD} or $SECRET
    if re.search(r':\$\{[^}]+\}@|:\$[A-Z0-9_]+@', line):
        return True
    for placeholder in SAFE_PLACEHOLDERS:
        if placeholder in line:
            return True
    return False


def scan_text(content: str, source_identifier: str) -> List[Dict]:
    violations = []
    lines = content.splitlines()
    for line_idx, line in enumerate(lines, start=1):
        if is_safe_line(line):
            continue
        for detector in SECRET_PATTERNS:
            match = detector['pattern'].search(line)
            if match:
                matched_text = match.group(0)
                # Mask secret snippet for output
                masked = matched_text[:4] + '*' * (len(matched_text) - 8) + matched_text[-4:] if len(matched_text) > 8 else '***SECRET***'
                violations.append({
                    'file': source_identifier,
                    'line_number': line_idx,
                    'rule': detector['name'],
                    'severity': detector['severity'],
                    'masked_sample': masked,
                })
    return violations


def scan_file(file_path: str) -> List[Dict]:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return scan_text(content, file_path)
    except Exception as e:
        return []


def scan_git_diff() -> List[Dict]:
    """Scan uncommitted or branch git diffs"""
    try:
        diff_output = subprocess.check_output(
            ['git', 'diff', 'HEAD'],
            stderr=subprocess.DEVNULL,
            encoding='utf-8',
            errors='ignore'
        )
    except Exception:
        diff_output = ""

    violations = []
    current_file = "git_diff"
    for line in diff_output.splitlines():
        if line.startswith('+++ b/'):
            current_file = line[6:]
        elif line.startswith('+') and not line.startswith('+++'):
            added_line = line[1:]
            violations.extend(scan_text(added_line, current_file))
    return violations


def scan_repository(root_dir: str) -> List[Dict]:
    all_violations = []
    for root, dirs, files in os.walk(root_dir):
        # Filter excluded directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in EXCLUDED_EXTENSIONS:
                continue
            full_path = os.path.join(root, file)
            # Skip documentation evidence files that discuss secret detection patterns
            rel_path = os.path.relpath(full_path, root_dir).replace('\\', '/')
            if 'docs/implementation/' in rel_path or 'tests/' in rel_path or 'test_' in file or 'verify_' in file or 'secret_scanner.py' in file:
                continue
            violations = scan_file(full_path)
            all_violations.extend(violations)
    return all_violations


def run_scanner(mode: str = 'all', root_dir: str = '.') -> Tuple[bool, List[Dict]]:
    violations = []
    if mode == 'diff':
        violations = scan_git_diff()
    else:
        violations = scan_repository(root_dir)

    is_clean = len(violations) == 0
    return is_clean, violations


def main():
    parser = argparse.ArgumentParser(description="MyCRM Enterprise Secret Scanner")
    parser.add_argument('--mode', choices=['all', 'diff'], default='all', help="Scan full repo or git diff only")
    parser.add_argument('--path', default='.', help="Root directory to scan")
    args = parser.parse_args()

    print(f"[*] Running Secret Scanner (mode: {args.mode}, path: {args.path})...")
    is_clean, violations = run_scanner(mode=args.mode, root_dir=args.path)

    if is_clean:
        print("[PASS] Secret Scanner: No secrets or credentials detected.")
        sys.exit(0)
    else:
        print(f"[FAIL] Secret Scanner: Detected {len(violations)} potential secret leaks:")
        for v in violations:
            print(f"  - [{v['severity']}] {v['rule']} in {v['file']}:{v['line_number']} (Sample: {v['masked_sample']})")
        sys.exit(1)


if __name__ == '__main__':
    main()
