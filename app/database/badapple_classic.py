"""
@author Jack Ringer
Date: 8/28/2024
Description:
Class for operations with badapple_classic.
"""

import psycopg2
import psycopg2.extras
from flask import abort, current_app
from psycopg2 import sql
from utils.request_processing import int_check


class BadappleClassicDB:
    @staticmethod
    def connect():
        return psycopg2.connect(
            host=current_app.config.get("DB_HOST"),
            database=current_app.config.get("DB_NAME"),
            user=current_app.config.get("DB_USER"),
            password=current_app.config.get("DB_PASSWORD"),
            port=current_app.config.get("DB_PORT"),
        )

    @staticmethod
    def select(query: sql.SQL):
        connection = BadappleClassicDB.connect()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query)
            res = cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            raise error
        finally:
            cursor.close()
            connection.close()
        return res

    def index_compound(cid: int):
        cid = int_check(cid, "CID")
        query = sql.SQL("SELECT isosmi from compound where cid={cid} LIMIT 1").format(
            cid=sql.Literal(cid)
        )
        result = BadappleClassicDB.select(query)
        return result

    def search_scaffold(scafsmi: str):
        if scafsmi is None:
            return abort(400, "Invalid SMILES provided")
        query = sql.SQL(
            "SELECT * from scaffold where scafsmi={scafsmi} LIMIT 1"
        ).format(scafsmi=sql.Literal(scafsmi))
        result = BadappleClassicDB.select(query)
        return result

    def get_associated_compounds(scafid: int):
        scafid = int_check(scafid, "scafid")
        query = sql.SQL(
            "select * from compound where cid IN (select cid from scaf2cpd where scafid={scafid})"
        ).format(scafid=sql.Literal(scafid))
        result = BadappleClassicDB.select(query)
        return result

    def get_associated_sids(cid_list: list[int]):
        formatted_cid_list = sql.SQL(", ").join(map(sql.Literal, cid_list))
        query = sql.SQL("SELECT * FROM sub2cpd WHERE cid IN ({cid_list})").format(
            cid_list=formatted_cid_list
        )
        result = BadappleClassicDB.select(query)
        return result

    def get_associated_assay_ids(scafid: int):
        scafid = int_check(scafid, "scafid")
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
        result = BadappleClassicDB.select(query)
        return result

    def get_assay_outcomes(sid: int):
        sid = int_check(sid, "SID")
        query = sql.SQL("SELECT aid,outcome FROM activity WHERE sid={sid}").format(
            sid=sql.Literal(sid)
        )
        result = BadappleClassicDB.select(query)
        return result