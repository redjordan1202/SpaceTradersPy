import requests
import json


class SpaceTrader:
    BASE_URL = "https://api.spacetraders.io/v2/"
    token = None
    header = None
    callsign = None
    headquarters = None
    starting_faction = None
    credits = None
    error = None

    def __init__(self, token=None, callsign=None):
        if token:
            self.token = token
            self.header = dict(
                Accept="application/json",
                Authorization=f"Bearer {self.token}"
            )
            agent_info = self.get_agent()
            self.callsign = agent_info["symbol"]
            self.headquarters = agent_info["headquarters"]
            self.starting_faction = agent_info["startingFaction"]
            self.credits = agent_info["credits"]
        else:
            if callsign:
                self.register_agent(callsign)
                self.header = dict(
                    Accept="application/json",
                    Authorization=f"Bearer {self.token}"
                )
            else:
                raise NoCallsign()

    def get_status(self):
        r = requests.get(self.BASE_URL, headers=self.header)
        status = r.json()
        return status

    def register_agent(self, callsign, faction="COSMIC"):
        header = {"Content-Type": "application/json"}
        payload = {
            "symbol": callsign,
            "faction": faction,
        }
        url = self.BASE_URL + "register"

        r = requests.post(url=url, headers=header, data=json.dumps(payload))

        if r.status_code == 200:
            agent_info = r.json()
            print(agent_info)
            self.token = agent_info["data"]["token"]
            self.callsign = agent_info["data"]["symbol"]
            self.callsign = agent_info["data"]["headquarters"]
            self.starting_faction = agent_info["data"]["startingFaction"]
            self.credits = agent_info["data"]["credits"]
        elif r.status_code == 409:
            raise AgentSymbolTaken(callsign=callsign)
        elif r.status_code == 401:
            raise TokenError()
        else:
            self.error = r.json()
            raise CouldNotRegisterAgent()

    # Agent Functions
    def get_agent(self):
        url = self.BASE_URL + "my/agent"

        r = requests.get(url, headers=self.header)

        if r.status_code == 200:
            agent_info = r.json()
            return agent_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        else:
            self.error = r.json()
            return self.error

    # Contract Functions
    def list_contracts(self, limit=10, page=1):
        url = self.BASE_URL + "my/contracts"
        if limit > 20:
            limit = 20
        if limit < 1:
            limit = 1
        if page < 1:
            page = 1
        params = dict(
            limit=limit,
            page=page
        )

        r = requests.get(url, headers=self.header, params=params)

        if r.status_code == 200:
            contract_list = r.json()
            return contract_list["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_contract(self, contract_id):
        url = self.BASE_URL + f"my/contracts/{contract_id}"

        r = requests.get(url, headers=self.header)

        if r.status_code == 200:
            contract_info = r.json()
            return contract_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def accept_contract(self, contract_id):
        url = self.BASE_URL + f"my/contracts/{contract_id}/accept"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            return 1
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            return 0

    def deliver_cargo_to_contract(self, contract_id):
        url = self.BASE_URL + f"my/contracts/{contract_id}/deliver"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            return 1
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            return 0

    def fulfill_contract(self, contract_id):
        url = self.BASE_URL + f"my/contracts/{contract_id}/fulfill"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            return 1
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            return 0

    # Faction Functions
    def list_factions(self, limit=10, page=1):
        url = self.BASE_URL + f"factions"

        if limit > 20:
            limit = 20
        if limit < 1:
            limit = 1
        if page < 1:
            page = 1
        params = dict(
            limit=limit,
            page=page
        )

        r = requests.get(url, headers=self.header, params=params)
        if r.status_code == 200:
            factions_list = r.json()
            return factions_list["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_faction(self, faction_symbol):
        url = self.BASE_URL + f"factions/{faction_symbol}"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            faction_info = r.json()
            return faction_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    # Fleet Functions
    def list_ships(self, limit=10, page=1):
        url = self.BASE_URL + f"my/ships"

        if limit > 20:
            limit = 20
        if limit < 1:
            limit = 1
        if page < 1:
            page = 1
        params = dict(
            limit=limit,
            page=page
        )

        r = requests.get(url, headers=self.header, params=params)
        if r.status_code == 200:
            ship_list = r.json()
            return ship_list["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def purchase_ship(self, ship_type, waypoint):
        url = self.BASE_URL + f"my/ships"

        data = dict(
            shipType=ship_type,
            waypointSymbol=waypoint
        )

        r = requests.post(url, headers=self.header, data=data)
        if r.status_code == 200:
            ship_info = r.json()
            self.credits = ship_info["agent"]["credits"]
            return ship_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_ship(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            ship_info = r.json()
            return ship_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_ship_cargo(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/cargo"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            cargo_info = r.json()
            return cargo_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def orbit_ship(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/orbit"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            nav_info = r.json()
            return nav_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def refine_material(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/refine"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            nav_info = r.json()
            return nav_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def create_chart(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/chart"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            chart_info = r.json()
            return chart_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_ship_cooldown(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/cooldown"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            chart_info = r.json()
            return chart_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def dock_ship(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/dock"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            nav_info = r.json()
            return nav_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def create_survey(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/survey"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            survey_info = r.json()
            return survey_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def extract_resources(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/extract"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            survey_info = r.json()
            return survey_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def jettison_cargo(self, ship_id, cargo, quantity):
        url = self.BASE_URL + f"my/ships/{ship_id}/jettison"

        data = dict(
            symbol=cargo,
            units=quantity
        )

        r = requests.post(url, headers=self.header, data=data)
        if r.status_code == 200:
            cargo_info = r.json()
            return cargo_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def jump_ship(self, ship_id, system):
        url = self.BASE_URL + f"my/ships/{ship_id}/jump"

        data = dict(systemSymbol=system)

        r = requests.post(url, headers=self.header, data=data)
        if r.status_code == 200:
            jump_info = r.json()
            return jump_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def navigate_ship(self, ship_id, system):
        url = self.BASE_URL + f"my/ships/{ship_id}/jump"

        data = dict(systemSymbol=system)

        r = requests.post(url, headers=self.header, data=data)
        if r.status_code == 200:
            nav_info = r.json()
            return nav_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def patch_ship_nav(self, ship_id, flight_mode):
        url = self.BASE_URL + f"my/ships/{ship_id}/nav"

        data = dict(flightMode=flight_mode)

        r = requests.patch(url, headers=self.header, data=data)
        if r.status_code == 200:
            nav_info = r.json()
            return nav_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_ship_nav(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/nav"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            nav_info = r.json()
            return nav_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def warp_ship(self, ship_id, waypoint):
        url = self.BASE_URL + f"my/ships/{ship_id}/jump"

        data = dict(waypointSymbol=waypoint)

        r = requests.post(url, headers=self.header, data=data)
        if r.status_code == 200:
            nav_info = r.json()
            return nav_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def sell_cargo(self, ship_id, cargo, quantity):
        url = self.BASE_URL + f"my/ships/{ship_id}/sell"

        data = dict(
            symbol=cargo,
            units=quantity,
        )

        r = requests.post(url, headers=self.header, data=data)
        if r.status_code == 200:
            cargo_info = r.json()
            return cargo_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def scan_systems(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/scan/systems"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            system_info = r.json()
            return system_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def scan_waypoints(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/scan/waypoints"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            waypoint_info = r.json()
            return waypoint_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def scan_ships(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/scan/ships"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            ship_info = r.json()
            return ship_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def refuel_ship(self, ship_id, quantity):
        url = self.BASE_URL + f"my/ships/{ship_id}/refuel"

        data = dict(units=quantity)

        r = requests.post(url, headers=self.header, data=data)
        if r.status_code == 200:
            refuel_info = r.json()
            return refuel_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def purchase_cargo(self, ship_id, cargo, quantity):
        url = self.BASE_URL + f"my/ships/{ship_id}/purchase"

        data = dict(
            symbol=cargo,
            units=quantity,
        )

        r = requests.post(url, headers=self.header, data=data)
        if r.status_code == 200:
            cargo_info = r.json()
            return cargo_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def transfer_cargo(self, ship_id, cargo, quantity, recipient):
        url = self.BASE_URL + f"my/ships/{ship_id}/transfer"

        data = dict(
            symbol=cargo,
            units=quantity,
            shipSymbol=recipient,
        )

        r = requests.post(url, headers=self.header, data=data)
        if r.status_code == 200:
            cargo_info = r.json()
            return cargo_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def negotiate_contract(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/negotiate/contract"

        r = requests.post(url, headers=self.header)
        if r.status_code == 200:
            contract_info = r.json()
            return contract_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_mounts(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}/mounts"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            mount_info = r.json()
            return mount_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def install_mount(self, ship_id, mount):
        url = self.BASE_URL + f"my/ships/{ship_id}/mount/install"

        data = dict(symbol=mount)

        r = requests.post(url, headers=self.header, data=data)
        if r.status_code == 200:
            mount_info = r.json()
            return mount_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def remove_mount(self, ship_id, mount):
        url = self.BASE_URL + f"my/ships/{ship_id}/mount/remove"

        data = dict(symbol=mount)

        r = requests.post(url, headers=self.header, data=data)
        if r.status_code == 200:
            mount_info = r.json()
            return mount_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    # System Functions
    def list_systems(self, limit=10, page=1):
        url = self.BASE_URL + f"systems"

        if limit > 20:
            limit = 20
        if limit < 1:
            limit = 1
        if page < 1:
            page = 1
        params = dict(
            limit=limit,
            page=page
        )

        r = requests.get(url, headers=self.header, params=params)
        if r.status_code == 200:
            system_list = r.json()
            return system_list["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_system(self, system):
        url = self.BASE_URL + f"systems/X1-{system}"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            system_info = r.json()
            return system_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def list_waypoints_in_system(self, system, limit=10, page=1):
        url = self.BASE_URL + f"systems/X1-{system}/waypoints"

        if limit > 20:
            limit = 20
        if limit < 1:
            limit = 1
        if page < 1:
            page = 1
        params = dict(
            limit=limit,
            page=page
        )

        r = requests.get(url, headers=self.header, params=params)
        if r.status_code == 200:
            waypoint_list = r.json()
            return waypoint_list["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_waypoint(self, system, waypoint):
        url = self.BASE_URL + f"systems/X1-{system}/waypoints/X1-{system}-{waypoint}"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            waypoint_info = r.json()
            return waypoint_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_market(self, system, waypoint):
        url = self.BASE_URL + f"systems/X1-{system}/waypoints/X1-{system}-{waypoint}/market"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            market_info = r.json()
            return market_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_shipyard(self, system, waypoint):
        url = self.BASE_URL + f"systems/X1-{system}/waypoints/X1-{system}-{waypoint}/shipyard"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            shipyard_info = r.json()
            return shipyard_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_jump_gate(self, system, waypoint):
        url = self.BASE_URL + f"systems/X1-{system}/waypoints/X1-{system}-{waypoint}/jump-gate"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            jump_gate_info = r.json()
            return jump_gate_info["data"]
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error


# Exceptions
class NoCallsign(Exception):
    def __init__(self):
        self.message = "Callsign needed to register new agent"
        super().__init__(self.message)


class CouldNotRegisterAgent(Exception):
    def __init__(self):
        self.message = "Error Registering Agent"
        super().__init__(self.message)


class AgentSymbolTaken(Exception):
    def __init__(self, callsign):
        self.message = f"Agent symbol {callsign} is already registered"
        super().__init__(self.message)


class TokenError(Exception):
    def __init__(self):
        self.message = "Failed to Parse Token. Token is missing or invalid"
        super().__init__(self.message)


class ResourceNotFound(Exception):
    def __init__(self):
        self.message = "The requested resource could not be found"
        super().__init__(self.message)
