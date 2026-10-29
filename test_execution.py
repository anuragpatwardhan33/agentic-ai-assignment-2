
import json
import tempfile
from pathlib import Path

app_path = Path(__file__).with_name("app.py")
source = app_path.read_text(encoding="utf-8")
prefix = source.split("# TOOL REGISTRY", 1)[0]

with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir)

    # Create isolated test data
    records_path = temp_path / "student_records.json"
    approvals_path = temp_path / "approval_requests.json"
    audit_path = temp_path / "audit_log.json"

    records_path.write_text(
        json.dumps({
            "STU001": {
                "name": "Student One",
                "fee_status": "Paid",
                "scholarship_status": "Approved",
                "scholarship_bank_details": "XXXX-1111"
            }
        }, indent=4),
        encoding="utf-8"
    )
    approvals_path.write_text("[]", encoding="utf-8")
    audit_path.write_text("[]", encoding="utf-8")

    namespace = {"__file__": str(app_path)}
    exec(compile(prefix, str(app_path), "exec"), namespace)

    # Redirect the functions to temporary files
    namespace["STUDENT_RECORDS_PATH"] = records_path
    namespace["APPROVAL_PATH"] = approvals_path
    namespace["AUDIT_LOG_PATH"] = audit_path

    # Create a pending request
    request = {
        "request_id": "TEST001",
        "student_id": "STU001",
        "action": "change_scholarship_bank_details",
        "new_bank_details": "XXXX-9999",
        "status": "pending"
    }
    approvals_path.write_text(json.dumps([request], indent=4), encoding="utf-8")

    execute = namespace["execute_approved_change"]

    # Test 1: Pending request must be blocked
    print("Test 1 — Pending request")
    print(execute("TEST001"))

    records = json.loads(records_path.read_text(encoding="utf-8"))
    print("Bank details:", records["STU001"]["scholarship_bank_details"])

    # Test 2: Approved request may execute
    request["status"] = "approved"
    approvals_path.write_text(json.dumps([request], indent=4), encoding="utf-8")

    print("\nTest 2 — Approved request")
    print(execute("TEST001"))

    records = json.loads(records_path.read_text(encoding="utf-8"))
    print("Bank details:", records["STU001"]["scholarship_bank_details"])


    # Test 2B: Executed request must not execute again
    print("\nTest 2B — Repeat execution")
    print(execute("TEST001"))


    # Test 3: Approved request with missing bank details
    request["status"] = "approved"
    request["new_bank_details"] = ""
    approvals_path.write_text(
        json.dumps([request], indent=4),
        encoding="utf-8"
    )

    print("\nTest 3 — Missing bank details")
    print(execute("TEST001"))

    records = json.loads(
        records_path.read_text(encoding="utf-8")
    )
    print(
        "Bank details:",
        records["STU001"]["scholarship_bank_details"]
    )
