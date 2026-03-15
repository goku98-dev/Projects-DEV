import numpy as np
import pandas as pd
import umap
import hdbscan
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import rand_score
from collections import defaultdict, deque

# ============================================================
# CONFIG
# ============================================================
SAMPLES_PER_CLASS = 300
RANDOM_STATE = 42

# ============================================================
# LOAD DATA
# ============================================================
features = np.load("resnet_features.npy")
labels = np.load("resnet_labels.npy")
image_ids = np.load("image_ids.npy")

# ============================================================
# BALANCED SAMPLING
# ============================================================
features_balanced = []
labels_balanced = []
image_ids_balanced = []

for label in np.unique(labels):
    idx = np.where(labels == label)[0]
    np.random.shuffle(idx)
    idx = idx[:SAMPLES_PER_CLASS]

    features_balanced.append(features[idx])
    labels_balanced.append(labels[idx])
    image_ids_balanced.append(image_ids[idx])

features_balanced = np.vstack(features_balanced)
labels_balanced = np.hstack(labels_balanced)
image_ids_balanced = np.hstack(image_ids_balanced)

# ============================================================
# STANDARDIZE
# ============================================================
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features_balanced)

# ============================================================
# UMAP
# ============================================================
umap_10d = umap.UMAP(
    n_components=10,
    n_neighbors=30,
    min_dist=0.1,
    metric="cosine",
    random_state=RANDOM_STATE
)
embedding_10d = umap_10d.fit_transform(features_scaled)

umap_3d = umap.UMAP(
    n_components=3,
    n_neighbors=30,
    min_dist=0.1,
    metric="cosine",
    random_state=RANDOM_STATE
)
embedding_3d = umap_3d.fit_transform(features_scaled)

# ============================================================
# MAIN HDBSCAN
# ============================================================
main_clusterer = hdbscan.HDBSCAN(
    min_cluster_size=25,
    min_samples=10,
    cluster_selection_method="eom"
)
main_labels = main_clusterer.fit_predict(embedding_10d)

print("Main clusters:",
      len(set(main_labels)) - (1 if -1 in main_labels else 0))
print("Rand Score (Main):",
      round(rand_score(labels_balanced, main_labels), 4))

# ============================================================
# BUILD PRUNED TREE
# ============================================================

rows = []

for planet_id in np.unique(main_labels):
    if planet_id == -1:
        continue

    idx = np.where(main_labels == planet_id)[0]
    subset_10d = embedding_10d[idx]
    subset_3d = embedding_3d[idx]

    sub_clusterer = hdbscan.HDBSCAN(
        min_cluster_size=5,
        min_samples=3,
        cluster_selection_method="eom",
        prediction_data=True
    )
    sub_clusterer.fit(subset_10d)

    condensed = sub_clusterer.condensed_tree_.to_pandas()

    # --------------------------------------------------------
    # Build tree structure
    # --------------------------------------------------------
    children_map = defaultdict(list)
    parent_map = {}

    for _, r in condensed.iterrows():
        p = int(r["parent"])
        c = int(r["child"])
        children_map[p].append(c)
        parent_map[c] = p

    all_nodes = set(condensed["parent"]).union(set(condensed["child"]))

    # --------------------------------------------------------
    # Leaf membership from flat labels
    # --------------------------------------------------------
    leaf_labels = sub_clusterer.labels_
    leaf_members = defaultdict(list)

    for local_i, label in enumerate(leaf_labels):
        if label != -1:
            leaf_members[label].append(local_i)

    # --------------------------------------------------------
    # Propagate membership upward
    # --------------------------------------------------------
    node_members = {}

    for leaf, members in leaf_members.items():
        node_members[leaf] = set(members)

    nodes_sorted = sorted(all_nodes, reverse=True)

    for node in nodes_sorted:
        if node not in node_members:
            node_members[node] = set()

        for child in children_map.get(node, []):
            node_members[node] |= node_members.get(child, set())

    # --------------------------------------------------------
    # Compute sizes
    # --------------------------------------------------------
    node_sizes = {n: len(members)
                  for n, members in node_members.items()
                  if len(members) > 0}

    # --------------------------------------------------------
    # PRUNE: remove redundant chains
    # Keep node only if size differs from parent
    # --------------------------------------------------------
    pruned_nodes = set()

    for node, size in node_sizes.items():
        parent = parent_map.get(node)
        parent_size = node_sizes.get(parent)

        if parent is None or parent_size != size:
            pruned_nodes.add(node)

    # --------------------------------------------------------
    # Add planet root
    # --------------------------------------------------------
    planet_node_id = f"planet_{planet_id}"
    planet_centroid = subset_3d.mean(axis=0)

    rows.append({
        "type": "node",
        "node_id": planet_node_id,
        "parent_id": "root",
        "planet_id": planet_id,
        "depth": 0,
        "size": len(idx),
        "x": planet_centroid[0],
        "y": planet_centroid[1],
        "z": planet_centroid[2],
        "image_id": None
    })

    # --------------------------------------------------------
    # Add pruned nodes
    # --------------------------------------------------------
    for node in pruned_nodes:
        members = node_members[node]
        centroid = subset_3d[list(members)].mean(axis=0)

        parent = parent_map.get(node)

        # climb up until we find a pruned parent
        while parent not in pruned_nodes and parent in parent_map:
            parent = parent_map.get(parent)

        parent_id = (f"{planet_id}_node_{parent}"
                     if parent in pruned_nodes
                     else planet_node_id)

        rows.append({
            "type": "node",
            "node_id": f"{planet_id}_node_{node}",
            "parent_id": parent_id,
            "planet_id": planet_id,
            
            "depth": None,  # Unity can compute dynamically
            "size": len(members),
            "x": centroid[0],
            "y": centroid[1],
            "z": centroid[2],
            "image_id": None
        })

    # --------------------------------------------------------
    # Attach images to leaf clusters (only if leaf kept)
    # --------------------------------------------------------
    for leaf, members in leaf_members.items():
        if leaf not in pruned_nodes:
            continue

        parent_node = f"{planet_id}_node_{leaf}"

        for local_i in members:
            global_i = idx[local_i]

            rows.append({
                "type": "image",
                "node_id": None,
                "parent_id": parent_node,
                "planet_id": planet_id,
                "depth": None,
                "size": 1,
                "x": embedding_3d[global_i][0],
                "y": embedding_3d[global_i][1],
                "z": embedding_3d[global_i][2],
                "image_id": image_ids_balanced[global_i]
            })

# ============================================================
# EXPORT
# ============================================================
df = pd.DataFrame(rows)
df.to_csv("unity_pruned_density_tree_3d.csv", index=False)

print("Saved: unity_pruned_density_tree_3d.csv")