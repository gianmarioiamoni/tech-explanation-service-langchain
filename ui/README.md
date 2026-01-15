# 🎨 UI Architecture Documentation

## 📊 Overview

The Gradio UI has been refactored from a monolithic 378-line file into a **modular, maintainable architecture** using the **Component Factory + Event Wiring** pattern.

---

## 📐 Architecture Pattern

### **Component Factory Pattern**
Each UI section is created by a factory function that returns configured Gradio components.

### **Event Wiring Pattern**
Event handlers are grouped by feature domain and wired in dedicated modules.

---

## 📁 Directory Structure

```
ui/
├── gradio_app.py                 # Main UI composition (163 lines)
│
├── components/                   # UI Component Factories
│   ├── __init__.py              # Package exports
│   ├── states.py                # Shared gr.State components (22 lines)
│   ├── rag_section.py           # RAG upload UI (43 lines)
│   ├── topic_section.py         # Topic input + mode (42 lines)
│   ├── buttons_section.py       # Action buttons (84 lines)
│   └── history_section.py       # History management (62 lines)
│
├── events/                       # Event Wiring Modules
│   ├── __init__.py              # Package exports
│   ├── initialization.py        # App load events (45 lines)
│   ├── rag_events.py            # Upload/clear (34 lines)
│   ├── explanation_events.py   # Explain/stop/clear (101 lines)
│   ├── history_events.py        # Search/load/delete (78 lines)
│   └── download_events.py       # Download formats (74 lines)
│
├── callbacks/                    # Business Logic Callbacks
│   ├── explanation_callbacks.py
│   ├── history_callbacks.py
│   ├── search_callbacks.py
│   ├── upload_callbacks.py
│   ├── rag_callbacks.py
│   └── download_callbacks.py
│
└── utils/                        # UI Utilities
    ├── ui_messages.py           # Constants and messages
    └── document_exporter.py     # Export to PDF/MD/DOCX
```

---

## 🧩 Component Modules

### `components/states.py`
Creates shared `gr.State` components:
- `history_state`: Chat history
- `rag_uploaded_state`: Uploaded RAG documents

**Usage:**
```python
history_state, rag_uploaded_state = create_shared_states()
```

---

### `components/rag_section.py`
Creates RAG document upload section:
- Collapsible accordion with file upload
- Clear all documents button
- Status display textbox

**Returns:**
```python
(file_upload, clear_btn, status_box)
```

---

### `components/topic_section.py`
Creates topic input section:
- Topic input textbox
- Multi-topic behavior radio (Aggregate vs Separate)
- Output textbox with autoscroll

**Returns:**
```python
(topic_input, history_mode, output_box)
```

---

### `components/buttons_section.py`
Creates action buttons section:
- Main buttons: Explain, Stop, Download, Clear
- Download format selection accordion
- Download file component

**Returns:**
```python
(explain_btn, stop_btn, download_btn, clear_btn,
 download_accordion, download_md_btn, download_pdf_btn, 
 download_docx_btn, download_file)
```

---

### `components/history_section.py`
Creates history management section:
- History dropdown with search
- Search textbox
- Delete section (accordion + dropdown + buttons)

**Returns:**
```python
(history_dropdown, search_box, delete_dropdown, 
 delete_btn, clear_all_btn)
```

---

## ⚡ Event Modules

### `events/initialization.py`
Wires `demo.load()` events:
- Load chat history from HF Hub
- Initialize Chroma vectorstore
- Initialize RAG document registry

**Function:**
```python
wire_initialization_events(demo, history_state, history_dropdown, 
                           delete_dropdown, search_box, 
                           rag_uploaded_state, rag_status_box)
```

---

### `events/rag_events.py`
Wires RAG upload/clear events:
- File upload → index documents
- Clear button → clear vectorstore and registry

**Function:**
```python
wire_rag_events(rag_file_upload, rag_clear_btn, 
                rag_uploaded_state, rag_status_box)
```

---

### `events/explanation_events.py`
Wires explanation generation events:
- Explain button click → stream LLM output
- Topic input submit → stream LLM output
- Stop button → cancel streaming
- Clear button → reset UI

**Function:**
```python
wire_explanation_events(explain_btn, topic_input, stop_btn, 
                        download_btn, clear_btn, history_state, 
                        history_mode, rag_uploaded_state, output_box,
                        history_dropdown, delete_dropdown, 
                        download_accordion, download_file)
```

---

### `events/history_events.py`
Wires history management events:
- Search box → filter history
- History dropdown → load selected chat
- Delete dropdown → enable/disable delete button
- Delete button → remove selected chat
- Clear all button → remove all chats

**Function:**
```python
wire_history_events(search_box, history_dropdown, delete_dropdown, 
                    delete_btn, clear_all_btn, history_state, 
                    topic_input, output_box, download_btn)
```

---

### `events/download_events.py`
Wires download/export events:
- Download button → show format selection
- Format buttons (MD/PDF/DOCX) → generate and download file

**Function:**
```python
wire_download_events(download_btn, download_accordion, 
                     download_md_btn, download_pdf_btn, 
                     download_docx_btn, download_file, 
                     topic_input, output_box)
```

---

