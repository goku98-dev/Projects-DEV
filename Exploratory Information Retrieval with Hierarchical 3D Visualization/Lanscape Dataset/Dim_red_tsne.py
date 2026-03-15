import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------
features = np.load("resnet_features.npy")
labels = np.load("resnet_labels.npy")
class_names = np.load("class_names.npy")

print("Total samples:", features.shape[0])
print("Classes:", class_names.tolist())

# ------------------------------------------------------------
# BALANCED SAMPLING (CRITICAL FIX)
# ------------------------------------------------------------
SAMPLES_PER_CLASS = 500  # adjust if needed

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

print("Balanced samples:", features_balanced.shape[0])

# ------------------------------------------------------------
# 2D t-SNE
# ------------------------------------------------------------
tsne_2d = TSNE(
    n_components=2,
    perplexity=30,
    learning_rate=200,
    max_iter=1000,
    init="pca",
    random_state=42
)

features_2d = tsne_2d.fit_transform(features_balanced)

# ------------------------------------------------------------
# 2D VISUALIZATION
# ------------------------------------------------------------
plt.figure(figsize=(10, 8))

for label in np.unique(labels_balanced):
    idx = labels_balanced == label
    plt.scatter(
        features_2d[idx, 0],
        features_2d[idx, 1],
        label=class_names[label],
        alpha=0.7,
        s=20
    )

plt.title("2D t-SNE Visualization (ResNet Features)")
plt.xlabel("Dim 1")
plt.ylabel("Dim 2")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ------------------------------------------------------------
# 3D t-SNE
# ------------------------------------------------------------
tsne_3d = TSNE(
    n_components=3,
    perplexity=30,
    learning_rate=200,
    max_iter=1000,
    init="pca",
    random_state=42
)

features_3d = tsne_3d.fit_transform(features_balanced)

# ------------------------------------------------------------
# 3D VISUALIZATION
# ------------------------------------------------------------
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

for label in np.unique(labels_balanced):
    idx = labels_balanced == label
    ax.scatter(
        features_3d[idx, 0],
        features_3d[idx, 1],
        features_3d[idx, 2],
        label=class_names[label],
        alpha=0.7,
        s=20
    )

ax.set_title("3D t-SNE Visualization (ResNet Features)")
ax.set_xlabel("Dim 1")
ax.set_ylabel("Dim 2")
ax.set_zlabel("Dim 3")
ax.legend()
plt.tight_layout()
plt.show()
