import gradio as gr
import requests

BASE_URL = "http://127.0.0.1:8000" # UPDATE TO YOUR MACHINE IP FOR PORTABLE SHARING
CHAT_URL = f"{BASE_URL}/api/chat"
UPLOAD_URL = f"{BASE_URL}/api/upload-excel"

def query_fastapi_backend(message, history):
    if not message.strip():
        return "", history

    payload = {"question": message}
    try:
        response = requests.post(CHAT_URL, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No response text received.")
            mode = data.get("mode", "Unknown Engine")
            formatted_answer = f"{answer}\n\n---\n*⚡ Engine: {mode}*"
        else:
            error_detail = response.json().get("detail", "Unknown backend error")
            formatted_answer = f"❌ **Backend Error:** {error_detail}"
    except Exception as e:
        formatted_answer = f"⚠️ **Connection Error:** {str(e)}"

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": formatted_answer})
    return "", history

# Handles multi-sheet configuration uploading
def handle_excel_upload(file, mappings_text):
    if file is None:
        return "❌ Please select an Excel workbook first."
        
    try:
        with open(file.name, "rb") as f:
            files = {"file": (file.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            data = {"sheet_mappings": mappings_text.strip()}
            
            response = requests.post(UPLOAD_URL, files=files, data=data, timeout=60)
            
        if response.status_code == 200:
            res_data = response.json()
            log_output = f"✅ {res_data['message']}\n\n"
            for item in res_data['details']:
                log_output += f"📁 Sheet '{item['sheet']}' ➔ Table '{item['target_table']}' ({item['rows']} rows imported)\n"
            return log_output
        else:
            error_detail = response.json().get("detail", "Processing failed")
            return f"❌ Server Error: {error_detail}"
            
    except Exception as e:
        return f"⚠️ Connection failed during file upload: {str(e)}"

def autofill_sample_query(evt: gr.SelectData):
    return evt.value

custom_css = """
body, .gradio-container { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
.sidebar-panel { background-color: #0f172a !important; border-right: 1px solid #1e293b !important; padding: 20px !important; border-radius: 12px; }
footer { display: none !important; }
"""

with gr.Blocks() as demo:
    gr.HTML("""
        <div style="border-bottom: 1px solid #1e293b; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <h1 style="color: #2dd4bf; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">📈 TraderBlotter AI Engine</h1>
                <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 12px;">Multi-Sheet Ingestion & SQL Modeling Terminal</p>
            </div>
        </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=1, elem_classes="sidebar-panel"):
            gr.Markdown("### 📤 Multi-Sheet Ingestion")
            gr.Markdown("Drop your multi-sheet workbook below. You can map explicit names or leave blank to auto-name tables after sheets.")
            
            excel_file = gr.File(label="Select Workbook (.xlsx, .xls)", file_types=[".xlsx", ".xls"])
            
            target_mappings = gr.Textbox(
                label="Table Destination Mappings (Optional)", 
                placeholder="Sheet1=funds, Sheet2=daily_pnl",
                info="Format: SheetName=TableName separated by commas. Leaves unmapped sheets matching their original name."
            )
            
            upload_btn = gr.Button("Ingest & Clean Workbook", variant="secondary")
            upload_status = gr.Textbox(label="Ingestion Logs", interactive=False, placeholder="Status: Idle")
            
            gr.HTML("<hr style='border:0; border-top:1px solid #334155; margin:15px 0;'>")
            gr.Markdown("### 💡 Quick Analytics Templates")
            sample_queries = gr.Dataset(
                components=[gr.Textbox(visible=False)],
                label="Templates",
                samples=[
                    ["Show me top 3 funds by daily PnL"],
                    ["What is the worst PnL for Emma Jenkins?"]
                ],
                type="values"
            )
            
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="Active Database Execution Session",
                height=580,
                placeholder="<div style='text-align: center; color: #64748b; padding-top: 180px;'><p style='font-size: 15px;'>Terminal Session Online.</p></div>"
            )
            
            with gr.Row():
                txt_input = gr.Textbox(show_label=False, placeholder="Ask questions about your data structures...", scale=5)
                submit_button = gr.Button("Execute", variant="primary", scale=1)

            txt_input.submit(query_fastapi_backend, [txt_input, chatbot], [txt_input, chatbot])
            submit_button.click(query_fastapi_backend, [txt_input, chatbot], [txt_input, chatbot])
            sample_queries.select(autofill_sample_query, None, txt_input)
            upload_btn.click(handle_excel_upload, [excel_file, target_mappings], upload_status)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861, share=True, css=custom_css, theme=gr.themes.Soft())