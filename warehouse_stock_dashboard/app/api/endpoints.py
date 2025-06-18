from fastapi import APIRouter, HTTPException
from app.db.database import get_connection
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stock")
async def get_stock():
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        query = """
        SELECT TOP 5
            MaterialNumber = mard.MATNR,
            MaterialDescription = makt.MAKTX,
            Plant = mard.WERKS,
            PlantName = t001w.NAME1,
            StorageLocation = mard.LGORT,
            StorageLocationDescription = t001l.LGOBE,
            MaterialType = mara.MTART,
            MaterialGroup = mara.MATKL,
            IsBatchManaged = marc.XCHAR,
            BatchNumber = mchb.CHARG,
            UnrestrictedStock = ISNULL(mchb.CLABS, ISNULL(mard.LABST, 0))
        FROM prd.MARD AS mard
        LEFT JOIN prd.MARA AS mara ON mard.MATNR = mara.MATNR
        LEFT JOIN prd.MAKT AS makt ON mard.MATNR = makt.MATNR AND makt.SPRAS = 'EN'
        LEFT JOIN prd.MARC AS marc ON mard.MATNR = marc.MATNR AND mard.WERKS = marc.WERKS
        LEFT JOIN prd.T001W AS t001w ON mard.WERKS = t001w.WERKS
        LEFT JOIN prd.T001L AS t001l ON mard.WERKS = t001l.WERKS AND mard.LGORT = t001l.LGORT
        LEFT JOIN prd.MCHB AS mchb 
            ON mard.MATNR = mchb.MATNR 
            AND mard.WERKS = mchb.WERKS 
            AND mard.LGORT = mchb.LGORT
        WHERE ISNULL(mchb.CLABS, 0) > 0 
            OR (mchb.CHARG IS NULL AND ISNULL(mard.LABST, 0) > 0)
        """
        
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()