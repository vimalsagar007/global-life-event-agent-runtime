from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AuthorityLevel(str, Enum):
    OFFICIAL_GOVERNMENT = "OFFICIAL_GOVERNMENT"
    OFFICIAL_ORGANIZATION = "OFFICIAL_ORGANIZATION"
    REGULATORY = "REGULATORY"
    INSTITUTIONAL = "INSTITUTIONAL"
    TRUSTED_SECONDARY = "TRUSTED_SECONDARY"
    GENERAL = "GENERAL"
    UNKNOWN = "UNKNOWN"


class ToolCategory(str, Enum):
    READ_ONLY = "READ_ONLY"
    ACTION = "ACTION"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class TaskPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Jurisdiction(BaseModel):
    country: str = Field(..., description="Country name or ISO code")
    region: Optional[str] = Field(None, description="State, Province, Territory, or Region")
    city: Optional[str] = Field(None, description="City or Municipality")
    postal_code: Optional[str] = Field(None, description="Postal/ZIP/PIN code")
    timezone: str = "UTC"
    currency: str = "USD"
    language: str = "en"
    locale: str = "en-US"
    measurement_system: str = "metric"

    def to_full_string(self) -> str:
        parts = [self.city, self.region, self.country]
        return ", ".join([p for p in parts if p])


class AuthoritySource(BaseModel):
    source_id: str
    source_url: str
    title: str
    source_type: str = "GOVERNMENT_PORTAL"
    authority_level: AuthorityLevel = AuthorityLevel.OFFICIAL_GOVERNMENT
    country: str
    jurisdiction: str
    effective_date: str
    expiry_date: Optional[str] = None
    last_verified: str
    language: str = "en"
    summary: str
    raw_content: Optional[str] = None


class Task(BaseModel):
    task_id: str
    title: str
    description: str
    category: str
    jurisdiction: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    deadline: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    sources: List[AuthoritySource] = Field(default_factory=list)
    agent: str
    requires_approval: bool = False
    approval_status: Optional[str] = None  # APPROVED, REJECTED, PENDING
    action_payload: Optional[Dict[str, Any]] = None


class LifeEvent(BaseModel):
    event_id: str
    title: str
    raw_input: str
    event_type: str  # RELOCATION, JOB_CHANGE, HOME_PURCHASE, BUSINESS_RELOCATION, etc.
    origin_jurisdiction: Jurisdiction
    destination_jurisdiction: Optional[Jurisdiction] = None
    is_cross_border: bool = False
    affected_people: Dict[str, Any] = Field(default_factory=dict)
    assets: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    status: str = "ACTIVE"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AgentCard(BaseModel):
    agent_id: str
    name: str
    title: str
    capabilities: List[str]
    skills: List[str]
    supported_input: List[str]
    supported_output: List[str]
    endpoint: str
    auth_required: bool = True
    status: str = "ONLINE"


class MCPTool(BaseModel):
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    requires_approval: bool
    parameters_schema: Dict[str, Any]
    status: str = "ACTIVE"


class ApprovalRequest(BaseModel):
    approval_id: str
    event_id: str
    task_id: str
    tool_name: str
    parameters: Dict[str, Any]
    reason: str
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class EventNotification(BaseModel):
    event_type: str  # SOURCE_CHANGED, JURISDICTION_CHANGED, TASK_BLOCKED, etc.
    source_id: Optional[str] = None
    event_id: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class EvaluationScenario(BaseModel):
    scenario_id: str
    name: str
    raw_input: str
    origin_country: str
    destination_country: Optional[str] = None
    is_cross_border: bool = False
    expected_domains: List[str]
    expected_agents: List[str]


class EvaluationResult(BaseModel):
    total_scenarios: int
    passed_scenarios: int
    jurisdiction_accuracy: float
    citation_precision: float
    safety_disclaimer_compliance: float
    average_latency_ms: float
    results_detail: List[Dict[str, Any]]
