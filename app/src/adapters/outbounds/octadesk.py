import httpx
from loguru import logger

from app.src.core.exceptions import IntegrationError
from app.src.domain.entities.agent import Agent
from app.src.ports.octadesk_port import OctadeskPort


class OctadeskAdapter(OctadeskPort):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    def set_api_key(self, api_key):
        self.api_key = api_key

    def _get_headers(self):
        return {"accept": "application/json", "X-API-KEY": self.api_key}

    def _request(self, method: str, url: str, **kwargs):
        try:
            logger.info(f"{method} {url}")
            response = httpx.request(method, url, headers=self._get_headers(), **kwargs)
            status_code = response.status_code
            response_text = response.text

            if status_code >= 400:
                logger.warning("REQUEST ERROR")
                logger.warning(kwargs)
                logger.warning(response_text)

            response.raise_for_status()
            # Some methods like check might not return JSON, handle carefully.
            # We'll just return response and let the caller .json() it,
            # but current implementation does .json() in the methods.
            return response
        except httpx.RequestError as exc:
            logger.error(f"Octadesk API RequestError: {exc}")
            raise IntegrationError(f"HTTP Request failed: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            logger.error(f"Octadesk API HTTPStatusError: {exc.response.status_code}")

            raise IntegrationError(
                f"HTTP Status error: {exc.response.status_code}"
            ) from exc

    def check(self):
        url = f"{self.base_url}/auth/check"
        response = self._request("GET", url)
        logger.info(response)

    def get_chats(self):
        logger.info("Getting chats")
        url = f"{self.base_url}/chat?sort[direction]=asc&limit=2"
        return self._request("GET", url).json()

    def get_chats_by_phone(self, phone: str):
        logger.info(f"Getting chat by phone {phone}")
        url = f"{self.base_url}/chat?filters[0][operator]=in&filters[0][value]={phone}&filters[0][property]=contact.phoneContacts.number"
        return self._request("GET", url).json()

    def get_chat_numbers(self):
        logger.info("Getting chats numbers")
        url = f"{self.base_url}/chat/numbers"
        return self._request("GET", url).json()

    def get_events(self, chat_id: str):
        logger.info("Getting events")
        url = f"{self.base_url}/chat/{chat_id}/events"
        return self._request("GET", url).json()

    def get_messages(self, chat_id: str):
        logger.info("Getting messages")
        url = f"{self.base_url}/chat/{chat_id}/messages"
        return self._request("GET", url).json()

    def post_contacts(self, email: str, name: str, phone: str):
        request_data = {
            "name": name,
            "email": email,
            "phoneContacts": [{"number": phone, "countryCode": "55"}],
        }
        logger.info("Creating contacts")
        url = f"{self.base_url}/contacts"
        return self._request("POST", url, json=request_data).json()

    def get_contacts(self):
        url = f"{self.base_url}/contacts"
        logger.info(f"Getting contacts {url}")
        return self._request("GET", url).json()

    def get_contacts_by_phone(self, phone: str):
        filter_str = f"?filters[0][operator]=in&filters[0][value]={phone}&filters[0][property]=phoneContacts.number"
        url = f"{self.base_url}/contacts{filter_str}"
        logger.info(f"Getting contacts {url}")
        return self._request("GET", url).json()

    def get_contacts_by_id(self, contact_id: str):
        url = f"{self.base_url}/contacts/{contact_id}"
        logger.info(f"Getting contacts {url}")
        return self._request("GET", url).json()

    def get_chats_in_progress(self, page, agent_id: str):
        filters = (
            f"filters[0][operator]=ne&filters[0][value]=closed&filters[0][property]=status"
            f"&filters[1][operator]=eq&filters[1][value]={agent_id}&filters[1][property]=agent.id"
        )
        url = f"{self.base_url}/chat?page={page}&limit=100&{filters}"
        return self._request("GET", url).json()

    def get_templates(self):
        logger.info("Getting templates")
        url = f"{self.base_url}/chat/templates-message"
        return self._request("GET", url).json()

    def start_chat(self, contact: dict, configuration: dict):
        url = f"{self.base_url}/chat/send-template"
        phone = contact["phone"]
        name = contact["name"]
        email = contact["email"]
        payload = {
            "origin": {
                "contact": {"channel": "whatsapp", "code": configuration["phone"]}
            },
            "target": {
                "contact": {
                    "channel": "whatsapp",
                    "name": name,
                    "email": email,
                    "code": f"+55{int(phone)}",
                }
            },
            "content": {"templateMessage": {"id": configuration["template"]}},
            "options": {"automaticAssign": True},
        }
        logger.info(payload)
        response = self._request("POST", url, json=payload)
        logger.info(
            f"Envio de mensagem responsta: {response.status_code}, {response.text}"
        )
        return response.json()

    def notify_agent(self, chat_id: str, message, agent: Agent):
        url = f"{self.base_url}/chat/{chat_id}/messages"

        payload = {
            "chatId": chat_id,
            "type": "internal",
            "channel": "whatsapp",
            "body": message,
            "mentions": [
                {
                    "type": "agent",
                    "id": agent.id,
                    "name": agent.name,
                    "email": agent.email,
                }
            ],
        }
        logger.info(payload)
        response = self._request("POST", url, json=payload)
        return response.json()
