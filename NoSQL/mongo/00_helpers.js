// Helpers / Settings
use("cryptobot");

const COL = "ohlcv";

print("DB:", db.getName());
print("Collection:", COL);
print("Sample doc:");
printjson(db.getCollection(COL).findOne());
