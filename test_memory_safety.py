
import json
from pathlib import Path

app_path = Path(__file__).with_name("app.py")
source = app_path.read_text(encoding="utf-8")
prefix = source.split("# TOOL REGISTRY", 1)[0]

namespace = {"__file__": str(app_path)}
exec(compile(prefix, str(app_path), "exec"), namespace)

remember_preference = namespace["remember_preference"]
load_memory = namespace["load_memory"]

# Test 1: Sensitive information must be rejected
result = remember_preference(
    preference="My password is demo-password-123"
)
print("Test 1 - Sensitive information")
print("Result:", result)

# Test 2: Ordinary preferences should still work
result = remember_preference(
    preference="Prefers concise explanations"
)
print("\nTest 2 - Ordinary preference")
print("Result:", result)

# Verify the sensitive text was not stored
memory = load_memory()
saved_text = json.dumps(memory).lower()

print(
    "\nSensitive text absent from memory:",
    "demo-password-123" not in saved_text
)
print(
    "Ordinary preference saved:",
    "Prefers concise explanations" in memory["preferences"]
)