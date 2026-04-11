#!/bin/bash
# apply_patches.sh — Patches Freqtrade to support Interactive Brokers exchange
# Run inside the Freqtrade Docker container during build
set -e

EXCHANGE_DIR="/freqtrade/freqtrade/exchange"
WEBSERVER="/freqtrade/freqtrade/rpc/api_server/webserver.py"

echo "📦 Applying IB addon patches..."

# 1. Copy exchange files
cp /patches/interactivebrokers.py "$EXCHANGE_DIR/"
cp /patches/foreignexchange.py "$EXCHANGE_DIR/"
echo "  ✅ Exchange files copied"

# 2. Register imports in exchange/__init__.py
INIT_FILE="$EXCHANGE_DIR/__init__.py"
if ! grep -q "Foreignexchange" "$INIT_FILE"; then
    echo "from freqtrade.exchange.foreignexchange import Foreignexchange" >> "$INIT_FILE"
    echo "  ✅ Foreignexchange import added"
fi
if ! grep -q "Interactivebrokers" "$INIT_FILE"; then
    echo "from freqtrade.exchange.interactivebrokers import Interactivebrokers" >> "$INIT_FILE"
    echo "  ✅ Interactivebrokers import added"
fi

# 2.5 Bypass CCXT validation for IB
CHECK_EXCHANGE="/freqtrade/freqtrade/exchange/check_exchange.py"
sed -i 's/if not is_exchange_known_ccxt(exchange):/if not is_exchange_known_ccxt(exchange) and exchange != "interactivebrokers":/' "$CHECK_EXCHANGE"
sed -i 's/valid, reason, _, _ = validate_exchange(exchange)/if exchange == "interactivebrokers":\n        valid, reason, _, _ = True, "", None, None\n    else:\n        valid, reason, _, _ = validate_exchange(exchange)/' "$CHECK_EXCHANGE"
echo "  ✅ Bypassed CCXT validation for interactivebrokers"

# 3. Fix FastAPI lifespan (add_event_handler deprecated in newer Starlette)
if grep -q "add_event_handler" "$WEBSERVER" 2>/dev/null; then
    echo "  🔧 Patching webserver.py for FastAPI lifespan..."

    # Add import
    sed -i '1s/^/from contextlib import asynccontextmanager\n/' "$WEBSERVER"

    # Add lifespan parameter to FastAPI() constructor
    sed -i 's/openapi_tags=_OPENAPI_TAGS,/openapi_tags=_OPENAPI_TAGS,\n            lifespan=self._lifespan,/' "$WEBSERVER"

    # Remove old event handlers and replace with lifespan
    # This is a sed-based approach; for robustness, a Python script could be used
    sed -i '/app.add_event_handler.*startup.*_api_startup_event/d' "$WEBSERVER"
    sed -i '/app.add_event_handler.*shutdown.*_api_shutdown_event/d' "$WEBSERVER"

    # Replace startup method with lifespan context manager
    python3 -c "
import re
with open('$WEBSERVER', 'r') as f:
    content = f.read()

# Replace the old startup/shutdown methods with a lifespan context manager
old_startup = r'    async def _api_startup_event\(self\):.*?ApiServer\._message_stream = MessageStream\(\)'
old_shutdown = r'    async def _api_shutdown_event\(self\):.*?ApiServer\._message_stream = None'

new_lifespan = '''    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        \"\"\"
        Lifespan context manager for FastAPI.
        Replaces deprecated add_event_handler for startup/shutdown.
        \"\"\"
        # Startup
        if not ApiServer._message_stream:
            ApiServer._message_stream = MessageStream()
        yield
        # Shutdown
        if ApiServer._message_stream:
            ApiServer._message_stream = None'''

content = re.sub(old_startup, new_lifespan, content, flags=re.DOTALL)
content = re.sub(old_shutdown, '', content, flags=re.DOTALL)

with open('$WEBSERVER', 'w') as f:
    f.write(content)
"
    echo "  ✅ webserver.py patched"
else
    echo "  ℹ️  webserver.py already patched or different version, skipping"
fi

echo "✅ All patches applied successfully!"
