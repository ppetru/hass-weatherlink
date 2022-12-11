from homeassistant.const import (
    UnitOfPressure,
    UnitOfTemperature,
)

from . import WeatherLinkCoordinator
from .api.conditions import LssBarCondition, LssTempHumCondition
from .const import DECIMALS_HUMIDITY, DOMAIN
from .sensor_air_quality import *
from .sensor_common import WeatherLinkSensor, round_optional
from .sensor_iss import *
from .sensor_moisture import *


async def async_setup_entry(hass, entry, async_add_entities):
    c: WeatherLinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(list(WeatherLinkSensor.iter_sensors_for_coordinator(c)))
    return True


class Pressure(
    WeatherLinkSensor,
    sensor_name="Pressure",
    native_unit_of_measurement=UnitOfPressure.HPA,
    device_class="pressure",
    state_class="measurement",
    required_conditions=(LssBarCondition,),
):
    @property
    def _lss_bar_condition(self) -> LssBarCondition:
        return self._conditions[LssBarCondition]

    @property
    def native_value(self):
        return self._lss_bar_condition.bar_sea_level

    @property
    def extra_state_attributes(self):
        condition = self._lss_bar_condition
        return {
            "trend": condition.bar_trend,
            "absolute": condition.bar_absolute,
        }


class InsideTemp(
    WeatherLinkSensor,
    sensor_name="Inside Temperature",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class="temperature",
    state_class="measurement",
    required_conditions=(LssTempHumCondition,),
):
    @property
    def _lss_temp_hum_condition(self) -> LssTempHumCondition:
        return self._conditions[LssTempHumCondition]

    @property
    def native_value(self):
        return self._lss_temp_hum_condition.temp_in

    @property
    def extra_state_attributes(self):
        condition = self._lss_temp_hum_condition
        return {
            "dew_point": condition.dew_point_in,
            "heat_index": condition.heat_index_in,
        }


class InsideHum(
    WeatherLinkSensor,
    sensor_name="Inside Humidity",
    native_unit_of_measurement="%",
    device_class="humidity",
    state_class="measurement",
    required_conditions=(LssTempHumCondition,),
):
    @property
    def _lss_temp_hum_condition(self) -> LssTempHumCondition:
        return self._conditions[LssTempHumCondition]

    @property
    def state(self):
        return round(self._lss_temp_hum_condition.hum_in, DECIMALS_HUMIDITY)
