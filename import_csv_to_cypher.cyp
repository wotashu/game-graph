CREATE CONSTRAINT ON (u:User) ASSERT u.username IS UNIQUE;
CREATE CONSTRAINT ON (g:Game) ASSERT g.title IS UNIQUE;



// LOAD CSV WITH HEADERS FROM "file:s:/vizmo.csv" AS csvLine
LOAD CSV WITH HEADERS FROM "https://dl.dropboxusercontent.com/u/1252814/vizmo.csv" AS csvLine
MERGE (genre:Genre { title: csvLine.genre })
MERGE (game:Game { title: csvLine.title})
MERGE (year:Year { year: csvLine.year})
MERGE (platform:Platform { title: csvLine.platform})
CREATE (edition:Edition { id: toInt(csvLine.titleID), title: csvLine.title, year:toInt(csvLine.year)})
CREATE (game)-[:HAS_EDITION]->(edition)
CREATE (game)-[:HAS_GENRE]->(genre)
CREATE (edition)-[:HAS_PLATFORM]->(platform)
CREATE (edition)-[:RELEASED]->(year)

// code to remove duplicate edges
// http://stackoverflow.com/questions/18724939/neo4j-cypher-merge-duplicate-relationships
MATCH A-[r:HAS_GENRE]->B
WITH A, COLLECT(r) as oldRels, B, SUM(r.weight) as W
FOREACH(r IN oldRels | DELETE r)
WITH A, W, B
CREATE A-[O:HAS_GENRE {weight:W}]->B;
