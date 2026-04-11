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
sed -i 's/if not is_exchange_officially_supported(exchange):/if not is_exchange_officially_supported(exchange) and exchange != "interactivebrokers":/' "$CHECK_EXCHANGE"
echo "  ✅ Bypassed CCXT validation for interactivebrokers"



echo "✅ All patches applied successfully!"
