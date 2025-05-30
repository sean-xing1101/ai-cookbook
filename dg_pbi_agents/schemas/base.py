from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class BusinessCheckResult(BaseModel):
    is_business: bool
    confidence: float
    response: str

class DatasetInfo(BaseModel):
    dataset_id: str
    dataset_name: str
    dataset_description: str
    response: str




class ColumnInfo(BaseModel):
    """
       表示数据表中的一个列的元数据。
       每个列都有一个名称、可选的描述、唯一标识符和可选的枚举值列表。
    """
    c_name: str
    column_description: Optional[str] = None
    column_id: str
    c_enum: Optional[str] = None

class TableInfo(BaseModel):
    """
        表示一个数据表的元数据。
        每个表都有一个名称、唯一标识符、可选的描述和一个列的列表。
    """
    t_name: str
    table_id: str
    table_description: Optional[str] = None
    columns: List[ColumnInfo]

class DatasetMetadata(BaseModel):
    """
        表示一个数据集的元数据。
        每个数据集都有一个名称、唯一标识符和一个表的列表。
    """
    d_name: str
    dataset_id: str
    tables: List[TableInfo]

class QueryPlan(BaseModel):
    target_tables: List[str] = Field(default_factory=list, description="Target tables for the query plan")
    required_columns: List[str] = Field(default_factory=list, description="Required columns for the query plan")
    filters: Optional[Dict[str, str]] = Field(default_factory=dict, description="Optional filters for the query plan")
    join_conditions: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Optional join conditions for the query plan")

class DAXRequest(BaseModel):
    question: str
    query_plan: QueryPlan

class DAXResponse(BaseModel):
    expression: str
    explanation: str
    version: str = "1.0"

class ExecutionResult(BaseModel):
    success: bool
    data: Optional[List[Dict]] = None
    error: Optional[str] = None
    execution_time_ms: int

class ValidationResult(BaseModel):
    is_valid: bool
    need_retry: bool = False
    retry_steps: List[int] = []
    confidence: float
    feedback: str