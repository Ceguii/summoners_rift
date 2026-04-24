import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .exceptions import (
    RiotAPIError,
    RiotNotFoundError,
    RiotForbiddenError,
    RiotRateLimitError,
    RiotServerError,
    RiotTimeoutError,
    RiotConnectionError,
)

# ACCOUNT/MATCHS : "https://europe.api.riotgames.com"
# LEAGUES : "https://euw1.api.riotgames.com"


class RiotClient:
    def __init__(
        self,
        api_riot: str,
        platform_region: str = "euw1",
        regional_region: str = "europe",
        tagline: str = "EUW",
    ) -> None:
        self.api_riot = api_riot
        self.tagline = tagline
        self.platform_region = platform_region
        self.regional_region = regional_region
        self.headers = {"X-Riot-Token": self.api_riot}

        # league
        self.platform_url = f"https://{self.platform_region}.api.riotgames.com"
        # account, matchs
        self.regional_url = f"https://{self.regional_region}.api.riotgames.com"

        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session = requests.Session()
        self.session.mount("https://", adapter)

    def _request(self, endpoint: str, routing: str, params: dict | None = None) -> dict:
        if routing == "platform":
            url = f"{self.platform_url}{endpoint}"
        elif routing == "regional":
            url = f"{self.regional_url}{endpoint}"
        else:
            raise ValueError("Invalid routing")

        try:
            response = self.session.get(
                url, headers=self.headers, params=params, timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            response = e.response
            status = response.status_code if response else None

            if status == 404:
                raise RiotNotFoundError(
                    "resource not found", status_code=status, url=url
                )
            elif status == 403:
                raise RiotForbiddenError(
                    "Invalid API key or forbidden", status_code=status, url=url
                )
            elif status == 429:
                raise RiotRateLimitError(
                    "rate limit exceeded, retry...", status_code=status, url=url
                )
            elif 500 <= status < 600:
                raise RiotServerError("riot server error", status_code=status, url=url)

            else:
                raise RiotAPIError(
                    f"unexpected error {status}", status_code=status, url=url
                )

        except requests.exceptions.Timeout:
            raise RiotTimeoutError("request timeout", url=url)

        except requests.exceptions.ConnectionError:
            raise RiotConnectionError("connection error", url=url)
