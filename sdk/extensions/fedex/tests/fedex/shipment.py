import re
import unittest
import logging
from unittest.mock import patch, ANY
from purplship.core.utils import DP
from purplship.core.models import ShipmentRequest, ShipmentCancelRequest
from purplship import Shipment
from tests.fedex.fixture import gateway

logger = logging.getLogger(__name__)


class TestFedExShipment(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.ShipmentRequest = ShipmentRequest(**shipment_data)
        self.ShipmentCancelRequest = ShipmentCancelRequest(**shipment_cancel_data)
        self.MultiPieceShipmentRequest = ShipmentRequest(**multi_piece_shipment_data)

    def test_create_shipment_request(self):
        request = gateway.mapper.create_shipment_request(self.ShipmentRequest)
        # Remove timeStamp for testing
        serialized_request = re.sub(
            "<v26:ShipTimestamp>[^>]+</v26:ShipTimestamp>",
            "",
            request.serialize()[0].replace(
                "                <v26:ShipTimestamp>", "<v26:ShipTimestamp>"
            ),
        )

        self.assertEqual(serialized_request, ShipmentRequestXml)

    def test_create_multi_piece_shipment_request(self):
        request = gateway.mapper.create_shipment_request(self.MultiPieceShipmentRequest)
        # Remove timeStamp for testing
        [master_request, second_shipment_request] = [
            re.sub(
                "<v26:ShipTimestamp>[^>]+</v26:ShipTimestamp>",
                "",
                request.replace(
                    "                <v26:ShipTimestamp>", "<v26:ShipTimestamp>"
                ),
            )
            for request in request.serialize()
        ]

        self.assertEqual(master_request, MasterShipmentRequestXml)
        self.assertEqual(second_shipment_request, SecondPieceShipmentRequestXml)

    def test_create_cancel_shipment_request(self):
        request = gateway.mapper.create_cancel_shipment_request(
            self.ShipmentCancelRequest
        )

        self.assertEqual(request.serialize(), ShipmentCancelRequestXML)

    @patch("purplship.mappers.fedex.proxy.http", return_value="<a></a>")
    def test_create_shipment(self, http_mock):
        Shipment.create(self.ShipmentRequest).from_(gateway)

        url = http_mock.call_args[1]["url"]
        self.assertEqual(url, f"{gateway.settings.server_url}/ship")

    @patch("purplship.mappers.fedex.proxy.http", return_value="<a></a>")
    def test_cancel_shipment(self, http_mock):
        Shipment.cancel(self.ShipmentCancelRequest).from_(gateway)

        url = http_mock.call_args[1]["url"]
        self.assertEqual(url, f"{gateway.settings.server_url}/ship")

    def test_parse_shipment_response(self):
        with patch("purplship.mappers.fedex.proxy.http") as mock:
            mock.return_value = ShipmentResponseXML
            parsed_response = (
                Shipment.create(self.ShipmentRequest).from_(gateway).parse()
            )

            self.assertListEqual(DP.to_dict(parsed_response), ParsedShipmentResponse)

    def test_parse_multi_piece_shipment_response(self):
        with patch("purplship.mappers.fedex.proxy.http") as mocks:
            mocks.side_effect = [ShipmentResponseXML, ShipmentResponseXML]
            parsed_response = (
                Shipment.create(self.MultiPieceShipmentRequest).from_(gateway).parse()
            )

            self.assertListEqual(
                DP.to_dict(parsed_response),
                ParsedMultiPieceShipmentResponse,
            )

    def test_parse_shipment_cancel_response(self):
        with patch("purplship.mappers.fedex.proxy.http") as mock:
            mock.return_value = ShipmentResponseXML
            parsed_response = (
                Shipment.cancel(self.ShipmentCancelRequest).from_(gateway).parse()
            )

            self.assertEqual(
                DP.to_dict(parsed_response), DP.to_dict(ParsedShipmentCancelResponse)
            )


if __name__ == "__main__":
    unittest.main()

shipment_data = {
    "shipper": {
        "person_name": "Input Your Information",
        "company_name": "Input Your Information",
        "phone_number": "Input Your Information",
        "email": "Input Your Information",
        "address_line1": "Input Your Information",
        "address_line2": "Input Your Information",
        "city": "MEMPHIS",
        "state_code": "TN",
        "postal_code": "38117",
        "country_code": "US",
    },
    "recipient": {
        "person_name": "Input Your Information",
        "company_name": "Input Your Information",
        "phone_number": "Input Your Information",
        "email": "Input Your Information",
        "address_line1": "Input Your Information",
        "address_line2": "Input Your Information",
        "city": "RICHMOND",
        "state_code": "BC",
        "postal_code": "V7C4v7",
        "country_code": "CA",
    },
    "parcels": [
        {
            "packaging_type": "your_packaging",
            "weight_unit": "LB",
            "dimension_unit": "IN",
            "weight": 20.0,
            "length": 12,
            "width": 12,
            "height": 12,
        }
    ],
    "service": "fedex_international_priority",
    "options": {"currency": "USD", "international_traffic_in_arms_regulations": True},
    "payment": {"paid_by": "third_party", "account_number": "2349857"},
    "customs": {
        "duty": {"paid_by": "sender", "declared_value": "100."},
        "commodities": [{"weight": "10", "description": "test"}],
    },
    "reference": "#Order 11111",
}

multi_piece_shipment_data = {
    **shipment_data,
    "parcels": [
        {
            "packaging_type": "your_packaging",
            "weight_unit": "LB",
            "dimension_unit": "IN",
            "weight": 1.0,
            "length": 12,
            "width": 12,
            "height": 12,
        },
        {
            "packaging_type": "your_packaging",
            "weight_unit": "LB",
            "dimension_unit": "IN",
            "weight": 2.0,
            "length": 11,
            "width": 11,
            "height": 11,
        },
    ],
}

shipment_cancel_data = {
    "shipment_identifier": "794947717776",
    "service": "express",
}

ParsedShipmentResponse = [
    {
        "carrier_name": "fedex",
        "carrier_id": "carrier_id",
        "label": ANY,
        "tracking_number": "794947717776",
        "shipment_identifier": "794947717776",
        "meta": {"tracking_numbers": ["794947717776"]},
    },
    [],
]

ParsedMultiPieceShipmentResponse = [
    {
        "carrier_name": "fedex",
        "carrier_id": "carrier_id",
        "label": ANY,
        "tracking_number": "794947717776",
        "shipment_identifier": "794947717776",
        "meta": {"tracking_numbers": ["794947717776", "794947717776"]},
    },
    [],
]

ParsedShipmentCancelResponse = [
    {
        "carrier_id": "carrier_id",
        "carrier_name": "fedex",
        "operation": "Cancel Shipment",
        "success": True,
    },
    [],
]


ShipmentRequestXml = """<tns:Envelope xmlns:tns="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v26="http://fedex.com/ws/ship/v26">
    <tns:Body>
        <v26:ProcessShipmentRequest>
            <v26:WebAuthenticationDetail>
                <v26:UserCredential>
                    <v26:Key>user_key</v26:Key>
                    <v26:Password>password</v26:Password>
                </v26:UserCredential>
            </v26:WebAuthenticationDetail>
            <v26:ClientDetail>
                <v26:AccountNumber>2349857</v26:AccountNumber>
                <v26:MeterNumber>1293587</v26:MeterNumber>
            </v26:ClientDetail>
            <v26:TransactionDetail>
                <v26:CustomerTransactionId>IE_v26_Ship</v26:CustomerTransactionId>
            </v26:TransactionDetail>
            <v26:Version>
                <v26:ServiceId>ship</v26:ServiceId>
                <v26:Major>26</v26:Major>
                <v26:Intermediate>0</v26:Intermediate>
                <v26:Minor>0</v26:Minor>
            </v26:Version>
            <v26:RequestedShipment>

                <v26:DropoffType>REGULAR_PICKUP</v26:DropoffType>
                <v26:ServiceType>INTERNATIONAL_PRIORITY</v26:ServiceType>
                <v26:PackagingType>YOUR_PACKAGING</v26:PackagingType>
                <v26:TotalWeight>
                    <v26:Units>LB</v26:Units>
                    <v26:Value>20</v26:Value>
                </v26:TotalWeight>
                <v26:PreferredCurrency>USD</v26:PreferredCurrency>
                <v26:Shipper>
                    <v26:AccountNumber>2349857</v26:AccountNumber>
                    <v26:Contact>
                        <v26:PersonName>Input Your Information</v26:PersonName>
                        <v26:CompanyName>Input Your Information</v26:CompanyName>
                        <v26:PhoneNumber>Input Your Information</v26:PhoneNumber>
                        <v26:EMailAddress>Input Your Information</v26:EMailAddress>
                    </v26:Contact>
                    <v26:Address>
                        <v26:StreetLines>Input Your Information</v26:StreetLines>
                        <v26:StreetLines>Input Your Information</v26:StreetLines>
                        <v26:City>MEMPHIS</v26:City>
                        <v26:StateOrProvinceCode>TN</v26:StateOrProvinceCode>
                        <v26:PostalCode>38117</v26:PostalCode>
                        <v26:CountryCode>US</v26:CountryCode>
                        <v26:CountryName>United States</v26:CountryName>
                        <v26:Residential>false</v26:Residential>
                    </v26:Address>
                </v26:Shipper>
                <v26:Recipient>
                    <v26:Contact>
                        <v26:PersonName>Input Your Information</v26:PersonName>
                        <v26:CompanyName>Input Your Information</v26:CompanyName>
                        <v26:PhoneNumber>Input Your Information</v26:PhoneNumber>
                        <v26:EMailAddress>Input Your Information</v26:EMailAddress>
                    </v26:Contact>
                    <v26:Address>
                        <v26:StreetLines>Input Your Information</v26:StreetLines>
                        <v26:StreetLines>Input Your Information</v26:StreetLines>
                        <v26:City>RICHMOND</v26:City>
                        <v26:StateOrProvinceCode>BC</v26:StateOrProvinceCode>
                        <v26:PostalCode>V7C4v7</v26:PostalCode>
                        <v26:CountryCode>CA</v26:CountryCode>
                        <v26:CountryName>Canada</v26:CountryName>
                        <v26:Residential>false</v26:Residential>
                    </v26:Address>
                </v26:Recipient>
                <v26:ShippingChargesPayment>
                    <v26:PaymentType>THIRD_PARTY</v26:PaymentType>
                    <v26:Payor>
                        <v26:ResponsibleParty>
                            <v26:AccountNumber>2349857</v26:AccountNumber>
                        </v26:ResponsibleParty>
                    </v26:Payor>
                </v26:ShippingChargesPayment>
                <v26:SpecialServicesRequested>
                    <v26:EventNotificationDetail>
                        <v26:EventNotifications>
                            <v26:Events>ON_DELIVERY</v26:Events>
                            <v26:Events>ON_ESTIMATED_DELIVERY</v26:Events>
                            <v26:Events>ON_EXCEPTION</v26:Events>
                            <v26:Events>ON_SHIPMENT</v26:Events>
                            <v26:Events>ON_TENDER</v26:Events>
                            <v26:NotificationDetail>
                                <v26:NotificationType>EMAIL</v26:NotificationType>
                                <v26:EmailDetail>
                                    <v26:EmailAddress>Input Your Information</v26:EmailAddress>
                                    <v26:Name>Input Your Information</v26:Name>
                                </v26:EmailDetail>
                                <v26:Localization>
                                    <v26:LanguageCode>EN</v26:LanguageCode>
                                </v26:Localization>
                            </v26:NotificationDetail>
                            <v26:FormatSpecification>
                                <v26:Type>TEXT</v26:Type>
                            </v26:FormatSpecification>
                        </v26:EventNotifications>
                    </v26:EventNotificationDetail>
                </v26:SpecialServicesRequested>
                <v26:CustomsClearanceDetail>
                    <v26:DutiesPayment>
                        <v26:PaymentType>SENDER</v26:PaymentType>
                    </v26:DutiesPayment>
                    <v26:CustomsValue>
                        <v26:Currency>USD</v26:Currency>
                        <v26:Amount>100</v26:Amount>
                    </v26:CustomsValue>
                    <v26:Commodities>
                        <v26:NumberOfPieces>1</v26:NumberOfPieces>
                        <v26:Description>test</v26:Description>
                        <v26:Weight>
                            <v26:Units>LB</v26:Units>
                        </v26:Weight>
                        <v26:Quantity>1</v26:Quantity>
                        <v26:QuantityUnits>EA</v26:QuantityUnits>
                        <v26:UnitPrice>
                            <v26:Currency>USD</v26:Currency>
                        </v26:UnitPrice>
                    </v26:Commodities>
                </v26:CustomsClearanceDetail>
                <v26:LabelSpecification>
                    <v26:LabelFormatType>COMMON2D</v26:LabelFormatType>
                    <v26:ImageType>PDF</v26:ImageType>
                    <v26:LabelStockType>STOCK_4X6</v26:LabelStockType>
                    <v26:LabelPrintingOrientation>TOP_EDGE_OF_TEXT_FIRST</v26:LabelPrintingOrientation>
                    <v26:LabelOrder>SHIPPING_LABEL_FIRST</v26:LabelOrder>
                </v26:LabelSpecification>
                <v26:PackageCount>1</v26:PackageCount>
                <v26:RequestedPackageLineItems>
                    <v26:SequenceNumber>1</v26:SequenceNumber>
                    <v26:Weight>
                        <v26:Units>LB</v26:Units>
                        <v26:Value>20</v26:Value>
                    </v26:Weight>
                    <v26:Dimensions>
                        <v26:Length>12</v26:Length>
                        <v26:Width>12</v26:Width>
                        <v26:Height>12</v26:Height>
                        <v26:Units>IN</v26:Units>
                    </v26:Dimensions>
                    <v26:CustomerReferences>
                        <v26:CustomerReferenceType>CUSTOMER_REFERENCE</v26:CustomerReferenceType>
                        <v26:Value>#Order 11111</v26:Value>
                    </v26:CustomerReferences>
                </v26:RequestedPackageLineItems>
            </v26:RequestedShipment>
        </v26:ProcessShipmentRequest>
    </tns:Body>
</tns:Envelope>
"""

MasterShipmentRequestXml = """<tns:Envelope xmlns:tns="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v26="http://fedex.com/ws/ship/v26">
    <tns:Body>
        <v26:ProcessShipmentRequest>
            <v26:WebAuthenticationDetail>
                <v26:UserCredential>
                    <v26:Key>user_key</v26:Key>
                    <v26:Password>password</v26:Password>
                </v26:UserCredential>
            </v26:WebAuthenticationDetail>
            <v26:ClientDetail>
                <v26:AccountNumber>2349857</v26:AccountNumber>
                <v26:MeterNumber>1293587</v26:MeterNumber>
            </v26:ClientDetail>
            <v26:TransactionDetail>
                <v26:CustomerTransactionId>IE_v26_Ship</v26:CustomerTransactionId>
            </v26:TransactionDetail>
            <v26:Version>
                <v26:ServiceId>ship</v26:ServiceId>
                <v26:Major>26</v26:Major>
                <v26:Intermediate>0</v26:Intermediate>
                <v26:Minor>0</v26:Minor>
            </v26:Version>
            <v26:RequestedShipment>

                <v26:DropoffType>REGULAR_PICKUP</v26:DropoffType>
                <v26:ServiceType>INTERNATIONAL_PRIORITY</v26:ServiceType>
                <v26:PackagingType>YOUR_PACKAGING</v26:PackagingType>
                <v26:TotalWeight>
                    <v26:Units>LB</v26:Units>
                    <v26:Value>3</v26:Value>
                </v26:TotalWeight>
                <v26:PreferredCurrency>USD</v26:PreferredCurrency>
                <v26:Shipper>
                    <v26:AccountNumber>2349857</v26:AccountNumber>
                    <v26:Contact>
                        <v26:PersonName>Input Your Information</v26:PersonName>
                        <v26:CompanyName>Input Your Information</v26:CompanyName>
                        <v26:PhoneNumber>Input Your Information</v26:PhoneNumber>
                        <v26:EMailAddress>Input Your Information</v26:EMailAddress>
                    </v26:Contact>
                    <v26:Address>
                        <v26:StreetLines>Input Your Information</v26:StreetLines>
                        <v26:StreetLines>Input Your Information</v26:StreetLines>
                        <v26:City>MEMPHIS</v26:City>
                        <v26:StateOrProvinceCode>TN</v26:StateOrProvinceCode>
                        <v26:PostalCode>38117</v26:PostalCode>
                        <v26:CountryCode>US</v26:CountryCode>
                        <v26:CountryName>United States</v26:CountryName>
                        <v26:Residential>false</v26:Residential>
                    </v26:Address>
                </v26:Shipper>
                <v26:Recipient>
                    <v26:Contact>
                        <v26:PersonName>Input Your Information</v26:PersonName>
                        <v26:CompanyName>Input Your Information</v26:CompanyName>
                        <v26:PhoneNumber>Input Your Information</v26:PhoneNumber>
                        <v26:EMailAddress>Input Your Information</v26:EMailAddress>
                    </v26:Contact>
                    <v26:Address>
                        <v26:StreetLines>Input Your Information</v26:StreetLines>
                        <v26:StreetLines>Input Your Information</v26:StreetLines>
                        <v26:City>RICHMOND</v26:City>
                        <v26:StateOrProvinceCode>BC</v26:StateOrProvinceCode>
                        <v26:PostalCode>V7C4v7</v26:PostalCode>
                        <v26:CountryCode>CA</v26:CountryCode>
                        <v26:CountryName>Canada</v26:CountryName>
                        <v26:Residential>false</v26:Residential>
                    </v26:Address>
                </v26:Recipient>
                <v26:ShippingChargesPayment>
                    <v26:PaymentType>THIRD_PARTY</v26:PaymentType>
                    <v26:Payor>
                        <v26:ResponsibleParty>
                            <v26:AccountNumber>2349857</v26:AccountNumber>
                        </v26:ResponsibleParty>
                    </v26:Payor>
                </v26:ShippingChargesPayment>
                <v26:SpecialServicesRequested>
                    <v26:EventNotificationDetail>
                        <v26:EventNotifications>
                            <v26:Events>ON_DELIVERY</v26:Events>
                            <v26:Events>ON_ESTIMATED_DELIVERY</v26:Events>
                            <v26:Events>ON_EXCEPTION</v26:Events>
                            <v26:Events>ON_SHIPMENT</v26:Events>
                            <v26:Events>ON_TENDER</v26:Events>
                            <v26:NotificationDetail>
                                <v26:NotificationType>EMAIL</v26:NotificationType>
                                <v26:EmailDetail>
                                    <v26:EmailAddress>Input Your Information</v26:EmailAddress>
                                    <v26:Name>Input Your Information</v26:Name>
                                </v26:EmailDetail>
                                <v26:Localization>
                                    <v26:LanguageCode>EN</v26:LanguageCode>
                                </v26:Localization>
                            </v26:NotificationDetail>
                            <v26:FormatSpecification>
                                <v26:Type>TEXT</v26:Type>
                            </v26:FormatSpecification>
                        </v26:EventNotifications>
                    </v26:EventNotificationDetail>
                </v26:SpecialServicesRequested>
                <v26:CustomsClearanceDetail>
                    <v26:DutiesPayment>
                        <v26:PaymentType>SENDER</v26:PaymentType>
                    </v26:DutiesPayment>
                    <v26:CustomsValue>
                        <v26:Currency>USD</v26:Currency>
                        <v26:Amount>100</v26:Amount>
                    </v26:CustomsValue>
                    <v26:Commodities>
                        <v26:NumberOfPieces>1</v26:NumberOfPieces>
                        <v26:Description>test</v26:Description>
                        <v26:Weight>
                            <v26:Units>LB</v26:Units>
                        </v26:Weight>
                        <v26:Quantity>1</v26:Quantity>
                        <v26:QuantityUnits>EA</v26:QuantityUnits>
                        <v26:UnitPrice>
                            <v26:Currency>USD</v26:Currency>
                        </v26:UnitPrice>
                    </v26:Commodities>
                </v26:CustomsClearanceDetail>
                <v26:LabelSpecification>
                    <v26:LabelFormatType>COMMON2D</v26:LabelFormatType>
                    <v26:ImageType>PDF</v26:ImageType>
                    <v26:LabelStockType>STOCK_4X6</v26:LabelStockType>
                    <v26:LabelPrintingOrientation>TOP_EDGE_OF_TEXT_FIRST</v26:LabelPrintingOrientation>
                    <v26:LabelOrder>SHIPPING_LABEL_FIRST</v26:LabelOrder>
                </v26:LabelSpecification>
                <v26:PackageCount>2</v26:PackageCount>
                <v26:RequestedPackageLineItems>
                    <v26:SequenceNumber>1</v26:SequenceNumber>
                    <v26:Weight>
                        <v26:Units>LB</v26:Units>
                        <v26:Value>1</v26:Value>
                    </v26:Weight>
                    <v26:Dimensions>
                        <v26:Length>12</v26:Length>
                        <v26:Width>12</v26:Width>
                        <v26:Height>12</v26:Height>
                        <v26:Units>IN</v26:Units>
                    </v26:Dimensions>
                    <v26:CustomerReferences>
                        <v26:CustomerReferenceType>CUSTOMER_REFERENCE</v26:CustomerReferenceType>
                        <v26:Value>#Order 11111</v26:Value>
                    </v26:CustomerReferences>
                </v26:RequestedPackageLineItems>
            </v26:RequestedShipment>
        </v26:ProcessShipmentRequest>
    </tns:Body>
</tns:Envelope>
"""

SecondPieceShipmentRequestXml = """<tns:Envelope xmlns:tns="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v26="http://fedex.com/ws/ship/v26">
    <tns:Body>
        <v26:ProcessShipmentRequest>
            <v26:WebAuthenticationDetail>
                <v26:UserCredential>
                    <v26:Key>user_key</v26:Key>
                    <v26:Password>password</v26:Password>
                </v26:UserCredential>
            </v26:WebAuthenticationDetail>
            <v26:ClientDetail>
                <v26:AccountNumber>2349857</v26:AccountNumber>
                <v26:MeterNumber>1293587</v26:MeterNumber>
            </v26:ClientDetail>
            <v26:TransactionDetail>
                <v26:CustomerTransactionId>IE_v26_Ship</v26:CustomerTransactionId>
            </v26:TransactionDetail>
            <v26:Version>
                <v26:ServiceId>ship</v26:ServiceId>
                <v26:Major>26</v26:Major>
                <v26:Intermediate>0</v26:Intermediate>
                <v26:Minor>0</v26:Minor>
            </v26:Version>
            <v26:RequestedShipment>

                <v26:DropoffType>REGULAR_PICKUP</v26:DropoffType>
                <v26:ServiceType>INTERNATIONAL_PRIORITY</v26:ServiceType>
                <v26:PackagingType>YOUR_PACKAGING</v26:PackagingType>
                <v26:TotalWeight>
                    <v26:Units>LB</v26:Units>
                    <v26:Value>3</v26:Value>
                </v26:TotalWeight>
                <v26:PreferredCurrency>USD</v26:PreferredCurrency>
                <v26:Shipper>
                    <v26:AccountNumber>2349857</v26:AccountNumber>
                    <v26:Contact>
                        <v26:PersonName>Input Your Information</v26:PersonName>
                        <v26:CompanyName>Input Your Information</v26:CompanyName>
                        <v26:PhoneNumber>Input Your Information</v26:PhoneNumber>
                        <v26:EMailAddress>Input Your Information</v26:EMailAddress>
                    </v26:Contact>
                    <v26:Address>
                        <v26:StreetLines>Input Your Information</v26:StreetLines>
                        <v26:StreetLines>Input Your Information</v26:StreetLines>
                        <v26:City>MEMPHIS</v26:City>
                        <v26:StateOrProvinceCode>TN</v26:StateOrProvinceCode>
                        <v26:PostalCode>38117</v26:PostalCode>
                        <v26:CountryCode>US</v26:CountryCode>
                        <v26:CountryName>United States</v26:CountryName>
                        <v26:Residential>false</v26:Residential>
                    </v26:Address>
                </v26:Shipper>
                <v26:Recipient>
                    <v26:Contact>
                        <v26:PersonName>Input Your Information</v26:PersonName>
                        <v26:CompanyName>Input Your Information</v26:CompanyName>
                        <v26:PhoneNumber>Input Your Information</v26:PhoneNumber>
                        <v26:EMailAddress>Input Your Information</v26:EMailAddress>
                    </v26:Contact>
                    <v26:Address>
                        <v26:StreetLines>Input Your Information</v26:StreetLines>
                        <v26:StreetLines>Input Your Information</v26:StreetLines>
                        <v26:City>RICHMOND</v26:City>
                        <v26:StateOrProvinceCode>BC</v26:StateOrProvinceCode>
                        <v26:PostalCode>V7C4v7</v26:PostalCode>
                        <v26:CountryCode>CA</v26:CountryCode>
                        <v26:CountryName>Canada</v26:CountryName>
                        <v26:Residential>false</v26:Residential>
                    </v26:Address>
                </v26:Recipient>
                <v26:ShippingChargesPayment>
                    <v26:PaymentType>THIRD_PARTY</v26:PaymentType>
                    <v26:Payor>
                        <v26:ResponsibleParty>
                            <v26:AccountNumber>2349857</v26:AccountNumber>
                        </v26:ResponsibleParty>
                    </v26:Payor>
                </v26:ShippingChargesPayment>
                <v26:SpecialServicesRequested>
                    <v26:EventNotificationDetail>
                        <v26:EventNotifications>
                            <v26:Events>ON_DELIVERY</v26:Events>
                            <v26:Events>ON_ESTIMATED_DELIVERY</v26:Events>
                            <v26:Events>ON_EXCEPTION</v26:Events>
                            <v26:Events>ON_SHIPMENT</v26:Events>
                            <v26:Events>ON_TENDER</v26:Events>
                            <v26:NotificationDetail>
                                <v26:NotificationType>EMAIL</v26:NotificationType>
                                <v26:EmailDetail>
                                    <v26:EmailAddress>Input Your Information</v26:EmailAddress>
                                    <v26:Name>Input Your Information</v26:Name>
                                </v26:EmailDetail>
                                <v26:Localization>
                                    <v26:LanguageCode>EN</v26:LanguageCode>
                                </v26:Localization>
                            </v26:NotificationDetail>
                            <v26:FormatSpecification>
                                <v26:Type>TEXT</v26:Type>
                            </v26:FormatSpecification>
                        </v26:EventNotifications>
                    </v26:EventNotificationDetail>
                </v26:SpecialServicesRequested>
                <v26:CustomsClearanceDetail>
                    <v26:DutiesPayment>
                        <v26:PaymentType>SENDER</v26:PaymentType>
                    </v26:DutiesPayment>
                    <v26:CustomsValue>
                        <v26:Currency>USD</v26:Currency>
                        <v26:Amount>100</v26:Amount>
                    </v26:CustomsValue>
                    <v26:Commodities>
                        <v26:NumberOfPieces>1</v26:NumberOfPieces>
                        <v26:Description>test</v26:Description>
                        <v26:Weight>
                            <v26:Units>LB</v26:Units>
                        </v26:Weight>
                        <v26:Quantity>1</v26:Quantity>
                        <v26:QuantityUnits>EA</v26:QuantityUnits>
                        <v26:UnitPrice>
                            <v26:Currency>USD</v26:Currency>
                        </v26:UnitPrice>
                    </v26:Commodities>
                </v26:CustomsClearanceDetail>
                <v26:LabelSpecification>
                    <v26:LabelFormatType>COMMON2D</v26:LabelFormatType>
                    <v26:ImageType>PDF</v26:ImageType>
                    <v26:LabelStockType>STOCK_4X6</v26:LabelStockType>
                    <v26:LabelPrintingOrientation>TOP_EDGE_OF_TEXT_FIRST</v26:LabelPrintingOrientation>
                    <v26:LabelOrder>SHIPPING_LABEL_FIRST</v26:LabelOrder>
                </v26:LabelSpecification>
                <v26:MasterTrackingId>
                    <v26:TrackingNumber>[MASTER_TRACKING_ID]</v26:TrackingNumber>
                </v26:MasterTrackingId>
                <v26:PackageCount>2</v26:PackageCount>
                <v26:RequestedPackageLineItems>
                    <v26:SequenceNumber>1</v26:SequenceNumber>
                    <v26:Weight>
                        <v26:Units>LB</v26:Units>
                        <v26:Value>2</v26:Value>
                    </v26:Weight>
                    <v26:Dimensions>
                        <v26:Length>11</v26:Length>
                        <v26:Width>11</v26:Width>
                        <v26:Height>11</v26:Height>
                        <v26:Units>IN</v26:Units>
                    </v26:Dimensions>
                    <v26:CustomerReferences>
                        <v26:CustomerReferenceType>CUSTOMER_REFERENCE</v26:CustomerReferenceType>
                        <v26:Value>#Order 11111</v26:Value>
                    </v26:CustomerReferences>
                </v26:RequestedPackageLineItems>
            </v26:RequestedShipment>
        </v26:ProcessShipmentRequest>
    </tns:Body>
</tns:Envelope>
"""

ShipmentResponseXML = """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
    <SOAP-ENV:Header/>
    <SOAP-ENV:Body>
        <ProcessShipmentReply xmlns="http://fedex.com/ws/ship/v26">
            <HighestSeverity>SUCCESS</HighestSeverity>
            <Notifications>
                <Severity>SUCCESS</Severity>
                <Source>ship</Source>
                <Code>0000</Code>
                <Message>Success</Message>
                <LocalizedMessage>Success</LocalizedMessage>
            </Notifications>
            <TransactionDetail>
                <CustomerTransactionId>IE_v18_Ship</CustomerTransactionId>
            </TransactionDetail>
            <Version>
                <ServiceId>ship</ServiceId>
                <Major>26</Major>
                <Intermediate>0</Intermediate>
                <Minor>0</Minor>
            </Version>
            <JobId>4cde266f831738s010fj248460</JobId>
            <CompletedShipmentDetail>
                <UsDomestic>false</UsDomestic>
                <CarrierCode>FDXE</CarrierCode>
                <MasterTrackingId>
                    <TrackingIdType>FEDEX</TrackingIdType>
                    <FormId>0430</FormId>
                    <TrackingNumber>794947717776</TrackingNumber>
                </MasterTrackingId>
                <ServiceDescription>
                    <ServiceType>INTERNATIONAL_PRIORITY</ServiceType>
                    <Code>01</Code>
                    <Names>
                        <Type>long</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>FedEx International Priority�</Value>
                    </Names>
                    <Names>
                        <Type>long</Type>
                        <Encoding>ascii</Encoding>
                        <Value>FedEx International Priority</Value>
                    </Names>
                    <Names>
                        <Type>medium</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>FedEx International Priority�</Value>
                    </Names>
                    <Names>
                        <Type>medium</Type>
                        <Encoding>ascii</Encoding>
                        <Value>FedEx International Priority</Value>
                    </Names>
                    <Names>
                        <Type>short</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>IP</Value>
                    </Names>
                    <Names>
                        <Type>short</Type>
                        <Encoding>ascii</Encoding>
                        <Value>IP</Value>
                    </Names>
                    <Names>
                        <Type>abbrv</Type>
                        <Encoding>ascii</Encoding>
                        <Value>IP</Value>
                    </Names>
                    <Description>International Priority</Description>
                    <AstraDescription>IP</AstraDescription>
                </ServiceDescription>
                <PackagingDescription>
                    <PackagingType>YOUR_PACKAGING</PackagingType>
                    <Code>01</Code>
                    <Names>
                        <Type>long</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>Your Packaging</Value>
                    </Names>
                    <Names>
                        <Type>long</Type>
                        <Encoding>ascii</Encoding>
                        <Value>Your Packaging</Value>
                    </Names>
                    <Names>
                        <Type>medium</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>Your Packaging</Value>
                    </Names>
                    <Names>
                        <Type>medium</Type>
                        <Encoding>ascii</Encoding>
                        <Value>Your Packaging</Value>
                    </Names>
                    <Names>
                        <Type>small</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>Your Pkg</Value>
                    </Names>
                    <Names>
                        <Type>small</Type>
                        <Encoding>ascii</Encoding>
                        <Value>Your Pkg</Value>
                    </Names>
                    <Names>
                        <Type>short</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>Your</Value>
                    </Names>
                    <Names>
                        <Type>short</Type>
                        <Encoding>ascii</Encoding>
                        <Value>Your</Value>
                    </Names>
                    <Names>
                        <Type>abbrv</Type>
                        <Encoding>ascii</Encoding>
                        <Value>YP</Value>
                    </Names>
                    <Description>Customer Packaging</Description>
                    <AstraDescription>CST PKG</AstraDescription>
                </PackagingDescription>
                <SpecialServiceDescriptions>
                    <Identifier>
                        <Id>EP1000000088</Id>
                        <Type>INTERNATIONAL_TRAFFIC_IN_ARMS_REGULATIONS</Type>
                        <Code>92</Code>
                    </Identifier>
                    <Names>
                        <Type>long</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>ITAR</Value>
                    </Names>
                    <Names>
                        <Type>long</Type>
                        <Encoding>ascii</Encoding>
                        <Value>ITAR</Value>
                    </Names>
                    <Names>
                        <Type>medium</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>ITAR</Value>
                    </Names>
                    <Names>
                        <Type>medium</Type>
                        <Encoding>ascii</Encoding>
                        <Value>ITAR</Value>
                    </Names>
                    <Names>
                        <Type>short</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>ITAR</Value>
                    </Names>
                    <Names>
                        <Type>short</Type>
                        <Encoding>ascii</Encoding>
                        <Value>ITAR</Value>
                    </Names>
                </SpecialServiceDescriptions>
                <SpecialServiceDescriptions>
                    <Identifier>
                        <Id>EP1000000060</Id>
                        <Type>DELIVER_WEEKDAY</Type>
                        <Code>02</Code>
                    </Identifier>
                    <Names>
                        <Type>long</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>Deliver Weekday</Value>
                    </Names>
                    <Names>
                        <Type>long</Type>
                        <Encoding>ascii</Encoding>
                        <Value>Deliver Weekday</Value>
                    </Names>
                    <Names>
                        <Type>medium</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>Deliver Weekday</Value>
                    </Names>
                    <Names>
                        <Type>medium</Type>
                        <Encoding>ascii</Encoding>
                        <Value>Deliver Weekday</Value>
                    </Names>
                    <Names>
                        <Type>short</Type>
                        <Encoding>utf-8</Encoding>
                        <Value>WDY</Value>
                    </Names>
                    <Names>
                        <Type>short</Type>
                        <Encoding>ascii</Encoding>
                        <Value>WDY</Value>
                    </Names>
                </SpecialServiceDescriptions>
                <OperationalDetail>
                    <UrsaPrefixCode>XQ</UrsaPrefixCode>
                    <UrsaSuffixCode>YVRA</UrsaSuffixCode>
                    <OriginLocationId>NQAA</OriginLocationId>
                    <OriginLocationNumber>0</OriginLocationNumber>
                    <OriginServiceArea>A1</OriginServiceArea>
                    <DestinationLocationId>YVRA</DestinationLocationId>
                    <DestinationLocationNumber>0</DestinationLocationNumber>
                    <DestinationServiceArea>AM</DestinationServiceArea>
                    <DestinationLocationStateOrProvinceCode>BC</DestinationLocationStateOrProvinceCode>
                    <IneligibleForMoneyBackGuarantee>false</IneligibleForMoneyBackGuarantee>
                    <AstraPlannedServiceLevel>AM</AstraPlannedServiceLevel>
                    <AstraDescription>INTL PRIORITY</AstraDescription>
                    <PostalCode>V7C4V7</PostalCode>
                    <StateOrProvinceCode>BC</StateOrProvinceCode>
                    <CountryCode>CA</CountryCode>
                    <AirportId>YVR</AirportId>
                    <ServiceCode>01</ServiceCode>
                    <PackagingCode>01</PackagingCode>
                </OperationalDetail>
                <ShipmentRating>
                    <ActualRateType>PAYOR_ACCOUNT_SHIPMENT</ActualRateType>
                    <ShipmentRateDetails>
                        <RateType>PAYOR_ACCOUNT_SHIPMENT</RateType>
                        <RateScale>0000000</RateScale>
                        <RateZone>US001O</RateZone>
                        <PricingCode>ACTUAL</PricingCode>
                        <RatedWeightMethod>ACTUAL</RatedWeightMethod>
                        <CurrencyExchangeRate>
                            <FromCurrency>USD</FromCurrency>
                            <IntoCurrency>USD</IntoCurrency>
                            <Rate>1.0</Rate>
                        </CurrencyExchangeRate>
                        <DimDivisor>139</DimDivisor>
                        <DimDivisorType>COUNTRY</DimDivisorType>
                        <FuelSurchargePercent>16.5</FuelSurchargePercent>
                        <TotalBillingWeight>
                            <Units>LB</Units>
                            <Value>20.0</Value>
                        </TotalBillingWeight>
                        <TotalBaseCharge>
                            <Currency>USD</Currency>
                            <Amount>215.83</Amount>
                        </TotalBaseCharge>
                        <TotalFreightDiscounts>
                            <Currency>USD</Currency>
                            <Amount>0.0</Amount>
                        </TotalFreightDiscounts>
                        <TotalNetFreight>
                            <Currency>USD</Currency>
                            <Amount>215.83</Amount>
                        </TotalNetFreight>
                        <TotalSurcharges>
                            <Currency>USD</Currency>
                            <Amount>35.61</Amount>
                        </TotalSurcharges>
                        <TotalNetFedExCharge>
                            <Currency>USD</Currency>
                            <Amount>261.44</Amount>
                        </TotalNetFedExCharge>
                        <TotalTaxes>
                            <Currency>USD</Currency>
                            <Amount>0.0</Amount>
                        </TotalTaxes>
                        <TotalNetCharge>
                            <Currency>USD</Currency>
                            <Amount>261.44</Amount>
                        </TotalNetCharge>
                        <TotalRebates>
                            <Currency>USD</Currency>
                            <Amount>0.0</Amount>
                        </TotalRebates>
                        <TotalDutiesAndTaxes>
                            <Currency>USD</Currency>
                            <Amount>0.0</Amount>
                        </TotalDutiesAndTaxes>
                        <TotalAncillaryFeesAndTaxes>
                            <Currency>USD</Currency>
                            <Amount>0.0</Amount>
                        </TotalAncillaryFeesAndTaxes>
                        <TotalDutiesTaxesAndFees>
                            <Currency>USD</Currency>
                            <Amount>0.0</Amount>
                        </TotalDutiesTaxesAndFees>
                        <TotalNetChargeWithDutiesAndTaxes>
                            <Currency>USD</Currency>
                            <Amount>261.44</Amount>
                        </TotalNetChargeWithDutiesAndTaxes>
                        <Surcharges>
                            <SurchargeType>FUEL</SurchargeType>
                            <Description>Fuel</Description>
                            <Amount>
                                <Currency>USD</Currency>
                                <Amount>35.61</Amount>
                            </Amount>
                        </Surcharges>
                    </ShipmentRateDetails>
                    <ShipmentRateDetails>
                        <RateType>PAYOR_LIST_SHIPMENT</RateType>
                        <RateScale>0000000</RateScale>
                        <RateZone>US001O</RateZone>
                        <PricingCode>ACTUAL</PricingCode>
                        <RatedWeightMethod>ACTUAL</RatedWeightMethod>
                        <CurrencyExchangeRate>
                            <FromCurrency>USD</FromCurrency>
                            <IntoCurrency>USD</IntoCurrency>
                            <Rate>1.0</Rate>
                        </CurrencyExchangeRate>
                        <DimDivisor>139</DimDivisor>
                        <DimDivisorType>COUNTRY</DimDivisorType>
                        <FuelSurchargePercent>5.0</FuelSurchargePercent>
                        <TotalBillingWeight>
                            <Units>LB</Units>
                            <Value>20.0</Value>
                        </TotalBillingWeight>
                        <TotalBaseCharge>
                            <Currency>USD</Currency>
                            <Amount>215.83</Amount>
                        </TotalBaseCharge>
                        <TotalFreightDiscounts>
                            <Currency>USD</Currency>
                            <Amount>0.0</Amount>
                        </TotalFreightDiscounts>
                        <TotalNetFreight>
                            <Currency>USD</Currency>
                            <Amount>215.83</Amount>
                        </TotalNetFreight>
                        <TotalSurcharges>
                            <Currency>USD</Currency>
                            <Amount>10.79</Amount>
                        </TotalSurcharges>
                        <TotalNetFedExCharge>
                            <Currency>USD</Currency>
                            <Amount>226.62</Amount>
                        </TotalNetFedExCharge>
                        <TotalTaxes>
                            <Currency>USD</Currency>
                            <Amount>0.0</Amount>
                        </TotalTaxes>
                        <TotalNetCharge>
                            <Currency>USD</Currency>
                            <Amount>226.62</Amount>
                        </TotalNetCharge>
                        <TotalRebates>
                            <Currency>USD</Currency>
                            <Amount>0.0</Amount>
                        </TotalRebates>
                        <TotalDutiesAndTaxes>
                            <Currency>USD</Currency>
                            <Amount>0.0</Amount>
                        </TotalDutiesAndTaxes>
                        <TotalAncillaryFeesAndTaxes>
                            <Currency>USD</Currency>
                            <Amount>0.0</Amount>
                        </TotalAncillaryFeesAndTaxes>
                        <TotalDutiesTaxesAndFees>
                            <Currency>USD</Currency>
                            <Amount>0.0</Amount>
                        </TotalDutiesTaxesAndFees>
                        <TotalNetChargeWithDutiesAndTaxes>
                            <Currency>USD</Currency>
                            <Amount>226.62</Amount>
                        </TotalNetChargeWithDutiesAndTaxes>
                        <Surcharges>
                            <SurchargeType>FUEL</SurchargeType>
                            <Description>Fuel</Description>
                            <Amount>
                                <Currency>USD</Currency>
                                <Amount>10.79</Amount>
                            </Amount>
                        </Surcharges>
                    </ShipmentRateDetails>
                </ShipmentRating>
                <ExportComplianceStatement>NO EEI 30.37(f)</ExportComplianceStatement>
                <DocumentRequirements>
                    <RequiredDocuments>COMMERCIAL_OR_PRO_FORMA_INVOICE</RequiredDocuments>
                    <RequiredDocuments>AIR_WAYBILL</RequiredDocuments>
                    <GenerationDetails>
                        <Type>COMMERCIAL_INVOICE</Type>
                        <MinimumCopiesRequired>3</MinimumCopiesRequired>
                        <Letterhead>OPTIONAL</Letterhead>
                        <ElectronicSignature>OPTIONAL</ElectronicSignature>
                    </GenerationDetails>
                    <GenerationDetails>
                        <Type>PRO_FORMA_INVOICE</Type>
                        <MinimumCopiesRequired>3</MinimumCopiesRequired>
                        <Letterhead>OPTIONAL</Letterhead>
                        <ElectronicSignature>OPTIONAL</ElectronicSignature>
                    </GenerationDetails>
                    <GenerationDetails>
                        <Type>AIR_WAYBILL</Type>
                        <MinimumCopiesRequired>3</MinimumCopiesRequired>
                    </GenerationDetails>
                </DocumentRequirements>
                <ShipmentDocuments>
                    <Type>COMMERCIAL_INVOICE</Type>
                    <ShippingDocumentDisposition>RETURNED</ShippingDocumentDisposition>
                    <ImageType>PDF</ImageType>
                    <Resolution>200</Resolution>
                    <CopiesToPrint>3</CopiesToPrint>
                    <Parts>
                        <DocumentPartSequenceNumber>1</DocumentPartSequenceNumber>
                        <Image>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UHJvY1NldFsvUERGXT4+L0JCb3hbMCAwIDI3OC4xOTQgOS4yNV0vTGVuZ3RoIDI3Pj5zdHJlYW0KMSBnCjAgMCAyNzguMTkzOCA5LjI1IHJlCmYKCmVuZHN0cmVhbQplbmRvYmoKNDggMCBvYmogPDwvU3VidHlwZS9Gb3JtL01hdHJpeFsxIDAgMCAxIDAgMF0vVHlwZS9YT2JqZWN0L0Zvcm1UeXBlIDEvUmVzb3VyY2VzPDwvUHJvY1NldFsvUERGXT4+L0JCb3hbMCAwIDI1Ni43MTggOS4yNV0vTGVuZ3RoIDI3Pj5zdHJlYW0KMSBnCjAgMCAyNTYuNzE4MiA5LjI1IHJlCmYKCmVuZHN0cmVhbQplbmRvYmoKNTIgMCBvYmogPDwvU3VidHlwZS9Gb3JtL01hdHJpeFsxIDAgMCAxIDAgMF0vVHlwZS9YT2JqZWN0L0Zvcm1UeXBlIDEvUmVzb3VyY2VzPDwvUHJvY1NldFsvUERGXT4+L0JCb3hbMCAwIDIzOS45MDUgMTAuMzcxXS9MZW5ndGggMjk+PnN0cmVhbQoxIGcKMCAwIDIzOS45MDUxIDEwLjM3MSByZQpmCgplbmRzdHJlYW0KZW5kb2JqCjUzIDAgb2JqIDw8L1N1YnR5cGUvRm9ybS9NYXRyaXhbMSAwIDAgMSAwIDBdL1R5cGUvWE9iamVjdC9Gb3JtVHlwZSAxL1Jlc291cmNlczw8L1Byb2NTZXRbL1BERl0+Pi9CQm94WzAgMCAxNzUuMjQ5IDguOTY1MDNdL0xlbmd0aCAyOD4+c3RyZWFtCjEgZwowIDAgMTc1LjI0OTIgOC45NjUgcmUKZgoKZW5kc3RyZWFtCmVuZG9iago1OSAwIG9iaiA8PC9TdWJ0eXBlL0Zvcm0vTWF0cml4WzEgMCAwIDEgMCAwXS9UeXBlL1hPYmplY3QvRm9ybVR5cGUgMS9SZXNvdXJjZXM8PC9Qcm9jU2V0Wy9QREZdPj4vQkJveFswIDAgMTIzLjkzNCAxMC4yMTQxXS9MZW5ndGggMjk+PnN0cmVhbQoxIGcKMCAwIDEyMy45MzQgMTAuMjE0MSByZQpmCgplbmRzdHJlYW0KZW5kb2JqCjYxIDAgb2JqIDw8L1N1YnR5cGUvRm9ybS9NYXRyaXhbMSAwIDAgMSAwIDBdL1R5cGUvWE9iamVjdC9Gb3JtVHlwZSAxL1Jlc291cmNlczw8L1Byb2NTZXRbL1BERl0+Pi9CQm94WzAgMCAyNTYuMjAyIDkuMjVdL0xlbmd0aCAyNz4+c3RyZWFtCjEgZwowIDAgMjU2LjIwMjMgOS4yNSByZQpmCgplbmRzdHJlYW0KZW5kb2JqCjYyIDAgb2JqIDw8L1N1YnR5cGUvRm9ybS9NYXRyaXhbMSAwIDAgMSAwIDBdL1R5cGUvWE9iamVjdC9Gb3JtVHlwZSAxL1Jlc291cmNlczw8L1Byb2NTZXRbL1BERl0+Pi9CQm94WzAgMCAxNTMuNjIzIDE5LjU0OV0vTGVuZ3RoIDI4Pj5zdHJlYW0KMSBnCjAgMCAxNTMuNjIzIDE5LjU0OSByZQpmCgplbmRzdHJlYW0KZW5kb2JqCjY4IDAgb2JqIDw8L1N1YnR5cGUvRm9ybS9NYXRyaXhbMSAwIDAgMSAwIDBdL1R5cGUvWE9iamVjdC9Gb3JtVHlwZSAxL1Jlc291cmNlczw8L1Byb2NTZXRbL1BERl0+Pi9CQm94WzAgMCAyNzguMTk0IDkuMjVdL0xlbmd0aCAyNz4+c3RyZWFtCjEgZwowIDAgMjc4LjE5MzggOS4yNSByZQpmCgplbmRzdHJlYW0KZW5kb2JqCjcxIDAgb2JqIDw8L1N1YnR5cGUvRm9ybS9NYXRyaXhbMSAwIDAgMSAwIDBdL1R5cGUvWE9iamVjdC9Gb3JtVHlwZSAxL1Jlc291cmNlczw8L1Byb2NTZXRbL1BERl0+Pi9CQm94WzAgMCAyMjYuMjk5IDcuOTI2OTRdL0xlbmd0aCAyOT4+c3RyZWFtCjEgZwowIDAgMjI2LjI5ODggNy45MjY5IHJlCmYKCmVuZHN0cmVhbQplbmRvYmoKNzIgMCBvYmogPDwvU3VidHlwZS9Gb3JtL01hdHJpeFsxIDAgMCAxIDAgMF0vVHlwZS9YT2JqZWN0L0Zvcm1UeXBlIDEvUmVzb3VyY2VzPDwvUHJvY1NldFsvUERGXT4+L0JCb3hbMCAwIDI3OC4xMTIgOS4yNV0vTGVuZ3RoIDI2Pj5zdHJlYW0KMSBnCjAgMCAyNzguMTEyIDkuMjUgcmUKZgoKZW5kc3RyZWFtCmVuZG9iago3NCAwIG9iaiA8PC9TdWJ0eXBlL0Zvcm0vTWF0cml4WzEgMCAwIDEgMCAwXS9UeXBlL1hPYmplY3QvRm9ybVR5cGUgMS9SZXNvdXJjZXM8PC9Qcm9jU2V0Wy9QREZdPj4vQkJveFswIDAgMTU5Ljk5MiAzMi41MjVdL0xlbmd0aCAyOT4+c3RyZWFtCjEgZwowIDAgMTU5Ljk5MTkgMzIuNTI1IHJlCmYKCmVuZHN0cmVhbQplbmRvYmoKNzkgMCBvYmogPDwvU3VidHlwZS9Gb3JtL01hdHJpeFsxIDAgMCAxIDAgMF0vVHlwZS9YT2JqZWN0L0Zvcm1UeXBlIDEvUmVzb3VyY2VzPDwvUHJvY1NldFsvUERGXT4+L0JCb3hbMCAwIDI3OC4xOTQgOS4yNV0vTGVuZ3RoIDI3Pj5zdHJlYW0KMSBnCjAgMCAyNzguMTkzOCA5LjI1IHJlCmYKCmVuZHN0cmVhbQplbmRvYmoKODcgMCBvYmogPDwvU3VidHlwZS9Gb3JtL01hdHJpeFsxIDAgMCAxIDAgMF0vVHlwZS9YT2JqZWN0L0Zvcm1UeXBlIDEvUmVzb3VyY2VzPDwvUHJvY1NldFsvUERGXT4+L0JCb3hbMCAwIDY3LjI1IDE1Ljc0Nl0vTGVuZ3RoIDI2Pj5zdHJlYW0KMSBnCjAgMCA2Ny4yNSAxNS43NDYgcmUKZgoKZW5kc3RyZWFtCmVuZG9iago4OCAwIG9iaiA8PC9TdWJ0eXBlL0Zvcm0vTWF0cml4WzEgMCAwIDEgMCAwXS9UeXBlL1hPYmplY3QvRm9ybVR5cGUgMS9SZXNvdXJjZXM8PC9Qcm9jU2V0Wy9QREZdPj4vQkJveFswIDAgODguMTIzIDguOTY1MDNdL0xlbmd0aCAyNj4+c3RyZWFtCjEgZwowIDAgODguMTIzIDguOTY1IHJlCmYKCmVuZHN0cmVhbQplbmRvYmoKOTEgMCBvYmogPDwvU3VidHlwZS9Gb3JtL01hdHJpeFsxIDAgMCAxIDAgMF0vVHlwZS9YT2JqZWN0L0Zvcm1UeXBlIDEvUmVzb3VyY2VzPDwvUHJvY1NldFsvUERGXT4+L0JCb3hbMCAwIDE2MC42MjMgOS4zNDAwM10vTGVuZ3RoIDI2Pj5zdHJlYW0KMSBnCjAgMCAxNjAuNjIzIDkuMzQgcmUKZgoKZW5kc3RyZWFtCmVuZG9iago5NCAwIG9iaiA8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</Image>
                    </Parts>
                </ShipmentDocuments>
                <CompletedPackageDetails>
                    <SequenceNumber>1</SequenceNumber>
                    <TrackingIds>
                        <TrackingIdType>FEDEX</TrackingIdType>
                        <FormId>0430</FormId>
                        <TrackingNumber>794947717776</TrackingNumber>
                    </TrackingIds>
                    <GroupNumber>0</GroupNumber>
                    <OperationalDetail>
                        <AstraHandlingText>ITAR</AstraHandlingText>
                        <OperationalInstructions>
                            <Number>2</Number>
                            <Content>TRK#</Content>
                        </OperationalInstructions>
                        <OperationalInstructions>
                            <Number>3</Number>
                            <Content>0430</Content>
                        </OperationalInstructions>
                        <OperationalInstructions>
                            <Number>5</Number>
                            <Content>XQ YVRA</Content>
                        </OperationalInstructions>
                        <OperationalInstructions>
                            <Number>7</Number>
                            <Content>1017547653890652726300794947717776</Content>
                        </OperationalInstructions>
                        <OperationalInstructions>
                            <Number>8</Number>
                            <Content>567J2/BE80/05A2</Content>
                        </OperationalInstructions>
                        <OperationalInstructions>
                            <Number>10</Number>
                            <Content>7949 4771 7776</Content>
                        </OperationalInstructions>
                        <OperationalInstructions>
                            <Number>12</Number>
                            <Content>AM</Content>
                        </OperationalInstructions>
                        <OperationalInstructions>
                            <Number>13</Number>
                            <Content>INTL PRIORITY</Content>
                        </OperationalInstructions>
                        <OperationalInstructions>
                            <Number>14</Number>
                            <Content>ITAR</Content>
                        </OperationalInstructions>
                        <OperationalInstructions>
                            <Number>15</Number>
                            <Content>V7C 4V7</Content>
                        </OperationalInstructions>
                        <OperationalInstructions>
                            <Number>16</Number>
                            <Content>BC-CA</Content>
                        </OperationalInstructions>
                        <OperationalInstructions>
                            <Number>17</Number>
                            <Content>YVR</Content>
                        </OperationalInstructions>
                        <Barcodes>
                            <BinaryBarcodes>
                                <Type>COMMON_2D</Type>
                                <Value>Wyk+HjAxHTAyVjdDNFY3HTEyNB0wMR03OTQ5NDc3MTc3NzYwNDMwHUZERR0xNTAwNjc2MDAdMjA2HR0xLzEdMjAuMDBMQh1OHVRlc3QgUmVjaXBpZW50IEFkZHJlc3MgTGluZTUdUklDSE1PTkQdQkMdQU5DHjA2HTEwWkVJTzA2HTExWlhUWUlVRx0xMlo5ODIyMjg3NzIxHTE0WlRlc3QgUmVjaXBpZW50IEFkZHJlc3MgTGluZTYdMTVaNzAwMzA0Mx0zMVoxMDE3NTQ3NjUzODkwNjUyNzI1MzAwNzk0OTQ3NzE3Nzc2HTMyWjAyOTIdMzlaTlFBQR05OVpFSTAwMDccVVMcMTM0HENBRBxBQkNEHE5PIEVFSSAzMC4zNyhmKRwcMTUwMDY3NjAwHR4wOR1GRFgdeh04HSsuCCAjDn9AHgQ=</Value>
                            </BinaryBarcodes>
                            <StringBarcodes>
                                <Type>FEDEX_1D</Type>
                                <Value>1017547653890652726300794947717776</Value>
                            </StringBarcodes>
                        </Barcodes>
                    </OperationalDetail>
                    <Label>
                        <Type>OUTBOUND_LABEL</Type>
                        <ShippingDocumentDisposition>RETURNED</ShippingDocumentDisposition>
                        <ImageType>PNG</ImageType>
                        <Resolution>200</Resolution>
                        <CopiesToPrint>1</CopiesToPrint>
                        <Parts>
                            <DocumentPartSequenceNumber>1</DocumentPartSequenceNumber>
                            <Image>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O1N4O3ncO+H9r4+M9989Mt6vCryJ+9yGZ+g3l9fQtZrM3W543xd479Ob+/uf/O8X1s+//OaHwf1NsGe8sMj7cHf3zcNvvoYnv/rmLvj7d+f7znsPV4j3d/Dk/PX9HvBmrz59uf705Z98+rKa9+4e3tznvN/Av4c75/2TJ8/ef+vlH37ro6CSN/7ncHn/8EvM+2ffOF/vnvePvvvZH333Z3/73c+qedf/2Xt3f//LX8P/jnhffQ13fd6yP/7wsz/+7mebv3v7L/+yUh7+9ubd/fp/PbXeIN7N19nOeV85n7168u9f1/HC39yd39+h53tw/mf3D+9O4M55z/7Zqz//j6++/PzLet6bL7D8/uv7h/Cnu+b97atf/+mrv3v7w89/9uX/rOV9x3jf/WT3vP/0T19997Na3rvf3AU/Oae83zyc/7dd88avnnxn/eSjP3zy0feuKnm/QrwB5v3V17+7P/8vo/MWXsn6L54he3HxrY/+VeU6jfvPb4J/A7/4Gv78y69/+Op8sWve1kj70Av+rXX0wrq8fueeBZVXGu0T787934l34p14J96Jd+KdeCfeiXfinXgn3ol34p14J96Jd+KdeCfeiXfinXgn3ol34p14J96Jd+KdeCfeiXfinXgn3ol34p14J96Jd+KdeCfeiXfinXgn3ol34p14J96Jd+KdeCfeiXfinXgn3ol34p14J96Jd+KdeCfeiXfinXgn3ol34p14J96Jd+KdeCfeiXfinXgn3ol34p14J96Jd+KdeCfeiXfinXgn3ol34p14J96Jd+KdeCde/vq/IYsam1SzVhkAAAAASUVORK5CYII=</Image>
                        </Parts>
                    </Label>
                    <PackageDocuments>
                        <Type>AUXILIARY_LABEL</Type>
                        <ShippingDocumentDisposition>RETURNED</ShippingDocumentDisposition>
                        <AccessReference>AWB-2DCommon</AccessReference>
                        <ImageType>PNG</ImageType>
                        <Resolution>200</Resolution>
                        <CopiesToPrint>3</CopiesToPrint>
                        <Parts>
                            <DocumentPartSequenceNumber>1</DocumentPartSequenceNumber>
                            <Image>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</Image>
                        </Parts>
                    </PackageDocuments>
                    <SignatureOption>SERVICE_DEFAULT</SignatureOption>
                </CompletedPackageDetails>
            </CompletedShipmentDetail>
        </ProcessShipmentReply>
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""

ShipmentCancelRequestXML = """<tns:Envelope xmlns:tns="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v23="http://fedex.com/ws/ship/v23">
    <tns:Body>
        <v23:DeleteShipmentRequest>
            <v23:WebAuthenticationDetail>
                <v23:UserCredential>
                    <v23:Key>user_key</v23:Key>
                    <v23:Password>password</v23:Password>
                </v23:UserCredential>
            </v23:WebAuthenticationDetail>
            <v23:ClientDetail>
                <v23:AccountNumber>2349857</v23:AccountNumber>
                <v23:MeterNumber>1293587</v23:MeterNumber>
            </v23:ClientDetail>
            <v23:TransactionDetail>
                <v23:CustomerTransactionId>Delete Shipment</v23:CustomerTransactionId>
            </v23:TransactionDetail>
            <v23:Version>
                <v23:ServiceId>ship</v23:ServiceId>
                <v23:Major>23</v23:Major>
                <v23:Intermediate>0</v23:Intermediate>
                <v23:Minor>0</v23:Minor>
            </v23:Version>
            <v23:TrackingId>
                <v23:TrackingIdType>EXPRESS</v23:TrackingIdType>
                <v23:TrackingNumber>794947717776</v23:TrackingNumber>
            </v23:TrackingId>
            <v23:DeletionControl>DELETE_ALL_PACKAGES</v23:DeletionControl>
        </v23:DeleteShipmentRequest>
    </tns:Body>
</tns:Envelope>
"""

ShipmentCancelResponseXML = """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
   <SOAP-ENV:Header/>
   <SOAP-ENV:Body>
      <ShipmentReply xmlns="http://fedex.com/ws/ship/v26">
         <HighestSeverity>SUCCESS</HighestSeverity>
         <Notifications>
            <Severity>SUCCESS</Severity>
            <Source>ship</Source>
            <Code>0000</Code>
            <Message>Success</Message>
            <LocalizedMessage>Success</LocalizedMessage>
         </Notifications>
         <TransactionDetail>
            <CustomerTransactionId>DeleteShipmentRequest_v26</CustomerTransactionId>
         </TransactionDetail>
         <Version>
            <ServiceId>ship</ServiceId>
            <Major>26</Major>
            <Intermediate>0</Intermediate>
            <Minor>0</Minor>
         </Version>
      </ShipmentReply>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""
