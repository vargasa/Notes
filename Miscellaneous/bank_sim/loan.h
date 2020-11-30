#include <vector>
#include <math.h>
#include <cassert>

class Loan {

  const double amount;
  const double interest;
  const int nperiod;

 public:
  Loan(double amount, double apy, int period);
  double GetInstallment();
  std::vector<std::pair<double,double>> GetAmortization();
  double GetCapital(uint period = 0) const;

};

Loan::Loan(double amount, double apy, int period) : amount(amount),
  interest(apy/100.),
  nperiod(period)
{

}

std::vector<std::pair<double,double>> Loan::GetAmortization(){

  std::vector<std::pair<double,double>> table;

  const double installment = Loan::GetInstallment();

  double capital = amount;

  for(uint i = 0; i<nperiod;++i){
    double interestPeriod = capital*(interest/12.);
    double amortizationPeriod = installment - interestPeriod;
    table.emplace_back(std::make_pair(capital,interestPeriod));
    capital -= amortizationPeriod;
  }

  return table;

}

double Loan::GetInstallment(){
  assert(interest != 0. and interest < 1.);
  double itm = interest/12.;
  return amount * itm * ( pow( 1. + itm, (double)nperiod) ) / ( pow( 1. + itm, (double)nperiod) - 1. ) ;
}

double Loan::GetCapital(uint period) const{

  //std::vector<std::pair<double,double>> table = GetAmortization();

  //return table[period].first;
  return amount;

}
