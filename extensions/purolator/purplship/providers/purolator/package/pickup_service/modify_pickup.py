from typing import Tuple, List
from functools import partial
from pypurolator.pickup_service_1_2_1 import (
    ModifyPickupInstruction,
    ModifyPickUpRequest,
    ModifyPickUpResponse,
    RequestContext,
)
from purplship.core.models import PickupUpdateRequest, PickupDetails, Message
from purplship.core.utils import (
    Serializable, create_envelope, Envelope, Element, build
)
from purplship.providers.purolator.error import parse_error_response
from purplship.providers.purolator.utils import Settings, standard_request_serializer


def parse_modify_pickup_reply(response: Element, settings: Settings) -> Tuple[PickupDetails, List[Message]]:
    reply = build(
        ModifyPickUpResponse,
        next(iter(response.xpath(".//*[local-name() = $name]", name="ModifyPickUpResponse")), None)
    )
    pickup = (
        _extract_pickup_details(reply, settings)
        if reply is not None and reply.PickUpConfirmationNumber is not None
        else None
    )

    return pickup, parse_error_response(response, settings)


def _extract_pickup_details(reply: ModifyPickUpResponse, settings: Settings) -> PickupDetails:

    return PickupDetails(
        carrier_id=settings.carrier_id,
        carrier_name=settings.carrier_name,
        confirmation_number=reply.PickUpConfirmationNumber,
    )


def modify_pickup_request(payload: PickupUpdateRequest, settings: Settings) -> Serializable[Envelope]:
    request = create_envelope(
        header_content=RequestContext(
            Version="1.2",
            Language=settings.language,
            GroupID="",
            RequestReference="",
            UserToken=settings.user_token,
        ),
        body_content=ModifyPickUpRequest(
            BillingAccountNumber=settings.account_number,
            ConfirmationNumber=payload.confirmation_number,
            ModifyPickupInstruction=ModifyPickupInstruction(
                UntilTime="".join(payload.closing_time.split(':')),
                PickUpLocation=payload.package_location,
                SupplyRequestCodes=None,
                TrailerAccessible=payload.options.get('TrailerAccessible'),
                LoadingDockAvailable=payload.options.get('LoadingDockAvailable'),
                ShipmentOnSkids=None,
                NumberOfSkids=None,
            ),
            ShipmentSummary=None
        )
    )

    return Serializable(request, partial(standard_request_serializer, version='v1'))
