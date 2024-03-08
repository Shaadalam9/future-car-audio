#include <Arduino_LSM9DS1.h>
#include <Arduino_APDS9960.h>
#include <Arduino_HTS221.h>


// Number of samples for averaging
const int numSamples = 10;
// Alpha value for the exponential moving average filter (0 < alpha <= 1)
const float alpha = 0.5;

// Variables for the filter
float xFiltered = 0;
float y, z;
int proximityThreshold = 0.002;  // Set based on your testing

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  if (!APDS.begin()) {
    Serial.println("Failed to initialize APDS9960 sensor!");
    while (1);
  }

  if (!HTS.begin()) {
    Serial.println("Failed to initialize humidity temperature sensor!");
    while (1);
  }

  Serial.println("IMU initialized!");
}

void loop() {
  float xSum = 0;
  float xAverage, x, y, z;

  // Averaging
  for (int i = 0; i < numSamples; i++) {
    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(x, y, z);
      xSum += x;
    }
    delay(10);  // Short delay between samples
  }

  xAverage = xSum / numSamples;

  // Exponential moving average filter
  xFiltered = alpha * xAverage + (1 - alpha) * xFiltered;

//  Serial.print("Filtered X-Axis Acceleration: ");
  if (xFiltered > 0) {
    Serial.print(xFiltered);
  } else {
    // Presumably, you might want to handle non-positive values differently or just print them.
    // As it stands, your 'else' clause does the same thing as the 'if' part.
    // Adjust based on your needs. For now, it will just print the value as is.
    Serial.print(0);
  }


  // Read temperature
  float temperature = HTS.readTemperature();
  Serial.print(" , ");
  Serial.println(temperature > 28.3 ? 1 : 0);




  delay(20);  // Update rate in milliseconds
}