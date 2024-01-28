#define DECODE_PANASONIC // alias for DECODE_KASEIKYO

// #define DEBUG // Activate this for lots of lovely debug output from the decoders.

// #define RAW_BUFFER_LENGTH  180  // Default is 112 if DECODE_MAGIQUEST is enabled, otherwise 100.

#define IR_RECEIVE_PIN 9

#include <Arduino.h>
#include <IRremote.hpp>

void setup()
{
    // 謎、遅延を入れないとハングする
    delay(1000);

    Serial.begin(115200);

    // Start the receiver and if not 3. parameter specified, take LED_BUILTIN pin from the internal boards definition as default feedback LED
    IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);
}

void loop()
{
    if (IrReceiver.decode())
    {
        // IrReceiver.printIRResultShort(&Serial);
        // IrReceiver.printIRSendUsage(&Serial);
        // if (IrReceiver.decodedIRData.protocol == UNKNOWN)
        // {
        //     Serial.println(F("Received noise or an unknown (or not yet enabled) protocol"));
        //     // We have an unknown protocol here, print more info
        //     IrReceiver.printIRResultRawFormatted(&Serial, true);
        // }
        // Serial.println();

        if (IrReceiver.decodedIRData.protocol == PANASONIC)
        {
            Serial.println(IrReceiver.decodedIRData.command);
        }

        /*
         * !!!Important!!! Enable receiving of the next value,
         * since receiving has stopped after the end of the current received data packet.
         */
        IrReceiver.resume(); // Enable receiving of the next value

        /*
         * Finally, check the received data and perform actions according to the received command
         */
        if (IrReceiver.decodedIRData.command == 0x10)
        {
            // do something
        }
        else if (IrReceiver.decodedIRData.command == 0x11)
        {
            // do something else
        }
    }
}