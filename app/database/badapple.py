"""
@author Jack Ringer
Date: 8/28/2024
Description:
Class for operations with badapple DBs (badapple_classic and badapple2).
"""

from typing import Dict, List

import psycopg2
import psycopg2.extras
from config import DB_NAME2HOST, DB_NAME2PASSWORD, DB_NAME2PORT, DB_NAME2USER
from flask import abort
from psycopg2 import sql


# queries used to read from Badapple databases
def _build_scaffold_by_smiles_query(scafsmi: str):
    # here we assume the given scafsmi is None if it was not a valid SMILES
    # and that the scafsmi was canonicalized (much faster to search scafsmi than use structural search!)
    if scafsmi is None:
        return abort(400, "Invalid SMILES provided")
    return sql.SQL("SELECT * from scaffold where scafsmi={scafsmi} LIMIT 1;").format(
        scafsmi=sql.Literal(scafsmi)
    )


def _build_scaffold_by_id_query(scafid: str):
    return sql.SQL("SELECT * from scaffold where id={scafid} LIMIT 1;").format(
        scafid=sql.Literal(scafid)
    )


def _build_scaffold_id_query(scafsmi: str):
    return sql.SQL("SELECT id FROM mols_scaf WHERE scafmol @= {scafsmi};").format(
        scafsmi=sql.Literal(scafsmi)
    )


def _build_associated_compounds_query(scafid: int):
    return sql.SQL(
        "SELECT * FROM compound WHERE cid IN (SELECT cid FROM scaf2cpd WHERE scafid={scafid});"
    ).format(scafid=sql.Literal(scafid))


def _build_associated_sids_query(cid_list: list[int]):
    formatted_cid_list = sql.SQL(", ").join(map(sql.Literal, cid_list))
    return sql.SQL("SELECT * FROM sub2cpd WHERE cid IN ({cid_list})").format(
        cid_list=formatted_cid_list
    )


def _build_associated_assay_ids_query(scafid: int):
    return sql.SQL(
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


def _build_assay_outcomes_query(sid: int):
    return sql.SQL("SELECT aid,outcome FROM activity WHERE sid={sid}").format(
        sid=sql.Literal(sid)
    )


# badapple2+ only
def _build_active_targets_query(scafid: int) -> sql.SQL:
    return sql.SQL(
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


def _build_associated_drugs_query(scafid: int) -> sql.SQL:
    return sql.SQL(
        "SELECT * FROM drug WHERE drug_id IN (SELECT drug_id FROM scaf2drug WHERE scafid={scafid});"
    ).format(scafid=sql.Literal(scafid))


# function to execute query using db cursor
def execute_query(query: sql.SQL, cursor) -> List[Dict]:
    """Execute a query and return results."""
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        raise error


# error handling
def _handle_data_exception(e):
    if isinstance(e, psycopg2.errors.DataException):
        return abort(400, "Invalid SMILES provided")
    raise e


class BadAppleSession:
    """
    Use this when you need to run multiple queries and want to reuse
    the same connection/cursor to avoid overhead.

    Usage:
        with BadAppleSession('badapple2') as session:
            results1 = session.search_scaffold_by_smiles(smiles1)
            results2 = session.get_associated_compounds(scafid)
            results3 = session.get_active_targets(scafid)
    """

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = psycopg2.connect(
            host=DB_NAME2HOST[self.db_name],
            database=self.db_name,
            user=DB_NAME2USER[self.db_name],
            password=DB_NAME2PASSWORD[self.db_name],
            port=DB_NAME2PORT[self.db_name],
        )
        self.connection.set_session(
            readonly=True
        )  # user in prod will also be read-only, but this is an additional safety measure
        self.cursor = self.connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        # NOTE: this API is read-only,
        # but if we added write methods we'd want to handle exceptions more robustly and rollback any changes
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def _execute_query_builder(self, query_builder, *args, error_handler=None):
        try:
            query = query_builder(*args)
            return execute_query(query, self.cursor)
        except Exception as e:
            if error_handler:
                return error_handler(e)
            raise

    def search_scaffold_by_smiles(self, scafsmi: str) -> List[Dict]:
        return self._execute_query_builder(_build_scaffold_by_smiles_query, scafsmi)

    def search_scaffold_by_id(self, scafid: str) -> List[Dict]:
        return self._execute_query_builder(_build_scaffold_by_id_query, scafid)

    def get_scaffold_id(self, scafsmi: str) -> List[Dict]:
        return self._execute_query_builder(
            _build_scaffold_id_query, scafsmi, error_handler=_handle_data_exception
        )

    def get_associated_compounds(self, scafid: int) -> List[Dict]:
        return self._execute_query_builder(_build_associated_compounds_query, scafid)

    def get_associated_sids(self, cid_list: List[int]) -> List[Dict]:
        return self._execute_query_builder(_build_associated_sids_query, cid_list)

    def get_associated_assay_ids(self, scafid: int) -> List[Dict]:
        return self._execute_query_builder(_build_associated_assay_ids_query, scafid)

    def get_assay_outcomes(self, sid: int) -> List[Dict]:
        return self._execute_query_builder(_build_assay_outcomes_query, sid)

    def get_active_targets(self, scafid: int) -> List[Dict]:
        return self._execute_query_builder(_build_active_targets_query, scafid)

    def get_associated_drugs(self, scafid: int) -> List[Dict]:
        return self._execute_query_builder(_build_associated_drugs_query, scafid)
