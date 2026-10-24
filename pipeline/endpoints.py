# Everything excluding shift charts
BASE_URL = "https://api-web.nhle.com"
SCHEDULE_ENDPOINT = "/v1/club-schedule-season/{team}/{season}"
PBP_ENDPOINT = "/v1/gamecenter/{game_id}/play-by-play"
BOXSCORE_ENDPOINT = "/v1/gamecenter/{game_id}/boxscore"
ROSTER_ENDPOINT = "/v1/roster/{team}/{season}"

# Shift Charts Information
BASE_REST_URL = "https://api.nhle.com/stats/rest"
SHIFTCHART_ENDPOINT = "/en/shiftcharts?cayenneExp=gameId={game_id}"