use("cryptobot");

// Step 4: min / max / avg close
print("=== Step 4: stats on close ===");
db.ohlcv.aggregate([
  {
    $group: {
      _id: null,
      minClose: { $min: "$close" },
      maxClose: { $max: "$close" },
      avgClose: { $avg: "$close" }
    }
  }
]).forEach(doc => printjson(doc));
