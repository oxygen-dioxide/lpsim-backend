from .system import SystemCharactorStatus
from .pyro_charactors import PyroCharactorStatus
from .dendro_charactors import DendroCharactorStatus
from .geo_charactors import GeoCharactorStatus
from .electro_charactors import ElectroCharactorStatus
from .foods import FoodStatus
from .artifacts import ArtifactCharactorStatus
from .event_cards import EventCardCharactorStatus


CharactorStatus = (
    PyroCharactorStatus | DendroCharactorStatus | GeoCharactorStatus
    | ElectroCharactorStatus
    | SystemCharactorStatus | FoodStatus | ArtifactCharactorStatus
    | EventCardCharactorStatus
)
