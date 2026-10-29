# Intelligent Student Support Agent

## 1. Project Overview

The Intelligent Student Support Agent is a Python-based agentic AI application designed to help students with academic questions. It uses a large language model (LLM), Python tools, handbook retrieval, persistent memory, and execution tracing to respond to student queries.

## 2. Features

- **LLM-powered responses:** Uses the Groq API to generate answers.
- **Tool calling:** Selects and executes Python functions according to the student's question.
- **Attendance calculator:** Calculates attendance percentages.
- **Course schedule lookup:** Retrieves sample course deadlines and schedule information.
- **Student handbook retrieval:** Searches a local text file for relevant academic information.
- **Persistent memory:** Saves and retrieves non-sensitive student preferences using JSON.
- **Execution tracing:** Records response latency, selected tools, and token usage.
- **Evaluation logging:** Saves agent run details and retrieved evidence to a CSV file.
- **Chat interface:** Provides a browser-based interface using Streamlit.

## 3. Technology Stack

- Python
- Groq API
- Streamlit
- python-dotenv
- JSON and CSV
- VS Code

## 4. Project Structure

```text
student-support-agent/
├── app.py
├── streamlit_app.py
├── requirements.txt
├── README.md
├── .env
├── .gitignore
├── memory.json
├── evaluation_log.csv
├── evaluation_results.csv
└── data/
    └── student_handbook.txt
```

The `.env` file contains the API key and must not be published. The `.venv` folder is a local virtual environment and should not be included in the repository.

## 5. Setup Instructions

### Prerequisites

- Python
- A Groq API key
- Internet access for LLM requests

### Installation

1. Clone or download the project.
2. Open the project folder in VS Code.
3. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root:

   ```text
   GROQ_API_KEY=your_groq_api_key
   ```

   Replace the example value with your own key. Do not share or commit the key.

## 6. Running the Application

Start the browser-based chat interface:

```powershell
python -m streamlit run streamlit_app.py
```

Open the local URL shown in the terminal, normally `http://localhost:8501`.

To run the terminal-based agent directly:

```powershell
python app.py
```

## 7. Example Questions

- I attended 18 out of 22 classes. What is my attendance percentage?
- What is the deadline for my Agentic AI assignment?
- What is the minimum attendance requirement?
- What programme am I studying, and what are my saved study preferences?
- Explain what an AI agent is in simple words.

## 8. Memory and Data

The application uses `memory.json` to store selected non-sensitive student preferences across program runs. The handbook is stored locally in `data/student_handbook.txt`.

The supplied handbook and schedule are demonstration data, not official college policy. Users should verify official deadlines and academic rules through their institution.

## 9. Tracing and Evaluation

The application records run-level metrics, including:

- Selected tools
- Response latency
- Input and output token counts
- Total reported token usage
- Retrieved handbook or memory evidence

`evaluation_log.csv` stores run traces. `evaluation_results.csv` records the expected and observed outcomes of manually tested scenarios.

The initial evaluation uses a small test set and should not be interpreted as proof of general model accuracy.

## 10. Limitations

- The handbook search uses basic keyword matching.
- The sample schedule and handbook are not official institutional records.
- Memory is stored locally and is not shared across devices.
- Model responses and tool selection may vary across questions.
- LLM requests require an available Groq model and an internet connection.

## 11. Conclusion

This project demonstrates an agentic workflow in which an LLM can select Python tools, retrieve relevant local information, use persistent memory, and produce traceable responses through a chat interface.