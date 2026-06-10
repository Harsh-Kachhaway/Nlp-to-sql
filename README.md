# TraderBlotter AI Workspace Terminal

## Quick Start

Follow these steps in order to launch the entire application stack from the parent workspace directory.

1. **Install Dependencies**
Open a terminal in the parent folder and run:
```text
pip install -r requirements.txt

```


2. **Launch the Backend Server**
Double-click `run_backend.bat` (or execute `run_backend.ps1` via PowerShell). This must remain running in the background to handle the database and AI coordination.
3. **Launch Your Preferred Frontend Client**
* To use the premium web console: Double-click `run_frontend_html.bat`. It will automatically launch the interface in your default web browser.
* To use the shareable interface: Double-click `run_frontend_gradio.bat`. This builds a secure network tunnel and outputs a public sharing link.



---

## How It Works

This system is decoupled into a high-performance backend architecture and multiple independent frontend interfaces.

### Data Ingestion Pipeline

When an Excel workbook is dropped into either frontend interface, the file stream is passed to the FastAPI `/api/upload-excel` endpoint. The backend uses Pandas to iterate through every worksheet.

To prevent database crashes, a custom sanitizer scans the columns, transforms data shapes (like converting timestamps into safe text strings), and normalizes all missing or null cell blocks to absolute numerical 0 values. The cleaned rows are then dynamically appended or merged into the SQLite `out.db` binary.

### Dynamic Context Injection

Instead of forcing the AI model to blindly look for tables using multiple sequential API requests (which drains your rate limits), the backend executes a live structural analysis using SQLAlchemy inspectors right when you submit a question.

The application maps the current database state and attaches it directly as a system guardrail instruction to the prompt. The AI receives the table layout immediately, skips the exploratory phase, translates the English request into an exact SQL statement, and pulls the relevant records in a single loop execution.

### Multi-Client Architecture

Both the Gradio engine wrapper and the native vanilla HTML5 application function as completely decoupled clients. They communicate asynchronously via JSON payloads over standard network networks to your laptop, acting as the centralized hosting server.

Application Screenshots
Here are some images showing the operational layouts of the system terminals and execution layers:
<img width="1919" height="1079" alt="Screenshot 2026-06-10 212606" src="https://github.com/user-attachments/assets/a34ecaae-ffd4-4230-93fc-b4907e8e90d4" />
<img width="1919" height="1077" alt="Screenshot 2026-06-10 212440" src="https://github.com/user-attachments/assets/7fc0f484-20c6-4a57-a20f-26c93e7b2312" />
<img width="592" height="648" alt="image (1)" src="https://github.com/user-attachments/assets/9c477036-e6e5-4492-ac32-61b63bf1a5be" />
<img width="1919" height="1077" alt="Screenshot 2026-06-10 212744" src="https://github.com/user-attachments/assets/f675f4a9-2d0f-47a5-886b-62002c9b89f5" />


---

## Troubleshooting

### Stuck or Receiving Rate Limit/Resource Exhausted Errors

If your analytics queries fail with a 429 error code or a compilation timeout statement, the system has exceeded the temporary public allocation limits enforced on the free API tier.

> **Crucial Fix:** Open your environment configuration file named `.env` located inside the project folder, locate the variable `GOOGLE_API_KEY`, and replace the string with a valid production credential or billing-enabled account token. Alternatively, switch your processing node toggle over to a local instance like Ollama to completely bypass external cloud quota limits.
