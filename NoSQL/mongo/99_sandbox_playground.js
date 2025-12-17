use("cryptobot");

// Put any experiments here, to avoid messing with the “clean” scripts.
print("Sandbox: latest 3 docs with key fields");
db.ohlcv.find({}, { _id: 0, open_time: 1, close: 1, volume_base: 1 })
  .sort({ open_time: -1 })
  .limit(3)
  .forEach(doc => printjson(doc));
