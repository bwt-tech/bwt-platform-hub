import httpx
from loguru import logger
from typing import Optional

from app.src.core.exceptions import IntegrationError
from app.src.domain.entities.pipeline import Pipeline
from app.src.ports.rdstation_port import RDStationPort
from app.src.config.settings import settings

BASEURL = settings.rdstation_url

class RDStationAdapter(RDStationPort):
    def __init__(self, token: str):
        self._token = token

    def _request(self, method: str, url: str, **kwargs):
        try:
            logger.info(f"Requesting {method} to {url}")
            response = httpx.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            logger.error(f"RDStation API RequestError: {exc}")
            raise IntegrationError(f"HTTP Request failed: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            logger.error(f"RDStation API HTTPStatusError: {exc.response.status_code}")
            raise IntegrationError(
                f"HTTP Status error: {exc.response.status_code}"
            ) from exc

    def get_users(self):
        return self._request("GET", f"{BASEURL}/users?token={self._token}")

    def get_campaigns(self, page):
        return self._request(
            "GET", f"{BASEURL}/campaigns?token={self._token}&page={page}"
        )

    def get_custom_fields(self, page):
        return self._request("GET", f"{BASEURL}/custom_fields?token={self._token}")

    def get_user(self, id):
        return self._request("GET", f"{BASEURL}/users/{id}?token={self._token}")

    def get_contacts(self, page_id: Optional[str] = None, phone: Optional[str] = None, start_date:Optional[str] = None):
        query_params = f"&phone={phone}" if phone else ""
        query_params += f"&page={page_id}" if page_id else ""
        query_params += f"&created_at_period=true&start_date={start_date}"if start_date else ""
        return self._request("GET", f"{BASEURL}/contacts?token={self._token}{query_params}")

    def get_products(self, page: str | None = None):
        page_param = f"&page={page}" if page else ""
        return self._request(
            "GET", f"{BASEURL}/products?token={self._token}{page_param}"
        )

    def get_tasks(self, page: str | None = None):
        page_param = f"&page={page}" if page else ""
        return self._request("GET", f"{BASEURL}/tasks?token={self._token}{page_param}")

    def get_deals(
        self,
        page_id: str | None = None,
        deal_stage_id: str | None = None,
        start_date: str | None = None,
        name: str | None = None
    ):
        query_params = f"&deal_stage_id={deal_stage_id}" if deal_stage_id else ""
        query_params += f"&page={page_id}" if page_id else ""
        query_params += f"&name={name}" if name else ""
        query_params += (
            f"&created_at_period=true&start_date={start_date}" if start_date else ""
        )
        return self._request(
            "GET", f"{BASEURL}/deals?token={self._token}{query_params}"
        )

    def get_deal_lost_reasons(self, page):
        page_param = f"&page={page}" if page else ""
        return self._request(
            "GET", f"{BASEURL}/deal_lost_reasons?token={self._token}{page_param}"
        )

    def get_deal_stages(self, page: str | None = None):
        page_param = f"&page={page}" if page else ""
        return self._request(
            "GET", f"{BASEURL}/deal_stages?token={self._token}{page_param}"
        )

    def get_deal_pipelines(self, page: str | None = None) -> list[Pipeline]:
        page_param = f"&page={page}" if page else ""
        raw = self._request(
            "GET", f"{BASEURL}/deal_pipelines?token={self._token}{page_param}"
        )
        pipelines = raw if isinstance(raw, list) else raw.get("deal_pipelines", [])
        return [Pipeline.from_dict(p) for p in pipelines]

    def get_deal_sources(self, page: str | None = None):
        page_param = f"&page={page}" if page else ""
        return self._request(
            "GET", f"{BASEURL}/deal_sources?token={self._token}{page_param}"
        )

    def get_deal(self, deal_id: Optional[str] ):
        return self._request("GET", f"{BASEURL}/deals/{deal_id}?token={self._token}")

    def put_deal(self, deal_id, stage_id, seller_name:Optional[str] = None, source: Optional[str] = None):
        url = f"{BASEURL}/deals/{deal_id}?token={self._token}"

        payload = {
            "deal_stage_id": stage_id
        }
        deal_custom_fields = [
                        {
                            "value": seller_name,
                            "custom_field_id": "6891173b068d8e001e46d643",
                        }
                    ]

        if source: 
            deal_custom_fields.append({
                            "value": "Octadesk",
                            "custom_field_id": "6887dd351b05cb0020089118"
                        })
            deal_custom_fields.append({
                            "value": "Octadesk",
                            "custom_field_id": "6a0c879e0b7a8a00163cc2d7"
                        })
        if seller_name:
            payload["deal"] = {
                    "deal_custom_fields": deal_custom_fields
                }
        return self._request("PUT", url, json=payload)

    def post_deal(self, stage_id:str, contact_name:str, phone:str):
        deal = {
            "deal": {
                "deal_stage_id": stage_id,
                "name": contact_name
            },
            "contacts":[{
                "name": contact_name, 
                "phones":[{
                    "phone": phone
                }]
            }],
            "deal_source": {
                "_id": "687f876171f45d0024099efd"
            }
        }
        return self._request("POST", f"{BASEURL}/deals?token={self._token}", json =deal)
