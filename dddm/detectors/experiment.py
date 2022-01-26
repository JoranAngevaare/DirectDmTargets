import typing as ty
import dddm
import numpy as np

export, __all__ = dddm.exporter()


@export
class Experiment:
    """
    Base class of experiments. To use, subclass and set the required attributes
    """
    detector_name: str = None
    target_material: str = None
    __version__: str = '0.0.0'
    e_min_kev: ty.Union[int, float] = None
    e_max_kev: ty.Union[int, float] = None
    exposure_tonne_year: ty.Union[int, float] = None
    energy_threshold_kev: ty.Union[int, float] = None
    cut_efficiency: ty.Union[int, float] = None
    detection_efficiency: ty.Union[int, float] = None
    interaction_type: str = 'SI'
    location: str = None  # Only needed when taking into account earth shielding
    n_energy_bins: int = 50

    _required_settings = ('detector_name',
                          'target_material',
                          'e_max_kev',
                          'e_min_kev',
                          'exposure_tonne_year',
                          'energy_threshold_kev',
                          'cut_efficiency',
                          'detection_efficiency',
                          'interaction_type',
                          'location',
                          'n_energy_bins',
                          'resolution',
                          'background_function',
                          )

    def __repr__(self):
        return f'{self.__class__.__name__}: {self.detector_name}. Hash:{self.detector_hash}'

    def _check_class(self):
        missing = []
        for att in set(self._required_settings) - {'resolution',
                                                   'background_function'}:
            if getattr(self, att) is None:
                missing.append(att)
        if missing:
            raise NotImplementedError(f'Missing {missing} for {self}')
        assert self.interaction_type in ['SI', 'migdal_SI'], f'{self.interaction_type} unknown'
        # Should not raise a ValueError
        self.resolution(energies_in_kev=[1])
        self.background_function(energies_in_kev=[1])

    def resolution(self, energies_in_kev):
        """Return resolution at <energies [keV]>"""
        raise NotImplementedError

    def background_function(self, energies_in_kev):
        """Return background at <energies [keV>"""
        raise NotImplementedError

    @property
    def effective_exposure(self):
        return self.exposure_tonne_year * self.cut_efficiency * self.detection_efficiency

    @property
    def config(self):
        config = {name: getattr(self, name) for name in self._required_settings}
        return config

    @property
    def detector_hash(self):
        return dddm.hashablize(self.config)

    @staticmethod
    def _flat_resolution(n_bins: int, resolution_kev: ty.Union[float, int]):
        """Return a flat resolution spectrum over energy range"""
        return np.full(n_bins, resolution_kev)

    @staticmethod
    def _flat_background(n_bins: int, events_per_kev_tonne_year: ty.Union[float, int]):
        """Return a background for n_bins in units of  1/(keV * t * yr)"""
        return np.full(n_bins, events_per_kev_tonne_year)
