from fastapi import APIRouter, Depends, HTTPException
from ..schemas import QueryRequest, QueryResponse
from ..auth import get_project_by_api_key
from ..database import SQLServerConnection
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def execute_sql_query(
    query_req: QueryRequest,
    context: dict = Depends(get_project_by_api_key)
):
    database = context["database"]
    
    try:
        conn = SQLServerConnection.get_connection(database=database)
        data = SQLServerConnection.execute_query(conn, query_req.sql, query_req.params, limit=query_req.limit)
        
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        print(f"SQL Server Query Error: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing SQL query: {str(e)}"
        )
