
## Installation and Environment Setup

To ensure all team members use the exact same technology stack and avoid library conflicts, this project utilizes a Conda virtual environment defined in the `environment.yml` file.

### 1. Install Anaconda (Full Distribution)

Before starting, you must install the  **full Anaconda distribution** , which includes the necessary tools for environment and package management, including the Conda command-line tool.

* Download: Go to the official download page and download the full installation package (approximately 1 GB):
  https://www.anaconda.com/download/success
* **Installation:** Run the downloaded installer. It is recommended to use the **default installation settings** to simplify the process of setting up the environment paths.

### 2. Create the Conda Environment (not needed, yml already created)

Once Anaconda is installed, open the **Anaconda Prompt** (on Windows) or your terminal (on macOS/Linux) and navigate to the project's root directory.

Use the `environment.yml` file, which contains all project dependencies (e.g., `mesa`, `pandas`, `pyreadstat`), to create the environment automatically:

**Bash**

```
conda env create -f environment.yml
```

This command will read the file and create the isolated environment named **`abm_seminario`** with all the required dependencies.

---

## Environment Usage

You **must** activate the `abm_seminario` environment every time you work on the project. This ensures that Python loads the correct, compatible versions of all the simulation libraries.

### a) Activate the Environment

To begin your work session, use the `conda activate` command:

**Bash**

```
conda activate abm_seminario
```

The name `(abm_seminario)` will appear at the start of your command line, confirming that the environment is active. You are now ready to run the Python scripts (e.g., `python run.py`).

### b) Deactivate the Environment

When you finish your session and want to return to your system's base environment, use the `conda deactivate` command:

**Bash**

```
conda deactivate
```

# ABM-Income-Interpersonal-Relations-Impact-on-Happiness

ABM: Income & Interpersonal Relations Impact on Happiness

This repository implements an Agent-Based Model (ABM) in Python to simulate happiness dynamics. The central goal is to model how rational agents allocate their limited time (T) between two main activities to maximize well‑being:

- Economic Goods (E): time spent generating income (T_E)
- Interpersonal Relations (R): time spent on relational goods (T_R)

The model explores how agents' prevailing values (materialist vs. relational) affect this optimal time allocation and resulting happiness.

Theoretical foundation and methodology
The framework is inspired by the economics of happiness and by:
Rojas, Mariano; and Ibarra‑López, Ignacio. 2014. "Happiness and Human Relations: The Role of Materialistic Values" (ABM illustration).

Happiness (utility) function
Each agent's happiness is initially modeled using a Cobb‑Douglas form that combines economic goods (E) and relational goods (R):

$$
H = E^\alpha R^{1-\alpha}, \quad \text{where } 0 \le \alpha \le 1
$$

The parameter α represents the agent's cultural/value orientation:

- α → 1: Materialist culture (happiness depends more on E)
- α → 0: Relational culture (happiness depends more on R)

Time constraint and optimization
Assuming goods are proportional to time invested (E ∝ T_E and R ∝ T_R) and the total time constraint T = T_E + T_R (e.g., 24 hours), the utility becomes:

$$
H = (T - T_R)^\alpha \, T_R^{1-\alpha}
$$

A rational agent chooses T_R that maximizes H. The simulation computes this optimal T_R for a population of agents with diverse α values.

Implementation and requirements
The project is implemented in Python. Key components and libraries:

| Component        |               Key libraries | Purpose                                                                     |
| ---------------- | --------------------------: | --------------------------------------------------------------------------- |
| Data processing  |       `pandas`, `numpy` | Data cleaning, transformation, and sampling of CIS microdata                |
| ABM core         |             Python (native) | `Agent` class, decision logic, simulation loop                            |
| Network analysis |                `networkx` | Model interpersonal relations as social networks                            |
| Visualization    | `matplotlib`, `seaborn` | Plots for happiness distributions, optimal time allocation, network effects |

Suggested environment

- Python 3.8+
- Install requirements via pip: `pip install -r requirements.txt`
- Use virtualenv or conda for isolation

Data sources (CIS)
Agents are initialized and validated using empirical data from the Spanish Centro de Investigaciones Sociológicas (CIS):

- Study 3145 (Post‑electoral 2016): contains variables such as Life Satisfaction (code D.1, scale 0–10) and social media usage indicators.
- FIES (Integrated Files of Social Studies): pooled monthly CIS surveys to obtain a larger, longitudinal sample.

Network modeling challenge
A more advanced stage involves explicit social network modeling. This includes:

1. Creating and simulating multiple networks (e.g., one per social platform).
2. Integrating network effects into R (relational goods) — for example, making R depend on neighbors’ states or network centrality.
3. Optionally combining network models with probabilistic graphical models (e.g., Bayesian networks) to capture complex dependencies.

Notes and next steps

- Provide unit tests for optimization routines (analytical solution vs numerical maximization).
- Document the `Agent` API and data preprocessing steps.
- Add examples/notebooks demonstrating calibration with CIS microdata and visualization of results.
- Consider privacy and data‑use constraints when sharing or publishing processed CIS data.
