# ============================================================
# FEATURE EXTRACTION USING PRETRAINED RESNET (WITH IMAGE IDS)
# ============================================================

import torch
import torchvision.transforms as transforms
from torchvision import models
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader

import numpy as np
from tqdm import tqdm
import os

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
DATASET_PATH = r"./seg_train"

BATCH_SIZE = 32
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

OUTPUT_FEATURES = "resnet_features.npy"
OUTPUT_LABELS = "resnet_labels.npy"
OUTPUT_CLASSES = "class_names.npy"
OUTPUT_IMAGE_IDS = "image_ids.npy"   # NEW

# ------------------------------------------------------------
# TRANSFORMS
# ------------------------------------------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# ------------------------------------------------------------
# DATASET
# ------------------------------------------------------------
dataset = ImageFolder(DATASET_PATH, transform=transform)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)

class_names = dataset.classes
print("Classes:", class_names)

# ------------------------------------------------------------
# EXTRACT IMAGE IDS (FILENAMES) IN ORDER
# ------------------------------------------------------------
image_ids = [
    os.path.basename(path) for path, _ in dataset.samples
]

# ------------------------------------------------------------
# LOAD RESNET (FEATURE EXTRACTOR)
# ------------------------------------------------------------
resnet = models.resnet50(pretrained=True)
resnet = torch.nn.Sequential(*list(resnet.children())[:-1])  # remove FC
resnet = resnet.to(DEVICE)
resnet.eval()

# ------------------------------------------------------------
# FEATURE EXTRACTION
# ------------------------------------------------------------
features = []
labels = []

with torch.no_grad():
    for images, targets in tqdm(dataloader, desc="Extracting features"):
        images = images.to(DEVICE)

        output = resnet(images)                   # (B, 2048, 1, 1)
        output = output.view(output.size(0), -1)  # (B, 2048)

        features.append(output.cpu().numpy())
        labels.append(targets.numpy())

features = np.vstack(features)
labels = np.hstack(labels)

print("Feature shape:", features.shape)
print("Image IDs:", len(image_ids))

# ------------------------------------------------------------
# SANITY CHECK (VERY IMPORTANT)
# ------------------------------------------------------------
assert features.shape[0] == len(image_ids), \
    "Mismatch between features and image IDs!"

# ------------------------------------------------------------
# SAVE TO DISK
# ------------------------------------------------------------
np.save(OUTPUT_FEATURES, features)
np.save(OUTPUT_LABELS, labels)
np.save(OUTPUT_CLASSES, np.array(class_names))
np.save(OUTPUT_IMAGE_IDS, np.array(image_ids))   # NEW

print("Features, labels, image IDs, and class names saved successfully.")
