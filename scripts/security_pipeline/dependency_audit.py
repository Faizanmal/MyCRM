"""
Dependency & Known Vulnerability (CVE) Audit Tool
Evaluates backend dependencies against known high/critical (P0/P1) security advisories.
"""
import argparse
import os
import re
import subprocess
import sys
from typing import Dict, List, Tuple

# Curated catalog of known exploitable P0/P1 advisories for Python CRM dependencies
CRITICAL_ADVISORIES = [
    {
        'package': 'django',
        'vulnerable_below': '4.2.16',
        'cve': 'CVE-2024-45230 / CVE-2024-45231',
        'severity': 'P0',
        'description': 'Potential Denial of Service and Email spoofing / authentication bypass in Django core.',
    },
    {
        'package': 'cryptography',
        'vulnerable_below': '42.0.0',
        'cve': 'CVE-2023-49083 / CVE-2023-50782',
        'severity': 'P1',
        'description': 'Memory corruption / NULL pointer dereference in PKCS7 and encryption parsing.',
    },
    {
        'package': 'pillow',
        'vulnerable_below': '10.2.0',
        'cve': 'CVE-2023-50447',
        'severity': 'P0',
        'description': 'Arbitrary code execution via PIL.ImageMath.eval in image parsing.',
    },
    {
        'package': 'celery',
        'vulnerable_below': '5.2.2',
        'cve': 'CVE-2021-23727',
        'severity': 'P0',
        'description': 'Remote code execution via untrusted deserialization in Celery task backend.',
    },
    {
        'package': 'requests',
        'vulnerable_below': '2.31.0',
        'cve': 'CVE-2023-32681',
        'severity': 'P1',
        'description': 'Proxy-Authorization header leakage to unintended destinations on redirects.',
    },
]


def parse_version_tuple(v_str: str) -> Tuple[int, ...]:
    parts = [int(p) for p in re.findall(r'[0-9]+', v_str)]
    return tuple(parts)


def parse_requirements_file(req_path: str) -> Dict[str, str]:
    packages = {}
    if not os.path.exists(req_path):
        return packages

    with open(req_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Match package==version or package>=version
            match = re.match(r'^([a-zA-Z0-9_\-]+)\s*(?:==|>=|<=|~=)\s*([0-9\.\-a-zA-Z]+)', line)
            if match:
                pkg_name = match.group(1).lower().replace('_', '-')
                pkg_version = match.group(2)
                packages[pkg_name] = pkg_version
    return packages


def get_installed_packages() -> Dict[str, str]:
    packages = {}
    try:
        output = subprocess.check_output(
            [sys.executable, '-m', 'pip', 'list', '--format=freeze'],
            stderr=subprocess.DEVNULL,
            encoding='utf-8'
        )
        for line in output.splitlines():
            if '==' in line:
                name, version = line.split('==', 1)
                packages[name.lower().replace('_', '-')] = version.strip()
    except Exception:
        pass
    return packages


def audit_dependencies(req_path: str = 'backend/requirements.txt') -> Tuple[bool, List[Dict]]:
    req_packages = parse_requirements_file(req_path)
    installed_packages = get_installed_packages()
    
    # Merge, preferring installed versions when present
    active_packages = dict(req_packages)
    active_packages.update(installed_packages)

    vulnerabilities = []
    for advisory in CRITICAL_ADVISORIES:
        pkg = advisory['package']
        if pkg in active_packages:
            active_ver = active_packages[pkg]
            active_tuple = parse_version_tuple(active_ver)
            target_tuple = parse_version_tuple(advisory['vulnerable_below'])
            if active_tuple < target_tuple:
                vulnerabilities.append({
                    'package': pkg,
                    'current_version': active_ver,
                    'fixed_version': advisory['vulnerable_below'],
                    'cve': advisory['cve'],
                    'severity': advisory['severity'],
                    'description': advisory['description'],
                })

    is_clean = len(vulnerabilities) == 0
    return is_clean, vulnerabilities


def main():
    parser = argparse.ArgumentParser(description="Dependency Security & P0/P1 Advisory Audit")
    parser.add_argument('--requirements', default='backend/requirements.txt', help="Path to requirements.txt")
    args = parser.parse_args()

    print(f"[*] Running Dependency Vulnerability Audit on {args.requirements}...")
    is_clean, vulns = audit_dependencies(args.requirements)

    if is_clean:
        print("[PASS] Dependency Audit: No known exploitable P0/P1 vulnerabilities detected.")
        sys.exit(0)
    else:
        print(f"[FAIL] Dependency Audit: Found {len(vulns)} exploitable P0/P1 package issues:")
        for v in vulns:
            print(f"  - [{v['severity']}] {v['package']} v{v['current_version']} < v{v['fixed_version']} ({v['cve']}): {v['description']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
