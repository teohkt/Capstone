#define stepPinP  2
#define dirPinP 3

#define stepPinT 6
#define dirPinT 7

char command;

void setup() {
  // put your setup code here, to run once:
  pinMode(stepPinP,OUTPUT);
  pinMode(dirPinP,OUTPUT);

  pinMode(stepPinT,OUTPUT);
  pinMode(dirPinT,OUTPUT);

  Serial.begin(9600);

  //j = 106
  //k = 107
  //l=108
  //i=105
}

void loop() {

    command = Serial.read();
    Serial.println(command);

    if(command == 'J'){//Pan CCW Step
      digitalWrite(dirPinP,HIGH);
      Serial.println("Pan CCW Step");

      digitalWrite(stepPinP,HIGH); 
      digitalWrite(stepPinP,LOW);   
    }
      
    while(command=='j'){//Pan CCW Continuous
      digitalWrite(dirPinP,HIGH);
      Serial.println("Pan CCW Continuous");
      digitalWrite(stepPinP,HIGH); 
      digitalWrite(stepPinP,LOW); 

      if (Serial.available() > 0){     //if there is another value to read exit this loop
        break;
      }
    }

    if(command == 'L'){//Pan CW Step
      digitalWrite(dirPinP,LOW);
      Serial.println("Pan CW Step");

      digitalWrite(stepPinP,HIGH); 
      digitalWrite(stepPinP,LOW);   
    }
      
    while(command=='l'){//Pan CW Continuous
      digitalWrite(dirPinP,LOW);
      Serial.println("Pan CW Continuous");
      digitalWrite(stepPinP,HIGH); 
      digitalWrite(stepPinP,LOW); 

      if (Serial.available() > 0){     //if there is another value to read exit this loop
        break;
      }
    }
    
    if(command == 'I'){//Tilt CCW Step
      digitalWrite(dirPinT,LOW);
      Serial.println("Tilt CCW Step");

      digitalWrite(stepPinT,HIGH); 
      digitalWrite(stepPinT,LOW);   
    }
      
    while(command=='i'){//Tilt CCW Continuous
      digitalWrite(dirPinT,LOW);
      Serial.println("Tilt CCW Continuous");
      digitalWrite(stepPinT,HIGH); 
      digitalWrite(stepPinT,LOW); 

      if (Serial.available() > 0){     //if there is another value to read exit this loop
        break;
      }
    }

    if(command == 'K'){//Tilt CW Step
      digitalWrite(dirPinT,HIGH);
      Serial.println("Tilt CW Step");

      digitalWrite(stepPinT,HIGH); 
      digitalWrite(stepPinT,LOW);   
    }
      
    while(command=='k'){//Tilt CW Continuous
      digitalWrite(dirPinT,HIGH);
      Serial.println("Tilt CW Continuous");
      digitalWrite(stepPinT,HIGH); 
      digitalWrite(stepPinT,LOW); 

      if (Serial.available() > 0){     //if there is another value to read exit this loop
        break;
      }
    }

}
    
