from logging import getLogger
from logging.config import dictConfig

from torch.utils.data import DataLoader
from torcheval.metrics import BinaryAUROC
from yaml import safe_load

from streamvigil import CSVDataset
from streamvigil.detectors import BasicAutoEncoder, BasicDetector


def main():
    # Logger
    with open("./examples/logging.yml", encoding="utf-8") as file:
        config = safe_load(file)
    dictConfig(config)
    logger = getLogger(__name__)

    random_state = 42

    # Dataset
    train_data = CSVDataset(
        "./data/INSECTS/INSECTS_Abr.csv.gz",
        train=True,
        random_state=random_state,
    )
    test_data = CSVDataset(
        "./data/INSECTS/INSECTS_Abr.csv.gz",
        train=False,
        random_state=random_state,
    )

    # DataLoader
    train_loader = DataLoader(
        train_data,
        batch_size=128,
    )
    test_loader = DataLoader(
        test_data,
        batch_size=64,
    )

    # Anomaly Detector
    auto_encoder = BasicAutoEncoder(
        encoder_dims=[33, 28, 23, 18],
        decoder_dims=[18, 23, 28, 33],
        batch_norm=True,
    )
    detector = BasicDetector(auto_encoder)

    # Training
    epochs = 5
    logger.info("Start training the model...")
    for epoch in range(epochs):
        logger.info(f"Epoch: {epoch+1}")
        for batch, (X, _) in enumerate(train_loader):
            loss = detector.train(X)

            if batch % 100 == 0:
                logger.info(f"Loss: {loss.item():>7f}")
    logger.info("Completed training the model!")

    # Evaluation
    metrics = BinaryAUROC()
    logger.info("Start evaluating the model...")

    for X, y in test_loader:
        scores = detector.predict(X)
        metrics.update(scores, y)

    # Compute AUROC score
    logger.info(f"AUROC Score: {metrics.compute()}")

    logger.info("Completed the evaluation of the model!")


if __name__ == "__main__":
    main()
