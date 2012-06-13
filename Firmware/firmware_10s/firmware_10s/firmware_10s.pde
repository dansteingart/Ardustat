#include <EEPROM.h>

#define DATAOUT 11//MOSI
#define DATAIN 12//MISO - not used, but part of builtin SPI
#define SPICLOCK  13//sck
#define SLAVESELECTD 10//ss
#define SLAVESELECTP 7//ss

long watchdog = 0;
long watchdogdiff = 30000; //one minute
float adc;    //out of pot
float dac;    //out of main dac
float adcgnd; //adc at ground
float adcref; //ref electrode
float refvolt;//ref voltage 2.5V
float current_adc;
int firstdac= 0;
int seconddac = 0;
int dacaddr = 0;
int dacmode=3;
boolean dactest = false;
boolean rtest = false;
int testcounter = 0;
int testlimit = 0;
int outvolt=1023;
byte pot= 0;
int temp;
byte resistance1=0;
int res=0;
int fixedres=0;
int cl=2;
int pdl = 4;
int counter = 0;
int sign = 1;
int waiter = 0;
int mode = 1;  //tells computer what's what
int pMode = 0; //saved variable to remember if the last mode was pstat or not
int lastData[10]; //previous error values for use in pstat's PID algorithm
int dacrun;
int adcrun;
int resmove;

//Serial Comm Stuff
int incomingByte;
boolean setVoltage;
char serInString[100];
char sendString[99];
char holdString[5];
//int adcArray[100];
//int adcArrayCounter = 0;
int output;
boolean whocares = false;
boolean positive = false;
boolean gstat = false;
boolean pstat = false;
boolean ocv = true;
boolean cv = false;
int setting = 0;
int speed = 1;
int countto = 0;
byte clr;


void setup()
{


  //Startup Serial
  Serial.begin(57600);
  //  Serial.println("Hi Dan!");

  analogReference(EXTERNAL);
  //SPI
  byte i;
  //byte clr;
  pinMode(DATAOUT, OUTPUT);
  pinMode(3,OUTPUT);
  pinMode(DATAIN, INPUT);
  pinMode(SPICLOCK,OUTPUT);
  pinMode(SLAVESELECTD,OUTPUT);
  pinMode(5,OUTPUT);
  pinMode(6,OUTPUT);
  pinMode(SLAVESELECTP,OUTPUT);
  pinMode(cl, OUTPUT);
  digitalWrite(SLAVESELECTD,HIGH); //disable device
  digitalWrite(SLAVESELECTP,HIGH); //disable device
  digitalWrite(cl, LOW);
  delay(1000);
  digitalWrite(cl,HIGH);
  //SPCR is 01010000.  write_pot turns off the SPI interface,
  // which means SPCR becomes 00010000 temporarily
  //SPCR = (1<<SPE)|(1<<MSTR);
  SPCR = B00010000;
  clr=SPSR;
  clr=SPDR;
  delay(10);
  // power on reset
  pot=144;
  resistance1=0;
  res=0;
  write_pot(pot,resistance1,res);
  // wakeup
  pot=B00010000;
  write_pot(pot,resistance1,res);
  // set resistance to High
  pot=B01000000;
  resistance1=B00000000;
  res=255;
  write_pot(pot,resistance1,res);
  for (int i=1;i<11;i++) lastData[i]=0;
  watchdog = millis();
}

