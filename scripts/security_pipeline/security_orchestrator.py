"""
Security Pipeline Orchestrator
Executes all 4 continuous security guardrails:
1. Secret Detection (Private keys, tokens, credentials)
2. Dependency & Vulnerability Audit (P0/P1 CVEs)
3. Tenancy & Authorization Abuse Suite (Isolation, IDOR, Forged Headers, Privilege Escalation)
4. Dangerous Endpoints Regression Gate (Mandatory regression test coverage on sensitive APIs)
"""
import argparse
import datetime
import json
import os
import sys
from typing import Dict, Any

from scripts.security_pipeline.secret_scanner import run_scanner
from scripts.security_pipeline.dependency_audit import audit_dependencies
from scripts.security_pipeline.tenancy_abuse_runner import run_tenancy_abuse_suite
from scripts.security_pipeline.dangerous_endpoints_gate import evaluate_dangerous_endpoints, get_changed_files


def run_pipeline(
    mode: str = 'all',
    root_dir: str = '.',
    report_output: str = 'docs/security/security-pipeline-report.json',
    override_reason: str = ""
) -> Dict[str, Any]:
    print("=" * 80)
    print("EXECUTING ENTERPRISE SECURITY PIPELINE")
    print("=" * 80)

    start_time = datetime.datetime.now(datetime.timezone.utc)
    pipeline_results = {
        'timestamp': start_time.isoformat(),
        'pipeline_status': 'RUNNING',
        'gates': {},
    }

    # GATE 1: Secret Detection
    print("\n[GATE 1/4] Running Secret Detection Scanner...")
    secrets_clean, secret_violations = run_scanner(mode=mode, root_dir=root_dir)
    pipeline_results['gates']['secret_scanner'] = {
        'status': 'PASSED' if secrets_clean else 'FAILED',
        'violations_count': len(secret_violations),
        'violations': secret_violations,
    }
    if secrets_clean:
        print("  [PASS] Gate 1: No secrets or plaintext credentials detected.")
    else:
        print(f"  [FAIL] Gate 1: Detected {len(secret_violations)} secret leaks!")

    # GATE 2: Dependency & Vulnerability Audit (P0/P1)
    print("\n[GATE 2/4] Running Dependency & P0/P1 Vulnerability Audit...")
    dep_clean, dep_violations = audit_dependencies()
    pipeline_results['gates']['dependency_audit'] = {
        'status': 'PASSED' if dep_clean else 'FAILED',
        'vulnerabilities_count': len(dep_violations),
        'vulnerabilities': dep_violations,
    }
    if dep_clean:
        print("  [PASS] Gate 2: No known exploitable P0/P1 package advisories detected.")
    else:
        print(f"  [FAIL] Gate 2: Detected {len(dep_violations)} vulnerable dependencies!")

    # GATE 3: Tenancy & Authorization Abuse Suite
    print("\n[GATE 3/4] Running Tenancy & Authz Abuse Test Suite...")
    tenancy_passed, tenancy_results = run_tenancy_abuse_suite()
    pipeline_results['gates']['tenancy_abuse'] = {
        'status': 'PASSED' if tenancy_passed else 'FAILED',
        'tests_executed': len(tenancy_results),
        'results': tenancy_results,
    }
    if tenancy_passed:
        print("  [PASS] Gate 3: All cross-tenant isolation and authorization checks passed.")
    else:
        print("  [FAIL] Gate 3: Identified multi-tenant isolation or authorization boundary flaws!")

    # GATE 4: Dangerous Endpoints Regression Gate
    print("\n[GATE 4/4] Running Dangerous Endpoints Regression Gate...")
    changed_files = get_changed_files()
    gate_passed, gate_violations = evaluate_dangerous_endpoints(changed_files, override_reason=override_reason)
    pipeline_results['gates']['dangerous_endpoints_gate'] = {
        'status': 'PASSED' if gate_passed else 'FAILED',
        'changed_files_count': len(changed_files),
        'violations': gate_violations,
    }
    if gate_passed:
        print("  [PASS] Gate 4: All modified critical endpoints have verified regression test coverage.")
    else:
        print(f"  [FAIL] Gate 4: {len(gate_violations)} critical endpoints modified without regression tests!")

    # Summary
    all_passed = (secrets_clean and dep_clean and tenancy_passed and gate_passed)
    pipeline_results['pipeline_status'] = 'PASSED' if all_passed else 'FAILED'
    pipeline_results['duration_seconds'] = (datetime.datetime.now(datetime.timezone.utc) - start_time).total_seconds()

    # Save JSON report
    os.makedirs(os.path.dirname(report_output), exist_ok=True)
    with open(report_output, 'w', encoding='utf-8') as f:
        json.dump(pipeline_results, f, indent=2)

    print("\n" + "=" * 80)
    if all_passed:
        print(f"SECURITY PIPELINE PASSED ({pipeline_results['duration_seconds']:.2f}s)")
        print(f"Detailed audit artifact saved to: {report_output}")
    else:
        print(f"SECURITY PIPELINE FAILED ({pipeline_results['duration_seconds']:.2f}s)")
        print(f"Check failure details in: {report_output}")
    print("=" * 80)

    return pipeline_results


def main():
    parser = argparse.ArgumentParser(description="MyCRM CI/CD Enterprise Security Pipeline")
    parser.add_argument('--mode', choices=['all', 'diff'], default='all', help="Scan mode for secret detection")
    parser.add_argument('--root', default='.', help="Repository root directory")
    parser.add_argument('--report', default='docs/security/security-pipeline-report.json', help="Output JSON path")
    parser.add_argument('--override-reason', default=os.environ.get('SECURITY_OVERRIDE_REASON', ''), help="Security gate override reason")
    args = parser.parse_args()

    results = run_pipeline(
        mode=args.mode,
        root_dir=args.root,
        report_output=args.report,
        override_reason=args.override_reason,
    )
    if results['pipeline_status'] == 'PASSED':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
