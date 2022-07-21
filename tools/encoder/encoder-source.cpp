//A source file that calls the header and returns the coeffiecients and the corresponding exponents.
#include <iostream>
#include <cmath>
#include<array>
#include<list>
#include<vector>
#include<string>
#include"NIBNAF.h"

int main()
{
    double theta, bw, epsil;
    int sz;
    std::cout<<"Enter the number to encode:";
    std::cin>>theta;
    std::cout<<"Enter the base to encode:";
    std::cin>>bw;
    std::cout<<"Enter the amount of precision:";
    std::cin>>epsil;
    std::cout<<"Enter the size of the array:";
    std::cin>>sz;
double enar[sz];	
std::list<int>en=gap(theta, bw, epsil, sz);
copy(en.begin(), en.end(), enar);

for (long i=0; i<sz;++i)
     if(enar[i]!=0)
std::cout<<enar[i]<<", "<<i<<std::endl;

return 0;
}
