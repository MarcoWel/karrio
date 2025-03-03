SCHEMAS=./vendor/schemas
LIB_MODULES=./eshipper_lib
find "${LIB_MODULES}" -name "*.py" -exec rm -r {} \;
touch "${LIB_MODULES}/__init__.py"

generateDS --no-namespace-defs -o "${LIB_MODULES}/quote_request.py" $SCHEMAS/quote_request.xsd
generateDS --no-namespace-defs -o "${LIB_MODULES}/quote_reply.py" $SCHEMAS/quote_reply.xsd
generateDS --no-namespace-defs -o "${LIB_MODULES}/shipping_request.py" $SCHEMAS/shipping_request.xsd
generateDS --no-namespace-defs -o "${LIB_MODULES}/shipping_reply.py" $SCHEMAS/shipping_reply.xsd
generateDS --no-namespace-defs -o "${LIB_MODULES}/error.py" $SCHEMAS/error.xsd
generateDS --no-namespace-defs -o "${LIB_MODULES}/shipment_cancel_request.py" $SCHEMAS/shipment_cancel_request.xsd
generateDS --no-namespace-defs -o "${LIB_MODULES}/shipment_cancel_reply.py" $SCHEMAS/shipment_cancel_reply.xsd
