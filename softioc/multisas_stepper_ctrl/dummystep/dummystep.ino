
int PUL = 25;
int DIR = 26;
int ENA = 27;

int CW = HIGH;
int CCW = LOW;



// Change to adjust step and direction
int numberStep = 1000;
int dir = CW;




void setup() {
  pinMode (PUL, OUTPUT);
  pinMode (DIR, OUTPUT);
  pinMode (ENA, OUTPUT);

  digitalWrite(ENA, HIGH);
  delay(1000);

  digitalWrite(ENA,LOW);

  for (int i=0; i<numberStep; i++)    //Forward 5000 steps
  {
    digitalWrite(DIR,dir);
    //digitalWrite(ENA,LOW);
    
    digitalWrite(PUL,HIGH);
    delayMicroseconds(20000);
    digitalWrite(PUL,LOW);
    delayMicroseconds(20000);
  }
 

}

void loop() {
  /*
  digitalWrite(ENA,LOW);
  for (int i=0; i<1000; i++)    //Forward 5000 steps
  {
    digitalWrite(DIR,LOW);
    //digitalWrite(ENA,LOW);
    digitalWrite(PUL,HIGH);
    delayMicroseconds(20000);
    digitalWrite(PUL,LOW);
    delayMicroseconds(20000);
  }
  
  for (int i=0; i<1000; i++)   //Backward 5000 steps
  {
    digitalWrite(DIR,HIGH);
    //digitalWrite(ENA,LOW);
    digitalWrite(PUL,HIGH);
    delayMicroseconds(20000);
    digitalWrite(PUL,LOW);
    delayMicroseconds(20000);
  }
  */
}
