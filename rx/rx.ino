#include <SPI.h>
#include "printf.h"
#include "RF24.h"

// instantiate an object for the nRF24L01 transceiver
RF24 radio(7, 8);  // using pin 7 for the CE pin, and pin 8 for the CSN pin

uint8_t address[][6] = { "1Node", "2Node" };
bool radioNumber = 0;
bool role = false;  // true = TX role, false = RX role
char payload[20] = "T12.3TP123456PH12.3H";

void setup() {

  Serial.begin(115200);
  while (!Serial) {
    // some boards need to wait to ensure access to serial over USB
  }

  // initialize the transceiver on the SPI bus
  if (!radio.begin()) {
    Serial.println(F("radio hardware is not responding!!"));
    while (1) {}  // hold in infinite loop
  }

  // print example's introductory prompt
//  Serial.println(F("RF24/examples/GettingStarted"));
//  Serial.print(F("radioNumber = "));
//  Serial.println((int)radioNumber);
  radio.setPALevel(RF24_PA_LOW);  // RF24_PA_MAX is default.
  radio.setPayloadSize(sizeof(payload));  // float datatype occupies 4 bytes
  radio.openWritingPipe(address[radioNumber]);  // always uses pipe 0
  radio.openReadingPipe(1, address[!radioNumber]);  // using pipe 1
  radio.startListening();  // put radio in RX mode

  // For debugging info
  // printf_begin();             // needed only once for printing details
  // radio.printDetails();       // (smaller) function that prints raw register values
  // radio.printPrettyDetails(); // (larger) function that prints human readable data
 int register_array[14]={0x0,0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8,0x9,0xA,0xB,0X1C,0x1D};
int send_byte; 
//  for (int i=0;i<14;i++){
//    Serial.print(register_array[i]);
//    Serial.print(": ");
//    digitalWrite(8, LOW);
//    send_byte=register_array[i];
//    Serial.println(SPI.transfer16(send_byte<<8));
//    digitalWrite(8, HIGH);
//  }
//    Serial.print(0xA);
//    Serial.print(": ");
//    digitalWrite(8, LOW);
//    Serial.println(SPI.transfer(0x0A));
//    Serial.println(SPI.transfer(0xFF));
//    Serial.println(SPI.transfer(0xFF));
//    Serial.println(SPI.transfer(0xFF));
//    Serial.println(SPI.transfer(0xFF));
//    Serial.println(SPI.transfer(0xFF));
//    digitalWrite(8, HIGH);
//    
//    Serial.print(0xB);
//    Serial.print(": ");
//    digitalWrite(8, LOW);
//    Serial.println(SPI.transfer(0x0B));
//    Serial.println(SPI.transfer(0xFF));
//    Serial.println(SPI.transfer(0xFF));
//    Serial.println(SPI.transfer(0xFF));
//    Serial.println(SPI.transfer(0xFF));
//    Serial.println(SPI.transfer(0xFF));
//    digitalWrite(8, HIGH);
}

void loop() {
    uint8_t pipe;
    if (radio.available(&pipe)) {      // is there a payload? get the pipe number that recieved it
      uint8_t bytes = radio.getPayloadSize();  // get the size of the payload
      radio.read(&payload, bytes);             // fetch payload from FIFO
//      Serial.print(F("Received "));
//      Serial.print(bytes);  // print the size of the payload
//      Serial.print(F(" bytes on pipe "));
//      Serial.print(pipe);  // print the pipe number
//      Serial.print(F(": "));
      Serial.println(payload);  // print the payload's value
    }

}  // loop
