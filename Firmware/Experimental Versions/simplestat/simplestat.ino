#include <EEPROM.h>

long watchdog = 0;
long watchdogdiff = 30000; //one minute
int adc;    //out of pot
int dac;    //out of main dac
int adcgnd; //adc at ground
int adcref; //ref electrode
int refvolt;//ref voltage 2.5V
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

int output;

boolean whocares = false;
boolean gstat = false;
boolean pstat = false;
boolean ocv = true;

int setting = 0;
int speed = 1;
int countto = 0;

int fakeDAC = 9;
int fakeGND = 10;


void setup()
{
  //Startup Serial
  Serial.begin(57600);

  pinMode(fakeDAC,INPUT);

  delay(1000);


  delay(10);
  // wakeup
  // set resistance to High

  for (int i=1;i<11;i++) lastData[i]=0;
  watchdog = millis();

}

void loop()
{
  //read the serial port and create a string out of what you read
  readSerialString(serInString);
  if(isStringEmpty(serInString) == false)
  { //this check is optional
    watchdog = millis();
    //delay(500);
    holdString[0] = serInString[0];
    holdString[1] = serInString[1];
    holdString[2] = serInString[2];
    holdString[3] = serInString[3];
    holdString[4] = serInString[4];

    int modeList[] = {43,45,114,103,112,80,82,99,100,101,86};

    boolean shouldIDoSomething = false;

    for (int i = 0; i < sizeof(modeList)/sizeof(modeList[0]); i++)
    {
      if (holdString[0] == modeList[i]) shouldIDoSomething = true;
    }

    if (shouldIDoSomething)
    {

      pstat = false;
      if (holdString[0] != 114) gstat = false;
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

      //Turn
      if (serInString[0] != 112)
      {
        cell_off();
      } 
      if (serInString[0] == 43)
      {
        outvolt = out;
        write_dac(out);        
        speed = 1;
        countto = 10;
      }
      if (serInString[0] == 100)
      {

        outvolt = out;
        write_dac(outvolt);
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
        //resistor changer placeholder
      }

      //Write ID to EEPROM
      if (serInString[0] == 86)  
      {
        Serial.print("writing id: ");
        Serial.println(out);

        EEPROM.write(32,byte(out)) ;

      }

      //galvanostat
      if (serInString[0] == 103)
      {
        dac_on();
        gstat = true;
        outvolt = analogRead(0);
        write_dac(outvolt);

        //if values are negative:
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
        outvolt = analogRead(0)+(sign*out);
        if (outvolt > 1023) outvolt = 1023;
        if (outvolt < 0) outvolt = 0;
        write_dac(outvolt);

      }

      //potentiostat
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
          dac_on();
        }
        pstat = true;
        pMode = 1;
        setting = out*sign;
        digitalWrite(3,HIGH);
        write_dac(setting);
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
        dac_on();
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
  if (ocv)
  {
    dac_on();
    gnd_on();
  }
  delay(speed);
  counter++;
  adcrun = adc + adcrun;
  dacrun = dac + dacrun;
  if (counter > countto)
  {
    dac = dacrun/counter;
    adc = adcrun/counter;
    counter = 0;
    adcrun =0;
    dacrun = 0;

  } 

}


void write_dac(int value)
{
  //This function replaces the old write_dac, which
  //is named send_dac now.
  //send_dac(address,value);
  // That's all noise.  In this version we're analog, son.
  pinMode(fakeDAC,OUTPUT);
  value = constrain(value,0,1023);
  analogWrite(fakeDAC,value/4); 

}

void write_gnd(int value)
{
  //This function replaces the old write_dac, which
  //is named send_dac now.
  //send_dac(address,value);
  // That's all noise.  In this version we're analog, son.
  pinMode(fakeGND,OUTPUT);
    value = constrain(value,0,1023);	
  analogWrite(fakeGND,value/4); 

}

byte gnd_on()
{
  pinMode(fakeGND,INPUT);
}

byte dac_on()
{
  pinMode(fakeDAC,INPUT);
}


//Below Here is Serial Comm Shizzle (for rizzle)

//utility function to know wither an array is empty or not
boolean isStringEmpty(char *strArray)
{
  if (strArray[0] == 0) {
    return true;
  }
  else {
    return false;
  }
}

//Flush String
void flushSerialString(char *strArray)
{
  int i=0;
  if (strArray[i] != 0) {
    while(strArray[i] != 0) {
      strArray[i] = 0;                  // optional: flush the content
      i++;
    }
  }
}

//Read String In
void readSerialString (char *strArray)
{
  int i = 0;
  if(Serial.available() > 5) {
    Serial.println("    ");  //optional: for confirmation
    while (Serial.available()){
      strArray[i] = Serial.read();
      i++;

    }
  }
}

int stringToNumber(char thisString[], int length)
{
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

long powerOfTen(char digit, int power)
{
  long val = 1;
  if (power == 0) 
  {
    return digit;
  }
  else 
  {
    for (int i = power; i >=1 ; i--) 
    {
      val = 10 * val;
    }
    return digit * val;
  }
}

void potentiostat()
{
  //read in values
  adc = analogRead(0);
  int adc_set = adc - analogRead(3);
  dac = analogRead(1);

  int resmove = 0;
  int move = 0;

  //if potential is too high
  if ((adc_set > setting) && (outvolt > 0))
  {
    move = gainer(adc_set,setting);
    outvolt=outvolt-move;
    write_dac(outvolt);

  }

  //if potential is too low
  else if ((adc_set < setting) && (outvolt < 1023))
  {
    move = gainer(adc_set,setting);
    outvolt=outvolt+move;
    write_dac(outvolt);
  }
}


void galvanostat()
{
  //get values
  adc = analogRead(0);
  dac = analogRead(1);

  int move = 1;
  int diff = 0;


  //if charging current
  if (sign > 0)
  {
    diff = dac - adc;
    //if over current step dac down
    if( ((diff) > (setting)) && (outvolt > 0))
    {

      move = gainer(diff,setting);
      outvolt = outvolt-move;
      write_dac(outvolt);

    }

    //if under current step dac up
    if (((diff) <(setting)) && (outvolt < 1023))
    {
      move = gainer(diff,setting);
      outvolt = outvolt+move;
      write_dac(outvolt);
    }
  }

  //if discharge current
  if (sign < 0)
  {
    diff = adc - dac;
    //if over current step dac up
    if( (diff) > (setting) && (outvolt < 1023))
    {
      move = gainer(diff,setting);
      outvolt =outvolt+move;
      write_dac(outvolt);
    }

    //if under current step dac down
    if ((diff) < (setting) && (outvolt > 0))
    {
      move = gainer(diff,setting);
      outvolt = outvolt-move;
      write_dac(outvolt);

    }
  }
}

void sendout()
{
  adc = analogRead(0);
  dac = analogRead(1);
  adcgnd = analogRead(2);
  adcref = analogRead(3);
  refvolt = analogRead(5);
  if (pstat) mode = 2;
  else if (gstat) mode = 3;
  else if (ocv) mode = 1;
  else if (dactest) mode = 4;
  else mode = 0;
  int setout = sign*setting;
  Serial.print("GO,");
  Serial.print(constrain(outvolt,0,1023),DEC);
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
  Serial.print(int(EEPROM.read(32)));
  Serial.println(",ST");
  //res=res+1;
  //if (res > 255) res = 0;
  //sendValue(0,1);
  //sendValue(0,255);
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

void cell_off()
{
  pinMode(fakeDAC,INPUT);
}





