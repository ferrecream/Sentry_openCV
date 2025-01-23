
#include <AccelStepper.h>

#define dirPin1 2
#define stepPin1 3
#define dirPin2 4
#define stepPin2 5
#define motorInterfaceType 1
#define shootPin 6
#define homePin 7

AccelStepper stepper1(motorInterfaceType, stepPin1, dirPin1);
AccelStepper stepper2(motorInterfaceType, stepPin2, dirPin2);

float kp = 0.2;
int deadZone = 5;

void setup() {
  Serial.begin(115200);

  // Configure max speed and acceleration
  stepper1.setMaxSpeed(4000); // Increased speed
  stepper1.setAcceleration(20000); // Increased acceleration
  stepper2.setMaxSpeed(4000);
  stepper2.setAcceleration(20000);

  pinMode(homePin, INPUT_PULLUP);
  pinMode(shootPin, OUTPUT);
}

void loop() {
  //if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input == "shoot") {
      digitalWrite(shootPin, HIGH);
      delay(80);
      digitalWrite(shootPin, LOW);
    } else {
      int commaIndex = input.indexOf(',');
      if (commaIndex > 0) {
        int xError = input.substring(0, commaIndex).toInt();
        int yError = input.substring(commaIndex + 1).toInt();

        if (abs(xError) > deadZone) {
          int xMove = kp * xError * 2; // Scale for faster movement
          stepper1.moveTo(stepper1.currentPosition() + xMove);
          stepper1.run();
        }
        if (abs(yError) > deadZone) {
          int yMove = kp * yError * 2; // Scale for faster movement
          stepper2.moveTo(stepper2.currentPosition() + yMove);
          stepper2.run();
        }
    } else if (digitalRead(homePin) == LOW) {
      stepper1.move(-1800);
      stepper1.runToPosition();
      delay(1000);
    }
  }
}
