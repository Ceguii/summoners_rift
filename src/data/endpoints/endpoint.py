class Endpoint:
    # get puuid using riot id
    ACCOUNT_BY_RIOT_ID = "/riot/account/v1/accounts/by-riot-id/{summoner_id}/{tagline}?api_key={api_riot}"
    
    # get match details using match_id
    MATCH_DETAILS_USING_MATCH_ID = "/lol/match/v5/matches/{match_id}?api_key={api_riot}"

    # get all plauyers league using queue, tier, division
    MASTER_LEAGUE = "/lol/league/v4/masterleagues/by-queue/{queue}?api_key={api_riot}"
    GRANDMASTER_LEAGUE = (
        "/lol/league/v4/grandmasterleagues/by-queue/{queue}?api_key={api_riot}"
    )
    CHALLENGER_LEAGUE = (
        "/lol/league/v4/challengerleagues/by-queue/{queue}?api_key={api_riot}"
    )
    ENTRIES_LEAGUE_BY_TIER_DIVISION = "/lol/league/v4/entries/{queue}/{tier}/{division}?page={page}&api_key={api_riot}"

    # get match using puuid
    MATCH_IDS_BY_PUUID = "/lol/match/v5/matches/by-puuid/{puuid}/ids?type={type}&start={start}&count={count}&api_key={api_riot}"
