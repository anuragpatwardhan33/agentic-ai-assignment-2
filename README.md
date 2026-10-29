# Intelligent Student Support Agent — Assignment 2

## 1. Project Overview

The Intelligent Student Support Agent is a Python-based agentic AI application designed to assist students with academic questions and student-support tasks.

The application uses a Large Language Model (LLM), Python tools, local handbook retrieval, persistent memory, and execution tracing. Assignment 2 extends the existing agent with **student privacy and access control, reviewer authorization, approval workflows, audit logging, and controlled execution of approved changes**.

The project demonstrates how an AI agent can use tools while keeping sensitive student-record operations subject to application-level authorization checks.

## 2. Features

- **LLM-powered responses:** Uses the Groq API to generate responses to student questions.
- **Tool calling:** Selects and executes registered Python functions according to the student's query.
- **Attendance calculator:** Calculates attendance percentages.
- **Course schedule lookup:** Retrieves sample course deadlines and schedule information.
- **Student handbook retrieval:** Searches a local handbook for relevant academic information.
- **Persistent memory:** Saves and retrieves selected non-sensitive student preferences using JSON.
- **Student identity verification:** Checks whether a student is permitted to access their own record.
- **Privacy and access control:** Prevents access to another student's private fee information.
- **Scholarship change requests:** Creates requests to change scholarship bank details and stores them with a pending status.
- **Reviewer authorization:** Requires a configured reviewer key before an approval decision can be made.
- **Approval workflow:** Supports approval or rejection of pending requests.
- **Audit logging:** Records authorization attempts, approval decisions, and execution outcomes.
- **Controlled execution:** Blocks pending or rejected requests, missing bank details, unsupported actions, and repeat execution.
- **Execution tracing:** Records response latency, selected tools, and token usage.
- **Evaluation logging:** Saves agent run details and retrieved evidence to CSV files.
- **Chat interface:** Provides a browser-based interface through Streamlit.

The approval and execution functions are kept outside the LLM's registered tool list. The AI agent cannot directly invoke them through the current tool-calling loop.

## 3. Technology Stack

- Python
- Groq API
- Streamlit
- python-dotenv
- JSON and CSV
- pathlib and datetime
- VS Code
- PowerShell

## 4. Project Structure

```text
student-support-agent-assignment2/
├── app.py
├── streamlit_app.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
├── memory.json
├── approval_requests.json
├── audit_log.json
├── evaluation_log.csv
├── evaluation_results.csv
├── test_privacy.py
├── test_approval.py
├── test_execution.py
└── data/
    ├── student_handbook.txt
    └── student_records.json
```

The `.venv/` directory contains the local Python virtual environment and should not be committed to GitHub.

The `.env` file stores configuration and secret keys. It must remain private and must not be committed to the repository.

The JSON files store demonstration student records, approval requests, audit events, and persistent memory. CSV files store execution traces and evaluation results.

## 5. Setup Instructions

### Prerequisites

- Python installed on the computer.
- A valid Groq API key.
- Internet access for LLM requests.
- Visual Studio Code or another Python-compatible editor.

### Step 1: Open the project

Open the `student-support-agent-assignment2` folder in VS Code.

### Step 2: Activate the virtual environment

In the VS Code PowerShell terminal, run:

```powershell
.\.venv\Scripts\Activate.ps1
```

If the virtual environment has not been created, create it first:

```powershell
python -m venv .venv
```

### Step 3: Install dependencies

With the virtual environment activated, run:

