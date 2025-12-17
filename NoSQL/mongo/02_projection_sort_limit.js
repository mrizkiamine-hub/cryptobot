use("cryptobot");

// Projection
print("=== Projection open_time, close, volume_base ===");
db.ohlcv.find(
  {},
  { _id: 0, open_time: 1, close_time: 1, close: 1, volume_base: 1 }
).limit(10).forEach(doc => printjson(doc));

// Sort by open_time desc
print("=== Sort by open_time DESC (latest first) ===");
db.ohlcv.find(
  {},
  { _id: 0, open_time: 1, close: 1 }
).sort({ open_time: -1 }).limit(10).forEach(doc => printjson(doc));
