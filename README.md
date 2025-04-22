\# Exploring Epistemic Bubbles and Echo Chambers — No Coding Experience Needed!

Welcome! This project lets you explore two important concepts from philosophy — **Epistemic Bubbles** and **Echo Chambers** — using an interactive simulation. You don't need any programming experience to use it. The simulation runs in your web browser, and you can change parameters and see what happens in real time.

**What is this about?**
- **Epistemic Bubble:** When people only hear from a limited set of sources, not because they distrust others, but simply because those voices are missing.
- **Echo Chamber:** When people actively distrust and ignore information from outside their group, reinforcing their own views.

This project helps you see how these phenomena might work in a social network, using a simplified model.

---

## Quick Start: How to Run the Simulation (Step by Step)

**You do NOT need to know how to code! Just follow these instructions:**

### 1. Install Python (if you don't have it yet)
- Go to [python.org/downloads](https://www.python.org/downloads/) and download Python 3.8 or newer.
- Install Python by opening the downloaded file and following the instructions. Make sure to check the box that says "Add Python to PATH" if asked.

### 2. Download the Project Files
- If you received this as a ZIP file, unzip it to a folder on your computer.
- If you are using GitHub, click the green **Code** button and choose **Download ZIP**. Then unzip.

### 3. Open a Terminal (Command Prompt)
- **Windows:** Press the Windows key, type `cmd`, and hit Enter.
- **Mac:** Open `Terminal` from Applications > Utilities.
- **Navigate** to the folder where you unzipped the project. For example, if you put it in Documents:
  ```bash
  cd "Documents/echo chamber"
  ```

### 4. (Optional but Recommended) Create a Virtual Environment
This keeps your Python packages organized.
```bash
python3 -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 5. Install the Required Packages
This project uses a few extra Python tools. Install them by running:
```bash
pip install -r requirements.txt
```

### 6. Run the Simulation (Streamlit — Recommended)
Streamlit gives you a simple, friendly web interface.
```bash
streamlit run streamlit_app.py
```
- Your web browser should open automatically. If not, copy the link from the terminal (usually http://localhost:8501) and open it in your browser.

---

## Two Ways to Explore: Streamlit vs. Dash

- **Streamlit (Recommended):**
  - Easiest to use, especially for beginners.
  - Simple interface, runs in your browser.
  - Start with: `streamlit run streamlit_app.py`

- **Dash (Advanced):**
  - More customizable, but a bit more complex.
  - If you want to try it: `python dash_app.py`
  - Then open http://127.0.0.1:8050 in your browser.

**Tip:** If you’re new, stick with Streamlit!

---

## What’s Happening in the Simulation?
- You’ll see a network of “agents” (people) with lines showing who talks to whom.
- You can choose between two models:
  - **Epistemic Bubble:** Agents don’t hear from everyone, just their direct contacts.
  - **Echo Chamber:** Agents may distrust and ignore some contacts, not just miss them.
- Adjust parameters (like number of agents, connection probability, etc.) and watch how beliefs change over time!

---

## Where’s the Interesting Logic? (For the Curious)
If you want to peek under the hood or try extending the model, here’s where to look:

- **`models.py`** — The heart of the belief update logic (difference between Bubble and Chamber).
- **`agent.py`** — Defines what each agent is and how it stores beliefs and trust.
- **`simulation.py`** — The simulation engine: how agents interact each step.
- **`network_utils.py`** — How the network of agents is built.
- **`visualization.py`** — How the network and results are visualized (using Plotly graphs).
- **`streamlit_app.py`** — The Streamlit web interface (where the buttons and sliders live).
- **`dash_app.py`** — The Dash web interface (alternative, more advanced).

If you want to change how agents behave, start with `models.py` and `agent.py`.

---

## Troubleshooting
- If you get errors about missing packages, make sure you ran `pip install -r requirements.txt`.
- If Python isn’t recognized, check that it’s installed and added to your PATH.
- If you get stuck, ask your instructor or a classmate!

---

## More to Explore (Advanced)
- Try changing the code in `models.py` to experiment with new update rules.
- Add new types of agents or connections in `agent.py` or `network_utils.py`.
- Visualize more metrics in `visualization.py`.

Have fun exploring epistemic bubbles and echo chambers! No programming experience required — but you’re welcome to dive deeper if you’re curious.
