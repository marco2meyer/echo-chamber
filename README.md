# Exploring Epistemic Bubbles and Echo Chambers — No Coding Experience Needed!

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

### 6. (Recommended) Install an IDE (Code Editor)
While you can use any text editor to edit code, using an Integrated Development Environment (IDE) makes things much easier:
- **[Visual Studio Code (VS Code)](https://code.visualstudio.com/):** Free, beginner-friendly, and works on Windows, Mac, and Linux.
- **AI-powered versions of VS Code:**
  - **[Windsurf](https://windsurf.ai/):** Free tier, built-in advanced AI coding assistant -- this is what I use.
  - **[Cursor](https://www.cursor.so/):** Free tier, advanced AI coding support -- also a great choice.
  - **[Cline](https://github.com/Clinet/cline):** Open source, supports many free AI models -- probably good but I've never tried.

To install, just follow the instructions on their websites. These tools can help you write, understand, and fix code with the help of AI. If you ever want to try editing or extending the code, these editors make it much easier—and the AI can help you every step of the way!

### 7. Run the Simulation (Streamlit — Recommended)
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
  - More customizable, and no flickering of the plot. But a bit more complex.
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
- **`streamlit_app.py`** — The Streamlit web interface (where the buttons and sliders live) For many updates to the code  you won't need to go there.
- **`dash_app.py`** — The Dash web interface (alternative to streamlit dashboard, slightly more advanced programming).

If you want to change how agents behave, start with `models.py` and `agent.py`.

---

## Troubleshooting & Using AI to Get Help
- **Missing packages?** Make sure you ran `pip install -r requirements.txt` in your terminal.
- **Python not recognized?** Check that Python is installed and added to your PATH (see Step 1 above).
- **Confused by an error message?**
  1. **Copy the error message.**
  2. **Paste it into your AI assistant** and ask for help (see below).
- **Want to try changing the code, but not sure how?**
  - **Write your idea in plain English or pseudocode**, then ask your AI assistant to translate it into Python.
  - Example: “I want agents to only update their belief if their neighbor’s belief is at least 0.2 different. How do I do this in `models.py`?” (then paste in all of the code from models.py)
- **Where to get AI help:**
  - If you’re using VS Code, Windsurf, Cursor, or Cline, you can highlight code or errors and ask the built-in AI assistant for help.
  - You can also use web-based tools like [ChatGPT](https://chat.openai.com), [Gemini](https://gemini.google.com), or [Claude](https://claude.ai) to get explanations, translations into other programming languages, or debugging help.
- **General tips:**
  - If something breaks, don’t panic! AI assistants are great at translating error messages, fixing bugs, and even turning your pseudocode or ideas into real code.
  - If you’re stuck, ask your instructor, a classmate, or an AI assistant—don’t struggle alone!

**Example AI prompts:**
- “I got this error: [paste error here]. What does it mean and how do I fix it?”
- “Can you turn this pseudocode into Python?”
- “Explain what this function does.”
- “How do I add a new type of agent to this simulation?”
- "I have some code here. How can I make it run? Explain step by step." 

---

## More to Explore (Advanced)
- Try changing the code in `models.py` to experiment with new update rules.
- Add new types of agents or connections in `agent.py` or `network_utils.py`.
- Visualize more metrics in `visualization.py`.

Have fun exploring epistemic bubbles and echo chambers! No programming experience required — but you’re welcome to dive deeper if you’re curious.