void loop()
{
  //read the serial port and create a string out of what you read
  readSerialString(serInString);
  if( isStringEmpty(serInString) == false) { //this check is optional
    watchdog = millis();
    //delay(500);
    holdString[0] = serInString[0];
    holdString[1] = serInString[1];
    holdString[2] = serInString[2];
    holdString[3] = serInString[3];
    holdString[4] = serInString[4];

    //try to print out collected information. it will do it only if there actually is some info.
    if (serInString[0] == 43 || serInString[0] == 45 || serInString[0] == 114 || serInString[0] == 103 || serInString[0] == 112|| serInString[0] == 80 ||  serInString[0] == 82 || serInString[0] == 99 || serInString[0] == 100 || serInString[0] == 86)
    {
      if (serInString[0] == 43) positive = true;
      else if (serInString[0] == 45) positive = false;
      pstat = false;
      if (serInString[0] != 114) gstat = false;
      dactest = false;
      rtest = false;
      ocv = false;
      sign = 1;
      for (int i = 0; i < 98; i++)
      {
        sendString [i] = serInString[i+1];
      }
      int out =  stringToNumber(sendString,4);
      //Serial.print(out,DEC);
      if (serInString[0] != 112)
      {
        pMode = 0;
      } 
      if (serInString[0] == 43)
      {
        outvolt = out;

        send_dac(0,checkvolt(outvolt));
        digitalWrite(3,HIGH);
        speed = 1;
        countto = 10;
      }
      if (serInString[0] == 100)
      {

        outvolt = out;
        send_dac(1,outvolt);
        digitalWrite(3,LOW);
        speed = 1;
        countto = 10;
      }
      if (serInString[0] == 45 || serInString[0] == 111)
      {
        //outvolt = -1;
        ocv = true;
        //if(out >= 1) write_dac(1,out);
        digitalWrite(3,LOW);
        //speed = 5;
        //countto = 10;

      }

      if (serInString[0] == 80)
      {
        dactest = true;
        testcounter = 0;
        testlimit = 1023;
        //speed = 5;
        //countto = 10;
      }

      if (serInString[0] == 82)
      {
        rtest = true;
        testcounter = 0;
        testlimit = 255;
        //speed = 10;
        //countto = 10;
      }


      if (serInString[0] == 114)
      {

        res = out;
        write_pot(pot,resistance1,res);
      }

      //Write ID to EEPROM
      if (serInString[0] == 86)  
      {
        Serial.println("fudge");
        Serial.println(out);

        EEPROM.write(32,byte(out)) ;

      }

      if (serInString[0] == 103)
      {
        dacon();
        gstat = true;

        outvolt = betteranaread(0);
        write_dac(0,checkvolt(outvolt));
        //speed = 5;
        //countto = 20;


        if (out > 2000)
        {

          out = out - 2000;
          sign = -1;
        }
        else if (out < 2000)
        {
          out = out;
          sign = 1;
        }

        setting = out;
        outvolt = betteranaread(0)+(sign*out);
        if (outvolt > 1023) outvolt = 1023;
        if (outvolt < 0) outvolt = 0;
        write_dac(0,checkvolt(outvolt));

        digitalWrite(3,HIGH);

      }
      if (serInString[0] == 112)
      {

        if (out > 2000)
        {

          out = out - 2000;
          sign = -1;
        }
        else if (out < 2000)
        {
          out = out;
          sign = 1;
        }
        if (pMode == 0)
        {
          dacon();
        }
        pstat = true;
        pMode = 1;
        //speed = 5;
        //countto = 20;
        setting = out*sign;
        //outvolt = setting; //initial guess
        digitalWrite(3,HIGH);
        write_dac(0,setting);
      }

      if (serInString[0] == 99)
      {

        if (out > 2000)
        {

          out = out - 2000;
          sign = -1;
        }
        else if (out < 2000)
        {
          out = out;
          sign = 1;
        }
        pstat = true;
        //speed = 5;
        //countto = 20;
        setting = sign*out;
        //outvolt = setting; //initial guess
        dacon();
        digitalWrite(3,HIGH);
      }
    }

    else if (serInString[0] == 32)
    {
      digitalWrite(5,HIGH);
      digitalWrite(6,LOW);
      delay(100);
      digitalWrite(5,LOW);
      digitalWrite(6,LOW);

    }


    else if (serInString[0] == 115)
    {
      sendout();
    }



    flushSerialString(serInString);
  }
  else if (millis()-watchdog > watchdogdiff)
  {

    ocv = true;
    gstat = false;
    pstat = false;
    digitalWrite(3,LOW);

    //blink 3 times
    for (int i = 0; i < 3; i++)
    {
      digitalWrite(5,HIGH);
      digitalWrite(6,LOW);
      delay(100);
      digitalWrite(5,LOW);
      digitalWrite(6,LOW);
      delay(100);
    }
  }


  //Work Section
  if (pstat) potentiostat();
  if (gstat) galvanostat();
  //if (cv)
  if (dactest) testdac();
  if (rtest) testr();
  delay(speed);
  counter++;
  adcrun = adc + adcrun;
  dacrun = dac + dacrun;
  if (counter > countto)
  {

    dac = dacrun/counter;

    adc = adcrun/counter;

    //sendout();
    counter = 0;
    adcrun =0;
    dacrun = 0;

  } 

}


