"""total control provides controlling heating devices connected via total control application."""

from json import JSONDecodeError
import logging

import httpx

from .const import MANUFACTURER, REGISTERS, JsonDataField, PayloadField

_LOGGER = logging.getLogger(__name__)

API_URL = "https://totalcontrol.extraflame.it"
API_PATH_LOGIN = "/frontend/index_do.jsp"
API_PATH_DEVICE_LIST = "/api/stove-list.jsp"
API_PATH_DEVICE_INFO = "/api/stove-get-state.jsp"
API_PATH_DEVICE_WRITING = "/api/stove-set-parameter.jsp"
DEFAULT_TIMEOUT_VALUE = 500

HEADER_ACCEPT = "application/json"
HEADER_CONTENT_TYPE = "application/json"
HEADER_KEEP_ALIVE = "keep-alive"
HEADER = {
    "Accept": HEADER_ACCEPT,
    "Content-Type": HEADER_CONTENT_TYPE,
    "Connection": HEADER_KEEP_ALIVE,
}


class totalcontrol:
    """Manage extraflame heating device."""

    def __init__(
        self,
        email,
        password,
        unique_id,
    ) -> None:
        """Initialize the total control."""
        self.email = email
        self.password = password
        self.unique_id = unique_id
        self.token = None
        self.httpClient = httpx.AsyncClient()
        self.devices = []

    async def connect(self):
        """Connect user to URL."""
        await self.fetch_devices()

    async def login(self):
        """Authenticate with email and password to Agua IOT."""

        url = API_URL + API_PATH_LOGIN

        payload = {
            PayloadField.ACTION: "login_json",
            PayloadField.EMAIL: self.email,
            PayloadField.PASSWORD: self.password,
            PayloadField.UNIQUE_ID: self.unique_id,
        }
        res = await self.handle_webcall(url, payload)
        if res is False:
            raise totalcontrolError("Error while login")

        data = res[JsonDataField.DATA]
        self.token = data[JsonDataField.TOKEN]
        return True

    async def fetch_devices(self):
        """Fetch heating devices."""
        if self.token is None:
            await self.login()

        url = API_URL + API_PATH_DEVICE_LIST

        payload = {PayloadField.TOKEN: self.token}

        res = await self.handle_webcall(url, payload)
        if res is False:
            self.token = None
            raise totalcontrolError("Error while fetching devices")

        for dev in res[JsonDataField.DATA]:
            device = Device(
                dev[JsonDataField.SERIAL],
                dev[JsonDataField.CODE_ART],
                dev[JsonDataField.FRIENDLY_NAME],
                MANUFACTURER,
                dev[JsonDataField.MAC],
                dev[JsonDataField.STOVE_STATE],
                self,
            )
            self.devices.append(device)

    async def fetch_device_information(self):
        """Fetch device information of heating devices."""
        for dev in self.devices:
            await dev.update()

    async def update(self):
        """Fetch device information of heating device."""
        for dev in self.devices:
            await dev.update()

    async def handle_webcall(self, url, payload):
        """Fetch data from Extraflame site."""
        headers = HEADER

        try:
            _LOGGER.debug("URL: %s - HEADERS: %s DATA: %s", url, headers, payload)
            response = await self.httpClient.post(
                url,
                params=payload,
                headers=headers,
                follow_redirects=False,
                timeout=DEFAULT_TIMEOUT_VALUE,
            )

            _LOGGER.debug("Status_code: %s", response.status_code)

            if response.status_code == 200:
                resJson = response.json()
                if resJson:
                    _LOGGER.debug("Response.json: %s", resJson)
                    if resJson[JsonDataField.RESULT_CODE] == 0:
                        return resJson

        except httpx.TransportError as error:
            _LOGGER.error("Connection error to: %s, error: %s", url, error)
        except JSONDecodeError as error:
            _LOGGER.error("Invalid json in response: %s", error)

        return False


