use("cryptobot");

// Recommended indexes (speed up sorts/filters)
print("=== Creating indexes ===");

// For time sorting
db.ohlcv.createIndex({ open_time: -1 });

// For top volume queries
db.ohlcv.createIndex({ volume_base: -1 });

// If later you add symbol/interval fields, this is a classic:
 // db.ohlcv.createIndex({ symbol: 1, interval: 1, open_time: -1 });

print("Indexes created.");
