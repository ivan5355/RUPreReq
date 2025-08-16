# Rutgers Course Dependencies Visualization

An interactive web application that visualizes course prerequisites across Rutgers subjects. It helps students understand course relationships and plan their academic journey more effectively.

<img width="1474" alt="App screenshot" src="https://github.com/user-attachments/assets/116054bc-a19b-44a8-8669-3aa27e246aa6" />

## Features
- Visual prerequisite graphs per subject using Cytoscape.js
- Color-coded nodes by course level (100/200/300/400)
- Sticky toolbar with subject filter and quick actions (Fit, Reset, Clear)
- Loading overlay for feedback on long fetches
- Works entirely from a simple Flask backend endpoint

## Prerequisites
- Python 3.9+ (3.11 recommended)
- pip

## Setup
1. Clone the repository and enter the project directory.
2. Create and activate a virtual environment:
   - macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     py -3 -m venv venv
     venv\Scripts\Activate.ps1
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run locally
```bash
python server.py
```
- The app starts at `http://localhost:7000`.
- If you change the port in `server.py`, update the URL accordingly.

## Production (optional)
Use gunicorn to serve the app:
```bash
gunicorn -w 2 -b 0.0.0.0:7000 server:app
```

## Usage
1. Use the Filter box to quickly find a subject by name or number (e.g., "Computer" or "198").
2. Select a subject and click "Search Subject".

### Legend
- Node color indicates course level:
  - 100: green
  - 200: amber
  - 300: indigo
  - 400: pink

## API
- `GET /api/graph/<major_number>`
  - Returns JSON `{ nodes: [], edges: [] }` for the subject code (e.g., `198` for Computer Science)
  - Each node has `id` and `label`
  - Each edge has `source` and `target`

## Data
- The file `rutgers_courses.json` is used to build graphs.
- Update or replace this file to refresh data.

## Troubleshooting
- If you see CORS-related errors, ensure you are accessing via the same origin as the Flask server or enable CORS as needed.
- If `pip install` fails, upgrade pip and wheel:
  ```bash
  python -m pip install --upgrade pip wheel
  ```
- If the page is blank, check the browser console and Flask logs for errors.

---
This project is not affiliated with Rutgers University.
