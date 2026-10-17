from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from configs.auth_dependencies import authenticated_context,csrf_context
from configs.database import get_db
from schemas.auth_schema import AuthContext
from schemas.bouquet_setting_schema import BouquetSettingsInput,BouquetSettingsResponse
from use_cases.bouquet_settings.get_settings import get_settings
from use_cases.bouquet_settings.update_settings import update_settings

router=APIRouter(prefix="/bouquet-settings",tags=["bouquet-settings"])

@router.get("",response_model=BouquetSettingsResponse)
def get_endpoint(actor:AuthContext=Depends(authenticated_context),db:Session=Depends(get_db)):
    return get_settings(db)

@router.put("",response_model=BouquetSettingsResponse)
def update_endpoint(data:BouquetSettingsInput,actor:AuthContext=Depends(csrf_context),db:Session=Depends(get_db)):
    return update_settings(db,actor,data)
