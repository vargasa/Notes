#include "loan.h"

////////////////////////////////////////////

class BalanceSheet {

protected:
  std::vector<double> assets;
  std::vector<double> liabilities;
public:
  BalanceSheet() {};
  double GetTotalLiabilities() const;
};

double BalanceSheet::GetTotalLiabilities() const{
  double total = 0.;
  for(const auto& l: liabilities){
    total += l;
  }
  return total;
};

////////////////////////////////////////////

class Bank : public BalanceSheet {

  double reserveRate;
  std::string name;
  std::vector<Loan> loans;
  std::vector<double> debits;
  std::vector<double> credits;

public:
  Bank(std::string name, double reserveRate, double initialDeposit);
  virtual void MakeDeposit(const double& amount);
  virtual double GetCash() const;
  bool GrantLoan(double amount, double interest, uint period);
  double GetTotalAssets() const;
  double MaxLoan() const;
  double GetReserveRate() const { return reserveRate; }
  std::vector<Loan> GetLoans() const { return loans; }
  std::string GetName() { return name; }
  bool PayInstallment(uint loanIdx);

};


Bank::Bank(std::string name, double reserveRate, double initialDeposit) : reserveRate(reserveRate),
  name(name)
{
  credits.emplace_back(initialDeposit);
}

bool Bank::PayInstallment(uint loanIdx){

  const double zero = 1e-3;

  assert(loanIdx < loans.size());

  Loan& loan = loans[loanIdx];

  double ins = loan.GetInstallment();
  double capital = loan.GetAmount();
  double interest = capital * loan.GetMonthlyInterest();
  credits.emplace_back(interest);
  loan.SetAmount(capital - (ins - interest));
  loan.SetPeriod(loan.GetPeriod()-1);

  if (loan.GetAmount() < zero) loans.erase(loans.begin() + loanIdx);

  return true;
}

void Bank::MakeDeposit(const double& amount){
  credits.emplace_back(amount);
  liabilities.emplace_back(amount);
}

double Bank::GetCash() const{
  double cash = 0;

  for(const auto c: credits)
    cash += c;
  for(const auto d: debits)
    cash -= d;

  assert(cash>=0);

  return cash;
}


bool Bank::GrantLoan(double amount, double interest, uint period){

  assert(amount>0);

  const double minLoan = 0.01;

  if (amount < minLoan) return false;

  double cash = GetCash();

  double l = GetTotalLiabilities();

  assert(l+amount>0.);

  if( ((cash - amount)/(l+amount)) > reserveRate ) {
    loans.emplace_back(Loan(amount,interest,period));
    debits.emplace_back(amount);
    return true;
  } else {
    std::cout << "Can't lend " << amount << std::endl;
    std::cout << "\tCash " << cash << std::endl;
    std::cout << "\tLiabilities "<< l << std::endl;
  }

  assert(cash>=0);

  return false;
}

double Bank::MaxLoan() const{
  double max = 0.;
  double cash = GetCash();
  max = (cash - GetTotalLiabilities()*reserveRate)/(1.+reserveRate);
  assert(max>0.);
  return max;
}

double Bank::GetTotalAssets() const{
  double total = 0.;
  for(const auto& l: loans){
    total += l.GetAmount();
  }
  return total + GetCash();
}
