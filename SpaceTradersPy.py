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
            headquarters_waypoint = agent_info["headquarters"]
            headquarters_system = (
                headquarters_waypoint.split("-")[0] + "-" + headquarters_waypoint.split("-")[1]
            )
            self.headquarters = self.get_waypoint(
                waypoint= headquarters_waypoint,
                system = headquarters_system
            )
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
            headquarters_waypoint = agent_info["data"]["headquarters"]
            headquarters_system = (
                    headquarters_waypoint.split("-")[0] + "-" + headquarters_waypoint.split("-")[1]
            )
            headquarters_info = self.get_waypoint(
                waypoint=headquarters_waypoint,
                system=headquarters_system
            )
            self.headquarters = Waypoint(headquarters_info)
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
            return contract_list["data"][0]
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
            return factions_list["data"][0]
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
            return faction_info["data"][0]
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
            response_list = r.json()
            ship_list = []
            for ship in response_list["data"]:
                s = Ship(symbol=ship["symbol"],ship_info=ship)
                ship_list.append(s)
            return ship_list
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
            ship = Ship(
                symbol=ship_info["ship"]["symbol"],
                ship_info=ship_info["ship"]
            )
            self.credits = ship_info["agent"]["credits"]
            return ship
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return None

    def get_ship(self, ship_id):
        url = self.BASE_URL + f"my/ships/{ship_id}"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            ship_info = r.json()
            ship = Ship(
                symbol=ship_info["data"]["symbol"],
                ship_info=ship_info["data"]
            )
            return ship
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            systems = r.json()
            system_list = []
            for i in systems["data"]:
                system = System(i)
                system_list.append(system)
            return system_list
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return None

    def get_system(self, system):
        url = self.BASE_URL + f"systems/{system}"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            system_info = r.json()
            system = System(system_info["data"])
            return system
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return None

    def list_waypoints_in_system(self, system, limit=10, page=1):
        url = self.BASE_URL + f"systems/{system}/waypoints"

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
            waypoints = r.json()
            waypoint_list = []
            for wp in waypoints["data"]:
                waypoint = Waypoint(wp)
                waypoint_list.append(waypoint)
            return waypoint_list
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_waypoint(self, system, waypoint):
        url = self.BASE_URL + f"systems/{system}/waypoints/{waypoint}/"

        r = requests.get(url, headers=self.header)
        if r.status_code == 200:
            waypoint_info = r.json()
            return Waypoint(waypoint_info["data"])
        elif r.status_code == 401:
            raise TokenError()
        elif r.status_code == 404:
            raise ResourceNotFound()
        else:
            self.error = r.json()
            return self.error

    def get_market(self, system, waypoint):
        url = self.BASE_URL + f"systems/{system}/waypoints/{waypoint}/market"

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
            return None

    def get_shipyard(self, system, waypoint):
        url = self.BASE_URL + f"systems/{system}/waypoints/{waypoint}/shipyard"

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
            return None

    def get_jump_gate(self, system, waypoint):
        url = self.BASE_URL + f"systems/{system}/waypoints/{waypoint}/jump-gate"

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
            return None


class Ship:
    def __init__(self, symbol, ship_info):
        if symbol:
            self.symbol = symbol
        else:
            raise ShipSymbolNotDefined()

        for key in ship_info.keys():
            match key:
                case "registration":
                    self.registration = ship_info[key]
                case "nav":
                    self.nav = ShipNav(ship_info[key])
                case "crew":
                    self.crew = ship_info[key]
                case "frame":
                    self.frame = ship_info[key]
                case "reactor":
                    self.nav = ship_info[key]
                case "engine":
                    self.engine = ship_info[key]
                case "modules":
                    self.modules = ship_info[key]
                case "mounts":
                    self.mounts = ship_info[key]
                case "cargo":
                    self.nav = ship_info[key]
                case "fuel":
                    self.fuel = ship_info[key]
                case _:
                    pass

    def __str__(self):
        if self.symbol:
            return self.symbol
        else:
            raise ShipSymbolNotDefined()


class ShipNav:
    def __init__(self, nav_info):
        for key in nav_info.keys():
            match key:
                case "systemSymbol":
                    self.system_symbol = nav_info[key]
                case "waypointSymbol":
                    self.waypoint_symbol = nav_info[key]
                case "route":
                    self.route = nav_info[key]
                    self.destination = Waypoint(self.route["destination"])
                    self.departure = Waypoint(self.route["departure"])
                case "status":
                    self.status = nav_info[key]
                case "flightMode":
                    self.status = nav_info[key]


class System:
    def __init__(self, system_info):
        for key in system_info.keys():
            match key:
                case"symbol":
                    self.symbol = system_info[key]
                case "sectorSymbol":
                    self.sector_symbol = system_info[key]
                case "type":
                    self.type = system_info[key]
                case "x":
                    self.x = system_info[key]
                case "y":
                    self.x = system_info[key]
                case "waypoints":
                    self.waypoints = []
                    for wp in system_info[key]:
                        waypoint = Waypoint(wp)
                        self.waypoints.append(waypoint)
                case "factions":
                    self.factions = system_info[key]

    def __str__(self):
        return self.symbol


class Waypoint:
    def __init__(self, waypoint_info):
        self.sector = "X1"

        for key in waypoint_info.keys():
            match key:
                case "symbol":
                    self.symbol = waypoint_info[key]
                case "systemSymbol":
                    self.system_symbol = waypoint_info[key]
                case "waypoint_type":
                    self.waypoint_type = waypoint_info[key]
                case "x":
                    self.x = waypoint_info[key]
                case "y":
                    self.y = waypoint_info[key]
                case "orbitals":
                    self.orbitals = waypoint_info[key]
                case "faction":
                    self.faction = waypoint_info[key]
                case "traits":
                    self.traits = waypoint_info[key]
                case "chart":
                    self.waypoint_type = waypoint_info[key]
                case _:
                    pass

    def __str__(self):
        if self.symbol:
            return self.symbol
        else:
            raise WaypointValueNotSet()


# Exceptions
class ShipSymbolNotDefined(Exception):
    def __init__(self):
        self.message = "No Ship Symbol was defined"
        super().__init__(self.message)


class WaypointValueNotSet(Exception):
    def __init__(self):
        self.message = "Waypoint object has no waypoint value set"


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
