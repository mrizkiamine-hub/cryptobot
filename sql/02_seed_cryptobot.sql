-- ==========================================
-- 02_seed_cryptobot.sql
-- Initialisation des dimensions CryptoBot
-- ==========================================
-- Objectif :
--  - Initialiser les tables de dimensions
--  - Script idempotent (relançable sans effet de bord)
--  - Compatible avec les scripts Python d’ingestion
-- ==========================================

BEGIN;

-- ==========================================================
-- DIMENSION : ASSET
-- ==========================================================
INSERT INTO cryptobot.dim_asset (symbol, name)
VALUES
    ('BTC',  'Bitcoin'),
    ('ETH',  'Ethereum'),
    ('USDT', 'Tether')
ON CONFLICT (symbol) DO NOTHING;

-- ==========================================================
-- DIMENSION : INTERVAL
-- ==========================================================
INSERT INTO cryptobot.dim_interval (interval_code, seconds)
VALUES
    ('1h', 3600),
    ('4h', 14400)
ON CONFLICT (interval_code) DO NOTHING;

-- ==========================================================
-- DIMENSION : MARKET
-- ==========================================================
INSERT INTO cryptobot.dim_market (
    symbol,
    base_asset_id,
    quote_asset_id,
    exchange
)
VALUES
    (
        'BTCUSDT',
        (SELECT id FROM cryptobot.dim_asset WHERE symbol = 'BTC'),
        (SELECT id FROM cryptobot.dim_asset WHERE symbol = 'USDT'),
        'BINANCE'
    ),
    (
        'ETHUSDT',
        (SELECT id FROM cryptobot.dim_asset WHERE symbol = 'ETH'),
        (SELECT id FROM cryptobot.dim_asset WHERE symbol = 'USDT'),
        'BINANCE'
    ),
    (
        'ETHBTC',
        (SELECT id FROM cryptobot.dim_asset WHERE symbol = 'ETH'),
        (SELECT id FROM cryptobot.dim_asset WHERE symbol = 'BTC'),
        'BINANCE'
    )
ON CONFLICT (symbol) DO NOTHING;

COMMIT;

-- ==========================================
-- Fin du seed CryptoBot
-- ==========================================
