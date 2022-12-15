#include <SPI.h>
#include "printf.h"
#include "RF24.h"
#include <Wire.h>
#include "SparkFunBME280.h"
BME280 mySensor;

// instantiate an object for the nRF24L01 transceiver
RF24 radio(7, 8);  // using pin 7 for the CE pin, and pin 8 for the CSN pin

uint8_t address[][6] = { "1Node", "2Node" };
bool radioNumber = 1;  // 0 uses address[0] to transmit, 1 uses address[1] to transmit
bool role = true;  // true = TX role, false = RX role
char payload[20] ="T12.3TP123456PH12.3H";

void setup() {

  Serial.begin(115200);
  Wire.begin();

  if (mySensor.beginI2C() == false) //Begin communication over I2C
  {
    Serial.println("The sensor did not respond. Please check wiring.");
    while(1); //Freeze
  }
  while (!Serial) {
    // some boards need to wait to ensure access to serial over USB
  }

  // initialize the transceiver on the SPI bus
  if (!radio.begin()) {
    Serial.println(F("radio hardware is not responding!!"));
    while (1) {}  // hold in infinite loop
  }

  // print example's introductory prompt
  Serial.println(F("RF24/examples/GettingStarted"));
  Serial.print(F("radioNumber = "));
  Serial.println((int)radioNumber);
  radio.setPALevel(RF24_PA_LOW);  // RF24_PA_MAX is default.
  radio.setPayloadSize(sizeof(payload));  // float datatype occupies 4 bytes
  radio.openWritingPipe(address[radioNumber]);  // always uses pipe 0
  radio.openReadingPipe(1, address[!radioNumber]);  // using pipe 1
  radio.stopListening();  // put radio in TX mode

  // For debugging info
  // printf_begin();             // needed only once for printing details
  // radio.printDetails();       // (smaller) function that prints raw register values
  // radio.printPrettyDetails(); // (larger) function that prints human readable data

}  // setup

void loop() {
    char humidity[] ="12.3";
    char pressure[] ="123456";
    char temp[]="12.3";
    float f_temp=mySensor.readTempF();
    dtostrf(mySensor.readFloatHumidity(),2,1,humidity);
    dtostrf(mySensor.readFloatPressure(), 5,0,pressure);
    dtostrf(mySensor.readTempF(), 2,1,temp);

    payload[0]=72; //"H"
    for (int i=0; i<5; i++){
      payload[i+1]=humidity[i];
    }
    payload[5]=72; //"H"
    payload[6]=80; //"P"
    for (int i=0; i<7; i++){
      payload[i+7]=pressure[i];
    }
    payload[13]=80; //"P"
    payload[14]=84; //"T"
    for (int i=0; i<5; i++){
      payload[i+15]=temp[i];
    }
    payload[19]=84; //"T"
    Serial.print("Sending: ");
    Serial.println(payload);
    
    unsigned long start_timer = micros();                // start the timer
    bool report = radio.write(&payload, sizeof(payload));  // transmit & save the report
    unsigned long end_timer = micros();                  // end the timer

    if (report) {
      Serial.print(F("Transmission successful! "));  // payload was delivered
      Serial.print(F("Time to transmit = "));
      Serial.print(end_timer - start_timer);  // print the timer result
      Serial.print(F(" us. Sent: "));
      Serial.println(payload);  // print payload sent
    } else {
      Serial.println(F("Transmission failed or timed out"));  // payload was not delivered
    }

    // to make this example readable in the serial monitor
    delay(1000);  // slow transmissions down by 1 second

}  // loop
