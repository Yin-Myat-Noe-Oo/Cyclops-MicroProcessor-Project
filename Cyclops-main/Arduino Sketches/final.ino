#include <LiquidCrystal.h>  //Include LCD Library
#include<Servo.h>           //Include Servo Library
#include <dhtnew.h>         // Include Temperature and Humidity Sensor library
#define outPin 10           // Defines pin number to which the sensor is connected
#define pirPin 8         // Define pin for PIR motion sensor
LiquidCrystal lcd(2,3,4,5,6,7); //defining workings for LCD
DHTNEW DHT(outPin);         //initialization for Temperature and Humidity Sensor
Servo Servo1;               //initialization for Servo Motor

String angle_input;         //angle input as string from serial monitor

int flag_game=0;
int count=0;
int X = 0;
int Y = 0;
int px = 0;
int py = 0;
 
// PIR sensor variables
int pirState = LOW;         // Start with no motion detected
int motionVal = 0;          // Variable to store PIR sensor reading
unsigned long lastMotionTime = 0;  // Last time motion was detected
const unsigned long motionTimeout = 30000; // 30 seconds timeout for motion detection
bool motionActivated = false;  // Flag to track if system is in motion-activated mode
 
int a = 0;
String angle;             //String input to the function (angle_servo) as angle taken from serial monitor as string
String emotion;
String emot="";
String status_on;
String txt="";           //String input taken from serial monitor to type text
int func_to_use=-1;
int flag=0;
int servoPin=9;
int y;
int value;
int ledPin = 11;          // the pin that the LED is attached to
int x;
int status = false; 
char text[]="WELCOME";
unsigned int i=0;
int blink_flag=0;

void setup() 
{  
   Servo1.attach(servoPin); //servo attachment to pin 9  
   Serial.begin(9600);     //serial data begin
   lcd.begin(16,2);       //lcd screen begin 
   Servo1.write(120);    //initial servo placement 120 degrees
   
   // Setup PIR sensor
   pinMode(pirPin, INPUT);
   pinMode(ledPin, OUTPUT);
   
   // Initial message
   lcd.clear();
  lcd.setCursor(0, 0);
   lcd.clear();
    Serial.println("Cyclops system ready");
}

void intro()
{ 
  //prints MANDRED TECH text at initial start up 
  lcd.begin(16,2);
  lcd.setCursor(2, 0);  
  while(text[i]!='\0'){
    lcd.print(text[i]);   
    if(i>=14)
    {
      lcd.command(0x18);
    }
    delay(500);
    i++;
  }   
}

void led_control(int onoff)
{
  //cyclops eye led control
  pinMode(ledPin, OUTPUT);
  if(onoff==1){
    digitalWrite(ledPin, HIGH);
  }
  else
  {
    digitalWrite(ledPin, LOW);
  }  
}

void led_blink()
{
  //cyclops eye led blink control
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);
  delay(200);
  digitalWrite(ledPin, HIGH);
  delay(100);
  digitalWrite(ledPin, LOW);
  delay(200);
  digitalWrite(ledPin, HIGH);
  delay(10);
  buzz();  
}

void angle_servo(String angle)
{
  //random angle string input, converts into integer and rotates servo accordingly 
  Servo1.write(angle.toInt());
  delay(1000);  
}

void print_text(String rx_str)
{
  //prints any text on lcd screen 
  String a1=rx_str.substring(0,16);
  String a2=rx_str.substring(16,32);
  lcd.begin(16,2);
  lcd.setCursor(0,0);
  lcd.setCursor(0,0);
  lcd.print(a1);
  lcd.setCursor(0,1);
  lcd.print(a2);
  delay(500);
  lcd.clear();  
}

void rotate1()
{  
  //rotates the servo (head movement)
  Servo1.attach(servoPin);  
  for(int measure=120;measure>=60;measure--)
  {
    Servo1.write(measure);
    delay(10);    
  }
  for(int measure=60;measure<=120;measure++){
    Servo1.write(measure);
    delay(10);     
  }
  for(int measure=120;measure<=180;measure++){
    Servo1.write(measure);
    delay(10);     
  }
  for(int measure=180;measure>=120;measure--){
    Servo1.write(measure);
    delay(10);     
  }
}

void rotate2()
{  
  //rotates the servo (head movement)
  Servo1.attach(servoPin);  
  for(int measure=120;measure>=60;measure--)
  {
    Servo1.write(measure);
    delay(20);    
  }
  for(int measure=60;measure<=120;measure++){
    Servo1.write(measure);
    delay(20);     
  }
  for(int measure=120;measure<=180;measure++){
    Servo1.write(measure);
    delay(20);     
  }
  for(int measure=180;measure>=120;measure--){
    Servo1.write(measure);
    delay(20);     
  }
}

