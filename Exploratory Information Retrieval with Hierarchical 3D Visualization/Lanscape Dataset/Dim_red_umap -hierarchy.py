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

print("Samples:", len(features_balanced))

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
# BUILD FULL RAW TREE WITH CORRECT AGGREGATION
# ============================================================

rows = []

for planet_id in np.unique(main_labels):
    if planet_id == -1:
        continue

    print(f"Processing planet {planet_id}")

    idx = np.where(main_labels == planet_id)[0]
    subset_10d = embedding_10d[idx]
    subset_3d = embedding_3d[idx]

    # Run HDBSCAN inside planet
    sub_clusterer = hdbscan.HDBSCAN(
        min_cluster_size=5,
        min_samples=3,
        cluster_selection_method="eom",
        prediction_data=True
    )
    sub_clusterer.fit(subset_10d)

    condensed = sub_clusterer.condensed_tree_.to_pandas()

    # --------------------------------------------------------
    # 1️⃣ Build parent-child graph
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
    # 2️⃣ Identify leaf clusters from flat labels
    # --------------------------------------------------------
    leaf_labels = sub_clusterer.labels_

    leaf_members = defaultdict(list)
    for local_i, label in enumerate(leaf_labels):
        if label != -1:
            leaf_members[label].append(local_i)

    # --------------------------------------------------------
    # 3️⃣ Propagate membership upward
    # --------------------------------------------------------
    node_members = {}

    # initialize leaf cluster membership
    for leaf, members in leaf_members.items():
        node_members[leaf] = set(members)

    # process nodes in reverse depth order
    nodes_sorted = sorted(all_nodes, reverse=True)

    for node in nodes_sorted:
        if node not in node_members:
            node_members[node] = set()

        for child in children_map.get(node, []):
            node_members[node] |= node_members.get(child, set())

    # --------------------------------------------------------
    # 4️⃣ Compute depth using BFS
    # --------------------------------------------------------
    depth_map = {}
    roots = [n for n in all_nodes if n not in parent_map]

    queue = deque()
    for r in roots:
        depth_map[r] = 1
        queue.append(r)

    while queue:
        node = queue.popleft()
        for child in children_map.get(node, []):
            depth_map[child] = depth_map[node] + 1
            queue.append(child)

    # --------------------------------------------------------
    # 5️⃣ Add planet root node
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
    # 6️⃣ Add all cluster nodes with correct centroid + size
    # --------------------------------------------------------
    for node in all_nodes:
        members_local = node_members.get(node, set())

        if len(members_local) == 0:
            continue

        members_global = idx[list(members_local)]

        centroid = subset_3d[list(members_local)].mean(axis=0)

        parent = parent_map.get(node)
        parent_id = (f"{planet_id}_node_{parent}"
                     if parent is not None
                     else planet_node_id)

        rows.append({
            "type": "node",
            "node_id": f"{planet_id}_node_{node}",
            "parent_id": parent_id,
            "planet_id": planet_id,
            "depth": depth_map.get(node, 1),
            "size": len(members_local),
            "x": centroid[0],
            "y": centroid[1],
            "z": centroid[2],
            "image_id": None
        })

    # --------------------------------------------------------
    # 7️⃣ Attach images to leaf clusters
    # --------------------------------------------------------
    for leaf, members in leaf_members.items():
        parent_node = f"{planet_id}_node_{leaf}"

        for local_i in members:
            global_i = idx[local_i]

            rows.append({
                "type": "image",
                "node_id": None,
                "parent_id": parent_node,
                "planet_id": planet_id,
                "depth": depth_map.get(leaf, 1) + 1,
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
df.to_csv("unity_full_raw_condensed_tree_3d.csv", index=False)

print("Saved: unity_full_raw_condensed_tree_3d.csv")