# ARGUS
## An LLM-RAG Guided Unified Reasoning System for Security Operational Centres

ARGUS is an LLM-RAG based security log analysis system that combines security log retrieval, security knowledge retrieval, Retrieval-Augmented Generation (RAG), and a locally hosted language model to analyse security-related queries.

The system provides a FastAPI backend and a lightweight web frontend for submitting security queries and displaying generated security analysis.

---

## 1. Purpose

The purpose of ARGUS is to provide a local security log analysis system that retrieves relevant information from monitored security logs and supporting security knowledge before generating a security analysis.

The system is designed to:

- Process and analyse security log data.
- Retrieve relevant log information for a security query.
- Retrieve relevant security knowledge.
- Combine retrieved information into a RAG context.
- Generate a security analysis using a local language model.
- Present the resulting security assessment through a web interface.
- Provide a REST API through FastAPI.
- Support server-based log synchronisation.

ARGUS is intended as a research and prototype system for security log analysis.

---

## 2. Requirements

### Hardware

ARGUS requires a computer capable of running the Python environment, ChromaDB, Sentence Transformers, and the local language model.

The system was developed and tested on a Windows environment.

### Software

The following software is required:

- Python 3.x
- Ollama
- Git
- A modern web browser
- Windows PowerShell or an equivalent terminal

### Python Dependencies

The Python dependencies required by ARGUS are provided in `requirements.txt`:

```text
fastapi
uvicorn
pydantic
chromadb
sentence-transformers
numpy
requests
```

These dependencies can be installed automatically during the installation process.

### Local Language Model

ARGUS uses Ollama to run the local Llama 3.1 8B model.

Required model:

```text
llama3.1:8b
```

The model must be available through Ollama before performing LLM-based security analysis.

---

## 3. Installation

### 3.1 Open the Project

Open PowerShell and navigate to the ARGUS project directory:

```powershell
cd C:\Users\koush\Desktop\D\ARGUS
```

If the project has been obtained from a Git repository, clone the repository first and then navigate into the project directory.

---

### 3.2 Create a Python Virtual Environment

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, the terminal should display:

```text
(.venv)
```

---

### 3.3 Install Python Dependencies

With the virtual environment activated, install the required Python packages:

```powershell
pip install -r requirements.txt
```

The required packages include FastAPI, Uvicorn, Pydantic, ChromaDB, Sentence Transformers, NumPy, and Requests.

---

### 3.4 Install and Prepare Ollama

Install Ollama and ensure that the Ollama service is running.

Download the required Llama 3.1 8B model:

```powershell
ollama pull llama3.1:8b
```

Verify that the model is available:

```powershell
ollama list
```

The output should contain:

```text
llama3.1:8b
```

---

## 4. How to Execute

ARGUS consists of a FastAPI backend and a lightweight web frontend. Both components should be running before using the web interface.

### 4.1 Start the Backend

Open PowerShell in the project root:

```powershell
cd C:\Users\koush\Desktop\D\ARGUS
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start the FastAPI backend:

```powershell
python -m uvicorn backend.api.app:app --host 127.0.0.1 --port 8001
```

The backend will run at:

```text
http://127.0.0.1:8001
```

Keep this terminal running.

---

### 4.2 Start the Frontend

Open a second PowerShell terminal.

Navigate to the frontend directory:

```powershell
cd C:\Users\koush\Desktop\D\ARGUS\frontend
```

Start the frontend HTTP server:

```powershell
python -m http.server 5500 --directory frontend
```

The frontend will run at:

```text
http://127.0.0.1:5500
```

Keep this terminal running.

---

### 4.3 Open ARGUS

Open a web browser and navigate to:

```text
http://127.0.0.1:5500
```

The ARGUS interface will be displayed.

---

### 4.4 Submit a Security Query

Enter a security-related query into the ARGUS query interface.

For example:

```text
failed SSH authentication brute force attack
```

Submit the query to start the analysis.

ARGUS retrieves relevant security log information and supporting security knowledge, constructs the RAG context, and sends the resulting prompt to the locally running Llama 3.1 8B model through Ollama.

The generated security analysis is then returned through the FastAPI backend and displayed in the frontend.

---

### 4.5 Server Synchronisation

ARGUS also provides server synchronisation functionality for configured log sources.

The synchronisation interface can be used to view the configured server sources and their synchronisation status.

Synchronised log data can then be processed by the ARGUS preprocessing and retrieval pipeline.

---

## 5. Execution Demonstration

The following video demonstrates the execution of ARGUS, including starting the system, accessing the frontend, submitting a security query, and viewing the resulting security analysis.

### YouTube Video
**ARGUS Execution Demonstration**

Watch the project demonstration, including the system interface and execution workflow:

[Watch the ARGUS demonstration on YouTube](https://youtu.be/cPUwVsyx-Ds)

[![ARGUS Execution Demonstration](https://img.youtube.com/vi/cPUwVsyx-Ds/hqdefault.jpg)](https://youtu.be/cPUwVsyx-Ds)

---

## 6. Licence

ARGUS is licensed under the Apache License 2.0.

See the LICENSE file for the complete licence terms.

Copyright 2026 Koushik Pasunoori and Dr Jose Maria Alcaraz Calero.