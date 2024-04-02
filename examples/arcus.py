from logging import getLogger
from logging.config import dictConfig

import numpy as np
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader
from yaml import safe_load

from streamvigil import ARCUS, CustomDataset
from streamvigil.detectors import RSRAE


def main():
    # Logger
    with open("./examples/logging.yml", encoding="utf-8") as file:
        config = safe_load(file)
    dictConfig(config)

    logger = getLogger(__name__)

    # Create ARCUS instance
    detector = RSRAE(encoder_dims=[128, 196, 256], rsr_dim=64, decoder_dims=[64, 96, 128])
    arcus = ARCUS(detector)

    # Dataset
    dataset = CustomDataset(csv_file="./data/GAS.csv")
    dataloader = DataLoader(dataset, batch_size=512, shuffle=False)

    # Initialize model pool with first batch
    logger.info("Start initializing model pool...")
    init_features, _ = next(iter(dataloader))
    arcus.init(x=init_features)
    logger.info("Complete model pool initialization!")

    all_scores = []
    all_labels = []

    # Train the models
    logger.info("Start anomaly detection simulation...")
    for x, y in dataloader:
        scores = arcus.run(x)
        all_scores.append(scores.detach().cpu().numpy())
        all_labels.append(y.numpy())

    all_scores = np.concatenate(all_scores)
    all_labels = np.concatenate(all_labels)

    # Compute ROC AUC score
    roc_auc = roc_auc_score(all_labels, all_scores)
    logger.info("ROC AUC Score: {}".format(roc_auc))

    logger.info("Completed anomaly detection simulation!")


if __name__ == "__main__":
    main()
