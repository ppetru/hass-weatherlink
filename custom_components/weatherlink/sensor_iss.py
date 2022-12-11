from typing import Optional

from homeassistant.const import (
    UnitOfPrecipitationDepth,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfVolumetricFlux,
)

# TODO: remove this after Home Assistant 2023.1 is rolled out
class UnitOfIrradiance:
    """Irradiance units."""

    WATTS_PER_SQUARE_METER = "W/m²"
    BTUS_PER_HOUR_SQUARE_FOOT = "BTU/(h⋅ft²)"

from .api.conditions import IssCondition
from .const import DECIMALS_HUMIDITY, DECIMALS_RADIATION, DECIMALS_UV
from .sensor_common import WeatherLinkSensor, round_optional

__all__ = [
    "IssStatus",
    "Temperature",
    "ThswIndex",
    "Humidity",
    "WindSpeed",
    "WindBearing",
    "SolarRad",
    "UvIndex",
    "Rainfall",
    "Rainstorm",
]


class IssSensor(WeatherLinkSensor, abc=True):
    def __init_subclass__(
        cls,
        abc: bool = False,
        **kwargs,
    ) -> None:
        if not abc:
            kwargs["required_conditions"] = (IssCondition,)
        super().__init_subclass__(abc=abc, **kwargs)

    @property
    def _iss_condition(self) -> IssCondition:
        return self._conditions[IssCondition]

    @property
    def unique_id(self):
        return f"{super().unique_id}-iss"


