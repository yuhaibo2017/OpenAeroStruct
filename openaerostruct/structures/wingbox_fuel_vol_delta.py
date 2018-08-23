from __future__ import print_function, division
import numpy as np

from openmdao.api import ExplicitComponent

try:
    from openaerostruct.fortran import OAS_API
    fortran_flag = True
    data_type = float
except:
    fortran_flag = False
    data_type = complex

def norm(vec):
    return np.sqrt(np.sum(vec**2))

class WingboxFuelVolDelta(ExplicitComponent):
    """
    Create a constraint to ensure the wingbox has enough internal volume to store the required fuel.

    parameters
    ----------
    nodes[ny, 3] : numpy array
        Coordinates of FEM nodes.
    A_int[ny-1] : numpy array
        Internal volume of each wingbox segment.
    fuelburn : float
        Fuel weight

    Returns
    -------
    fuel_vol_delta : numpy array
        If the value is negative, then there isn't enough volume for the fuel.
    fuel_vols[ny-1] : numpy array
        The magnitude of each individual panel's fuel-carrying volumes.
    """

    def initialize(self):
        self.options.declare('surface', types=dict)

    def setup(self):
        self.surface = surface = self.options['surface']

        self.ny = surface['num_y']

        self.add_input('fuelburn', val=0., units='kg')
        self.add_input('fuel_vols', val=np.zeros((self.ny-1)), units='m**3')
        self.add_output('fuel_vol_delta', val=0., units='m**3')

        self.declare_partials('*', '*', method='cs')

    def compute(self, inputs, outputs):
        fuel_weight = inputs['fuelburn']
        reserves = self.surface['Wf_reserve']
        fuel_density = self.surface['fuel_density']
        vols = inputs['fuel_vols']

        if self.surface['symmetry'] == True:
             fuel_weight /= 2.
             reserves /= 2.

        sum_vols = np.sum(vols)

        # This is used for the fuel-volume constraint. It should be positive for fuel to fit.
        outputs['fuel_vol_delta'] = sum_vols - (fuel_weight + reserves) / fuel_density
