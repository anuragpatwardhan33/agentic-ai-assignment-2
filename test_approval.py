import os
from pathlib import Path
import json

app_path = Path(__file__).with_name("app.py")
source = app_path.read_text(encoding="utf-8")
prefix = source.split("# AGENT LOOP", 1)[0]

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