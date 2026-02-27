from fastapi import APIRouter, Depends, HTTPException, Request
from ..schemas import QueryRequest, QueryResponse
from ..auth import get_project_by_api_key
from ..database import SQLServerConnection
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def execute_sql_query(
    request: Request,
    query_req: QueryRequest,
    context: dict = Depends(get_project_by_api_key)
):
    database = context["database"]
    
    # Store query body in request state for logging
    request.state.query_body = query_req.sql

    conn = None
    try:
        conn = SQLServerConnection.get_connection(database=database)
        
        # 1. Get Total Count
        # Wrap the original query to count total records
        # Using a subquery approach is generally safer for complex queries
        count_sql = f"SELECT COUNT(*) as total FROM ({query_req.sql}) as _count_wrapper"
        
        # We don't close connection yet as we need it for the data query
        count_result = SQLServerConnection.execute_query(
            conn, 
            count_sql, 
            query_req.params, 
            close_conn=False
        )
        
        total_records = count_result[0]['total'] if count_result else 0
        
        # 2. Pagination Logic
        limit = query_req.limit if query_req.limit else 50
        page = query_req.page if query_req.page and query_req.page > 0 else 1
        
        # If total records > limit (or forced pagination via page > 1), use pagination query
        if total_records > limit or page > 1:
            offset = (page - 1) * limit
            
            # Use ROW_NUMBER() for pagination (SQL Server 2005+)
            # ORDER BY (SELECT NULL) works even if original query has no ORDER BY
            paginated_sql = f"""
            SELECT * FROM (
                SELECT *, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) as _rn 
                FROM ({query_req.sql}) as _subquery
            ) as _paginated
            WHERE _rn > {offset} AND _rn <= {offset + limit}
            """
            
            data = SQLServerConnection.execute_query(
                conn, 
                paginated_sql, 
                query_req.params, 
                close_conn=True
            )
            
            # Remove the _rn column from results
            for row in data:
                if '_rn' in row:
                    del row['_rn']
        else:
            # If total <= limit and page is 1 (or 0/None), just run the original query
            # This is safer for simple queries and avoids overhead
            # We pass limit just in case, though logically we know count <= limit
            data = SQLServerConnection.execute_query(
                conn, 
                query_req.sql, 
                query_req.params, 
                limit=limit, 
                close_conn=True
            )

        # Calculate pagination metadata
        total_pages = (total_records + limit - 1) // limit if limit > 0 else 1

        return {
            "success": True,
            "data": data,
            "count": len(data),
            "total": total_records,
            "page": page,
            "page_size": limit,
            "total_pages": total_pages
        }
    except Exception as e:
        print(f"SQL Server Query Error: {str(e)}")
        if conn:
            try:
                conn.close()
            except:
                pass
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing SQL query: {str(e)}"
        )
