# Nemesis spawn data per level (list of dictionaries)
NEMESIS_SPAWN_DATA = [
    {"weak": 15, "medium": 0, "strong": 0, "elite": 0},  # Level 1
    {"weak": 20, "medium": 0, "strong": 0, "elite": 0},  # Level 2
    {"weak": 15, "medium": 5, "strong": 0, "elite": 0},  # Level 3
    {"weak": 15, "medium": 10, "strong": 0, "elite": 0}, # Level 4
    {"weak": 5, "medium": 15, "strong": 0, "elite": 0},  # Level 5
    {"weak": 10, "medium": 8, "strong": 4, "elite": 0}, # Level 6
    {"weak": 15, "medium": 15, "strong": 5, "elite": 0}, # Level 7
    {"weak": 10, "medium": 10, "strong": 10, "elite": 0},# Level 8
    {"weak": 15, "medium": 10, "strong": 5, "elite": 0}, # Level 9
    {"weak": 0, "medium": 20, "strong": 0, "elite": 0}, # Level 10
    {"weak": 5, "medium": 10, "strong": 12, "elite": 2}, # Level 11
    {"weak": 0, "medium": 15, "strong": 10, "elite": 5}, # Level 12
    {"weak": 10, "medium": 0, "strong": 8, "elite": 6},# Level 13
    {"weak": 15, "medium": 15, "strong": 15, "elite": 15},# Level 14
    {"weak": 25, "medium": 25, "strong": 25, "elite": 25} # Level 15
]

# Nemesis stats by type
NEMESIS_DATA = {
    "weak": {"health": 10, "speed": 2},
    "medium": {"health": 15, "speed": 3},
    "strong": {"health": 20, "speed": 4},
    "elite": {"health": 25, "speed": 5}
}