use("cryptobot");

// Total docs
print("=== Count all docs ===");
print(db.ohlcv.countDocuments({}));

// Missing fields checks
print("=== Missing close field ===");
print(db.ohlcv.countDocuments({ close: { $exists: false } }));

print("=== Missing volume_base field ===");
print(db.ohlcv.countDocuments({ volume_base: { $exists: false } }));

// Duplicates check on open_time (simple indicator)
print("=== Potential duplicates by open_time (top 10) ===");
db.ohlcv.aggregate([
  { $group: { _id: "$open_time", n: { $sum: 1 } } },
  { $match: { n: { $gt: 1 } } },
  { $sort: { n: -1 } },
  { $limit: 10 }
]).forEach(doc => printjson(doc));
