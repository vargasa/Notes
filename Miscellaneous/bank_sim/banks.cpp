#include <iostream>
#include <map>
#include "bank.h"

int main(){

  std::vector<Bank> banks;
  banks.emplace_back(Bank("A",0.10,100.));
  banks.emplace_back(Bank("B",0.15,40.));
  banks.emplace_back(Bank("C",0.14,35.));
  banks.emplace_back(Bank("D",0.13,25.));
  // banks.emplace_back(Bank("E",0.10,0.));
  // banks.emplace_back(Bank("F",0.99,0.));
  // banks.emplace_back(Bank("G",0.10,0.));
  // banks.emplace_back(Bank("H",0.10,0.));

  auto getIndex = [&](int n){ return n % banks.size(); };

  double amount = 10.;
  uint i = 0;
  while(amount>0.01){
    uint j = getIndex(i);
    uint k = getIndex(i+1);
    if(banks[j].GrantLoan(amount,3.,12)){
      std::cout << "Bank " << banks[j].GetName() << " Granted Loan: $" << amount << "\n";
      banks[k].MakeDeposit(amount);
      std::cout << "\tMade deposit to bank " << banks[k].GetName() << " $" << amount << "\n";
      std::cout << "\t"<< banks[k].GetName() <<" New Balance: " << banks[k].GetCash() << "\n";
      amount = banks[k].MaxLoan() - 0.1;
      std::cout << "\tNew Request " << i << " will be for: " << amount << "\n";
    } else {
      std::cout << "Loan denied: " << amount << "\n";
      break;
    }
    ++i;
  }

  double total = 0.;

  for(auto b: banks){
    total += b.GetCash();
    std::cout << b.GetName() << " Cash:\t" <<  b.GetCash() << std::endl;
  }
  std::cout << "\tTotal Cash: " << total << "\n";

   for(auto& b: banks){
    std::cout << b.GetName() << " Total Assets\t" << b.GetTotalAssets() << std::endl;
  }

  for(auto& b: banks){
    std::cout << b.GetName() << "Reserves:\t"  << b.GetCash()/b.GetTotalLiabilities() << "\n";
  }

  for(auto& b: banks){
    std::vector<Loan> loans = b.GetLoans();
    for(auto& l: loans){ /*We need some kind of loan identifier*/
      for(uint i=0; i < l.GetPeriod(); ++i){
        //std::cout << "Making Payment " << l.GetInstallment() << "\t" << l.GetAmortization()[0].second  << "\n";
        b.PayInstallment(l);
      }
    }
  }

  std::cout << "\n====\nLoans paid\n=====\n";


  for(auto& b: banks){
    std::cout << b.GetName() << " Total Assets\t" << b.GetTotalAssets() << std::endl;
  }

  for(auto& b: banks){
    std::cout << b.GetName() << "Reserves:\t"  << b.GetCash()/b.GetTotalLiabilities() << "\n";
  }


  total = 0.;
  for(auto& b: banks){
    total += b.GetCash();
    std::cout << b.GetName() << " Cash:\t" <<  b.GetCash() << std::endl;
  }
  std::cout << "\tTotal Cash: " << total << "\n";




  // int n = 1;
  // std::cout << l1.GetInstallment() << "\n";
  // for(const auto& row: l1.GetAmortization()){
  //   std::cout << n++ << "\t" << row.first << "\t" << row.second << "\t" <<l1.GetInstallment() << "\n";
  // }


  return 0;
}
