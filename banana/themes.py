from pydantic import BaseModel


class Theme(BaseModel):
    primary: str
    light: str
    dark: str


BANANA = Theme(primary="#E3CF57", light="#F5EDC0", dark="1C1A0B")
