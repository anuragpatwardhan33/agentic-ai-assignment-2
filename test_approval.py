import os
import copy
from pathlib import Path
import json

app_path = Path(__file__).with_name("app.py")
source = app_path.read_text(encoding="utf-8")
prefix = source.split("# TOOL REGISTRY", 1)[0]

namespace = {"__file__": str(app_path)}
exec(compile(prefix, str(app_path), "exec"), namespace)

request_change = namespace["request_scholarship_change"]
decide_approval = namespace["decide_approval"]
approval_path = Path(__file__).with_name("approval_requests.json")

# Start with an empty request list for this test
approval_path.write_text("[]", encoding="utf-8")

# Create a sensitive change request
result = request_change("STU001", "XXXX-9999")
print("Request:", result)

# Verify the request is pending
requests = json.loads(approval_path.read_text(encoding="utf-8"))
print("Initial status:", requests[0]["status"])

# Approve the request
result = decide_approval(
    requests[0]["request_id"],
    "approved",
    os.getenv("APPROVAL_REVIEWER_KEY")
)

# Check the audit log
audit_path = Path(__file__).with_name("audit_log.json")
audit_records = json.loads(
    audit_path.read_text(encoding="utf-8")
)

print("Audit records:", len(audit_records))

if audit_records:
    print("Latest audit event:", audit_records[-1])
else:
    print("No audit events recorded.")

print("\nAll audit events:")
for event in audit_records:
    print(event)

# Verify the final approval status
with approval_path.open("r", encoding="utf-8") as file:
    requests = json.load(file)

print("Final status:", requests[0]["status"])

# Save bank details before rejection
records_path = Path(__file__).with_name("data") / "student_records.json"
records_before = json.loads(
    records_path.read_text(encoding="utf-8")
)
bank_before = records_before["STU001"]["scholarship_bank_details"]

# --------------------------------
# TEST 2: REJECTED REQUEST
# --------------------------------

print("\nTest 2 - Rejected request")

# Create a fresh pending request
result = request_change("STU001", "XXXX-2222")
print("Request:", result)

requests = json.loads(
    approval_path.read_text(encoding="utf-8")
)

# Get the newly created request
rejected_request = requests[-1]
request_id = rejected_request["request_id"]

# Reject the request using the authorized reviewer key
result = decide_approval(
    request_id,
    "rejected",
    os.getenv("APPROVAL_REVIEWER_KEY")
)

print("Decision result:", result)

# Verify the final request status
requests = json.loads(
    approval_path.read_text(encoding="utf-8")
)

print("Final rejected status:", requests[-1]["status"])

records_after = json.loads(
    records_path.read_text(encoding="utf-8")
)
bank_after = records_after["STU001"]["scholarship_bank_details"]

print("Bank details unchanged:", bank_before == bank_after)