```powershell
python -m pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create or update the `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_api_key
APPROVAL_REVIEWER_KEY=your_private_reviewer_secret
```

Replace both example values with your own secrets. Use a strong, unique reviewer key.

The application must load the environment variables before using them. Never print, share, or commit these secrets.

## 6. Running the Application

### Terminal-based agent

Run:

```powershell
python app.py
```

Enter a student-support question when prompted.

Example:

```text
What is my fee status for student STU001?
```

The agent selects an appropriate registered tool, processes its result, and generates a response.

### Streamlit interface

If the Streamlit interface is included and configured for this project, run:

```powershell
python -m streamlit run streamlit_app.py
```

Open the local URL displayed in the terminal.

The terminal-based agent and Streamlit interface should be tested separately because they may use different application flows.

## 7. Privacy and Access Control

The application demonstrates access control using a logged-in demo student identity.

The student-record access function checks whether the requested student ID matches the configured logged-in identity and exists in the student-record data.

For example:

- `STU001` requests their own fee status: access is allowed.
- `STU001` requests `STU002`'s fee status: access is denied.

The access check is performed by Python rather than relying only on the LLM's instructions.

Student records are demonstration data and must not be treated as actual institutional records.

## 8. Scholarship Change Approval Workflow

The scholarship change workflow separates requesting a change, approving it, and executing it.

### Step 1: Create a request

The application checks student access and creates a request containing the request ID, student ID, requested action, proposed bank details, and pending status.

### Step 2: Authorize the reviewer

The approval function checks the supplied reviewer key against the configured environment variable.

An incorrect or missing reviewer key results in a denied approval attempt, which is recorded in the audit log.

### Step 3: Approve or reject

A valid reviewer can approve or reject a pending request.

An approved request is authorized for execution but is not automatically executed by the approval function.

A rejected request remains ineligible for execution.

### Step 4: Execute an approved request

The execution function checks that the request exists and has an approved status. It also checks that the student record exists, the requested action is supported, and the bank details are present.

If the checks pass, the demonstration implementation updates the student-record JSON file, marks the request as executed, and writes an execution audit event.

Repeat execution is blocked because the request is no longer in the approved state.

**Important:** The current implementation is a local educational demonstration. Production deployment would require stronger reviewer authentication, integrity protection for approval records, and additional safeguards against concurrent requests and unauthorized modification of local files.

## 9. Audit Logging

The application stores audit records in `audit_log.json`.

The records include:

- Timestamp
- Student ID or an unknown identifier for an unauthorized attempt
- Requested action
- Permission result
- Approval status
- Execution result

Example outcomes include:

- `permission: denied`
- `approval_status: not_authorized`
- `result: not_executed`
- `approval_status: approved`
- `approval_status: executed`
- `result: executed`

The audit log supports review of authorization attempts and changes performed by the demonstration workflow. A local JSON audit log is not tamper-proof and should not be treated as a production security audit system.

## 10. Testing and Verification

Run the tests from the project root with the virtual environment activated.

### Syntax verification

```powershell
python -m py_compile app.py test_privacy.py test_approval.py test_execution.py
```

### Privacy test

```powershell
python test_privacy.py
```

Expected behavior:

- The student's own record can be accessed.
- Another student's record is denied.

### Approval test

```powershell
python test_approval.py
```

Expected behavior:

- A request is created with pending status.
- A valid reviewer key allows the approval decision.
- An incorrect reviewer key is denied.
- Unauthorized approval attempts are recorded in the audit log.

The test script uses the configured reviewer key for the successful approval case. To test the invalid-key case, use an incorrect key in the test call and verify that the request remains pending.

### Execution test

```powershell
python test_execution.py
```

The execution test uses temporary files to avoid changing the original student-record data.

It verifies:

1. Pending requests are blocked.
2. Approved requests can execute.
3. Repeat execution is blocked.
4. Requests with missing bank details are rejected.

### Agent tool tests

Run `python app.py` and test the registered tools with questions about fee status, attendance, course schedules, and handbook policies.

The actual output depends on the sample data and the configured LLM.

## 11. Tracing and Evaluation

The application records run-level metrics, including:

- Selected tools
- Response latency
- Input token count
- Output token count
- Total reported token usage
- Retrieved handbook or memory evidence

`evaluation_log.csv` stores agent execution traces.

`evaluation_results.csv` stores evaluation results where the evaluation workflow writes them.

The evaluation data is intended to support inspection and demonstration. A small set of manual tests does not establish general model accuracy or production readiness.

## 12. Example Questions

- I attended 18 out of 22 classes. What is my attendance percentage?
- What is the deadline for my Agentic AI assignment?
- What does the student handbook say about attendance?
- What is my fee status for student STU001?
- What is the fee status for student STU002?
- What programme am I studying, and what are my saved preferences?

The final two fee-status examples can be used to demonstrate the difference between authorized and unauthorized access.

## 13. Security and Limitations

- The handbook uses basic keyword-based retrieval.
- The handbook and course schedule contain demonstration data, not official institutional policy.
- The student identity is configured for the demonstration rather than authenticated through a production identity provider.
- The reviewer key is a basic local authorization mechanism, not a complete reviewer authentication system.
- Approval and audit records are stored locally in JSON files and can be modified by users with file access.
- The execution function changes local student-record data when called with an approved request.
- The LLM cannot directly call approval or execution functions through the current registered tool list.
- Application security still depends on protecting local files, environment variables, and the Python execution environment.
- Memory is stored locally and is not automatically shared across devices.
- LLM responses and tool selection may vary across questions.
- LLM requests require internet access and an available Groq model.
- The tests verify the demonstrated scenarios, not every possible security failure.

## 14. GitHub Submission Checklist

Before uploading the project:

- [ ] Include the complete source code.
- [ ] Include `README.md` and `requirements.txt`.
- [ ] Include the test scripts.
- [ ] Include the sample handbook and appropriate demonstration data.
- [ ] Exclude `.env`, API keys, and reviewer secrets.
- [ ] Exclude `.venv/` and unnecessary Python cache files.
- [ ] Review JSON and CSV files for private or sensitive information.
- [ ] Run the syntax checks and all three test scripts.
- [ ] Confirm the README instructions match the actual project files.

## 15. Conclusion

The Intelligent Student Support Agent demonstrates an agentic AI workflow that combines LLM-driven tool selection, local information retrieval, persistent memory, student-record access control, reviewer authorization, approval workflows, audit logging, and controlled execution.

The project illustrates how application-level checks can restrict sensitive operations while allowing an AI agent to assist with routine student-support questions.

The implementation and tests provide an educational demonstration of these concepts and a foundation for further improvements in authentication, authorization, audit integrity, and secure execution.