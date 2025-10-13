from enum import Enum


# Unit options
class UnitEnum(str, Enum):
    kg = "kg"
    stacks = "stacks"


# Equipment options
class EquipmentEnum(str, Enum):
    MACHINE = "machine"
    DUMBBELL = "dumbbell"
    BARBELL = "barbell"
    BODYWEIGHT = "bodyweight"
    KETTLEBELL = "kettlebell"
    RESISTANCE_BAND = "resistance_band"


# Category options
class CategoryEnum(str, Enum):
    CHEST = "chest"
    BACK = "back"
    LEGS = "legs"
    SHOULDERS = "shoulders"
    ARMS = "arms"
    CORE = "core"
