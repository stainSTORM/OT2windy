from typing import Dict, Any
from pydantic import BaseModel

class HardFakts(BaseModel):
    fakts: Dict[str, Any]

    async def aload(self) -> Dict[str, Any]:
        return self.fakts