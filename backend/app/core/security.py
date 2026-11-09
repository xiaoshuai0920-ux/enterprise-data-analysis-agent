from dataclasses import dataclass
from fastapi import Header

@dataclass
class CurrentUser:
    user_id: str
    username: str
    role: str
    region_scope: list[str]

ROLE_REGION_SCOPE = {
    "sales_rep": ["华东"],
    "regional_manager": ["华东", "华南"],
    "admin": ["华东", "华南", "华北", "西部"],
}

async def get_current_user(
    x_user_id: str = Header(default="u_demo"),
    x_username: str = Header(default="dawei"),
    x_user_role: str = Header(default="regional_manager"),
) -> CurrentUser:
    role = x_user_role if x_user_role in ROLE_REGION_SCOPE else "sales_rep"
    return CurrentUser(
        user_id=x_user_id,
        username=x_username,
        role=role,
        region_scope=ROLE_REGION_SCOPE[role],
    )
