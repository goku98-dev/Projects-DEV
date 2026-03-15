import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import umap
import hdbscan
from sklearn.metrics import rand_score
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# ------------------------------------------------------------
# LOAD DATA (UNCHANGED)
# ------------------------------------------------------------
features = np.load("resnet_features.npy")
labels = np.load("resnet_labels.npy")
class_names = np.load("class_names.npy")

# ------------------------------------------------------------
# BALANCED SAMPLING (UNCHANGED)
# ------------------------------------------------------------
SAMPLES_PER_CLASS = 300

features_balanced = []
labels_balanced = []

for label in np.unique(labels):
    idx = np.where(labels == label)[0]
    np.random.shuffle(idx)
    idx = idx[:SAMPLES_PER_CLASS]

    features_balanced.append(features[idx])
    labels_balanced.append(labels[idx])

features_balanced = np.vstack(features_balanced)
labels_balanced = np.hstack(labels_balanced)

print("Samples:", features_balanced.shape[0])
print("Classes:", len(np.unique(labels_balanced)))

# ------------------------------------------------------------
# UMAP 
# ------------------------------------------------------------
umap_2d = umap.UMAP(
    n_components=2,
    n_neighbors=30,
    min_dist=0.1,
    metric="cosine",
    init="spectral",
    random_state=42
)

umap_3d = umap.UMAP(
    n_components=3,
    n_neighbors=20,
    min_dist=0.2,
    metric="cosine",
    init="spectral",
    random_state=42
)

embedding_2d = umap_2d.fit_transform(features_balanced)
embedding_3d = umap_3d.fit_transform(features_balanced)

# ------------------------------------------------------------
# HDBSCAN (CLUSTERING ON UMAP SPACE)
# ------------------------------------------------------------
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=25,
    min_samples=10,
    metric="euclidean",
    cluster_selection_method="eom"
)

cluster_labels = clusterer.fit_predict(embedding_2d)

n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
n_noise = np.sum(cluster_labels == -1)

print(f"HDBSCAN clusters: {n_clusters}")
print(f"Noise points: {n_noise}")

# ------------------------------------------------------------
# RAND SCORE
# ------------------------------------------------------------
rs = rand_score(labels_balanced, cluster_labels)
print(f"Rand Score: {rs:.4f}")

# ------------------------------------------------------------
# SAVE CSV FILES FOR UNITY (NEW)
# ------------------------------------------------------------
df_umap_2d = pd.DataFrame({
    "x": embedding_2d[:, 0],
    "y": embedding_2d[:, 1],
    "cluster_id": cluster_labels,
    "class_label": labels_balanced,
    "class_name": [class_names[l] for l in labels_balanced]
})

df_umap_2d.to_csv("umap_2d_coordinates.csv", index=False)

df_umap_3d = pd.DataFrame({
    "x": embedding_3d[:, 0],
    "y": embedding_3d[:, 1],
    "z": embedding_3d[:, 2],
    "cluster_id": cluster_labels,
    "class_label": labels_balanced,
    "class_name": [class_names[l] for l in labels_balanced]
})

df_umap_3d.to_csv("umap_3d_coordinates.csv", index=False)

print("Saved CSV files:")
print(" - umap_2d_coordinates.csv")
print(" - umap_3d_coordinates.csv")

# ------------------------------------------------------------
# COLOR MAP (CLUSTERS)
# ------------------------------------------------------------
unique_clusters = np.unique(cluster_labels)
cmap = plt.cm.get_cmap("tab20", len(unique_clusters))

cluster_to_color = {
    cl: cmap(i) if cl != -1 else (0, 0, 0, 0.25)
    for i, cl in enumerate(unique_clusters)
}

# ------------------------------------------------------------
# 2D PLOT
# ------------------------------------------------------------
fig2d = plt.figure(figsize=(14, 10))

for cl in unique_clusters:
    idx = cluster_labels == cl
    label_name = f"Cluster {cl}" if cl != -1 else "Noise"
    plt.scatter(
        embedding_2d[idx, 0],
        embedding_2d[idx, 1],
        s=18,
        alpha=0.7,
        color=cluster_to_color[cl],
        label=label_name
    )

plt.title("UMAP 2D + HDBSCAN Clusters")
plt.xlabel("UMAP-1")
plt.ylabel("UMAP-2")
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
plt.grid(True)

# ------------------------------------------------------------
# 3D PLOT
# ------------------------------------------------------------
fig3d = plt.figure(figsize=(14, 10))
ax = fig3d.add_subplot(111, projection="3d")

for cl in unique_clusters:
    idx = cluster_labels == cl
    label_name = f"Cluster {cl}" if cl != -1 else "Noise"
    ax.scatter(
        embedding_3d[idx, 0],
        embedding_3d[idx, 1],
        embedding_3d[idx, 2],
        s=18,
        alpha=0.7,
        color=cluster_to_color[cl],
        label=label_name
    )

ax.set_title("UMAP 3D + HDBSCAN Clusters")
ax.set_xlabel("UMAP-1")
ax.set_ylabel("UMAP-2")
ax.set_zlabel("UMAP-3")
ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)

# ------------------------------------------------------------
# SHOW BOTH WINDOWS
# ------------------------------------------------------------
plt.show()
