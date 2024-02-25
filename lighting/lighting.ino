
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

#define LED_PIN 6
#define LED_COUNT 600
#define BUFFER_SIZE 60

// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

byte buffer[BUFFER_SIZE];

unsigned int index = 0;

void setup()
{
    delay(1000);          // reduces Serial issues
    Serial.begin(115200); // not 9600 - so it's fast

    strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
    strip.show();            // Turn OFF all pixels ASAP
    strip.setBrightness(50); // Set BRIGHTNESS to about 1/5 (max = 255)
}

void loop()
{

    while (Serial.available() < BUFFER_SIZE)
        ;

    Serial.readBytes(buffer, BUFFER_SIZE);
    Serial.write(buffer, BUFFER_SIZE);

    process_buffer();
}

void process_buffer()
{
    for (int i = 0; i < BUFFER_SIZE; i += 3)
    {
        if ((uint8_t)buffer[i] & 1)
        {
            // control bit is set
            index = 0;
        }
        index = index % LED_COUNT;
        // leds[index] = (struct led) {buffer[i], buffer[i+1], buffer[i+2], buffer[i+3]};
        // uint32_t color = strip.Color(leds[index].r, leds[index].g, leds[index].b);
        // uint32_t color = strip.Color(0, 255, 0);

        // strip.setPixelColor(index, color);
        strip.setPixelColor(index, buffer[i], buffer[i + 1], buffer[i + 2]);
        index += 1;
    }
    if (index >= 590)
    {
        strip.show();
    }
}
