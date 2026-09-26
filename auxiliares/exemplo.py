import requests
import json

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json; version=v1_web"
}

base_url = "https://api.homolog.brasileiroswinetours.com.br"

auth_response = requests.post(f"{base_url}/auth/login/",
                    headers=headers,
              json={
    "scope": "b2bit",
    "email": "supervisor_vendas@b2bit.company",
    "password": "b2bit123"
}).json()

# print(json.dumps( auth_response, indent=2))

token = auth_response["tokens"]["access"]
headers["Authorization"] = f"Bearer {token}"

#  Pesquisa por nomes
# print(requests.get(f"{base_url}/sales/accounts?search=Rosilene L", headers=headers).json())

print(json.dumps(requests.get(f"{base_url}/sales/deals?account=28", headers=headers).json(), indent=2))


# print(requests.post(f"{base_url}/sales/accounts/", headers=headers,  json={
#     "name": "M Venancio",
#     "type": "B2C"
# }).json())

# RESPONSE DA CRIACAO DE CONTA
# {"id":27,"name":"M Venancio","document":null,"type":"B2C","net_fare_percentage":"0.00"}


# print(requests.post(f"{base_url}/sales/accounts/27/contacts/", headers=headers,  json={
#     "name": "M Venancio",
#     "email": "newemail@email.com",
#     "phone": {
#         "country_code": "+55",
#         "number": "11222223333"
#     },
#     "document": "111111"
# }).text)

# RESPONSE DO CONTATO
# {"id":35,"name":"M Venancio","email":"newemail@email.com","document":"111111","phone":{"id":182,"country_code":"+55","number":"11222223333"},"address":null,"zip_code":null,"is_foreign":false,"account":{"id":27,"name":"M Venancio","document":null,"type":"B2C","net_fare_percentage":"0.00"}}

# print(requests.post(f"{base_url}/sales/deals/", headers=headers,  json={
#    "contact":"35",
#    "account":"27",
#    "origin":"WHATSAPP"
# }).text)

# RESPONSE DA NEGOCIACAO
#  {"id":47,"contact":{"id":35,"name":"M Venancio","email":"newemail@email.com","document":"111111","phone":{"id":182,"country_code":"+55","number":"11222223333"},"address":null,"zip_code":null,"is_foreign":false,"account":{"id":27,"name":"M Venancio","document":null,"type":"B2C","net_fare_percentage":"0.00"}},"account":{"id":27,"name":"M Venancio","document":null,"type":"B2C","net_fare_percentage":"0.00"},"responsible":{"id":3,"name":"Miguel","avatar":{"id":96,"high":"https://wine-tour-homologation-bucket.s3.amazonaws.com/media/images/02f1067ba209434fb582008246e38e3a_high.png","medium":"https://wine-tour-homologation-bucket.s3.amazonaws.com/media/images/02f1067ba209434fb582008246e38e3a_medium.png","low":"https://wine-tour-homologation-bucket.s3.amazonaws.com/media/images/02f1067ba209434fb582008246e38e3a_low.png"}},"stage":"NEW_DEAL","origin":"WHATSAPP","description":null,"created":"2026-07-27T16:16:05.416686-03:00","modified":"2026-07-27T16:16:05.416686-03:00","contact_info":{"id":35,"name":"M Venancio","email":"newemail@email.com","document":"111111","phone":{"id":182,"country_code":"+55","number":"11222223333"},"is_foreign":false},"categories":[],"lost_reason":null,"lost_reason_notes":null,"finished_at":null}

# print(requests.get(f"{base_url}/sales/deals/47", headers=headers).text)

# print(requests.post(f"{base_url}/sales/deals/47/update-deal-status/", headers=headers,  json={
#    "stage":"CONTACTED"
# }).text)

# Obter funcionarios
# https://api.homolog.brasileiroswinetours.com.br/auth/company-users/?page=1&pageSize=6&fields=id,avatar,name&page_size=6


# https://api.homolog.brasileiroswinetours.com.br/sales/deals/46/set-responsible/
# {responsible: 7}

