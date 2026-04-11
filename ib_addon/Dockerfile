# Freqtrade + Interactive Brokers — Multi-Asset Addon
# ===================================================
# Extends official Freqtrade Docker image with IB Gateway support
# for Forex, US Stocks, and Futures (CME/CBOT/COMEX/NYMEX).

FROM freqtradeorg/freqtrade:stable

# Install IB connector dependency
RUN pip install --no-cache-dir ib_insync

# Switch to root to copy and modify files
USER root

# Copy exchange connector files
COPY patches/interactivebrokers.py /patches/
COPY patches/foreignexchange.py /patches/
COPY patches/apply_patches.sh /patches/

# Apply patches at build time
RUN chmod +x /patches/apply_patches.sh && bash /patches/apply_patches.sh

# Cleanup
RUN rm -rf /patches

# Switch back to the default non-root user
USER ftuser