void get_dht()
{
  //Humidity and Temperature Function
  delay(1000);
  lcd.clear();
  // int readData = DHT.read11(outPin);
  DHT.read();
  float t = DHT.getTemperature();        // Read temperature
  float h = DHT.getHumidity();           // Read humidity
  lcd.setCursor(0,0);
  lcd.print("Temp(C):");
  lcd.setCursor(9,0);
  lcd.print(t);
  lcd.setCursor(0,1);
  lcd.print("Humidity(%):");
  lcd.setCursor(12,1);
  lcd.print(h);
  delay(100); // wait two seconds
}

void processing()
{
    lcd.write("Processing");
    delay(200);
    lcd.clear();
    lcd.write("Processing.");
    delay(200); 
    lcd.clear();
    lcd.write("Processing..");
    delay(200);
    lcd.clear();      
    lcd.write("Processing...");
    delay(200);
    lcd.clear();
    lcd.write("Processing....");
    delay(200);
    lcd.clear();      
    lcd.write("Processing.....");  
    lcd.clear();    
}

// Update the checkMotion function to be more reliable
void checkMotion() {
  // Read the PIR sensor
  motionVal = digitalRead(pirPin);
  
  // Debug output if state changed
  if (motionVal != pirState) {
    Serial.print("Motion state changed to: ");
    Serial.println(motionVal == HIGH ? "Motion Detected" : "No Motion");
  }
  
  if (motionVal == HIGH) {  // Motion detected
    if (pirState == LOW) {  // If we were previously not detecting motion
      Serial.println("Motion detected!");
      
      // Turn on LED
      led_control(1);
      
      // Display motion detected message
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Motion Detected!");
      lcd.setCursor(0, 1);
      lcd.print("Hello there!");
      
      // Perform a greeting movement
      rotate1();
      
      // Update state and time
      pirState = HIGH;
      lastMotionTime = millis();
    }
  } 
  else {  // No motion
    if (pirState == HIGH) {  // If we were previously detecting motion
      Serial.println("Motion ended!");
      pirState = LOW;
    }
    
    // Check if timeout has elapsed since last motion
    if (millis() - lastMotionTime > motionTimeout && motionActivated) {
      // Turn off LED and clear LCD if no motion for timeout period
      led_control(0);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Waiting for");
      lcd.setCursor(0, 1);
      lcd.print("motion...");
    }
  }
}

