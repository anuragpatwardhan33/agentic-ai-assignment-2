import re
import subprocess
import sys
from pathlib import Path

import streamlit as st

PROJECT_DIR = Path(__file__).parent
AGENT_FILE = PROJECT_DIR / "app.py"

st.set_page_config(
    page_title="Student Support Agent",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Intelligent Student Support Agent")
st.caption(
    "Ask about course schedules, attendance, academic policies, "
    "or your saved study preferences."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display earlier messages in this browser session
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("trace"):
            with st.expander("View run trace"):
                st.code(message["trace"])

# Accept a new question
question = st.chat_input("Ask your student support question...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and checking available tools..."):
            try:
                result = subprocess.run(
                    [sys.executable, "-u", str(AGENT_FILE)],
                    input=question + "\n",
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=str(PROJECT_DIR),
                    timeout=120
)

                output = result.stdout
                if result.returncode != 0:
                    st.error("The agent encountered an error.")
                    st.code(result.stderr[-3000:])
                    st.stop()

                # Extract the final answer from terminal output
                match = re.search(
                    r"Agent:\s*(.*?)\n\s*=+\s*AGENT RUN TRACE",
                    output,
                    re.DOTALL
                )

                if match:
                    answer = match.group(1).strip()
                else:
                    answer = (
                        "The agent finished, but its final answer "
                        "could not be extracted. Check the run trace."
                    )

                # Extract the measurement report
                marker = "========== AGENT RUN TRACE =========="
                trace_start = output.find(marker)

                trace = (
                    output[trace_start:]
                    if trace_start >= 0
                    else "No run trace was found."
                )

                clean_answer = answer.replace("â€¦", "").replace("…", "")
                clean_answer = clean_answer.replace(" %", "%")
                st.text(clean_answer)

                with st.expander("View run trace"):
                    st.code(trace)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "trace": trace
                })

            except subprocess.TimeoutExpired:
                st.error("The agent took too long. Please try again.")
            except Exception as error:
                st.error(f"Could not run the agent: {error}")
