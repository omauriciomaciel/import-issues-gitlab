import http
import requests
from typing import Mapping

# https://github.com/Kludex/starlette/blob/main/starlette/exceptions.py#L7
class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str | None = None, headers: Mapping[str, str] | None = None) -> None:
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

    def __str__(self) -> str:
        return f"{self.status_code}: {self.detail}"

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"


class GithubClient:
    def __init__(self, token, owner, repo):
        self.base_url = f'https://api.github.com/repos/{owner}/{repo}'
        self.token = token

    def _get_headers(self) -> dict[str, str]:
        headers = {
            'accept': 'application/vnd.github+json',
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        return headers

    def _get_full_url(self, endpoint) -> str:
        return f"{self.base_url}/{endpoint}"

    def _handle_response(self, response):
        if response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Falha na autenticação.",
            )
        if response.status_code == 404:
            raise HTTPException(
                status_code=404, detail="Recurso não encontrado."
            )
        if response.ok:
            try:
                return response.json()
            except Exception as e:
                return response.content
        try:
            error_detail = f" - {response.json()}"
        except Exception as e:
            error_detail = f" - {response.text}"
        raise HTTPException(
            status_code=500,
            detail=f"Erro na requisição: {response.status_code}{error_detail}",
        )

    def get(self, endpoint: str):
        """Faz uma requisição GET."""
        url = self._get_full_url(endpoint)
        response = requests.get(url, headers=self._get_headers())
        return self._handle_response(response)

    def post(self, endpoint: str, data: dict = None):
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def put(self, endpoint, data=None):
        """Faz uma requisição PUT."""
        url = self._get_full_url(endpoint)
        response = requests.put(url, headers=self.headers, json=data)
        return self._handle_response(response)

    def delete(self, endpoint: str):
        """Faz uma requisição DELETE."""
        url = self._get_full_url(endpoint)
        response = requests.delete(url, headers=self._get_headers())
        return self._handle_response(response)
