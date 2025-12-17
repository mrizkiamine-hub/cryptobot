use("cryptobot");

// Step 6: Daily aggregation from open_time (string -> YYYY-MM-DD with substr)
print("=== Step 6: daily aggregation ===");
db.ohlcv.aggregate([
  {
    $group: {
      _id: { $substrBytes: ["$open_time", 0, 10] },
      totalVolumeBase: { $sum: "$volume_base" },
      avgClose: { $avg: "$close" },
      nbCandles: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } },
  {
    $project: {
      _id: 0,
      day: "$_id",
      totalVolumeBase: 1,
      avgClose: { $round: ["$avgClose", 2] },
      nbCandles: 1
    }
  }
]).forEach(doc => printjson(doc));