## 🚀 Main UI File: `gradio_app.py`

The main file is now a **clean composition** of components and events:

```python
with gr.Blocks(title="Tech Explanation Service") as demo:
    # 1. Create states
    history_state, rag_uploaded_state = create_shared_states()
    
    # 2. Create UI sections
    with gr.Row():
        with gr.Column(scale=2):
            rag_file, rag_clear, rag_status = create_rag_section()
            topic_input, history_mode, output_box = create_topic_section()
            explain_btn, stop_btn, ... = create_buttons_section()
        
        with gr.Column(scale=1):
            history_dropdown, search_box, ... = create_history_section()
    
    # 3. Wire events
    wire_initialization_events(demo, ...)
    wire_rag_events(...)
    wire_explanation_events(...)
    wire_history_events(...)
    wire_download_events(...)

demo.queue()
```

---

## 📊 Metrics: Before vs After

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Main file size** | 378 lines | 163 lines | ⬇️ **57% reduction** |
| **Largest module** | 378 lines | 101 lines | ⬇️ **73% reduction** |
| **Files count** | 1 monolithic | 11 modular | ✅ **Better SoC** |
| **Maintainability** | 🔴 Difficult | 🟢 Easy | ✅ **High** |
| **Testability** | 🔴 Monolithic | 🟢 Isolated | ✅ **Per-module** |
| **Reusability** | 🔴 None | 🟢 High | ✅ **Composable** |

---

## 🎯 Benefits

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility:
- UI components → `ui/components/`
- Event wiring → `ui/events/`
- Business logic → `app/services/`
- Callbacks → `ui/callbacks/`

### 2. **Improved Readability**
- Main file is now **57% smaller**
- Each module is **< 110 lines**
- Clear naming and structure

### 3. **Easy Maintenance**
- Modify one feature without touching others
- Add new sections by creating new modules
- Remove features by deleting modules

### 4. **Better Testing**
- Test each component factory in isolation
- Test event wiring separately
- Mock dependencies easily

### 5. **Reusability**
- Component factories can be reused in other UIs
- Event wiring patterns are portable
- Clear API for each module

---

## 🛠️ How to Add New Features

### Add a New UI Section
1. Create `ui/components/new_section.py`
2. Define `create_new_section()` factory
3. Import and use in `gradio_app.py`

### Add New Events
1. Create `ui/events/new_events.py`
2. Define `wire_new_events()` function
3. Import and call in `gradio_app.py`

### Example: Add a Settings Section

```python
# ui/components/settings_section.py
def create_settings_section():
    with gr.Accordion("⚙️ Settings", open=False):
        model_dropdown = gr.Dropdown(["gpt-4", "gpt-3.5"], label="Model")
        temp_slider = gr.Slider(0, 1, value=0.2, label="Temperature")
    return model_dropdown, temp_slider

# ui/events/settings_events.py
def wire_settings_events(model_dropdown, temp_slider, ...):
    model_dropdown.change(fn=update_model, ...)
    temp_slider.change(fn=update_temperature, ...)

# ui/gradio_app.py
from ui.components import create_settings_section
from ui.events import wire_settings_events

with gr.Blocks() as demo:
    model, temp = create_settings_section()
    wire_settings_events(model, temp, ...)
```

---

## 📚 Best Practices

### 1. **Component Factories**
- Return all created components as a tuple
- Use clear, descriptive parameter names
- Add docstrings with Args and Returns

### 2. **Event Wiring**
- Accept all needed components as parameters
- Group related events together
- Use clear event chain patterns (`.click().then()`)

### 3. **Naming Conventions**
- Components: `create_<section>_section()`
- Events: `wire_<feature>_events()`
- Variables: descriptive names (e.g., `explain_btn`, not `btn1`)

### 4. **Documentation**
- Add module-level docstrings
- Document function signatures
- Explain complex event chains

---

## 🧪 Testing Strategy

### Unit Tests (Components)
```python
def test_create_rag_section():
    file_upload, clear_btn, status_box = create_rag_section()
    assert isinstance(file_upload, gr.File)
    assert clear_btn.value == "🗑️ Clear All Documents"
```

### Integration Tests (Events)
```python
def test_wire_explanation_events():
    # Mock components
    explain_btn = gr.Button()
    # ...
    
    # Wire events
    wire_explanation_events(explain_btn, ...)
    
    # Assert events are wired
    assert explain_btn.click is not None
```

---

## 🔄 Migration Guide (for Contributors)

If you need to modify the old monolithic `gradio_app.py`:

1. **Identify the section** you want to modify (RAG, Topic, History, etc.)
2. **Find the corresponding component** in `ui/components/`
3. **Find the corresponding events** in `ui/events/`
4. **Make your changes** in the appropriate modular file
5. **Test** the specific module in isolation
6. **Update** the main `gradio_app.py` only if needed

---

## 📖 References

- [Gradio Documentation](https://www.gradio.app/docs)
- [Component Factory Pattern](https://refactoring.guru/design-patterns/factory-method)
- [Separation of Concerns](https://en.wikipedia.org/wiki/Separation_of_concerns)

---

**Author:** Gianmario Iamoni  
**Date:** 2026-01-16  
**Version:** 1.0.0
