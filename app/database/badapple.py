"""
@author Jack Ringer
Date: 8/28/2024
Description:
Class for operations with badapple DBs (badapple_classic and badapple2).
"""

import psycopg2
import psycopg2.extras
from config import DB_NAME2HOST, DB_NAME2PASSWORD, DB_NAME2PORT, DB_NAME2USER
from flask import abort
from psycopg2 import sql


def connect(db_name: str):
    return psycopg2.connect(
        host=DB_NAME2HOST[db_name],
        database=db_name,
        user=DB_NAME2USER[db_name],
        password=DB_NAME2PASSWORD[db_name],
        port=DB_NAME2PORT[db_name],
    )


def select(query: sql.SQL, db_name: str):
    connection = connect(db_name)
    return execute_query(query, connection)


def execute_query(query: sql.SQL, connection):
    cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        raise error
    finally:
        cursor.close()
        connection.close()
    return result


def search_scaffold_by_smiles(scafsmi: str, db_name: str):
    # here we assume the given scafsmi is None if it was not a valid SMILES
    # and that the scafsmi was canonicalized (much faster to search scafsmi than use structural search!)
    if scafsmi is None:
        return abort(400, "Invalid SMILES provided")
    query = sql.SQL("SELECT * from scaffold where scafsmi={scafsmi} LIMIT 1").format(
        scafsmi=sql.Literal(scafsmi)
    )
    return select(query, db_name)


def search_scaffold_by_id(scafid: str, db_name: str):
    query = sql.SQL("SELECT * from scaffold where id={scafid} LIMIT 1").format(
        scafid=sql.Literal(scafid)
    )
    return select(query, db_name)


def get_scaffold_id(scafsmi: str, db_name: str):
    query = sql.SQL("SELECT id FROM mols_scaf WHERE scafmol @= {scafsmi};").format(
        scafsmi=sql.Literal(scafsmi)
    )
    result = None
    try:
        result = select(query, db_name)
    except psycopg2.errors.DataException:
        return abort(400, "Invalid SMILES provided")
    return result


def get_associated_compounds(scafid: int, db_name: str):
    query = sql.SQL(
        "select * from compound where cid IN (select cid from scaf2cpd where scafid={scafid})"
    ).format(scafid=sql.Literal(scafid))
    return select(query, db_name)


def get_associated_sids(cid_list: list[int], db_name: str):
    formatted_cid_list = sql.SQL(", ").join(map(sql.Literal, cid_list))
    query = sql.SQL("SELECT * FROM sub2cpd WHERE cid IN ({cid_list})").format(
        cid_list=formatted_cid_list
    )
    return select(query, db_name)


def get_associated_assay_ids(scafid: int, db_name: str):
    query = sql.SQL(
        """SELECT DISTINCT aid 
FROM activity 
WHERE sid IN (
SELECT sid 
FROM sub2cpd 
WHERE cid IN (
    SELECT cid 
    FROM scaf2cpd 
    WHERE scafid = {scafid}
)
) ORDER BY aid;"""
    ).format(scafid=sql.Literal(scafid))
    return select(query, db_name)


def get_assay_outcomes(sid: int, db_name: str):
    query = sql.SQL("SELECT aid,outcome FROM activity WHERE sid={sid}").format(
        sid=sql.Literal(sid)
    )
    return select(query, db_name)


# badapple2+ only
def get_active_targets(scafid: int, db_name: str = "badapple2"):
    query = sql.SQL(
        """
SELECT 
target.*, 
scaf2activeaid.aid 
FROM 
target
RIGHT JOIN  
aid2target 
ON target.target_id = aid2target.target_id
RIGHT JOIN  
scaf2activeaid 
ON aid2target.aid = scaf2activeaid.aid
WHERE 
scaf2activeaid.scafid = {scafid}
ORDER BY aid;
"""
    ).format(scafid=sql.Literal(scafid))
    return select(query, db_name)


def get_associated_drugs(scafid: int, db_name: str = "badapple2"):
    query = sql.SQL(
        "SELECT * FROM drug WHERE drug_id IN (SELECT drug_id FROM scaf2drug WHERE scafid={scafid});"
    ).format(scafid=sql.Literal(scafid))
    return select(query, db_name)