// Update the toggleMotionDetection function to provide better feedback
void toggleMotionDetection(bool enable) {
  motionActivated = enable;
  
  if (enable) {
    // Reset the PIR state when activating
    pirState = LOW;
    
    // Clear display and show activation message
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Motion Detection");
    lcd.setCursor(0, 1);
    lcd.print("Activated");
    delay(1000);
    
    // Show waiting message
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Waiting for");
    lcd.setCursor(0, 1);
    lcd.print("motion...");
    
    // Send confirmation to serial
    Serial.println("Motion detection activated");
  } 
  else {
    // Clear display and show deactivation message
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Motion Detection");
    lcd.setCursor(0, 1);
    lcd.print("Deactivated");
    delay(1000);
    lcd.clear();
    
    // Send confirmation to serial
    Serial.println("Motion detection deactivated");
  }
}
void loop() 
{     
    // Check for motion if in motion detection mode
    if (motionActivated) {
      checkMotion();
    }
    
    //looks for the serial function input 
    if (Serial.available()>0)
    {
      emotion=Serial.readStringUntil('\r');
      Serial.print("Received command: ");
      Serial.println(emotion);
    } 

    //declaration of different function parameters
    if(emotion=="on")
    {
      lcd.begin(16,2);
      intro();
      intro_tune(); 
      led_control(1);
             
    }     
    else if(emotion=="sine")
    {
      func_to_use=1;
    }
    else if(emotion=="happy")
    {
      func_to_use=2;
    }
    else if(emotion=="sad")
    {
      func_to_use=3;
    }
    else if(emotion=="angry")
    {
      func_to_use=4;
    }
    else if(emotion=="rotate1")
    {
      led_control(1);
      lcd.clear();
      rotate1();
      logo();      
    }
    else if(emotion=="rotate2")
    {
      led_control(1);
      lcd.clear();
      rotate2();
      logo();
    }
    else if(emotion=="temph")
    {
      func_to_use=5;
    }
    // Handle music wave commands
    else if(emotion=="#MusicWave")
    {
      led_control(1);
      lcd.clear();
      sinewave_music1();
      emotion = "";
    }
    else if(emotion=="#MusicWave2")
    {
      led_control(1);
      lcd.clear();
      sinewave_music2();
      emotion = "";
    }
    else if(emotion=="#MusicWave3")
    {
      led_control(1);
      lcd.clear();
      sinewave_music3();
      emotion = "";
    }
    // Handle text display commands (including "Now Playing" text)
    else if(emotion.indexOf("#")>=0)
    {
      txt=emotion.substring(1,emotion.length());
      func_to_use=6;
    }      
    else if(emotion=="#NewsIcon")
    {
      led_control(1);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("  NEWS UPDATE  ");
      lcd.setCursor(0, 1);
      lcd.print("Getting Headlines");
      delay(1000);
      emotion = "";
    }
    else if(emotion=="camera")
    {
      func_to_use=7;
      
    }
    else if(emotion=="clock")
    {
        func_to_use=8;
        
    }
    else if(emotion=="game")
    {
           X = 0;
           Y = 0;
           px = 0;
           py = 0;
          func_to_use=9;          
    }
    else if(emotion.indexOf("@")>=0)
    {
      angle_input=emotion.substring(1,emotion.length());
      func_to_use=10;
      
    } 
    else if(emotion=="exercise")
    {
        func_to_use=11;
    }
    else if(emotion=="logo")
    {
          func_to_use=12;
          
    } 
    else if(emotion=="led_blink")
    {
       
      
        lcd.clear();
        led_blink();      
        processing();
        func_to_use=13;
          
    } 
    // New commands for motion detection
    else if(emotion=="motion_on")
    {
        toggleMotionDetection(true);
        func_to_use=-1;  // Reset function to avoid other operations
        emotion = "";  
    }
    else if(emotion=="motion_off")
    {
        toggleMotionDetection(false);
        func_to_use=-1;  // Reset function to avoid other operations
        emotion = "";
    }
    else if(emotion=="off")
    {
      func_to_use=-1;
      led_control(0);
      lcd.clear();
    }
    else if(emotion=="idle")
    {
      func_to_use=-1;
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Cyclops Ready");
      emotion = "";
    }
    
    //loopings for the functions   
       
    if (func_to_use==1)
    {
      led_control(1);
      sinewave2();
    }
    else if (func_to_use==2)
    {
      led_control(1);
      happy();
    }
    else if (func_to_use==3)
    {
      led_control(1);
      sad();
    }
    else if (func_to_use==4)
    {
      led_control(1);
      angry();
    }
    
    // Add this new command handler in the loop() function, right after the other command handlers
    else if(emotion=="pir_init_silent")
    {
        // Initialize PIR sensor without using the LCD display
        pinMode(pirPin, INPUT);
        pinMode(ledPin, OUTPUT);
        // No LCD updates here
        Serial.println("PIR sensor initialized silently");
        func_to_use=-1;  // Reset function to avoid other operations
        emotion = "";    // Clear the command
    }

    else if (func_to_use==5)
    {
      led_control(1);
      get_dht();
    }
    else if (func_to_use==6)
    {
      led_control(1);
      print_text(txt);        
    }
    else if (func_to_use==7)
    {
      led_control(1);
      camera();      
    }
    else if (func_to_use==8)
    {
      led_control(1);
      clock1();
      clock2();
      clock3();
      clock4();
      clock5();
      clock6();
      clock7();        
    }
    else if (func_to_use==9)
    {  
      led_control(1);  
      init_game(); 
      if(flag_game==0)
      {
      //pac1
      lcd.setCursor(0,0);
      lcd.write(1); 
      }
        game();
        count++;
        if(count!=32)
        {           
           flag_game=1;   
        }
        else
        {
          flag_game=0;
          count=0;
        }            
        Serial.println(func_to_use);                     
        Serial.println(count);
        Serial.println(flag_game);                
     }          
    else if(func_to_use==10)
    {
      led_control(1); 
      angle_servo(angle_input);
      logo();    
    }
    else if(func_to_use==11)
    {
      led_control(1);
      exercise();            
    }
    else if(func_to_use==12)
    {
      led_control(1);
      logo();
    }
    else if(func_to_use==13)
    {
      led_control(1);
      processing();
    }

    // Reset emotion to avoid repeated processing
    emotion = "";
}