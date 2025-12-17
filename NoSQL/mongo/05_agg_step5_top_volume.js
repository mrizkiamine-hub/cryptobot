use("cryptobot");

// Step 5: Top 5 biggest volumes
print("=== Step 5: Top 5 volume_base ===");
db.ohlcv.aggregate([
  { $sort: { volume_base: -1 } },
  {
    $project: {
      _id: 0,
      open_time: 1,
      close_time: 1,
      close: 1,
      volume_base: 1,
      quote_volume: 1,
      trade_count: 1
    }
  },
  { $limit: 5 }
]).forEach(doc => printjson(doc));
