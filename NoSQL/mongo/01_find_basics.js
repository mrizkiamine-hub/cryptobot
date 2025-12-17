use("cryptobot");

// 1) Find all (preview)
print("=== Find 5 docs ===");
db.ohlcv.find({}).limit(5).forEach(doc => printjson(doc));

// 2) Find exact open_time example
print("=== Find exact open_time ===");
db.ohlcv.find({ open_time: "2025-09-01 00:00:00" }).limit(5).forEach(doc => printjson(doc));
