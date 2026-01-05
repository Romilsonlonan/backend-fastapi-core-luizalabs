# Facilita imports como: from app.crud_modules import create_club, get_athletes_with_health_data, ...
from .clubs import (
    create_club, get_clubs, get_club, get_club_with_players, update_club, delete_club, get_total_clubs_count
)
from .goalkeepers import (
    create_goalkeeper, get_goalkeepers, get_goalkeeper, update_goalkeeper, delete_goalkeeper
)
from .field_players import (
    create_field_player, get_field_players, get_field_player, update_field_player, delete_field_player
)
from .athletes_common import (
    update_athlete_health, create_athlete_progress, get_athlete_progress,
    create_nutritional_plan, get_nutritional_plans,
    get_top_goal_scorers, get_top_players_by_statistic, get_top_players_by_age,
    get_total_athletes_count, get_athletes_with_health_data
)
from .users import (
    get_user, get_user_by_email, get_users, create_user, update_user_profile_image,
    update_user_profile, update_user_password, delete_user, create_admin_user_if_not_exists
)
from .training_routines import (
    create_training_routine, get_training_routines, get_training_routine,
    update_training_routine, delete_training_routine
)

__all__ = [
    # clubs
    "create_club", "get_clubs", "get_club", "get_club_with_players", "update_club", "delete_club", "get_total_clubs_count",
    # goalkeepers
    "create_goalkeeper", "get_goalkeepers", "get_goalkeeper", "update_goalkeeper", "delete_goalkeeper",
    # field_players
    "create_field_player", "get_field_players", "get_field_player", "update_field_player", "delete_field_player",
    # athletes_common
    "update_athlete_health", "create_athlete_progress", "get_athlete_progress",
    "create_nutritional_plan", "get_nutritional_plans",
    "get_top_goal_scorers", "get_top_players_by_statistic", "get_top_players_by_age",
    "get_total_athletes_count", "get_athletes_with_health_data",
    # users
    "get_user", "get_user_by_email", "get_users", "create_user", "update_user_profile_image",
    "update_user_profile", "update_user_password", "delete_user", "create_admin_user_if_not_exists",
    # training_routines
    "create_training_routine", "get_training_routines", "get_training_routine",
    "update_training_routine", "delete_training_routine",
]