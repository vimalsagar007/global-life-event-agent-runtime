from typing import List, Dict, Any
from backend.agents.base import BaseAgent
from backend.models.domain import Task, TaskPriority, TaskStatus
from backend.rag.pipeline import RAG_PIPELINE
from backend.security.defense import DISCLAIMER_TEXT


class GovernmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="gov_agent",
            name="GovernmentAgent",
            title="Government & Public Administration Specialist",
            capabilities=["Identify authority hierarchy", "Municipal registration", "Identity documents"],
            skills=["Government Portal Retrieval", "Registration Workflows"],
            supported_input=["jurisdiction", "event_type"],
            supported_output=["tasks", "citations"]
        )

    def generate_tasks(self, event_id: str, context: Dict[str, Any]) -> List[Task]:
        juris = context.get("destination_jurisdiction") or context.get("origin_jurisdiction")
        country = juris.country if juris else "Local"
        sources = RAG_PIPELINE.retrieve(f"government registration residency {country}", country=country)

        return [
            Task(
                task_id=f"gov_{event_id}_1",
                title=f"Register Residency & Local Address with {country} Authorities",
                description=f"Submit address registration and identity verification to municipal council/city hall in {country}.",
                category="Government",
                jurisdiction=juris.to_full_string() if juris else country,
                priority=TaskPriority.HIGH,
                status=TaskStatus.PENDING,
                deadline="Within 14 days of arrival",
                sources=sources,
                agent=self.name,
                requires_approval=False
            )
        ]


class EducationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="edu_agent",
            name="EducationAgent",
            title="Global Education & Schools Specialist",
            capabilities=["School catchment discovery", "University admission rules", "Credit evaluation"],
            skills=["School Search", "Educational Transfer Checklist"],
            supported_input=["children_count", "jurisdiction"],
            supported_output=["tasks"]
        )

    def generate_tasks(self, event_id: str, context: Dict[str, Any]) -> List[Task]:
        affected = context.get("affected_people", {})
        if affected.get("children", 0) <= 0:
            return []

        juris = context.get("destination_jurisdiction") or context.get("origin_jurisdiction")
        country = juris.country if juris else "Local"
        sources = RAG_PIPELINE.retrieve(f"school education enrollment {country}", country=country)

        return [
            Task(
                task_id=f"edu_{event_id}_1",
                title=f"Identify Local Primary/Secondary Schools in {country}",
                description=f"Gather immunization records, previous school transcripts, and submit catchment area enrolment applications.",
                category="Education",
                jurisdiction=juris.to_full_string() if juris else country,
                priority=TaskPriority.HIGH,
                status=TaskStatus.PENDING,
                deadline="30 days prior to school term start",
                sources=sources,
                agent=self.name,
                requires_approval=False
            )
        ]


class ImmigrationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="imm_agent",
            name="ImmigrationAgent",
            title="International Visa & Immigration Information Specialist",
            capabilities=["Visa entry checklist", "Passport validity verification", "Biometric appointment guidance"],
            skills=["Visa Checklist Retrieval", "Entry Formalities"],
            supported_input=["origin_jurisdiction", "destination_jurisdiction"],
            supported_output=["tasks"]
        )

    def generate_tasks(self, event_id: str, context: Dict[str, Any]) -> List[Task]:
        if not context.get("is_cross_border"):
            return []

        dest = context.get("destination_jurisdiction")
        country = dest.country if dest else "Destination Country"
        sources = RAG_PIPELINE.retrieve(f"visa entry requirements {country}", country=country)

        return [
            Task(
                task_id=f"imm_{event_id}_1",
                title=f"Verify Visa & Entry Permit Requirements for {country}",
                description=f"Check passport expiration (minimum 6 months validity required), biometric residence permits, and official entry clearance checklist. {DISCLAIMER_TEXT}",
                category="Immigration",
                jurisdiction=dest.to_full_string() if dest else country,
                priority=TaskPriority.CRITICAL,
                status=TaskStatus.PENDING,
                deadline="60 days prior to departure",
                sources=sources,
                agent=self.name,
                requires_approval=False
            )
        ]


class HousingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="house_agent",
            name="HousingAgent",
            title="Housing, Real Estate & Utilities Specialist",
            capabilities=["Lease administrative requirements", "Property transfer checklists", "Utility setup"],
            skills=["Housing Search", "Utility Connection"],
            supported_input=["jurisdiction"],
            supported_output=["tasks"]
        )

    def generate_tasks(self, event_id: str, context: Dict[str, Any]) -> List[Task]:
        juris = context.get("destination_jurisdiction") or context.get("origin_jurisdiction")
        location = juris.to_full_string() if juris else "Target City"
        sources = RAG_PIPELINE.retrieve("housing rental lease utilities", country=juris.country if juris else "Local")

        return [
            Task(
                task_id=f"house_{event_id}_1",
                title=f"Secure Housing Accommodation & Utilities in {location}",
                description="Finalize rental lease/purchase contract, establish electricity, water, gas, and broadband internet services.",
                category="Housing",
                jurisdiction=location,
                priority=TaskPriority.HIGH,
                status=TaskStatus.PENDING,
                deadline="14 days prior to move date",
                sources=sources,
                agent=self.name,
                requires_approval=False
            )
        ]


class HealthcareAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="health_agent",
            name="HealthcareAgent",
            title="Healthcare & Health Insurance Administration Specialist",
            capabilities=["Public health registration", "GP/Primary physician lookup", "Health insurance transfer"],
            skills=["Healthcare System Navigation", "GP Registration"],
            supported_input=["jurisdiction"],
            supported_output=["tasks"]
        )

    def generate_tasks(self, event_id: str, context: Dict[str, Any]) -> List[Task]:
        juris = context.get("destination_jurisdiction") or context.get("origin_jurisdiction")
        country = juris.country if juris else "Local"
        sources = RAG_PIPELINE.retrieve(f"health registration GP insurance {country}", country=country)

        return [
            Task(
                task_id=f"health_{event_id}_1",
                title=f"Register with Local Public Healthcare / GP Surgery in {country}",
                description=f"Transfer medical records, register with local family doctor or public healthcare system (e.g., NHS/OHIP/Medicare). {DISCLAIMER_TEXT}",
                category="Healthcare",
                jurisdiction=juris.to_full_string() if juris else country,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.PENDING,
                deadline="Within 30 days of arrival",
                sources=sources,
                agent=self.name,
                requires_approval=False
            )
        ]


class FinanceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="fin_agent",
            name="FinanceAgent",
            title="Banking & International Finance Specialist",
            capabilities=["Local bank account opening", "Foreign exchange planning", "Credit transfer"],
            skills=["Banking Onboarding", "Currency Exchange Checklist"],
            supported_input=["jurisdiction"],
            supported_output=["tasks"]
        )

    def generate_tasks(self, event_id: str, context: Dict[str, Any]) -> List[Task]:
        juris = context.get("destination_jurisdiction") or context.get("origin_jurisdiction")
        country = juris.country if juris else "Local"
        sources = RAG_PIPELINE.retrieve(f"banking account opening proof of address {country}", country=country)

        return [
            Task(
                task_id=f"fin_{event_id}_1",
                title=f"Open Local Bank Account & Set Up Financial Services in {country}",
                description="Schedule appointment with local retail bank, gather proof of address, tax ID, and passport identity verification.",
                category="Finance",
                jurisdiction=juris.to_full_string() if juris else country,
                priority=TaskPriority.HIGH,
                status=TaskStatus.PENDING,
                deadline="Within 7 days of arrival",
                sources=sources,
                agent=self.name,
                requires_approval=False
            )
        ]


class TransportationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="trans_agent",
            name="TransportationAgent",
            title="Vehicle & Transportation Requirements Specialist",
            capabilities=["Driver's license exchange rules", "Vehicle importation/exportation", "Public transit info"],
            skills=["DMV/Driver Licensing Rules", "Vehicle Transfer"],
            supported_input=["assets", "jurisdiction"],
            supported_output=["tasks"]
        )

    def generate_tasks(self, event_id: str, context: Dict[str, Any]) -> List[Task]:
        assets = context.get("assets", [])
        juris = context.get("destination_jurisdiction") or context.get("origin_jurisdiction")
        country = juris.country if juris else "Local"
        sources = RAG_PIPELINE.retrieve(f"driver license exchange vehicle registration {country}", country=country)

        tasks = [
            Task(
                task_id=f"trans_{event_id}_1",
                title=f"Exchange Driver's License for {country} License",
                description=f"Verify reciprocal driver's license agreements and complete DMV/transportation authority transfer form.",
                category="Transportation",
                jurisdiction=juris.to_full_string() if juris else country,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.PENDING,
                deadline="Within 60 days of relocation",
                sources=sources,
                agent=self.name,
                requires_approval=False
            )
        ]

        if "vehicle" in assets or "car" in assets:
            tasks.append(
                Task(
                    task_id=f"trans_{event_id}_2",
                    title=f"Vehicle Customs Clearance & Registration in {country}",
                    description="Submit export declaration, pay import duties/taxes if applicable, pass roadworthiness inspection, and register plates.",
                    category="Transportation",
                    jurisdiction=country,
                    priority=TaskPriority.HIGH,
                    status=TaskStatus.PENDING,
                    deadline="Within 30 days of vehicle arrival",
                    sources=sources,
                    agent=self.name,
                    requires_approval=False
                )
            )

        return tasks


class PetRelocationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="pet_agent",
            name="PetRelocationAgent",
            title="Global Pet & Animal Relocation Specialist",
            capabilities=["Pet import permits", "Rabies antibody titers & vaccinations", "Quarantine requirements"],
            skills=["Pet Import Checklist", "Airline Pet Rules"],
            supported_input=["assets", "destination_jurisdiction"],
            supported_output=["tasks"]
        )

    def generate_tasks(self, event_id: str, context: Dict[str, Any]) -> List[Task]:
        assets = context.get("assets", [])
        if "pet" not in assets and "dog" not in assets and "cat" not in assets:
            return []

        dest = context.get("destination_jurisdiction") or context.get("origin_jurisdiction")
        country = dest.country if dest else "Destination Country"
        sources = RAG_PIPELINE.retrieve(f"pet import rabies quarantine {country}", country=country)

        return [
            Task(
                task_id=f"pet_{event_id}_1",
                title=f"Complete Pet Import Clearance & Vaccination for {country}",
                description="Obtain ISO microchip, rabies vaccination certificate, veterinary health certificate, and reserve mandatory quarantine space if required.",
                category="Pet Relocation",
                jurisdiction=country,
                priority=TaskPriority.CRITICAL,
                status=TaskStatus.PENDING,
                deadline="90 days prior to travel",
                sources=sources,
                agent=self.name,
                requires_approval=False
            )
        ]


class CrossBorderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="cross_agent",
            name="CrossBorderAgent",
            title="Cross-Border Relocation & International Customs Coordinator",
            capabilities=["Multi-jurisdiction coordination", "Customs declaration", "International logistics"],
            skills=["Cross-Border Workflow", "Customs Manifest Checklist"],
            supported_input=["origin_jurisdiction", "destination_jurisdiction"],
            supported_output=["tasks"]
        )

    def generate_tasks(self, event_id: str, context: Dict[str, Any]) -> List[Task]:
        if not context.get("is_cross_border"):
            return []

        orig = context.get("origin_jurisdiction")
        dest = context.get("destination_jurisdiction")
        
        return [
            Task(
                task_id=f"cross_{event_id}_1",
                title=f"Prepare Cross-Border Customs Manifest: {orig.country} → {dest.country}",
                description=f"Inventory personal effects, complete duty-free personal move customs declaration forms, and coordinate international shipping cargo.",
                category="Cross-Border Logistics",
                jurisdiction=f"{orig.country} / {dest.country}",
                priority=TaskPriority.HIGH,
                status=TaskStatus.PENDING,
                deadline="30 days prior to departure",
                sources=[],
                agent=self.name,
                requires_approval=False
            )
        ]
