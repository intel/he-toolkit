// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// Takes in the number to encode, the base, the precision and the size of the
// array returns a list of coefficients after the shift. So the list can
// directly be turned into a polynomial.

#pragma once

#include <algorithm>
#include <cmath>
#include <vector>
#include <map>
#include <iterator>

inline constexpr double signum(double x) { return (x > 0.0) - (x < 0.0); }

class Coder{
        private: double bw=1.2;
                 double epsil=0.00000001;


        public:
                 std::map<long,long> encode(double num){

                 const double log_bw = std::log(bw);
                 std::map<long, long> a;
                 long r;
                 double t_minus_po; 
                 for (double t = std::abs(num), sigma = signum(num); t >= epsil;
                 t = std::abs(t_minus_po), sigma *= signum(t_minus_po)) {
                 r = std::ceil(std::log(t) / log_bw);
                 r -= (std::pow(bw, r) - t > t - std::pow(bw, r - 1));

                 a[r] = sigma;
                 t_minus_po = t - std::pow(bw, r);
                   }
                 return a;
                 }

                 template <typename T>
                 void print_out_results(const T& en) {
                 for (const auto& [key, value] : en) {
                 std::cout << "(" << key << " , " << value << ")" << std::endl;
                 }
                }

                 template <typename T, typename U, typename W>
                 void print_poly_rep(const T& en, U mi,  W de){
                 for(const auto& [key, value] : en){
                 std::cout<<value<<"x^" << key-mi;
                 if(key-mi!=de)
                 std::cout<<" + ";

                }
               }

                
                //The polynomial representation for fractional decoding, where a power of 2 cyclcotomic is used
                //x^-i is replaced by -x^(N-i), where N is the degree of the cyclotomic.
                 template <typename T>
                 void print_poly_rep_frac(const T& en, int N){
                 for(const auto& [key, value] : en){
                 if(key<0)
                 std::cout<<(-1)*value<<"x^" <<N+key;
                 else
                 std::cout<<value<<"x^"<<key;

                 if (key!=prev(en.end())->first)
                 std::cout<<" + ";

                }
               } 


                template<typename T>
                 double decoder(const T& en){
                 double sum=0;
                 for(const auto& [key, value] :en) {
                sum+=value*pow(bw,key);
                }
                return sum;
               }

};