# print(requests.get(f"{base_url}/auth/company-users/", headers=headers).text)
#  {"count":9,"next":null,"previous":null,"results":[{"id":62,"name":"Supervisor de Logística","email":"supervisor_logistica@b2bit.company","avatar":null,"is_active":true,"language":"pt-BR","created":"2026-01-19T10:59:56.121530-03:00","modified":"2026-02-26T16:02:50.580660-03:00","company":{"id":2,"name":"B2bit"},"company_branch":null,"document":null,"phone":{"id":118,"country_code":"55","number":"84999999999"},"deal_categories_names":[],"date_of_birth":"1999-01-19","rocket_chat_id":"vYr2P3hwucSXnS4ro","address":{"id":573,"info":"Avenida Amintas 3700 Torre Trade, Sala 1903 - Lagoa Nova, Natal - RN, 59075-810, Brazil"}},{"id":61,"name":"João Elias","email":"contato@brasilierosemmendoza.com.br","avatar":null,"is_active":true,"language":"pt-BR","created":"2026-01-12T10:53:43.357244-03:00","modified":"2026-01-12T10:53:44.486731-03:00","company":{"id":2,"name":"B2bit"},"company_branch":null,"document":"06642002903","phone":{"id":114,"country_code":"55","number":"46999400630"},"deal_categories_names":[],"date_of_birth":"1988-11-16","rocket_chat_id":"DFPwEaqaLY8qxbaTC","address":{"id":570,"info":"R. Elias Scalco, 69 - Luther King, Francisco Beltrão - PR, 85605-400, Brazil"}},{"id":16,"name":"Administrador","email":"administrador@b2bit.company","avatar":null,"is_active":true,"language":"pt-BR","created":"2025-03-10T09:08:21.203440-03:00","modified":"2026-04-18T10:07:08.607447-03:00","company":{"id":2,"name":"B2bit"},"company_branch":null,"document":"123","phone":{"id":18,"country_code":"55","number":"84988312556"},"deal_categories_names":[],"date_of_birth":"2025-03-10","rocket_chat_id":"9Km4myuNKpSWsvPtm","address":{"id":19,"info":"Av. Amintas Barros, 3700 - Lagoa Nova, Natal - RN, 59075-810, Brazil"}},{"id":8,"name":"Operador de Logística","email":"logistica@b2bit.company","avatar":null,"is_active":true,"language":"pt-BR","created":"2025-02-07T20:20:14.171814-03:00","modified":"2026-01-19T11:02:36.819428-03:00","company":{"id":2,"name":"B2bit"},"company_branch":null,"document":"123","phone":{"id":7,"country_code":"55","number":"84988312556"},"deal_categories_names":[],"date_of_birth":"2025-02-07","rocket_chat_id":"JuQNtZ8syHJfkHRcQ","address":{"id":6,"info":"Av. Amintas Barros, 3700 - Lagoa Nova, Natal - RN, 59075-810, Brazil"}},{"id":7,"name":"Reservista","email":"reservista@b2bit.company","avatar":null,"is_active":true,"language":"pt-BR","created":"2025-02-07T20:19:38.535722-03:00","modified":"2025-12-01T10:56:02.836991-03:00","company":{"id":2,"name":"B2bit"},"company_branch":null,"document":"123","phone":{"id":6,"country_code":"55","number":"84988312556"},"deal_categories_names":[],"date_of_birth":"2025-02-07","rocket_chat_id":"TLt8J26gG8ieorFxR","address":{"id":5,"info":"Av. Amintas Barros, 3700 - Lagoa Nova, Natal - RN, 59075-810, Brazil"}},{"id":6,"name":"Supervisor Reservas","email":"supervisor_reservas@b2bit.company","avatar":null,"is_active":true,"language":"pt-BR","created":"2025-02-07T20:19:08.560012-03:00","modified":"2026-07-14T10:08:05.953415-03:00","company":{"id":2,"name":"B2bit"},"company_branch":null,"document":"123","phone":{"id":5,"country_code":"55","number":"84988312556"},"deal_categories_names":[],"date_of_birth":"2025-02-07","rocket_chat_id":"SLTHMvtGkiyCKii8a","address":{"id":4,"info":"Av. Amintas Barros, 3700 - Lagoa Nova, Natal - RN, 59075-810, Brazil"}},{"id":5,"name":"Vendedor","email":"vendedor@b2bit.company","avatar":null,"is_active":true,"language":"pt-BR","created":"2025-02-07T20:18:23.238286-03:00","modified":"2025-12-10T09:39:30.928997-03:00","company":{"id":2,"name":"B2bit"},"company_branch":null,"document":"123","phone":{"id":4,"country_code":"55","number":"84988312556"},"deal_categories_names":[],"date_of_birth":"2025-02-07","rocket_chat_id":"GjRacc43TPExAYzBp","address":{"id":3,"info":"Av. Amintas Barros, 3700 - Lagoa Nova, Natal - RN, 59075-810, Brazil"}},{"id":4,"name":"Supervisor Vendas","email":"supervisor_vendas@b2bit.company","avatar":null,"is_active":true,"language":"pt-BR","created":"2025-02-07T20:17:51.804581-03:00","modified":"2026-07-27T18:36:04.669141-03:00","company":{"id":2,"name":"B2bit"},"company_branch":null,"document":"123","phone":{"id":3,"country_code":"55","number":"84988312556"},"deal_categories_names":[],"date_of_birth":"2025-02-07","rocket_chat_id":"aCmXoj4jTaCtXMAf2","address":{"id":2,"info":"Av. Amintas Barros, 3700 - Lagoa Nova, Natal - RN, 59075-810, Brazil"}},{"id":3,"name":"Miguel","email":"miguel@b2bit.company","avatar":{"id":96,"high":"https://wine-tour-homologation-bucket.s3.amazonaws.com/media/images/02f1067ba209434fb582008246e38e3a_high.png","medium":"https://wine-tour-homologation-bucket.s3.amazonaws.com/media/images/02f1067ba209434fb582008246e38e3a_medium.png","low":"https://wine-tour-homologation-bucket.s3.amazonaws.com/media/images/02f1067ba209434fb582008246e38e3a_low.png"},"is_active":true,"language":"pt-BR","created":"2025-02-07T19:53:26.743965-03:00","modified":"2026-07-27T18:41:09.837625-03:00","company":{"id":2,"name":"B2bit"},"company_branch":null,"document":"123","phone":{"id":2,"country_code":"55","number":"84988312556"},"deal_categories_names":[],"date_of_birth":"2025-02-07","rocket_chat_id":"rJL3mxuyBGsZLDuXq","address":{"id":1,"info":"483 Green Lanes, London N13 4BS, United Kingdom"}}]}

# print(requests.post(f"{base_url}/sales/deals/47/set-responsible/", headers=headers,  json={
#     "responsible": 61
# }).text)