char spi_transfer(volatile char data)
{
  SPDR = data;                    // Start the transmission
  while (!(SPSR & (1<<SPIF)))     // Wait the end of the transmission
  {
  };
  return SPDR;                    // return the received byte
}

void write_dac(int address, int value)
{
  //This function replaces the old write_dac, which
  //is named send_dac now.
  send_dac(address,value);
}
byte send_dac(int address, int value)
{
  SPCR = B01010000;
  firstdac = (address << 6) + (3 << 4) + (value >> 6);
  seconddac = (value << 2 )&255;
  digitalWrite(SLAVESELECTD,LOW);
  //2 byte opcode
  spi_transfer(firstdac);
  spi_transfer(seconddac);
  digitalWrite(SLAVESELECTD,HIGH); //release chip, signal end transfer
  //delay(3000);*/
  SPCR = B00010000;
}

byte dacoff()
{
  SPCR = B01010000;
  firstdac = (3 << 6) ;
  seconddac = 0;
  digitalWrite(SLAVESELECTD,LOW);
  //2 byte opcode
  spi_transfer(firstdac);
  spi_transfer(seconddac);
  digitalWrite(SLAVESELECTD,HIGH); //release chip, signal end transfer
  //delay(3000);*/
  SPCR = B00010000;
}

byte dacon()
{
  SPCR = B01010000;
  firstdac = (1 << 6) ;
  seconddac = 0;
  digitalWrite(SLAVESELECTD,LOW);
  //2 byte opcode
  spi_transfer(firstdac);
  spi_transfer(seconddac);
  digitalWrite(SLAVESELECTD,HIGH); //release chip, signal end transfer
  //delay(3000);*/
  SPCR = B00010000;
}

byte write_pot(int address, int value1, int value2)
{
  /*digitalWrite(SLAVESELECTP,LOW);
   //3 byte opcode
   spi_transfer(address);
   spi_transfer(value1);
   spi_transfer(value2);
   digitalWrite(SLAVESELECTP,HIGH);*/  //release chip, signal end transfer
  sendValue(0,255-value2);
}


//Below Here is Serial Comm Shizzle (for rizzle)

//utility function to know wither an array is empty or not
boolean isStringEmpty(char *strArray) {
  if (strArray[0] == 0) {
    return true;
  }
  else {
    return false;
  }
}

//Flush String
void flushSerialString(char *strArray) {
  int i=0;
  if (strArray[i] != 0) {
    while(strArray[i] != 0) {
      strArray[i] = 0;                  // optional: flush the content
      i++;
    }
  }
}

//Read String In
void readSerialString (char *strArray) {
  int i = 0;
  if(Serial.available()) {
    Serial.println("    ");  //optional: for confirmation
    while (Serial.available()){
      strArray[i] = Serial.read();
      i++;

    }
  }
}

int stringToNumber(char thisString[], int length) {
  int thisChar = 0;
  int value = 0;

  for (thisChar = length-1; thisChar >=0; thisChar--) {
    char thisByte = thisString[thisChar] - 48;
    value = value + powerOfTen(thisByte, (length-1)-thisChar);
  }
  return value;
}

/*
 This method takes a number between 0 and 9,
 and multiplies it by ten raised to a second number.
 */

long powerOfTen(char digit, int power) {
  long val = 1;
  if (power == 0) {
    return digit;
  }
  else {
    for (int i = power; i >=1 ; i--) {
      val = 10 * val;
    }
    return digit * val;
  }
}

