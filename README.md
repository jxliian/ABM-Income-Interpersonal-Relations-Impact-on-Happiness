# ABM-Income-Interpersonal-Relations-Impact-on-Happiness
ABM: Income &amp; Interpersonal Relations Impact on Happiness
📈 ABM: Income & Interpersonal Relations Impact on Happiness 📝

Project description
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

| Component | Key libraries | Purpose |
| --- | ---: | --- |
| Data processing | `pandas`, `numpy` | Data cleaning, transformation, and sampling of CIS microdata |
| ABM core | Python (native) | `Agent` class, decision logic, simulation loop |
| Network analysis | `networkx` | Model interpersonal relations as social networks |
| Visualization | `matplotlib`, `seaborn` | Plots for happiness distributions, optimal time allocation, network effects |

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
