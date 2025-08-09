# DADA Mathematical Programming Model 🏫📊

**Multi-objective optimization for classroom assignment with sector minimization and workload balancing**

---

## Overview

DADA (Didattiche per Ambienti Di Apprendimento) is a mathematical programming model that optimally assigns classrooms to teachers given a school schedule. The model addresses two key challenges:

1. **Minimize the number of classrooms per sector** (each teacher belongs to a specific sector)
2. **Balance teaching workload** among teachers

Two optimization models have been developed with different objective functions and complexity levels.

---

## Problem Description

### Context
- **Teachers** are assigned to specific **sectors** (e.g., Science, Humanities, Languages)
- **Classrooms** are designated for specific sectors
- **Goal**: Optimize classroom assignment while minimizing resources and balancing workload

### Key Challenges
- Minimize total number of classrooms needed per sector
- Balance the number of hours assigned to different teachers
- Ensure classroom availability constraints are met
- Optimize resource allocation across school facilities

---

## Model 1: Three-Objective Optimization

### Parameters
- $P = 102$: Number of teachers
- $N = 53$: Number of classrooms (equal to number of classes)
- $G = 5$: Number of days
- $O = 8$: Number of hours per day
- $S = 3$: Number of sectors
- $t_{k,o,g} \in \{0,1\}$: Teaching schedule matrix (1 if teacher $k$ has class at hour $o$ on day $g$)
- $p_s \subseteq \{0,1,...,P-1\}$: Set of teachers assigned to sector $s$

### Decision Variables
- $x_{k,l,o,g} \in \{0,1\}$: Binary variable (1 if teacher $k$ uses classroom $l$ at hour $o$ on day $g$)
- $y_{k,l} \in [0,1]$: Continuous variable indicating classroom $l$ assignment to teacher $k$
- $z_{max} \in \mathbb{R}^+$: Maximum number of classrooms assigned to any teacher
- $u_{l,s} \in \{0,1\}$: Binary variable (1 if classroom $l$ is assigned to sector $s$)

### Objective Function
$$
\min \alpha \sum_{k=0}^{P-1} \sum_{l=0}^{N-1} y_{k,l} + \beta \cdot z_{max}
$$

### Key Constraints
$$
\begin{align}
    \sum_{l=0}^{N-1} x_{k,l,o,g}   \hspace{0.3cm} & = \hspace{0.3cm} t_{k,o,g}                                        \hspace{2cm} && \forall k, o, g           && \text{(Class Assignment)} \\
    \sum_{k=0}^{P-1} x_{k,l,o,g}   \hspace{0.3cm} & \leq \hspace{0.3cm} 1                                             \hspace{2cm} && \forall l, o, g           && \text{(Single Occupancy)} \\
    x_{k,l,o,g}                    \hspace{0.3cm} & \leq \hspace{0.3cm} y_{k,l}                                       \hspace{2cm} && \forall k, l, o, g        && \text{(Teacher-Classroom Link)} \\
    y_{k,l}                        \hspace{0.3cm} & \leq \hspace{0.3cm} \sum_{o=0}^{O-1} \sum_{g=0}^{G-1} x_{k,l,o,g} \hspace{2cm} && \forall k, l              && \text{(Classroom Coverage)} \\
    z_{max}                        \hspace{0.3cm} & \geq \hspace{0.3cm} \sum_{l=0}^{N-1} y_{k,l}                      \hspace{2cm} && \forall k                 && \text{(Workload Balance)} \\
    u_{l,s}                        \hspace{0.3cm} & \geq \hspace{0.3cm} y_{k,l}                                       \hspace{2cm} && \forall l, s,\; k \in p_s && \text{(Sector Assignment)} \\
    \sum_{s=0}^{S-1} u_{l,s}       \hspace{0.3cm} & = \hspace{0.3cm} 1                                                \hspace{2cm} && \forall l                 && \text{(Single Sector)}
\end{align}
$$

---

## Model 2: Four-Objective Optimization

### Additional Parameters
- $C$: Number of classes
- $F$: Number of floors
- $L_f \subseteq \{0,1,...,N-1\}$: Set of classrooms on floor $f$

### Enhanced Decision Variables
- $x_{k,l,o,g,c} \in \{0,1\}$: Enhanced assignment variable (includes class $c$ dimension)
- $w_{f,c,g} \in \{0,1\}$: Binary variable (1 if class $c$ uses floor $f$ on day $g$)

### Enhanced Objective Function
$$
\min \alpha \sum_{k=0}^{P-1} \sum_{l=0}^{N-1} y_{k,l} + \beta \cdot z_{max} + \gamma \sum_{f=0}^{F-1} \sum_{c=0}^{C-1} \sum_{g=0}^{G-1} w_{f,c,g}
$$

### Additional Constraints
$$
w_{f,c,g} \geq x_{k,l,o,g,c} \quad \forall f,k,l \in L_f,o,g,c \quad \text{(Floor Usage)}
$$

Where $L_f$ represents the set of classrooms on floor $f$.

### Improvements
- **Floor optimization**: Minimizes movement between floors
- **Class-specific assignments**: More granular classroom allocation
- **Enhanced scheduling**: Better spatial distribution of classes

---

## Implementation Details

### Technology Stack
- **Gurobi Optimizer**: Commercial mathematical programming solver
- **Python**: Implementation language
- **NumPy**: Numerical computations
- **Excel/CSV**: Data input/output

### Project Structure
```
modello-dada/
├── first_model/          # 3-objective optimization model
│   ├── modello_gurobi.py # Main optimization model
│   ├── constants.py      # Model parameters
│   └── utils.py          # Helper functions
├── second_model/         # 4-objective optimization model
│   ├── modello_gurobi_2.py # Enhanced model
│   └── constants.py      # Extended parameters
├── data/                 # Input datasets
└── results/              # Optimization results
```

### Input Data
- **Schedule Files**: Teacher timetables (CSV format)
- **Sector Assignments**: Teacher-sector mapping
- **Classroom Data**: Available classrooms and capacity
- **Floor Plans**: Classroom-floor assignments (Model 2)

---

## Results & Performance

### Model Comparison
- **Model 1**: Faster computation, basic optimization
- **Model 2**: More comprehensive, includes spatial optimization
- **Trade-offs**: Computational complexity vs. solution quality

### Key Metrics
- **Classroom Utilization**: Percentage of classrooms actively used
- **Workload Balance**: Standard deviation of teacher assignments
- **Sector Efficiency**: Number of classrooms per sector
- **Floor Movement**: Inter-floor transitions (Model 2)

---

## Usage

### Running Model 1 (3 Objectives)
```bash
cd first_model
python modello_gurobi.py
```

### Running Model 2 (4 Objectives)
```bash
cd second_model
python modello_gurobi_2.py
```

### Configuration
- Modify `constants.py` to adjust problem parameters
- Update data files in `data/` directory
- Adjust objective weights (α, β, γ) for different optimization priorities

---


**Technologies:** Gurobi, Python, Mathematical Programming, Multi-objective Optimization