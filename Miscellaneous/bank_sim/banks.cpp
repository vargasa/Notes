#include <iostream>
#include <functional>
#include <map>
#include "bank.h"

int main(){

  std::function<void(std::vector<Bank>&,double, int)> MakeAllLoans = [&]
    (std::vector<Bank>& banks, double interest, int period){

    auto getIndex = [&](int n){ return n % banks.size(); };

    double amount = banks[0].MaxLoan() - 0.01;
    uint i = 0;
    while(amount>1.){
      uint j = getIndex(i);
      uint k = getIndex(i+1);
      if(banks[j].GrantLoan(amount,interest,period)){
        //std::cout << banks[j].GetName() << " Granted Loan " << amount << "\n";
        banks[k].MakeDeposit(amount);
      } else {
        //std::cout << banks[j].GetName() <<  " Loan denied: " << amount << "\n";
        break;
      }
      amount = banks[k].MaxLoan() - 0.01;
      ++i;
    }
  };

  auto PrintListOfLoans = [&](std::vector<Bank>& banks) {
    std::cout << "\n=======\nList of Loans\n=======\n";
    for(auto& b:banks){
      uint k = 0;
      for(auto& l: b.GetLoans()){
        std::cout << b.GetName() << "Loan" << k << "\t"
                  << l.GetAmount() << "\t" << l.GetAPY() << "\t"
                  << l.GetPeriod() << "\t" << l.GetInstallment() << "\n";
        k++;
      }
    }
    std::cout << "=======\nEOF\n=======\n";
  };


  std::function<double(std::vector<Bank>&)> PayAllLoans = [](std::vector<Bank>& banks) {

    auto GetTotalCash = [&] {
      double total = 0.;
      for(auto& b: banks){
        total += b.GetCash();
      }
      return total;
    };

    auto GetTotalLiabilities = [&] {
      double tot = 0.;
      for(auto& b: banks){
        tot += b.GetTotalLiabilities();
      }
      return tot;
    };

    //PrintListOfLoans();
    const int periods = banks[0].GetLoans()[0].GetPeriod(); /*Assuming all periods are same*/
    for(uint m = 0; m < periods; ++m){
      for(auto& b: banks){
        uint priorSize = b.GetLoans().size();
        for(uint i = 0; i< b.GetLoans().size();++i){
          b.PayInstallment(i);
          uint newSize = b.GetLoans().size();
          if(newSize<priorSize /*A loan has been dropped fully paid*/) --i;
        }
      }
    }
    //PrintListOfLoans();
    return GetTotalCash();
    //return GetTotalLiabilities();
  };

  for(uint k = 1; k < 10; ++k){ /*Loan Interest*/
    double interest = 0.01*k;

    for(uint j = 1; j < 20; ++j){ /*Bank reserve requirement*/
      double reserve = 0.005*j;

      for(uint i = 1; i < 30; ++i){ /*Loan period of time in years*/
        int period = 12 * i;

        std::vector<Bank> banks;
        banks.emplace_back(Bank("A",reserve,0.));
        banks[0].MakeDeposit(10);
        MakeAllLoans(banks,interest,period);
        std::cout << period << "\t" << PayAllLoans(banks) << "\n";
        break
      }
      break;
    }
    break;

    // double total;
    // for(auto& b: banks){
    //   total = 0.;
    //   for(auto& l: b.GetLoans()){
    //     total += l.GetAmount();
    //   }
    //   std::cout << b.GetName() << " Total Loans\t" << total << std::endl;
    // }

    // for(auto& b: banks){
    //   std::cout << b.GetName() << " Cash:\t" <<  b.GetCash() << std::endl;
    //   std::cout << b.GetName() << " Total Assets\t" << b.GetTotalAssets() << std::endl;
    //   std::cout << b.GetName() << " Liabilities:\t"  << b.GetTotalLiabilities() << "\n";
    //   std::cout << b.GetName() << " Reserves:\t"  << b.GetCash()/b.GetTotalLiabilities() << "\n";
    // }

  }



  return 0;
}
