// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// A program that calls the header and returns the coefficients and the
// corresponding exponents.
#include <iostream>
#include <iterator>
#include <map>

#include "nibnaf.h"
#include "iomanip"

//Prints out the coefficients and the exponents of the Laurent Expansion
template <typename T>
void print_out_results(const T& en) {
  for (const auto& [key, value] : en) {
    std::cout << "(" << key << " , " << value << ")" << std::endl;
  }
}

// Prints out the polynomial emcoding
template <typename T, typename U, typename W>
 void PrintPolyRep(const T& en, U mi, W de){
  for(const auto& [key, value] : en){
   std::cout<<value<<"x^" << key-mi;
   if(key-mi!=de)
     std::cout<<" + ";
  }
 }

//Gets back the original number from the coefficients
template<typename T, typename U>
double Decoder(const T& en, U b){
double sum=0;
 for(const auto& [key, value] :en) {
  sum+=value*pow(b,key);
  }
return sum;
}

//To print the zero polynomial and the zero results when en is empty, which happens when theta=0 or |theta|<epsil
void PrintZeroPol() {
        std::cout<<"0";
}
void PrintZeroRes(){
        std::cout<<"(0,0)";
}

void test_integer() {
  double number = 546;
  double bw = 2;
  double epsil = 0.4;
  
  const auto en = gap(number, bw, epsil);
//Gets back the minimal negative exponent, the maximal degree and the degree of the polynomial
long frac_exp=(en.begin()->first-std::abs(en.begin()->first))/2;
long max_exp=std::prev(en.end())->first;
long deg=max_exp-frac_exp;
  print_out_results(en);
  PrintPolyRep(en, frac_exp, deg);
  std::cout<<std::endl;
 std::cout<<std::fixed<<std::setprecision(10)<<Decoder(en,bw)<<std::endl;
}

void test_float() {
  double number = 546.789;
  double bw = 2;
  double epsil = 0.0001;   //Increased the precision so we can see negative exponents. 

  const auto en = gap(number, bw, epsil);
 //Gets back the minimal negative exponent, the maximal degree and the degree of the polynomial
long frac_exp=(en.begin()->first-std::abs(en.begin()->first))/2;
long max_exp=std::prev(en.end())->first;
long deg=max_exp-frac_exp;
  print_out_results(en);
  PrintPolyRep(en, frac_exp, deg);
  std::cout<<std::endl;
 std::cout<<std::fixed<<std::setprecision(10)<<Decoder(en,bw)<<std::endl;
}

void test_zero() {
  double number = 0;
  double bw = 2;
  double epsil = 0.4;
  
  const auto en = gap(number, bw, epsil);
  //Gets back the minimal negative exponent, the maximal degree and the degree of the polynomial
  long frac_exp=en.empty() ? 0: (en.begin()->first-std::abs(en.begin()->first))/2;
  long max_exp=en.empty() ? 0:std::prev(en.end())->first;
  long deg=max_exp-frac_exp;
 en.empty() ? PrintZeroRes() : print_out_results(en); 
  std::cout<<std::endl;
  en.empty() ? PrintZeroPol() :PrintPolyRep(en, frac_exp, deg);
  std::cout<<std::endl;
 std::cout<<std::fixed<<std::setprecision(10)<<Decoder(en,bw)<<std::endl;
}

int main(void) {
  std::cout << "test float\n";
  test_float();
  std::cout << "test integer\n";
  test_integer();
  std::cout << "test zero\n";
  test_zero();

  return 0;
}