void potentiostat()
{
  //read in values
  adc = betteranaread(0);
  float adc_set = adc - betteranaread(3);
  // if ( ! adc_set ) adc_set = adc;
  //  if ( sign == -1 ) {  adc_set = analogRead(3) - adc;  if ( ! analogRead(3) ) adc_set = analogRead(2) - adc;}
  dac = betteranaread(1);
  int resmove = 0;
  int move = 0;
  //if potential is too high
  if ((adc_set > setting) && (outvolt > 0))
  {
    move = gainer(adc_set,setting);
    outvolt=outvolt-move;
    write_dac(0,checkvolt(outvolt));

  }

  //if potential is too losw
  else if ((adc_set < setting) && (outvolt < 1023))
  {
    move = gainer(adc_set,setting);
    outvolt=outvolt+move;
    write_dac(0,checkvolt(outvolt));
  }

  // if range is limited decrease R
  if ((outvolt > 1022) && (res > 0))
  {
    outvolt = 1000;
    write_dac(0,checkvolt(outvolt));
    resmove = resgainer(adc_set,setting);
    res = res - resmove;
    res = constrain(res,0,255);
    write_pot(pot,resistance1,res);

  }
  else if ((outvolt < 1) && (res > 0))
  {
    outvolt = 23;
    write_dac(0,checkvolt(outvolt));
    resmove = resgainer(adc_set,setting);
    res = res - resmove;
    res = constrain(res,0,255);
    write_pot(pot,resistance1,res);
    delay(waiter);
  }

  //if range is truncated increase R
  int dude = abs(dac-adc);
  if ((dude < 100) && (res < 255))
  {
    res = res+1;
    res = constrain(res,1,255);
    write_pot(pot,resistance1,res);
    delay(waiter);
  }

}

int checkvolt(int volt)
{
  int out = volt;
  if (volt > 1023) volt = 1023;
  if (volt < 0) volt = 0;
  return volt;
}

void galvanostat()
{
  //get values
  current_adc = betteranaread(4);
  adcgnd = betteranaread(2);
  

  int move = 1;
  float diff = 0;


  //if charging current
  if (sign > 0)
  {
    diff = adcgnd - current_adc;
    //if over current step dac down
    if( ((diff) > (setting)) && (outvolt > 0))
    {

      move = gainer(diff,setting);
      outvolt = outvolt-move;
      write_dac(0,checkvolt(outvolt));

    }

    //if under current step dac up
    if (((diff) <(setting)) && (outvolt < 1023))
    {
      move = gainer(diff,setting);
      outvolt = outvolt+move;
      write_dac(0,checkvolt(outvolt));

    }
  }

  //if discharge current
  if (sign < 0)
  {
    diff = current_adc - adcgnd;
    //if over current step dac up
    if( (diff) > (setting) && (outvolt < 1023))
    {
      move = gainer(diff,setting);
      outvolt =outvolt+move;
      write_dac(0,checkvolt(outvolt));
    }

    //if under current step dac down
    if ((diff) < (setting) && (outvolt > 0))
    {
      move = gainer(diff,setting);
      outvolt = outvolt-move;
      write_dac(0,checkvolt(outvolt));

    }
  }
}

void sendout()
{

  adc = betteranaread(0);
  dac = betteranaread(1);
  adcgnd = betteranaread(2);
  adcref = betteranaread(3);
  current_adc = betteranaread(4);
  refvolt = betteranaread(5);

  if (pstat) mode = 2;
  else if (gstat) mode = 3;
  else if (ocv) mode = 1;
  else if (dactest) mode = 4;
  else mode = 0;
  int setout = sign*setting;
  Serial.print("GO,");
  Serial.print(checkvolt(outvolt),DEC);
  Serial.print(",");
  Serial.print(adc);
  Serial.print(",");
  Serial.print(dac);
  Serial.print(",");
  Serial.print(res);
  Serial.print(",");
  Serial.print(setout);
  Serial.print(",");
  Serial.print(mode);
  Serial.print(",");
  Serial.print(holdString[0]);
  Serial.print(holdString[1]);
  Serial.print(holdString[2]);
  Serial.print(holdString[3]);
  Serial.print(holdString[4]);
  Serial.print(",");
  Serial.print(adcgnd);
  Serial.print(",");
  Serial.print(adcref);
  Serial.print(",");
  Serial.print(refvolt);
  Serial.print(",");
  Serial.print(current_adc);
  Serial.print(",");
  Serial.print(int(EEPROM.read(32)));
  Serial.println(",ST");
  //res=res+1;
  //if (res > 255) res = 0;
  //sendValue(0,1);
  //sendValue(0,255);
}

