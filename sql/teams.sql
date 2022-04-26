CREATE TABLE team
(
    id SERIAL,
    full_team_name VARCHAR(200),
    team_name_slug VARCHAR(50),
    team_name_header VARCHAR(50),
    name VARCHAR(50),
    base VARCHAR(100),
    team_chief VARCHAR(100),
    technical_chief VARCHAR(100),
    power_unit VARCHAR(100),
    first_team_entry VARCHAR(100),
    highest_race_finish VARCHAR(50),
    pole_positions VARCHAR(50),
    fastest_laps VARCHAR(50),
    main_image VARCHAR(500),
    flag_img_url VARCHAR(500),
    main_logo_url VARCHAR(500),
    small_logo_url VARCHAR(500),
    podium_finishes VARCHAR(50),
    championship_titles VARCHAR(50),
    drivers_scraped BYTEA
)