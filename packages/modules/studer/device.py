#!/usr/bin/env python3
""" Modul zum Auslesen von Alpha Ess Speichern, Zählern und Wechselrichtern.
"""
import sys
from typing import Dict, List, Union

from helpermodules import log
from modules.common import modbus
from modules.common.abstract_device import AbstractDevice
from modules.common.component_context import SingleComponentUpdateContext
from modules.studer import bat
from modules.studer import inverter


def get_default_config() -> dict:
    return {
        "name": "Studer",
        "type": "studer",
        "id": 0,
        "configuration":
        {
            "ip_address": "192.168.193.15"
        }
    }


studer_component_classes = Union[bat.StuderBat, inverter.StuderInverter]


class Device(AbstractDevice):
    COMPONENT_TYPE_TO_CLASS = {
        "bat": bat.StuderBat,
        "inverter": inverter.StuderInverter
    }

    def __init__(self, device_config: dict) -> None:
        self._components = {}  # type: Dict[str, studer_component_classes]
        try:
            ip_address = device_config["configuration"]["ip_address"]
            self.client = modbus.ModbusClient(ip_address, 502)
            self.device_config = device_config
        except Exception:
            log.MainLogger().exception("Fehler im Modul "+device_config["name"])

    def add_component(self, component_config: dict) -> None:
        component_type = component_config["type"]
        if component_type in self.COMPONENT_TYPE_TO_CLASS:
            self._components["component"+str(component_config["id"])] = (self.COMPONENT_TYPE_TO_CLASS[component_type](
                component_config, self.client))
        else:
            raise Exception(
                "illegal component type " + component_type + ". Allowed values: " +
                ','.join(self.COMPONENT_TYPE_TO_CLASS.keys())
            )

    def update(self) -> None:
        log.MainLogger().debug("Start device reading " + str(self._components))
        if self._components:
            for component in self._components:
                # Auch wenn bei einer Komponente ein Fehler auftritt, sollen alle anderen noch ausgelesen werden.
                with SingleComponentUpdateContext(self._components[component].component_info):
                    self._components[component].update()
        else:
            log.MainLogger().warning(
                self.device_config["name"] +
                ": Es konnten keine Werte gelesen werden, da noch keine Komponenten konfiguriert wurden."
            )


def read_legacy(argv: List[str]) -> None:
    COMPONENT_TYPE_TO_MODULE = {
        "bat": bat,
        "inverter": inverter
    }
    component_type = argv[1]
    ip_address = argv[2]

    device_config = get_default_config()
    device_config["configuration"]["ip_address"] = ip_address
    dev = Device(device_config)
    if component_type in COMPONENT_TYPE_TO_MODULE:
        component_config = COMPONENT_TYPE_TO_MODULE[component_type].get_default_config()
        if component_type == "bat":
            try:
                num = int(argv[3])
            except IndexError:
                num = None
        else:
            vc_count = int(argv[3])
            vc_type = argv[4]
            try:
                num = int(argv[5])
            except IndexError:
                num = None
            component_config["configuration"]["vc_count"] = vc_count
            component_config["configuration"]["vc_type"] = vc_type
    else:
        raise Exception(
            "illegal component type " + component_type + ". Allowed values: " +
            ','.join(COMPONENT_TYPE_TO_MODULE.keys())
        )
    component_config["id"] = num
    dev.add_component(component_config)

    log.MainLogger().debug('Studer IP-Adresse: ' + str(ip_address))

    dev.update()


if __name__ == "__main__":
    try:
        read_legacy(sys.argv)
    except Exception:
        log.MainLogger().exception("Fehler im Studer Skript")
