from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel


class ProxyType(str, Enum):
    proxy = "proxy"


class ModelType(str, Enum):
    model = "model"


class BaseModelCard(BaseModel):
    id: str
    """The ID of the model object."""

    object: ModelType = ModelType.model
    """The object type, which is always "model" for a model object."""

    created: int
    """The Unix timestamp when the model was created."""

    owned_by: str
    """The organization ID of the owner of the model."""

    plan: str = "free"
    """The minimum plan required to use the model."""


class VerboseModelCard(BaseModelCard):
    name: str
    """The pretty name of the model."""

    description: str
    """The description of the model."""

    type: str
    """The type of the model (e.g chat.completions)."""

    modality: Optional[str]
    """The modality of the model (e.g text,image->text)"""

    request_multiplier: float = 1.0
    """The multiplier for request costs when using the model."""

    permission: Optional[dict] = {}
    """The permissions for the model. TODO: write out types"""

    active: bool = True
    """The status of the model."""


class ProxyCard(BaseModel):
    id: str
    """The ID of the proxy object."""

    object: ProxyType = ProxyType.proxy
    """The object type, which is always "proxy" for a proxy object."""

    proxy_to: str
    """The model ID that the proxy points to."""

    @property
    def parent(self) -> BaseModelCard | str:
        """The parent model card that the proxy points to."""
        return f"tmp-{self.proxy_to}"

    @parent.setter
    def parent(self, value: BaseModelCard) -> None:
        self._parent = value


ListModelsData = List[Union[BaseModelCard, ProxyCard]]


ListVerboseModelsData = List[Union[VerboseModelCard, ProxyCard]]


class ListModelsResponse(BaseModel):
    object: str
    """The object type, which is always "list" for a list of model objects."""

    data: ListModelsData
    """The list of model/proxy cards."""

    count: int
    """The number of model/proxy cards returned."""


class ListVerboseModelsResponse(BaseModel):
    object: str
    """The object type, which is always "list" for a list of model objects."""

    data: ListVerboseModelsData
    """The list of model/proxy cards."""

    count: int
    """The number of model/proxy cards returned."""
