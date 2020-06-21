
// C program for generating a 
// random number in a given range 
#include <stdio.h>
#include <stdlib.h>
#include <time.h>



float randRangeFloat(float lower, float upper){
 clock_t t;
 srand(clock());
 return lower + ((float)rand()/(float)(RAND_MAX)) * (upper - lower);
}

int randRange(int lower, int upper)
{
  srand(clock());
  return (rand() % (upper - lower  + 1)) + lower;  
}

