import os
import json
import time
import csv
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

os.environ["PYTHONIOENCODING"] = "utf-8"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from .env")

client = Groq(api_key=api_key)

MODEL = "openai/gpt-oss-20b"


# --------------------------------
# PERSISTENT MEMORY
# --------------------------------
MEMORY_PATH = Path(__file__).parent / "memory.json"


def load_memory():
    if not MEMORY_PATH.exists():
        return {
            "preferred_name": "",
            "programme": "",
            "preferences": []
        }

    try:
        with MEMORY_PATH.open("r", encoding="utf-8") as file:
            memory = json.load(file)

        if not isinstance(memory, dict):
            raise ValueError("Memory must be a JSON object.")

        memory.setdefault("preferred_name", "")
        memory.setdefault("programme", "")
        memory.setdefault("preferences", [])

        return memory

    except (json.JSONDecodeError, ValueError):
        return {
            "preferred_name": "",
            "programme": "",
            "preferences": []
        }


def save_memory(memory):
    with MEMORY_PATH.open("w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4, ensure_ascii=False)


def remember_preference(preferred_name="", programme="", preference=""):
    memory = load_memory()

    if preferred_name:
        memory["preferred_name"] = preferred_name

    if programme:
        memory["programme"] = programme

    if preference and preference not in memory["preferences"]:
        memory["preferences"].append(preference)

    save_memory(memory)

    return "Useful, non-sensitive information saved to persistent memory."


def get_saved_memory():
    memory = load_memory()

    if not memory["preferred_name"] and not memory["programme"] and not memory["preferences"]:
        return "No saved information yet."

    return json.dumps(memory, indent=2, ensure_ascii=False)



# -------------------------------
# TOOL 1: COURSE SCHEDULE
# -------------------------------
def get_course_schedule(course_name):
    schedules = {
        "agentic ai": "Agentic AI: Complete Assignment 1 by 31 October.",
        "deep learning": "Deep Learning: Review neural networks, CNNs, and training.",
        "image processing": "Image Processing: Review transformations, interpolation, and filtering."
    }

    course = course_name.lower().strip()
    return schedules.get(
        course,
        "Schedule information not found for this course."
    )


# -------------------------------
# TOOL 2: ATTENDANCE CALCULATOR
# -------------------------------
def calculate_attendance(attended, total):
    if total <= 0:
        return "Error: Total classes must be greater than zero."

    if attended < 0 or attended > total:
        return "Error: Attended classes must be between zero and total classes."

    percentage = (attended / total) * 100
    return f"Attendance percentage: {percentage:.2f}%"



# TOOL 3: STUDENT HANDBOOK RETRIEVAL
HANDBOOK_PATH = Path(__file__).parent / "data" / "student_handbook.txt"


def search_student_handbook(question):
    if not HANDBOOK_PATH.exists():
        return "Error: Student handbook file was not found."

    text = HANDBOOK_PATH.read_text(encoding="utf-8")

    sections = text.split("SECTION ")
    question_words = set(question.lower().split())
    matches = []

    for section in sections:
        section_lower = section.lower()

        score = sum(
            1 for word in question_words
            if len(word) > 3 and word in section_lower
        )

        if score > 0:
            matches.append((score, section.strip()))

    matches.sort(key=lambda item: item[0], reverse=True)

    if not matches:
        return (
            "No relevant handbook section found. "
            "Please check official college sources."
        )

    results = [section for score, section in matches[:2]]
    return "\n\n".join(results)


# TOOL REGISTRY — keep this below all three functions
available_tools = {
    "get_course_schedule": get_course_schedule,
    "calculate_attendance": calculate_attendance,
    "search_student_handbook": search_student_handbook,
    "remember_preference": remember_preference,
    "get_saved_memory": get_saved_memory
}


# -------------------------------
# TOOL SCHEMAS
# Tell the LLM which tools exist
# and what arguments they need
# -------------------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_course_schedule",
            "description": "Look up schedule information for a course.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_name": {
                        "type": "string",
                        "description": "Course name, such as Agentic AI."
                    }
                },
                "required": ["course_name"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_attendance",
            "description": "Calculate attendance percentage from attended and total classes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "attended": {
                        "type": "integer",
                        "description": "Number of classes attended."
                    },
                    "total": {
                        "type": "integer",
                        "description": "Total number of classes."
                    }
                },
                "required": ["attended", "total"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_student_handbook",
            "description": (
                "Search the local sample student handbook for relevant "
                "attendance, assignment, examination, or academic support "
                "policies. Use this tool for student policy questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The student's policy question."
                    }
                },
                "required": ["question"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remember_preference",
            "description": (
                "Save useful, non-sensitive student information, "
                "such as their preferred name, programme, or study preferences. "
                "Only save information when the student clearly provides it "
                "for remembering. Never save sensitive information."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "preferred_name": {
                        "type": "string",
                        "description": "Name the student prefers to be called."
                    },
                    "programme": {
                        "type": "string",
                        "description": "Student's academic programme."
                    },
                    "preference": {
                        "type": "string",
                        "description": "A useful, non-sensitive preference."
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_saved_memory",
            "description": (
                "Retrieve previously saved student information "
                "when it is relevant to the current question."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    }
]


# -------------------------------
# AGENT LOOP
# -------------------------------
user_question = input("Ask your student support question: ")
messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful Student Support Assistant."
            "Use the available tools when they are useful."
            "For student policy questions, search the handbook and base"
            "your answer on the retrieved evidence."
            "The handbook is demonstration data, not official college policy."
            "Never invent official policy information."
            "Retrieve saved memory when relevant to the question."
            "Save useful, non-sensitive information only when the student"
            "clearly asks you to remember it."
            "Never save sensitive information."
            "If information is missing, explain that clearlyz"
            "Use get_course_schedule for specific course deadlines"
            "and schedule questions. Use search_student_handbook for"
            "general academic policies and handbook questions."
            "Use get_saved_memory for relevant saved student information."
            "Use calculate_attendance for attendance calculations. "
            )
    },
    {
        "role": "user",
        "content": user_question
    }
]

