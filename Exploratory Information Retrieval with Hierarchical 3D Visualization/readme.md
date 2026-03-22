# 🌌 Exploratory Information Retrieval with Hierarchical 3D Visualization

<p align="center">
  <img src="https://raw.githubusercontent.com/goku98-dev/Projects-DEV/main/Exploratory%20Information%20Retrieval%20with%20Hierarchical%203D%20Visualization/img/0.jpeg" width="45%">
  <img src="https://raw.githubusercontent.com/goku98-dev/Projects-DEV/main/Exploratory%20Information%20Retrieval%20with%20Hierarchical%203D%20Visualization/img/1.jpeg" width="45%">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/goku98-dev/Projects-DEV/main/Exploratory%20Information%20Retrieval%20with%20Hierarchical%203D%20Visualization/img/2.jpeg" width="45%">
  <img src="https://raw.githubusercontent.com/goku98-dev/Projects-DEV/main/Exploratory%20Information%20Retrieval%20with%20Hierarchical%203D%20Visualization/img/3.jpeg" width="45%">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/goku98-dev/Projects-DEV/main/Exploratory%20Information%20Retrieval%20with%20Hierarchical%203D%20Visualization/img/4.jpeg" width="45%">
</p>

An advanced **machine learning and visualization pipeline** for exploring large image datasets through **deep feature extraction, dimensionality reduction, clustering, and immersive 3D visualization**.

This project processes **10,000+ images**, extracts high-level semantic features using **ResNet50 CNN**, reduces feature dimensionality using **PCA and UMAP**, performs clustering with **HDBSCAN**, and visualizes relationships between images using a **hierarchical "Planets and Moons" metaphor in Unity 3D**.

---

# 📊 Project Overview

The goal of this project is to create an **interactive information retrieval system** that allows users to explore similarities between images in a **hierarchical and intuitive 3D environment**.

The pipeline includes:

1. **Deep Feature Extraction**
2. **Dimensionality Reduction**
3. **Hierarchical Clustering**
4. **Data Export**
5. **Interactive 3D Visualization**

By transforming high-dimensional image embeddings into structured clusters, the system enables **efficient exploration of semantic relationships between images**.

---

# 🧠 Machine Learning Pipeline

## 1️⃣ Feature Extraction

High-level image representations are extracted using **ResNet50 CNN**.

- Pretrained **ResNet50 model**
- Implemented using **PyTorch and TensorFlow**
- Feature vectors extracted from the final convolutional layers
- Normalization and preprocessing applied


---

## 2️⃣ Dimensionality Reduction

High-dimensional embeddings are reduced to a **10-dimensional latent space** (identified as the optimal "sweet spot" through hyperparameter tuning).

Techniques used:

- **PCA (Principal Component Analysis)** for initial reduction
- **UMAP (Uniform Manifold Approximation and Projection)** for nonlinear manifold learning


Benefits:

- Preserves global and local structure
- Improves clustering performance
- Reduces computational complexity

---

## 3️⃣ Clustering

Clusters are detected using **HDBSCAN**, a density-based clustering algorithm.

Features:

- Automatically detects cluster structure
- Handles noise and outliers
- No need to predefine number of clusters

Additional outputs:

- **Cluster labels**
- **Cluster probabilities**
- **Condensed tree hierarchy**

The **condensed tree** is used to identify hierarchical relationships between clusters.

---

# 🌳 Hierarchical Relationships

The **HDBSCAN condensed tree** captures hierarchical grouping relationships.

This allows:

- Identification of **parent-child cluster structures**
- Visualization of **similarity relationships**
- Easier exploration of semantic groupings

These hierarchical relationships are used in the **Unity visualization layer**.

---

# 📂 Data Export

After clustering and dimensionality reduction, the processed dataset is exported to CSV for visualization.

# 🌌 3D Visualization (Unity)

The clustered data is visualized using an interactive **3D hierarchical metaphor**.

### Planet and Moons Model

- **Planets → Clusters**
- **Moons → Individual images**
- **Orbit distance → Similarity relationships**

Features:

- Interactive exploration
- Cluster hierarchy navigation
- Visual representation of semantic similarity
- Scalable exploration of large datasets

Unity loads the **CSV data** and generates the 3D scene dynamically.

---

# 🧰 Tech Stack

### Machine Learning
- Python
- PyTorch
- TensorFlow
- Scikit-learn

### Dimensionality Reduction
- PCA
- UMAP

### Clustering
- HDBSCAN

### Visualization
- Unity 3D
- C#

### Data Processing
- NumPy
- Pandas

---

# 📈 Key Features

- Deep image embeddings using **ResNet50**
- Efficient **dimensionality reduction pipeline**
- **Automatic cluster detection** using HDBSCAN
- **Hierarchical cluster exploration**
- **Interactive 3D visualization in Unity**
- Scalable to **large image datasets (10k+ images)**



