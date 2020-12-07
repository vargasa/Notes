#include <vector>
#include <math.h>
#include <cassert>

class Loan {

  double amount;
  const double interest;
  uint nperiod;

 public:
  Loan(double amount, double apy, int period);
  double GetInstallment() const;
  std::vector<std::pair<double,double>> GetAmortizationTable() const;
  std::pair<double,double> GetAmortization() const;
  double GetAmount() const { return amount; }
  uint GetPeriod() const { return nperiod; }
  void SetAmount(double newCapital) { amount = newCapital; }
  bool SetPeriod(uint newPeriod) { nperiod = newPeriod; }
  double GetMonthlyInterest() const;

  void PrintAmortizationTable() const;
};

Loan::Loan(double amount, double apy, int period) : amount(amount),
  interest(apy),
  nperiod(period)
{

}

void Loan::PrintAmortizationTable() const{

  std::vector<std::pair<double,double>> table = Loan::GetAmortizationTable();

  double installment = GetInstallment();

  std::cout << "\tAmount:" << amount << "\n";
  std::cout << "\tInterest(Year): " << interest << "\n";
  std::cout << "\tInterest(Month): " << Loan::GetMonthlyInterest() << "\n";
  std::cout << "\tInstallment\t\tCapital\t\tInterest\n";

  for(const auto& row: table){
    std::cout << "\t\t" << installment
              << "\t\t" << row.first
              << "\t\t" << row.second << "\n";
  }
}

std::vector<std::pair<double,double>> Loan::GetAmortizationTable() const{

  std::vector<std::pair<double,double>> table;

  double installment = Loan::GetInstallment();
  double itm = Loan::GetMonthlyInterest();

  double capital = amount;

  for(uint i = 0; i<nperiod;++i){
    double interestPeriod = capital*itm;
    double amortizationPeriod = installment - interestPeriod;
    table.emplace_back(std::make_pair(capital,interestPeriod));
    capital -= amortizationPeriod;
  }

  return table;

}

double Loan::GetMonthlyInterest() const{
  return pow(1. + interest,(1/12.)) - 1.;
}

double Loan::GetInstallment() const{
  assert(interest != 0. and interest < 1.);
  double itm = Loan::GetMonthlyInterest();
  return amount * itm * ( pow( 1. + itm, (double)nperiod) ) / ( pow( 1. + itm, (double)nperiod) - 1. ) ;
}
