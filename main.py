import os

from dotenv import load_dotenv
from src.pipelines.data_pipeline import DataPipeline

load_dotenv()


def main() -> None:
    api_key: str | None = os.getenv("RIOT_API_KEY")
    if api_key is None:
        raise ValueError(f"error API Key, his value : {api_key}")

    # data recovery - each tier/division
    data_pipeline = DataPipeline(api_key)
    data_pipeline.run()


if __name__ == "__main__":
    main()