void testdac ()
{
  digitalWrite(3,LOW);
  write_dac(0,testcounter);
  outvolt = testcounter;
  testcounter = testcounter + 1;
  if (testcounter > testlimit) testcounter = 0;


}

void testr ()
{
  digitalWrite(3,HIGH);
  write_dac(0,1023);
  outvolt = 1023;
  res = testcounter;
  write_pot(pot,resistance1,res);
  testcounter = testcounter + 1;
  if (testcounter > testlimit) testcounter = 0;

}

int gainer(int whatitis, int whatitshouldbe)
{
  //Serial.print(whatitis);
  //Serial.print(",");
  //Serial.println(whatitshouldbe);


  int move = abs(whatitis-whatitshouldbe);
  move = constrain(move,-100,100);
  //Minimize hyperactivity
  //if (abs(move) < 2) move = 0;
  return move;
}

int resgainer(int whatitis, int whatitshouldbe)
{
  int move = 0;
  int diff = abs(whatitis-whatitshouldbe); 
  if (diff > 20) move = 30;
  else move = 10;
  //move = constrain(move,1,100);
  return move;
}

//Barry's hacky functions

byte value;

byte sendBit(boolean state)
{
  digitalWrite(SPICLOCK,LOW);
  delayMicroseconds(10);
  digitalWrite(DATAOUT,state);
  digitalWrite(SPICLOCK,HIGH);
  delayMicroseconds(10);
}

byte sendValue(int wiper, int val)
//tested cycle time for this function is ~565 microseconds.
{
  value =  byte(val);
  //digitalWrite(SPICLOCK,LOW);
  //digitalWrite(DATAOUT,LOW);
  digitalWrite(SLAVESELECTP,LOW);
  delayMicroseconds(10);

  //Select wiper
  for(int i=0;i<3;i++){
    sendBit(false);
  }
  sendBit(wiper);

  //write command
  for(int i=0;i<4;i++){
    sendBit(false);
  }
  //data
  sendBit(HIGH && (value & B10000000));
  sendBit(HIGH && (value & B01000000));
  sendBit(HIGH && (value & B00100000));
  sendBit(HIGH && (value & B00010000));
  sendBit(HIGH && (value & B00001000));
  sendBit(HIGH && (value & B00000100));
  sendBit(HIGH && (value & B00000010));
  sendBit(HIGH && (value & B00000001));
  //sendBit(true);  //fudge
  digitalWrite(SLAVESELECTP,HIGH);
  //Serial.println(in);
  delayMicroseconds(10);
}

byte readWiper()
{
  //send read command
  digitalWrite(SLAVESELECTP,LOW);
  delayMicroseconds(10);
  sendBit(false);
  sendBit(false);
  sendBit(false);
  sendBit(false);
  sendBit(true);
  sendBit(true);

  //get data
  int data[9];
  //Serial.print("  ");
  for(int i=0;i<9;i++)
  {
    digitalWrite(SPICLOCK,LOW);
    delayMicroseconds(10);
    digitalWrite(DATAOUT,LOW);
    delayMicroseconds(10);
    data[i] = digitalRead(DATAIN);
    digitalWrite(SPICLOCK,HIGH);
    delayMicroseconds(10);
    Serial.print(data[i]);
  }
  digitalWrite(SLAVESELECTP,HIGH);
}


float betteranaread(int adcin)
{
  int limit = 50;
  int goer = 0;
  float out = 0;
  for (goer = 0; goer < limit; goer ++)
  {
    out = out + float(analogRead(adcin));
  }
  float limer = float(limit);
  return out/limer;
}





