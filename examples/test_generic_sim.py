from typing import Optional

from hdf5_dataclass import HDF5Dataclass

from endgame_simulations.models import BaseInitialParams
from endgame_simulations.simulations import BaseState, GenericSimulation

# This example demonstrates how to use "GenericSimulation".

# Define the parameters
class Params(BaseInitialParams):
    w_rate: float = 0.1
    delta_time: float = 0.2


# The state class.
# The use of HDF5Dataclass implements a way to encode the state object into
# hdf5 format, allowing the state to be easily stored and reimported.
class State(HDF5Dataclass, BaseState[Params]):
    current_time: float
    params: Params
    _previous_delta_time: Optional[float] = None
    state_int: int = 0

    @classmethod
    def from_params(cls, params: Params, current_time):
        return cls(params=params, current_time=current_time)

    def get_params(self) -> Params:
        return self.params

    def reset_params(self, params: Params):
        self.params = params


# Here state has an integer that gets advanced by 1 every timestep. This just represents
# a way that the state might be advanced for a disease. Typically through the advancement
# would scale with delta time.
def advance_state(state: State, debug: bool = False):
    print(state)
    state.state_int = state.state_int + 1


# The new simulation
class NewSim(
    GenericSimulation[Params, State], state_class=State, advance_state=advance_state
):
    @property
    def _delta_time(self) -> float:
        return self.state.params.delta_time


sim = NewSim(start_time=1, params=Params(w_rate=0.2))
sim.run(end_time=4)
sim.reset_current_params(Params(delta_time=0.3))
sim.run(end_time=8)
