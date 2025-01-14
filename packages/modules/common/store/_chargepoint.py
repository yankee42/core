from modules.common.component_state import ChargepointState
from modules.common.store import ValueStore
from modules.common.store._broker import pub_to_broker


class ChargepointValueStoreBroker(ValueStore[ChargepointState]):
    def __init__(self, cp_id: int):
        self.num = cp_id

    def set(self, state: ChargepointState) -> None:
        pub_to_broker("openWB/set/chargepoint/" + str(self.num) + "/get/voltage", state.voltages, 2)
        pub_to_broker("openWB/set/chargepoint/" + str(self.num) + "/get/current", state.currents, 2)
        pub_to_broker("openWB/set/chargepoint/" + str(self.num) + "/get/power_factor", state.power_factors, 2)
        pub_to_broker("openWB/set/chargepoint/" + str(self.num) + "/get/counter", state.imported, 2)
        pub_to_broker("openWB/set/chargepoint/" + str(self.num) + "/get/exported", state.exported, 2)
        pub_to_broker("openWB/set/chargepoint/" + str(self.num) + "/get/power_all", state.power_all, 2)
        pub_to_broker("openWB/set/chargepoint/" + str(self.num) + "/get/phases_in_use", state.phases_in_use, 2)
        pub_to_broker("openWB/set/chargepoint/" + str(self.num) + "/get/charge_state", state.charge_state, 2)
        pub_to_broker("openWB/set/chargepoint/" + str(self.num) + "/get/plug_state", state.plug_state, 2)


def get_chargepoint_value_store(id: int) -> ValueStore[ChargepointState]:
    return ChargepointValueStoreBroker(id)
