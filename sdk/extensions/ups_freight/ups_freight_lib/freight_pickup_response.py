from attr import s
from typing import Optional, List
from jstruct import JStruct, JList


@s(auto_attribs=True)
class ResponseStatusType:
    Code: Optional[str] = None
    Description: Optional[str] = None


@s(auto_attribs=True)
class TransactionReferenceType:
    CustomerContext: Optional[str] = None
    TransactionIdentifier: Optional[str] = None


@s(auto_attribs=True)
class ResponseType:
    ResponseStatus: Optional[ResponseStatusType] = JStruct[ResponseStatusType]
    Alert: List[ResponseStatusType] = JList[ResponseStatusType]
    TransactionReference: Optional[TransactionReferenceType] = JStruct[TransactionReferenceType]


@s(auto_attribs=True)
class FreightPickupResponseClassType:
    Response: Optional[ResponseType] = JStruct[ResponseType]
    PickupRequestConfirmationNumber: Optional[str] = None


@s(auto_attribs=True)
class FreightPickupResponseType:
    FreightPickupResponse: Optional[FreightPickupResponseClassType] = JStruct[FreightPickupResponseClassType]
