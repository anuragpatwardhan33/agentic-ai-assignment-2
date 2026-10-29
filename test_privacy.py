
from pathlib import Path

# Read the actual Assignment 2 app.py
app_path = Path(__file__).with_name("app.py")
source = app_path.read_text(encoding="utf-8")

# Load definitions without starting the agent loop
prefix = source.split("# TOOL REGISTRY", 1)[0]
namespace = {"__file__": str(app_path)}

exec(compile(prefix, str(app_path), "exec"), namespace)

check_student_access = namespace["check_student_access"]
get_student_fee_status = namespace["get_student_fee_status"]

print("Test 1 — Own record")
print("Access:", check_student_access("STU001"))
print("Result:", get_student_fee_status("STU001"))

print("\nTest 2 — Another student's record")
print("Access:", check_student_access("STU002"))
print("Result:", get_student_fee_status("STU002"))