class Device:
    """Agua IOT heating device representation."""

    def __init__(
        self,
        serial,
        codArt,
        name,
        manufacturer,
        mac,
        stovestate,
        totalcontrolmanager,
    ) -> None:
        """Initialize extraflame device."""
        self.id = serial
        self.codArt = codArt
        self.name = name
        self.manufacturer = manufacturer
        self.mac = mac
        self.is_online = 1
        self.__totalcontrol = totalcontrolmanager
        self.__update_information(stovestate)

    async def update(self):
        """Update device entities."""
        await self.__update_device_information()

    async def __update_device_information(self):
        if self.__totalcontrol.token is None:
            await self.__totalcontrol.login()

        url = API_URL + API_PATH_DEVICE_INFO

        payload = {
            PayloadField.TOKEN: self.__totalcontrol.token,
            PayloadField.MAC: self.mac,
        }

        res = await self.__totalcontrol.handle_webcall(url, payload)
        if res is False:
            self.__totalcontrol.token = None
            raise totalcontrolError("Error while making device buffer read request.")

        self.__update_information(res[JsonDataField.DATA])

    def __update_information(self, data):
        information_dict = {}
        for key in REGISTERS:
            information_dict[key] = data[key]

        self.__information_dict = information_dict

    async def __request_writing(self, key, value):
        if self.__totalcontrol.token is None:
            await self.__totalcontrol.login()

        url = API_URL + API_PATH_DEVICE_WRITING

        payload = {
            PayloadField.TOKEN: self.__totalcontrol.token,
            PayloadField.MAC: self.mac,
            PayloadField.PARAMETER_ID: key,
            PayloadField.PARAMETER_VALUE: value,
        }

        res = await self.__totalcontrol.handle_webcall(url, payload)
        if res is False:
            self.__totalcontrol.token = None
            raise totalcontrolError("Error while request device writing")

    @property
    def registers(self):
        """Returns list of registers."""
        return list(REGISTERS.keys())

    def get_register(self, key):
        """Return register by key."""
        try:
            register = REGISTERS[key]
            register["value"] = self.__information_dict[key]
        except (KeyError, ValueError):
            return {}
        return register

    def get_register_value(self, key):
        """Return register value by key."""
        return self.get_register(key).get("value")

    def get_register_value_min(self, key):
        """Return register min value by key."""
        return self.get_register(key).get("set_min")

    def get_register_value_max(self, key):
        """Return register max value by key."""
        return self.get_register(key).get("set_max")

    def get_register_value_name(self, key):
        """Return register value name by key."""
        return REGISTERS(key).get(self.get_register_value(key))

    def get_register_value_description(self, key):
        """Return register description by key."""
        options = self.get_register_value_options(key)
        if options:
            return options.get(self.get_register_value(key))

        return self.get_register_value(key)

    def get_register_value_options(self, key):
        """Return register option by key."""
        if "enc_val" in self.get_register(key):
            return self.get_register(key).get("enc_val")

        return {}

    async def set_register_value(self, key, value):
        """Set register value."""
        set_min = REGISTERS[key]["set_min"]
        set_max = REGISTERS[key]["set_max"]
        parameterId = REGISTERS[key]["parameterId"]
        if float(value) < set_min or float(value) > set_max:
            raise ValueError(f"Value must be between {set_min} and {set_max}: {value}")
        parameterValue = int(value)
        try:
            await self.__request_writing(parameterId, parameterValue)
        except totalcontrolError as error:
            raise totalcontrolError(
                f"Error while trying to set: key={key} value={value} error={error}"
            ) from error

    async def set_register_value_description(self, key, value_description):
        """Set register value description."""
        try:
            options = self.get_register_value_options(key)
            value = list(options.keys())[
                list(options.values()).index(value_description)
            ]
        except (AttributeError, ValueError):
            value = value_description

        await self.set_register_value(key, value)


class totalcontrolError(Exception):
    """Exception type for Agua IOT."""

    def __init__(self, message) -> None:
        """Initialize totalcontrolError."""
        Exception.__init__(self, message)
