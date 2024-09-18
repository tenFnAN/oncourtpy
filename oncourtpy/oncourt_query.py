
###
# QUERY DEFINITION
###
# query = open('query/query_schedule.sql', 'r').read()
query_dict = {'schedule_today' : """SELECT podzap.DATE_GAME as DATE_G, Hour(DATE_GAME) as DATE_H, podzap.DRAW, podzap.P1, podzap.idP1 as id_P1, podzap.P2, podzap.idP2 as id_P2, podzap.Country_P1, podzap.Country_P2, podzap.NAME_R, podzap.TIER_T, podzap.NAME_T, podzap.PRIZE_T,
podzap.NAME_C, podzap.RANK_T, podzap.LATITUDE_T, podzap.LONGITUDE_T, podzap.COUNTRY_T, podzap.PLAY_LEFT_P1, podzap.PLAY_LEFT_P2,
podzap.DATE_Birth_P1, podzap.DATE_Birth_P2 ,seed_type.SEEDING AS SEED_P1, seed_type_1.SEEDING AS SEED_P2,
odds_type.K1 as ODDS_P1, odds_type.K2 as ODDS_P2, odds_type.ID_B_O as ODDS_B, podzap.ITF_ID
FROM odds_type RIGHT JOIN (seed_type AS seed_type_1 RIGHT JOIN (seed_type RIGHT JOIN
                                                                (SELECT
                                                                  players_type.NAME_P AS P1,
                                                                  players_type.ID_P AS idP1,
                                                                  players_type_1.NAME_P AS P2,
                                                                  players_type_1.ID_P AS idP2,
                                                                  players_type.COUNTRY_P as Country_P1,
                                                                  players_type_1.COUNTRY_P as Country_P2,
                                                                  players_type.DATE_P   AS DATE_Birth_P1,
                                                                  players_type_1.DATE_P AS DATE_Birth_P2,
                                                                  players_type_1.ITF_ID ,
                                                                  rounds.NAME_R,rounds.ID_R,
                                                                  today_type.DATE_GAME,
                                                                  today_type.DRAW,
                                                                  tours_type.NAME_T,
                                                                  tours_type.TIER_T,
                                                                  tours_type.PRIZE_T,
                                                                  courts.NAME_C,
                                                                  tours_type.RANK_T+1 AS RANK_T,
                                                                  tours_type.LATITUDE_T,
                                                                  tours_type.LONGITUDE_T,
                                                                  tours_type.COUNTRY_T,
                                                                  tours_type.ID_T,
                                                                  categories_type.CAT1 as PLAY_LEFT_P1,
                                                                  categories_type_1.CAT1 as PLAY_LEFT_P2
                                                                  FROM categories_type AS categories_type_1 INNER JOIN (categories_type INNER JOIN ((((players_type AS players_type_1 INNER JOIN (players_type INNER JOIN today_type ON players_type.ID_P = today_type.ID1) ON players_type_1.ID_P = today_type.ID2)
                                                                                                                                                      INNER JOIN rounds ON today_type.ROUND = rounds.ID_R) INNER JOIN tours_type ON today_type.TOUR = tours_type.ID_T)
                                                                                                                                                    INNER JOIN courts ON tours_type.ID_C_T = courts.ID_C) ON categories_type.ID_P = players_type.ID_P) ON categories_type_1.ID_P = players_type_1.ID_P
                                                                  WHERE (((players_type.NAME_P) Not Like '%Unknown Player%') AND ((players_type_1.NAME_P) Not Like '%Unknown Player%') AND (today_type.RESULT='')))
                                                                AS podzap ON (seed_type.ID_P_S = podzap.idP1) AND (seed_type.ID_T_S = podzap.ID_T)) ON (seed_type_1.ID_T_S = podzap.ID_T) AND
                           (seed_type_1.ID_P_S = podzap.idP2)) ON (odds_type.ID_R_O = podzap.ID_R) AND
(odds_type.ID_T_O = podzap.ID_T) AND (odds_type.ID2_O = podzap.idP2) AND (odds_type.ID1_O = podzap.idP1)
WHERE (( (odds_type.ID_B_O)=1 or (odds_type.ID_B_O)=2 Or (odds_type.ID_B_O) Is Null));
""",

'schedule_historical' : """SELECT
P1, ID1 as id_P1, P2, ID2 as id_P2, idPlayer, idPlayer2, Country_P1,  Country_P2, DATE_G, RESULT_G, score,
NAME_R,TIER_T, NAME_T, PRIZE_T, NAME_C, RANK_T, LATITUDE_T, LONGITUDE_T,
COUNTRY_T, PLAY_LEFT_P1,PLAY_LEFT_P2,
DATE_Birth_P1, DATE_Birth_P2,
seed_type.SEEDING AS SEED_P1, seed_type_1.SEEDING AS SEED_P2,
odds_type.K1 as ODDS_P1, odds_type.K2 as ODDS_P2, odds_type.ID_B_O as ODDS_B

FROM odds_type RIGHT JOIN (seed_type AS seed_type_1 RIGHT JOIN (seed_type RIGHT JOIN (SELECT podzap1.*,
                                                                                      s.ID1, s.ID2 from ( SELECT
                                                                                                          pl1.ID_P as idPlayer,
                                                                                                          pl2.ID_P as idPlayer2,
                                                                                                          pl1.NAME_P AS P1,
                                                                                                          pl2.NAME_P AS P2,
                                                                                                          g.RESULT_G,
                                                                                                          g.DATE_G,
                                                                                                          'win' AS score,
                                                                                                          pl1.COUNTRY_P as Country_P1,
                                                                                                          pl2.COUNTRY_P as Country_P2,
                                                                                                          r.NAME_R,
                                                                                                          c.NAME_C,
                                                                                                          t.NAME_T,
                                                                                                          t.TIER_T,
                                                                                                          [t].[ID_T],
                                                                                                          [r].[ID_R] ,
                                                                                                          t.RANK_T+1 as RANK_T,
                                                                                                          t.PRIZE_T,
                                                                                                          t.COUNTRY_T,
                                                                                                          t.LATITUDE_T, t.LONGITUDE_T,
                                                                                                          cat.CAT1 as PLAY_LEFT_P2,
                                                                                                          cat_P1.CAT1 as PLAY_LEFT_P1,
                                                                                                          pl1.DATE_P   AS DATE_Birth_P1,
                                                                                                          pl2.DATE_P AS DATE_Birth_P2
                                                                                                          
                                                                                                          FROM
                                                                                                          players_type AS pl2, rounds AS r, tours_type AS t, courts AS c, players_type AS pl1, games_type AS g, categories_type as cat, categories_type as cat_P1
                                                                                                          WHERE ( ((g.ID2_G)=[pl2].[ID_P]) AND ((g.ID_R_G)=[r].[ID_R]) AND (cat.ID_P = pl2.ID_P) AND (cat_P1.ID_P = pl1.ID_P) AND
                                                                                                                  ((t.ID_C_T)=[c].[ID_C]) AND ((pl1.ID_P)=[g].[ID1_G])) and t.ID_T = g.ID_T_G ) as podzap1  LEFT JOIN (
                                                                                                                    select * from stat_type ) as s ON podzap1.idPlayer = s.ID1 AND podzap1.idPlayer2 = s.ID2  and podzap1.ID_T = s.ID_T and podzap1.ID_R = s.ID_R
                                                                                      where podzap1.DATE_G is not null and podzap1.DATE_G >= #{date_min}# and podzap1.DATE_G <= #{date_max}#
)  AS podzap2 ON (seed_type.ID_T_S = podzap2.ID_T) AND (seed_type.ID_P_S = podzap2.ID1)) ON (seed_type_1.ID_P_S = podzap2.ID2) AND (seed_type_1.ID_T_S = podzap2.ID_T)) ON
(odds_type.ID_T_O = podzap2.ID_T) AND (odds_type.ID2_O = podzap2.ID2) AND (odds_type.ID1_O = podzap2.ID1) AND (odds_type.ID_R_O = podzap2.ID_R)
WHERE (( (odds_type.ID_B_O)=1 or (odds_type.ID_B_O)=2 Or (odds_type.ID_B_O) Is Null))
UNION

SELECT
P1, ID1 as id_P1, P2, ID2 as id_P2, idPlayer, idPlayer2, Country_P1,  Country_P2, DATE_G, RESULT_G, score,
NAME_R,TIER_T, NAME_T, PRIZE_T, NAME_C, RANK_T, LATITUDE_T, LONGITUDE_T,
COUNTRY_T, PLAY_LEFT_P1,PLAY_LEFT_P2,
DATE_Birth_P1, DATE_Birth_P2,
seed_type_1.SEEDING AS SEED_P1, seed_type.SEEDING AS SEED_P2,
odds_type.K1 as ODDS_P1, odds_type.K2 as ODDS_P2, odds_type.ID_B_O as ODDS_B

FROM odds_type RIGHT JOIN (seed_type AS seed_type_1 RIGHT JOIN (seed_type RIGHT JOIN (SELECT podzap1.*,
                                                                                      s.ID2 as ID1,         s.ID1 as ID2 from ( SELECT
                                                                                                                                pl2.ID_P as idPlayer,
                                                                                                                                pl1.ID_P as idPlayer2,
                                                                                                                                pl2.NAME_P AS P1,
                                                                                                                                pl1.NAME_P AS P2,
                                                                                                                                g.RESULT_G,
                                                                                                                                g.DATE_G,
                                                                                                                                'lost' AS score,
                                                                                                                                pl2.COUNTRY_P as Country_P1,
                                                                                                                                pl1.COUNTRY_P as Country_P2,
                                                                                                                                r.NAME_R,
                                                                                                                                c.NAME_C,
                                                                                                                                t.NAME_T,
                                                                                                                                t.TIER_T,
                                                                                                                                [t].[ID_T],
                                                                                                                                [r].[ID_R] ,
                                                                                                                                t.RANK_T+1 as RANK_T,
                                                                                                                                t.PRIZE_T,
                                                                                                                                t.COUNTRY_T,
                                                                                                                                t.LATITUDE_T, t.LONGITUDE_T,
                                                                                                                                cat.CAT1 as PLAY_LEFT_P2,
                                                                                                                                cat_P1.CAT1 as PLAY_LEFT_P1,
                                                                                                                                pl2.DATE_P AS DATE_Birth_P1,
                                                                                                                                pl1.DATE_P   AS DATE_Birth_P2
                                                                                                                                
                                                                                                                                FROM
                                                                                                                                players_type AS pl2, rounds AS r, tours_type AS t, courts AS c, players_type AS pl1, games_type AS g, categories_type as cat, categories_type as cat_P1
                                                                                                                                WHERE ( ((g.ID2_G)=[pl2].[ID_P]) AND ((g.ID_R_G)=[r].[ID_R]) AND (cat.ID_P = pl1.ID_P) AND (cat_P1.ID_P = pl2.ID_P) AND
                                                                                                                                        ((t.ID_C_T)=[c].[ID_C]) AND ((pl1.ID_P)=[g].[ID1_G])) and t.ID_T = g.ID_T_G ) as podzap1  LEFT JOIN (
                                                                                                                                          select * from stat_type ) as s ON podzap1.idPlayer = s.ID2 AND podzap1.idPlayer2 = s.ID1 and podzap1.ID_T = s.ID_T and podzap1.ID_R = s.ID_R
                                                                                      where podzap1.DATE_G is not null and podzap1.DATE_G >= #{date_min}# and podzap1.DATE_G <= #{date_max}#
)  AS podzap2 ON (seed_type.ID_T_S = podzap2.ID_T) AND (seed_type.ID_P_S = podzap2.ID2)) ON (seed_type_1.ID_P_S = podzap2.ID1) AND (seed_type_1.ID_T_S = podzap2.ID_T)) ON
(odds_type.ID_T_O = podzap2.ID_T) AND (odds_type.ID1_O = podzap2.ID1) AND (odds_type.ID2_O = podzap2.ID2) AND (odds_type.ID_R_O = podzap2.ID_R)
WHERE (( (odds_type.ID_B_O)=1 or (odds_type.ID_B_O)=2 Or (odds_type.ID_B_O) Is Null));""",

'playerdata' : """SELECT * from (
  SELECT podzap1.*,
  s.MT,
  s.ID1,        s.ID2,
  s.ACES_1,     s.ACES_2,
  s.DF_1,       s.DF_2,
  s.TPW_1,      s.TPW_2,
  s.TPW_1     + s.TPW_2 as PW,
  
  s.FS_1,       s.FS_2,
  s.FSOF_1,     s.FSOF_2,
  s.W1S_1,      s.W1S_2,
  s.W1SOF_1,    s.W1SOF_2,
  s.W2S_1,      s.W2S_2,
  s.W2SOF_1,    s.W2SOF_2,
  s.RPW_1,      s.RPW_2,
  s.RPWOF_1,    s.RPWOF_2,
  s.BP_1,       s.BP_2,
  s.BPOF_1,     s.BPOF_2 from ( SELECT
                                pl1.ID_P as idPlayer,
                                pl2.ID_P as idPlayer2,
                                pl1.NAME_P AS P1,
                                pl2.NAME_P AS P2,
                                g.RESULT_G,
                                g.DATE_G,
                                'win' AS score,
                                r.NAME_R,
                                c.NAME_C,
                                t.NAME_T,
                                t.TIER_T,
                                [t].[ID_T],
                                [r].[ID_R] ,
                                t.RANK_T+1 as RANK_T,
                                t.PRIZE_T,
                                t.COUNTRY_T,
                                t.LATITUDE_T, t.LONGITUDE_T,
                                cat.CAT1 as PLAY_LEFT_P2,
                                pl1.DATE_P AS DATE_Birth_P1,
                                pl2.DATE_P AS DATE_Birth_P2,
                                pl1.COUNTRY_P AS Country_P1,
                                pl2.COUNTRY_P AS Country_P2
                                
                                FROM
                                players_type AS pl2, rounds AS r, tours_type AS t, courts AS c, players_type AS pl1, games_type AS g, categories_type as cat 
                                WHERE ((pl1.ID_P) IN ({players_id}) AND ((g.ID2_G)=[pl2].[ID_P]) AND ((g.ID_R_G)=[r].[ID_R]) AND (cat.ID_P = pl2.ID_P) AND
                                       ((t.ID_C_T)=[c].[ID_C]) AND ((pl1.ID_P)=[g].[ID1_G])) and t.ID_T = g.ID_T_G and g.DATE_G >= #{date_min}# and g.DATE_G <= #{date_max}# ) as podzap1  LEFT JOIN (
                                  select * from stat_type where ID1 IN ({players_id}) ) as s ON podzap1.idPlayer = s.ID1 AND podzap1.idPlayer2 = s.ID2  and podzap1.ID_T = s.ID_T and podzap1.ID_R = s.ID_R
  where podzap1.DATE_G is not null
  UNION
  SELECT podzap1.*,
  s.MT,
  s.ID2 as ID1,         s.ID1 as ID2,
  s.ACES_2 as ACES_1,   s.ACES_1 as ACES_2,
  s.DF_2 as DF_1,       s.DF_1 as DF_2,
  s.TPW_2 as TPW_1,     s.TPW_1 as TPW_2,
  s.TPW_2             + s.TPW_1  as PW,
  s.FS_2 as FS_1,       s.FS_1 as FS_2,
  
  s.FSOF_2 as FSOF_1,   s.FSOF_1 as FSOF_2,
  s.W1S_2  as W1S_1,    s.W1S_1 as W1S_2,
  s.W1SOF_2 as W1SOF_1, s.W1SOF_1 as W1SOF_2,
  s.W2S_2 as W2S_1,     s.W2S_1 as W2S_2,
  s.W2SOF_2 as W2SOF_1, s.W2SOF_1 as W2SOF_2,
  s.RPW_2 as RPW_1,     s.RPW_1 as RPW_2,
  s.RPWOF_2 as RPWOF_1 ,s.RPWOF_1 as RPWOF_2,
  s.BP_2    as BP_1,    s.BP_1  as BP_2,
  s.BPOF_2  as BPOF_1,  s.BPOF_1 as BPOF_2 from (SELECT
                                                 pl2.ID_P as idPlayer,
                                                 pl1.ID_P as idPlayer2,
                                                 pl2.NAME_P AS P1,
                                                 pl1.NAME_P AS P2,
                                                 g.RESULT_G,
                                                 g.DATE_G,
                                                 'lost' AS score,
                                                 r.NAME_R,
                                                 c.NAME_C,
                                                 t.NAME_T,
                                                 t.TIER_T,
                                                 [t].[ID_T],
                                                 [r].[ID_R] ,
                                                 t.RANK_T+1 as RANK_T,
                                                 t.PRIZE_T,
                                                 t.COUNTRY_T,
                                                 t.LATITUDE_T, t.LONGITUDE_T,
                                                 cat.CAT1 as PLAY_LEFT_P2,
                                                 pl2.DATE_P AS DATE_Birth_P1,
                                                 pl1.DATE_P AS DATE_Birth_P2,
                                                 pl2.COUNTRY_P AS Country_P1,
                                                 pl1.COUNTRY_P AS Country_P2
                                                 
                                                 FROM
                                                 players_type AS pl2, rounds AS r, tours_type AS t, courts AS c, players_type AS pl1, games_type AS g, categories_type as cat
                                                 WHERE (((pl2.ID_P) IN ({players_id})) AND (g.ID2_G)=[pl2].[ID_P]
                                                        AND ((g.ID_R_G)=[r].[ID_R])  AND (cat.ID_P = pl1.ID_P) AND ((t.ID_C_T)=[c].[ID_C]) AND ((pl1.ID_P)=[g].[ID1_G])) and t.ID_T = g.ID_T_G and g.DATE_G >= #{date_min}# and g.DATE_G <= #{date_max}# ) as podzap1  LEFT JOIN (
                                                   select * from stat_type where ID2 IN ({players_id}) ) as s ON podzap1.idPlayer = s.ID2 AND podzap1.idPlayer2 = s.ID1  and podzap1.ID_T = s.ID_T and podzap1.ID_R = s.ID_R
  where podzap1.DATE_G is not null
) ORDER BY DATE_G DESC;""",

'matches' : """SELECT * from (
  
  SELECT podzap1.*,
  s.MT,
  s.ID1, s.ID2,
  s.ACES_1,     s.ACES_2,
  s.DF_1,       s.DF_2,
  s.TPW_1,      s.TPW_2,
  s.TPW_1     + s.TPW_2 as PW,
  s.FS_1,       s.FS_2,
  s.FSOF_1,     s.FSOF_2,
  s.W1S_1,      s.W1S_2,
  s.W1SOF_1,    s.W1SOF_2,
  s.W2S_1,      s.W2S_2,
  s.W2SOF_1,    s.W2SOF_2,
  s.RPW_1,      s.RPW_2,
  s.RPWOF_1,    s.RPWOF_2,
  s.BP_1,       s.BP_2,
  s.BPOF_1,     s.BPOF_2  from ( SELECT
                                 pl1.ID_P as idPlayer,
                                 pl2.ID_P as idPlayer2,
                                 pl1.NAME_P AS P1,
                                 pl2.NAME_P AS P2,
                                 g.RESULT_G,
                                 g.DATE_G,
                                 'win' AS score,
                                 r.NAME_R,
                                 c.NAME_C,
                                 t.NAME_T,
                                 t.TIER_T,
                                 [t].[ID_T],
                                 [r].[ID_R] ,
                                 t.RANK_T+1 as RANK_T,
                                 t.PRIZE_T,
                                 t.COUNTRY_T,
                                 t.LATITUDE_T, t.LONGITUDE_T
                                 
                                 FROM
                                 players_type AS pl2, rounds AS r, tours_type AS t, courts AS c, players_type AS pl1, games_type AS g, categories_type as cat
                                 WHERE ( ((g.ID2_G)=[pl2].[ID_P]) AND ((g.ID_R_G)=[r].[ID_R]) AND (cat.ID_P = pl2.ID_P) AND
                                         ((t.ID_C_T)=[c].[ID_C]) AND ((pl1.ID_P)=[g].[ID1_G])) and t.ID_T = g.ID_T_G and g.DATE_G >= #{date_min}# and g.DATE_G <= #{date_max}# ) as podzap1  LEFT JOIN (
                                   select * from stat_type ) as s ON podzap1.idPlayer = s.ID1 AND podzap1.idPlayer2 = s.ID2  and podzap1.ID_T = s.ID_T and podzap1.ID_R = s.ID_R
  where podzap1.DATE_G is not null
  UNION
  SELECT podzap1.*,
  s.MT,
  s.ID2 as ID1,         s.ID1 as ID2,
  s.ACES_2 as ACES_1,   s.ACES_1 as ACES_2,
  s.DF_2 as DF_1,       s.DF_1 as DF_2,
  s.TPW_2 as TPW_1,     s.TPW_1 as TPW_2,
  s.TPW_2             + s.TPW_1  as PW,
  s.FS_2 as FS_1,       s.FS_1 as FS_2,
  
  s.FSOF_2 as FSOF_1,   s.FSOF_1 as FSOF_2,
  s.W1S_2  as W1S_1,    s.W1S_1 as W1S_2,
  s.W1SOF_2 as W1SOF_1, s.W1SOF_1 as W1SOF_2,
  s.W2S_2 as W2S_1,     s.W2S_1 as W2S_2,
  s.W2SOF_2 as W2SOF_1, s.W2SOF_1 as W2SOF_2,
  s.RPW_2 as RPW_1,     s.RPW_1 as RPW_2,
  s.RPWOF_2 as RPWOF_1 ,s.RPWOF_1 as RPWOF_2,
  s.BP_2  as BP_1      ,s.BP_1    as BP_2,
  s.BPOF_2 as BPOF_1   ,s.BPOF_1 as BPOF_2 from (SELECT
                                                 pl2.ID_P as idPlayer,
                                                 pl1.ID_P as idPlayer2,
                                                 pl2.NAME_P AS P1,
                                                 pl1.NAME_P AS P2,
                                                 g.RESULT_G,
                                                 g.DATE_G,
                                                 'lost' AS score,
                                                 r.NAME_R,
                                                 c.NAME_C,
                                                 t.NAME_T,
                                                 t.TIER_T,
                                                 [t].[ID_T],
                                                 [r].[ID_R] ,
                                                 t.RANK_T+1 as RANK_T,
                                                 t.PRIZE_T,
                                                 t.COUNTRY_T,
                                                 t.LATITUDE_T, t.LONGITUDE_T
                                                 
                                                 FROM
                                                 players_type AS pl2, rounds AS r, tours_type AS t, courts AS c, players_type AS pl1, games_type AS g, categories_type as cat
                                                 WHERE ( (g.ID2_G)=[pl2].[ID_P] AND ((g.ID_R_G)=[r].[ID_R])  AND (cat.ID_P = pl1.ID_P) AND ((t.ID_C_T)=[c].[ID_C]) AND ((pl1.ID_P)=[g].[ID1_G])) and t.ID_T = g.ID_T_G and g.DATE_G >= #{date_min}# and g.DATE_G <= #{date_max}# ) as podzap1  LEFT JOIN (
                                                   select * from stat_type ) as s ON podzap1.idPlayer = s.ID2 AND podzap1.idPlayer2 = s.ID1  and podzap1.ID_T = s.ID_T and podzap1.ID_R = s.ID_R
  where podzap1.DATE_G is not null
) ORDER BY DATE_G DESC""",

'playerranking' : """SELECT distinct *
  FROM ratings_type INNER JOIN players_type ON ratings_type.ID_P_R = players_type.ID_P
  WHERE (((ratings_type.DATE_R)>Now()-{offset}))
  ORDER BY DATE_R DESC, POS_R ASC"""}
