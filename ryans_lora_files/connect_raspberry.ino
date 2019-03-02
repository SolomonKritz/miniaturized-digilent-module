#include <SPI.h>
#include <RH_RF95.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

Adafruit_SSD1306 display = Adafruit_SSD1306(128, 32, &Wire);

// OLED FeatherWing buttons map to different pins depending on board:
#if defined(ESP8266)
  #define BUTTON_A  0
  #define BUTTON_B 16
  #define BUTTON_C  2
#elif defined(ESP32)
  #define BUTTON_A 15
  #define BUTTON_B 32
  #define BUTTON_C 14
#elif defined(ARDUINO_STM32_FEATHER)
  #define BUTTON_A PA15
  #define BUTTON_B PC7
  #define BUTTON_C PC5
#elif defined(TEENSYDUINO)
  #define BUTTON_A  4
  #define BUTTON_B  3
  #define BUTTON_C  8
#elif defined(ARDUINO_FEATHER52832)
  #define BUTTON_A 31
  #define BUTTON_B 30
  #define BUTTON_C 27
#else // 32u4, M0, M4, nrf52840 and 328p
  #define BUTTON_A  9
  #define BUTTON_B  6
  #define BUTTON_C  5
#endif

#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3

// Blinky on receipt
#define LED 13

char incomingByte[4]; // for incoming serial data

void setup() {
  pinMode(LED, OUTPUT);
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C); // Address 0x3C for 128x32
  display.display();
  delay(1000);

  // Clear the buffer.
  display.clearDisplay();
  display.display();

  pinMode(BUTTON_A, INPUT_PULLUP);
  pinMode(BUTTON_B, INPUT_PULLUP);
  pinMode(BUTTON_C, INPUT_PULLUP);

  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0,0);
  display.println("Feather LoRa TX Test!");
  display.display(); // actually display all of the above    
  
  Serial.begin(115200);
  //while (!Serial) {
    //display.setCursor(0,0);
    //display.println("No serial");
    //display.display(); // actually display all of the above   
    //delay(1);
    //display.clearDisplay();
    //display.display();
  //}
  delay(100);
}

void loop() {
  // send data only when you receive data:
  int length;
  unsigned long recv = 0;
  if (Serial.available() > 0) {
    display.setCursor(0,0);
    display.clearDisplay();
    display.display(); // actually display all of the above 
    // read the incoming byte:
    length = Serial.readBytes(incomingByte,2);

    memcpy(&recv,incomingByte,2);
    // say what you got:
    display.print("I received: ");
    display.println(recv);
    display.display();
  }
}
