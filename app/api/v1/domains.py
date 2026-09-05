from fastapi import APIRouter
from app.models.domain import DomainRegistry
from app.schemas.responses import DomainsResponse, DomainInfo

router = APIRouter(tags=["Domains"])

@router.get("/domains", response_model=DomainsResponse)
async def list_domains():
    """
    List all available domains and their capabilities.
    """
    domain_infos = []
    for domain_type in DomainRegistry.list_domains():
        config = DomainRegistry.get_domain_config(domain_type)
        if config:
            domain_infos.append(
                DomainInfo(
                    name=config.name,
                    label=config.label,
                    description=config.description,
                    supported_question_types=[t.value if hasattr(t, 'value') else str(t) for t in config.supported_question_types],
                    topics=config.example_topics
                )
            )
        
    return DomainsResponse(domains=domain_infos)
