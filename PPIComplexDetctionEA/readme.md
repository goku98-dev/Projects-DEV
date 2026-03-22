# 🧬 Protein–Protein Interaction Complex Detection using Evolutionary Algorithms

## 📌 Overview

This project focuses on detecting protein complexes in **Protein–Protein Interaction (PPI) networks** using an **Evolutionary Algorithm (EA)**. Protein complexes are groups of proteins that interact closely to perform biological functions, and identifying them is a key problem in bioinformatics.

The implemented approach combines **Q-guided mutation strategies** and **frequency-matrix encoding/decoding** to improve the accuracy of complex detection.

---

## 🚀 Features

* Evolutionary Algorithm for clustering in graph-based biological networks
* Multiple mutation strategies:

  * Canonical Mutation
  * Topological Mutation
  * Delta Mutation
* Q-guided mutation for enhanced exploration
* Frequency-based encoding and decoding of protein complexes
* Modularity-based fitness function for evaluating clustering quality
* Supports multiple benchmark datasets (Yeast D1, Yeast D2, Collins)

---

## 🧠 Methodology

### 🔹 Representation

Each individual (chromosome) represents a potential set of protein complexes using a **frequency-matrix encoding scheme**.

### 🔹 Evolutionary Process

1. Initialize population
2. Decode individuals into protein complexes
3. Evaluate fitness using modularity
4. Apply mutation strategies
5. Select best individuals
6. Repeat until convergence

### 🔹 Fitness Function

A **modularity-based fitness function** is used to measure the quality of detected complexes:

* Maximizes intra-cluster density
* Minimizes inter-cluster connections

---

## 📊 Results

* Achieved **0.90 precision** on the **Collins PPI dataset**
* Demonstrated robustness across multiple datasets
* Improved detection accuracy using Q-guided mutation

---

## 📂 Dataset

The following datasets are supported:

* Yeast D1
* Yeast D2
* Collins PPI Network

> Note: Dataset files are stored in `.mat` format and loaded within MATLAB.

---

## ⚙️ Installation & Setup

### 🖥️ Requirements

* MATLAB (R2020 or later recommended)

### ▶️ Run the Project

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/ppi-evolutionary-detection.git
   cd ppi-evolutionary-detection
   ```

2. Open MATLAB and run:

   ```matlab
   main.m
   ```

3. Select:

   * Dataset (1/2/3)
   * Mutation type

---

## 🗂️ Project Structure

```
├── DataSets/
│   ├── Protein/
│   ├── Complex/
├── Repositories/        # Output results
├── main.m               # Entry point
├── EA.m                 # Evolutionary algorithm
├── ComputeFitnessEA.m
├── CreatePopulation.m
├── Individual2CmplxDecoding.m
```

---

## 📈 Future Improvements

* Parallelization using MATLAB `parfor`
* Visualization of detected protein complexes
* Conversion to Python (NetworkX / PyTorch)
* Integration with Graph Neural Networks (GNNs)

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 📧 Contact

**Gokul Venugopal**
📩 [gokulvenugopal24101998@gmail.com](mailto:gokulvenugopal24101998@gmail.com)

---

## ⭐ Acknowledgements

* Biological datasets used for benchmarking PPI networks
* Research in evolutionary algorithms and bioinformatics

---