print("Student Support Agent is starting...\n")

# --------------------------------
# TRACE: INITIALIZE METRICS
# --------------------------------
run_start_time = time.perf_counter()

total_input_tokens = 0
total_output_tokens = 0
tools_used = []
retrieved_evidence = []
run_start_time_iso = datetime.now().isoformat(timespec="seconds")

for step in range(5):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0
    )
    

    # Add token usage from this model call
    if response.usage:
            total_input_tokens += response.usage.prompt_tokens
            total_output_tokens += response.usage.completion_tokens

    message = response.choices[0].message

        # No tool requested: the agent has a final answer
    if not message.tool_calls:
            print("Agent:", message.content.encode("utf-8", errors="replace").decode("utf-8"))
            break

        # Record the assistant's tool request
    messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    call.model_dump(exclude_none=True)
                    for call in message.tool_calls
                ]
            }
        )

    # Execute the requested Python tools
    for call in message.tool_calls:
        tool_name = call.function.name
        print("Tool selected:", tool_name)
        tools_used.append(tool_name)

        try:
            if tool_name not in available_tools:
                raise ValueError("Unknown tool requested.")

            arguments = json.loads(call.function.arguments)
            result = available_tools[tool_name](**arguments)

        
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            result = f"Tool error: {error}"

        if tool_name in (
            "search_student_handbook",
            "get_saved_memory"
        ):
            retrieved_evidence.append(str(result))

        print("Tool result:", result, "\n")

        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result)
            }
        )

else:
    print("Agent stopped: maximum tool steps reached.")


# --------------------------------
# TRACE: REPORT RUN METRICS
# --------------------------------
latency_seconds = time.perf_counter() - run_start_time

print("\n========== AGENT RUN TRACE ==========")
print(f"Latency: {latency_seconds:.2f} seconds")
print("Tools used:", tools_used if tools_used else "None")
print("Total input tokens:", total_input_tokens)
print("Total output tokens:", total_output_tokens)
print("Total tokens:", total_input_tokens + total_output_tokens)
print("=====================================")


# --------------------------------
# SAVE TRACE TO CSV
# --------------------------------
EVALUATION_PATH = Path(__file__).parent / "evaluation_log.csv"

log_row = {
    "timestamp": run_start_time_iso,
    "question": user_question,
    "tools_used": ", ".join(tools_used) if tools_used else "None",
    "latency_seconds": round(latency_seconds, 2),
    "input_tokens": total_input_tokens,
    "output_tokens": total_output_tokens,
    "total_tokens": total_input_tokens + total_output_tokens,
    "retrieved_evidence": " | ".join(retrieved_evidence)
}

file_exists = EVALUATION_PATH.exists()

with EVALUATION_PATH.open(
    "a", newline="", encoding="utf-8"
) as file:
    writer = csv.DictWriter(file, fieldnames=log_row.keys())

    if not file_exists:
        writer.writeheader()

    writer.writerow(log_row)

print("\nEvaluation trace saved to evaluation_log.csv")
