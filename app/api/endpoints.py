from fastapi import APIRouter, HTTPException, Query
from app.db.database import get_connection
import logging
import traceback

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stock")
async def get_stock(plant_name: str = Query(None, description="Plant Name")):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        SELECT DISTINCT
            mard.MATNR AS MaterialNumber,
            makt.MAKTX AS MaterialDescription,  -- Using MAKTX directly
            mara.MTART AS MaterialType,
            mara.MATKL AS MaterialGroup,
            mard.WERKS AS Plant,
            t001w.NAME1 AS PlantName,
            mard.LGORT AS StorageLocation,
            t001l.LGOBE AS StorageLocationDescription,
            marc.XCHAR AS IsBatchManaged,
            mchb.CHARG AS BatchNumber,
            ISNULL(mchb.CLABS, ISNULL(mard.LABST, 0)) AS UnrestrictedStock,
            ISNULL(mard.UMLME, 0) AS StockInTransfer,
            ISNULL(mard.SPEME, 0) AS BlockedStock,
            ISNULL(mbew.VERPR, 0) AS StandardPrice
        FROM prd.MARD AS mard
        INNER JOIN prd.MARA AS mara 
            ON mard.MATNR = mara.MATNR
        LEFT JOIN prd.MAKT AS makt 
            ON mard.MATNR = makt.MATNR 
            AND makt.SPRAS = 'E'  
        LEFT JOIN prd.MARC AS marc 
            ON mard.MATNR = marc.MATNR 
            AND mard.WERKS = marc.WERKS
        LEFT JOIN prd.T001W AS t001w 
            ON mard.WERKS = t001w.WERKS
        LEFT JOIN prd.T001L AS t001l 
            ON mard.WERKS = t001l.WERKS 
            AND mard.LGORT = t001l.LGORT
        LEFT JOIN prd.MBEW AS mbew 
            ON mard.MATNR = mbew.MATNR 
            AND mard.WERKS = mbew.BWKEY
        LEFT JOIN prd.MCHB AS mchb 
            ON mard.MATNR = mchb.MATNR 
            AND mard.WERKS = mchb.WERKS 
            AND mard.LGORT = mchb.LGORT
        WHERE (ISNULL(mchb.CLABS, 0) > 0
            OR (mchb.CHARG IS NULL AND ISNULL(mard.LABST, 0) > 0))
        """
        params = []
        if plant_name:
            query += " AND t001w.NAME1 = ?"
            params.append(plant_name)

        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        result = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            # Remove leading zeros from MaterialNumber
            if "MaterialNumber" in row_dict and row_dict["MaterialNumber"]:
                row_dict["MaterialNumber"] = row_dict["MaterialNumber"].lstrip("0")
            # Add StockValue column
            try:
                row_dict["StockValue"] = float(row_dict["UnrestrictedStock"] or 0) * float(row_dict["StandardPrice"] or 0)
            except Exception:
                row_dict["StockValue"] = 0
            result.append(row_dict)
        return result

    except Exception as e:
        error_details = f"{str(e)}\n{traceback.format_exc()}"
        logger.error(f"Error: {error_details}")
        raise HTTPException(status_code=500, detail=error_details)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@router.get("/stock/filters")
async def get_filters():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT t001w.NAME1 FROM prd.T001W t001w WHERE t001w.NAME1 IS NOT NULL ORDER BY t001w.NAME1")
        plants = [row[0] for row in cursor.fetchall()]
        return {
            "plants": plants,
            "material_types": [],
            "material_groups": [],
            "storage_locations": []
        }
    except Exception as e:
        error_details = f"{str(e)}\n{traceback.format_exc()}"
        logger.error(f"Error in filters: {error_details}")
        raise HTTPException(status_code=500, detail=error_details)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()