import json
from typing import Optional
import yaml
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from app.src.domain.entities.deal import Deal
from app.src.domain.entities.contact import Contact
from app.src.core.datetime_utils import get_timezone
from app.src.domain.entities.deal_stage import DealStage
from app.src.domain.repositories.chat_repository import ChatRepositoryPort
from app.src.domain.repositories.contact_repository import ContactRepositoryPort
from app.src.domain.repositories.deal_repository import DealRepositoryPort
from app.src.ports.octadesk_port import OctadeskPort
from app.src.ports.rdstation_port import RDStationPort
from app.src.contracts.octadesk.contact_response import OctadeskContactResponse


import os
from datetime import datetime
from pathlib import Path
import gc



class Importador:
    def __init__(
        self,
        octadesk_port: OctadeskPort,
        rdstation_port: RDStationPort,
        contact_repo: ContactRepositoryPort | None = None,
        deal_repo: DealRepositoryPort | None = None,
        chat_repo: ChatRepositoryPort | None = None,
    ):
        self._octadesk: OctadeskPort = octadesk_port
        self._rdstation: RDStationPort = rdstation_port
        self._contact_repo = contact_repo
        self._deal_repo = deal_repo
        self._chat_repo = chat_repo

    def all_phones(self, full_phone: str) -> list[str]:
        old_phone_format = full_phone[-8:]
        phone_without_9 = full_phone[:2] + old_phone_format
        return [full_phone, phone_without_9]

    def has_chat(self, full_phone: str) -> bool:
        for phone in self.all_phones(full_phone):
            chats = self._octadesk.get_chats_by_phone(phone)
            if chats is not None and len(chats) > 0:
                return True
        return False

    def get_existing_chat_id(self, full_phone: str) -> str | None:
        for phone in self.all_phones(full_phone):
            chats = self._octadesk.get_chats_by_phone(phone)
            if chats is not None and len(chats) > 0:
                return chats[0].get("id")
        return None  # pragma: no cover

    def has_contact(self, full_phone: str) -> str | None:
        for phone in self.all_phones(full_phone):
            contacts = self._octadesk.get_contacts_by_phone(phone)
            if contacts is not None and len(contacts) > 0:
                validated = [
                    OctadeskContactResponse.model_validate(c) for c in contacts
                ]
                return validated[0].id
        return None

    def start_process(self) -> None:
        dados =  json.loads(open(f"/home/mateus/bwt/formatador-planilha/final.json", "r").read())
        count = 0

        path = "/home/mateus/bwt/processados.txt"
        try:
            processados = open(path, "r").readlines()

        except FileNotFoundError:
            open(path, "w").write("")
            processados = []

        print(processados)

        with open(path, "a") as file:
            for _, value in dados.items():

                for data_str, dados_data in value.items():
                    all_data = (
                        # dados_data["contadadoscts_with_recurring_no_answer_data"] +
                        dados_data["contacts_created_data"] + 
                        dados_data["contacts_existing_data"]
                    )
                    created_at = datetime.fromisoformat(dados_data["insert_time"])
                    for info in all_data:
                        phone = info["phone"]
                        name = info["name"]

                        if f"{phone}\n" not in processados:
                            count +=1
                            try:
                                deals = self._rdstation.get_deals(name=name)
                                for deal_dict in deals["deals"]:
                                    deal = Deal.from_dict(deal_dict)
                                    contact_deal = deal.to_contact()
                                    if contact_deal.phone == phone:
                                        contact = self._contact_repo.find_by_phone(phone) 
                                        if contact:
                                            existing_deal = self._deal_repo.find_by_contact_id_and_rd_station_id (contact.id, deal.rdstation_id)
                                            if existing_deal is None:
                                                print("Deal para contato nao encontrado", contact_deal)
                                                self._deal_repo.save(deal=deal)
                                            else:
                                                existing_deal.created_at = created_at
                                                existing_deal.deal_status = deal.deal_status
                                                self._deal_repo.save(deal=existing_deal)


    
                            except Exception as e:
                                print ("ERRROOOO >>> ", e)

                            print(f"{data_str} {count} >>>>>> ", phone)
                            file.write(f"{phone}\n")
                            
                            processados.append(phone)

                            if count == 10:
                                gc.collect()
                                count = 0
                                file.flush()


                print("FInalizadp")


                            
                    # for info in dados_data["contacts_created_data"]:
                    #     aba.append([data_str, "contato criado", info["name"], info["phone"]] )
        
                    # for info in dados_data["contacts_with_recurring_no_answer_data"]:
                    #     aba.append([data_str, "contato sem comunicacao", info["name"], info["phone"]] )
        
                    # for info in dados_data["chats_started_data"]:
                    #     aba.append([data_str, "chat iniciado confirmado", info["name"], info["phone"]] )
                    
                    # for info in dados_data["chats_existing_data"]:
                    #     aba.append([data_str, "chat existente", info["name"], info["phone"]] )
                    
                    # for info in dados_data["chats_not_started_data"]:
                    #     aba.append([data_str, "chat iniciado sem confirmacao", info["name"], info["phone"]] )