class IssStatus(
    IssSensor,
    sensor_name="ISS Status",
    native_unit_of_measurement=None,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:information"

    @property
    def state(self):
        rx_state = self._iss_condition.rx_state
        if rx_state is None:
            return None
        return rx_state.name

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        return {
            "txid": c.txid,
            "battery": c.trans_battery_flag,
        }


class Temperature(
    IssSensor,
    sensor_name="Temperature",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class="temperature",
    state_class="measurement",
):
    @property
    def native_value(self):
        return self._iss_condition.temp

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        return {
            "dew_point": c.dew_point,
            "wet_bulb": c.wet_bulb,
            "heat_index": c.heat_index,
            "wind_chill": c.wind_chill,
            "thw_index": c.thw_index,
            "thsw_index": c.thsw_index,
        }


class ThswIndex(
    IssSensor,
    sensor_name="THSW index",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class="temperature",
    state_class="measurement",
):
    @property
    def native_value(self):
        return self._iss_condition.thsw_index


class Humidity(
    IssSensor,
    sensor_name="Humidity",
    native_unit_of_measurement="%",
    device_class="humidity",
    state_class="measurement",
):
    @property
    def state(self):
        return round_optional(self._iss_condition.hum, DECIMALS_HUMIDITY)


class WindSpeed(
    IssSensor,
    sensor_name="Wind speed",
    native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
    device_class="wind_speed",
    state_class="measurement",
):
    @property
    def icon(self):
        return "mdi:weather-windy"

    @property
    def native_value(self):
        return self._iss_condition.wind_speed_avg_last_2_min

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        return {
            "10_min": c.wind_speed_avg_last_10_min,
        }


class WindSpeedNow(
    IssSensor,
    sensor_name="Wind speed last",
    native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
    device_class="wind_speed",
    state_class="measurement",
):
    @property
    def icon(self):
        return "mdi:weather-windy"

    @property
    def native_value(self):
        return self._iss_condition.wind_speed_last


class WindMaxSpeed(
    IssSensor,
    sensor_name="Wind max speed",
    native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
    device_class="wind_speed",
    state_class="measurement",
):
    @property
    def icon(self):
        return "mdi:weather-windy"

    @property
    def native_value(self):
        return self._iss_condition.wind_speed_hi_last_2_min

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        return {
            "10_min": c.wind_speed_hi_last_10_min,
        }


class WindBearing(
    IssSensor,
    sensor_name="Wind bearing",
    native_unit_of_measurement="°",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:compass-rose"

    @property
    def state(self):
        return self._iss_condition.wind_dir_scalar_avg_last_2_min

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        return {
            "high": c.wind_dir_at_hi_speed_last_2_min,
            "10_min": c.wind_dir_scalar_avg_last_10_min,
            "10_min_high": c.wind_dir_at_hi_speed_last_10_min,
        }


class WindBearingNow(
    IssSensor,
    sensor_name="Wind bearing last",
    native_unit_of_measurement="°",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:compass-rose"

    @property
    def state(self):
        return self._iss_condition.wind_dir_last


class WindDirection(
    IssSensor,
    sensor_name="Wind direction",
    native_unit_of_measurement=None,
    device_class=None,
):
    _DIRECTIONS = (
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
        "N",
    )

    @property
    def icon(self):
        return "mdi:compass"

    @property
    def state(self):
        return self.bearing_to_dir(self._iss_condition.wind_dir_scalar_avg_last_2_min)

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        return {
            "high": self.bearing_to_dir(c.wind_dir_at_hi_speed_last_2_min),
            "10_min": self.bearing_to_dir(c.wind_dir_scalar_avg_last_10_min),
            "10_min_high": self.bearing_to_dir(c.wind_dir_at_hi_speed_last_10_min),
        }

    @classmethod
    def bearing_to_dir(cls, deg: Optional[int]) -> Optional[str]:
        if deg is None:
            return None
        return cls._DIRECTIONS[int(((deg % 360) + 11.25) / 22.5)]


class SolarRad(
    IssSensor,
    sensor_name="Solar rad",
    native_unit_of_measurement=UnitOfIrradiance.WATTS_PER_SQUARE_METER,
    device_class="irradiance",
    state_class="measurement",
):
    @property
    def icon(self):
        return "mdi:white-balance-sunny"

    @property
    def native_value(self):
        return round_optional(self._iss_condition.solar_rad, DECIMALS_RADIATION)


class UvIndex(
    IssSensor,
    sensor_name="UV index",
    native_unit_of_measurement="UV Index",
    device_class=None,
    state_class="measurement",
):
    @property
    def icon(self):
        return "mdi:shield-sun"

    @property
    def state(self):
        return round_optional(self._iss_condition.uv_index, DECIMALS_UV)


class RainRate(
    IssSensor,
    sensor_name="Rain rate",
    native_unit_of_measurement=UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR,
    device_class="precipitation_intensity",
    state_class="measurement",
):
    @property
    def icon(self):
        return "mdi:water"

    @property
    def native_value(self):
        return self._iss_condition.rain_rate_last

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        return {
            "high": c.rain_rate_hi,
            "15_min_high": c.rain_rate_hi_last_15_min,
        }


class Rainfall(
    IssSensor,
    sensor_name="Rainfall",
    native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
    device_class="precipitation",
    state_class="measurement",
):
    @property
    def icon(self):
        return "mdi:weather-pouring"

    @property
    def native_value(self):
        return self._iss_condition.rainfall_daily

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        return {
            "15_min": c.rainfall_last_15_min,
            "60_min": c.rainfall_last_60_min,
            "24_hr": c.rainfall_last_24_hr,
            "monthly": c.rainfall_monthly,
            "yearly": c.rainfall_year,
        }


class Rainstorm(
    IssSensor,
    sensor_name="Rainstorm",
    native_unit_of_measurement=UnitOfPrecipitationDepth.MILLIMETERS,
    device_class="precipitation",
    state_class="measurement",
):
    @property
    def icon(self):
        return "mdi:weather-lightning-rainy"

    @property
    def native_value(self):
        return self._iss_condition.rain_storm

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        return {
            "start": c.rain_storm_start_at,
            "last": c.rain_storm_last,
            "last_start": c.rain_storm_last_start_at,
            "last_end": c.rain_storm_last_end_at,
        }
