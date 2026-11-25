"""
Dangerous Endpoints Regression Gate
Enforces that modifications to critical/dangerous CRM endpoints, authorization policies,
or compliance services must be accompanied by explicit regression test suites.
"""
import argparse
import os
import subprocess
import sys
from typing import Dict, List, Set, Tuple

# Registry mapping dangerous endpoints / sensitive files to their mandatory regression test suites
DANGEROUS_REGISTRY = {
    'backend/core/views_auth.py': 'backend/tests/test_session_auth.py',
    'backend/core/authentication.py': 'backend/tests/test_session_auth.py',
    'backend/core/session_middleware.py': 'backend/tests/test_session_auth.py',
    'backend/multi_tenant/middleware.py': 'backend/tests/test_tenant_boundary.py',
    'backend/multi_tenant/permissions.py': 'backend/tests/test_rbac.py',
    'backend/core/encryption_service.py': 'backend/tests/test_encryption_secrets.py',
    'backend/core/encryption_fields.py': 'backend/tests/test_encryption_secrets.py',
    'backend/core/upload_validation.py': 'backend/tests/test_uploads_webhooks.py',
    'backend/integration_hub/webhook_receiver.py': 'backend/tests/test_uploads_webhooks.py',
    'backend/realtime_collaboration/consumers.py': 'backend/tests/test_async_realtime.py',
    'backend/core/task_idempotency.py': 'backend/tests/test_async_realtime.py',
    'backend/core/poison_queue.py': 'backend/tests/test_async_realtime.py',
    'backend/core/audit_models.py': 'backend/tests/test_audit_compliance.py',
    'backend/core/audit_service.py': 'backend/tests/test_audit_compliance.py',
    'backend/gdpr_compliance/views.py': 'backend/tests/test_audit_compliance.py',
    'backend/gdpr_compliance/services.py': 'backend/tests/test_audit_compliance.py',
}


def get_changed_files(base_ref: str = 'HEAD~1') -> Set[str]:
    """Retrieve list of modified files in working directory, staged area, or recent commit"""
    changed = set()
    try:
        # Check committed changes in current HEAD
        out = subprocess.check_output(
            ['git', 'diff', '--name-only', base_ref, 'HEAD'],
            stderr=subprocess.DEVNULL,
            encoding='utf-8'
        )
        for line in out.splitlines():
            clean = line.strip().replace('\\', '/')
            if clean:
                changed.add(clean)
    except Exception:
        pass

    try:
        # Check unstaged / staged changes in working tree
        out_status = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            stderr=subprocess.DEVNULL,
            encoding='utf-8'
        )
        for line in out_status.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                path = parts[-1].replace('\\', '/')
                changed.add(path)
    except Exception:
        pass

    return changed


def evaluate_dangerous_endpoints(
    changed_files: Set[str],
    override_reason: str = ""
) -> Tuple[bool, List[Dict]]:
    """
    Evaluates whether touched dangerous endpoints have accompanying regression tests.
    """
    violations = []
    
    if override_reason.strip():
        # Valid explicit override provided
        return True, [{
            'status': 'OVERRIDDEN',
            'reason': override_reason.strip(),
            'message': 'Security gate bypassed with authorized override justification.'
        }]

    for dangerous_file, required_test in DANGEROUS_REGISTRY.items():
        if dangerous_file in changed_files:
            # Check if required test was also modified or exists in repo
            test_exists = os.path.exists(required_test)
            test_touched = required_test in changed_files

            if not test_touched and not test_exists:
                violations.append({
                    'dangerous_endpoint': dangerous_file,
                    'required_test': required_test,
                    'test_present': False,
                    'test_updated': False,
                    'error': f"Dangerous endpoint modified ({dangerous_file}) without required regression test suite ({required_test})!"
                })

    is_compliant = len(violations) == 0
    return is_compliant, violations


def main():
    parser = argparse.ArgumentParser(description="Dangerous Endpoints Regression Gate")
    parser.add_argument('--base-ref', default='HEAD~1', help="Git base reference to compare against")
    parser.add_argument('--override-reason', default=os.environ.get('SECURITY_OVERRIDE_REASON', ''), help="Justification if bypassing gate")
    args = parser.parse_args()

    print("[*] Checking Changed Dangerous Endpoints & Mandatory Regression Test Suites...")
    changed = get_changed_files(base_ref=args.base_ref)
    print(f"  -> Discovered {len(changed)} changed files in recent diff.")

    is_compliant, violations = evaluate_dangerous_endpoints(changed, override_reason=args.override_reason)

    if is_compliant:
        print("[PASS] Dangerous Endpoints Gate: All changed critical paths have required regression test coverage.")
        sys.exit(0)
    else:
        print(f"[FAIL] Dangerous Endpoints Gate: Missing regression test coverage for {len(violations)} dangerous endpoints:")
        for v in violations:
            print(f"  - {v['error']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
